#!/bin/sh
#
# Render every XSLT-styled XML output in a built site to a static HTML
# companion next to it: public/atom.xml -> public/atom.xml.html.
#
# Why: the feeds and the sitemap carry an <?xml-stylesheet?> instruction, and
# browsers are removing the XSLT engine that acts on it (Chrome stops running
# XSLT on stable in 158, removes it in 176; Firefox and WebKit have signalled
# the same). Rather than shipping an engine to the browser, do the transform
# here, once, at build time -- xsltproc is the same libxslt that Blink's XSLT
# implementation is built on, so the companion is what the browser would have
# produced from the same stylesheet.
#
# The server then hands the companion to browser navigations and the untouched
# XML to everything else, so a reader who opens /atom.xml still sees a page
# while feed readers and crawlers see exactly the bytes they see today. The
# stylesheet stays the single source of truth: there is no second copy of the
# design to drift out of step.
#
# Safe to skip: if a companion is missing the server falls back to serving the
# XML, which browsers that still have XSLT render themselves.
#
# The feeds take the other route and load polyxslt, which does the transform
# in the browser; a companion would only duplicate it, so a document that loads
# polyxslt gets none. What remains here is the sitemap, which has to stay a
# plain sitemaps.org document and so cannot carry a <script>.
#
# Usage: render_xsl_companions.sh [public-dir]

set -e

pub="${1:-public}"

if [ ! -d "$pub" ]; then
	echo "render_xsl_companions: no such directory: $pub" >&2
	exit 1
fi

if ! command -v xsltproc >/dev/null 2>&1; then
	echo "render_xsl_companions: xsltproc not found (FreeBSD: textproc/libxslt)" >&2
	exit 1
fi

# Locate the stylesheet an already-built document asks for. The href is a URL,
# so an absolute one carries the site's URL prefix, which is not part of the
# published path when the site lives under a subdirectory (baseURL
# ".../blog/" publishes /blog/feed.xsl to public/feed.xsl). Drop leading
# segments until the file turns up.
find_stylesheet() {
	_xml=$1
	_href=$2

	case "$_href" in
	/*)
		_rel=${_href#/}
		while [ -n "$_rel" ]; do
			if [ -f "$pub/$_rel" ]; then
				echo "$pub/$_rel"
				return 0
			fi
			case "$_rel" in
			*/*) _rel=${_rel#*/} ;;
			*) _rel= ;;
			esac
		done
		;;
	*)
		if [ -f "$(dirname "$_xml")/$_href" ]; then
			echo "$(dirname "$_xml")/$_href"
			return 0
		fi
		;;
	esac

	return 1
}

# The stylesheet is named by the document itself, so nothing here needs to know
# which outputs a site happens to build. Only the prolog is searched: a minified
# document puts the processing instruction and the root element on one line.
# That byte-bounded slice can end mid-character, which a sed running under a
# UTF-8 locale rejects as an illegal byte sequence -- hence LC_ALL=C, under
# which the ASCII-only pattern still matches exactly the same text.
find "$pub" -type f -name '*.xml' -print | while IFS= read -r xml; do
	prolog=$(head -c 2048 "$xml")

	# A document that loads polyxslt (the Atom and RSS templates)
	# transforms itself in a browser without XSLT, so it gets no companion,
	# and one left by an earlier build is removed so the server stops handing
	# it out. Matched on the <script> element in the prolog slice only: a feed
	# carries full post bodies, and a post merely mentioning polyxslt must not
	# cost its feed the companion.
	if printf '%s\n' "$prolog" |
		LC_ALL=C grep -q '<script[^>]*src="[^"]*_3p/polyxslt/'; then
		rm -f "$xml.html"
		echo "render_xsl_companions: $xml: loads polyxslt, no companion needed"
		continue
	fi

	href=$(printf '%s\n' "$prolog" |
		LC_ALL=C sed -n 's/.*<?xml-stylesheet[^?]*href="\([^"]*\)".*/\1/p' |
		head -1)

	[ -n "$href" ] || continue

	case "$href" in
	*://*)
		echo "render_xsl_companions: $xml: skipping remote stylesheet $href" >&2
		continue
		;;
	esac

	if ! xsl=$(find_stylesheet "$xml" "$href"); then
		echo "render_xsl_companions: $xml: stylesheet not found: $href" >&2
		exit 1
	fi

	# Via a temporary file, so a failed transform cannot leave a truncated
	# page where the server would serve it as the real thing.
	tmp="$xml.html.$$"
	if ! xsltproc --nonet -o "$tmp" "$xsl" "$xml"; then
		rm -f "$tmp"
		exit 1
	fi
	mv "$tmp" "$xml.html"
	echo "render_xsl_companions: $xml.html <- $xsl"
done
