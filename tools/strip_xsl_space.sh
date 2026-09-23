#!/bin/sh
#
# Strip the insignificant whitespace from the built XSLT stylesheets, in place.
#
# Why this needs its own pass: Hugo's minifier dispatches on media type and has
# nothing registered for application/xslt+xml, and the obvious workaround --
# naming the resource .xml so the XML minifier picks it up -- is wrong. That
# minifier trims the ends of text nodes that have content, and in XSLT
# <xsl:text> </xsl:text> is the only way to emit a literal space, so it
# silently turns "2026-09-18 06:40" into "2026-09-1806:40".
#
# The safe rule is narrower: remove text nodes that are entirely whitespace,
# and touch nothing else. That is exactly what an XSLT processor already does
# with a stylesheet when it loads one (XSLT 1.0 section 3.4), so removing them
# from the file cannot change what the stylesheet produces -- which is why
# xsl:strip-space, applied by an XSLT processor that understands those rules,
# is the right tool rather than a regex or a generic XML minifier. Comments go
# too: a comment in a stylesheet is never copied to the result.
#
# One thing this cannot do: xsl:strip-space is defined to ignore
# xml:space="preserve" in the document it is stripping, so a stylesheet that
# uses xml:space to protect a run of whitespace would be damaged exactly the
# way the XML minifier damages <xsl:text> </xsl:text>. Rather than quietly
# risk it, such a file is left alone -- see the guard below.
#
# Roughly 11% off each stylesheet, about 200 bytes once compressed. The point
# is less the bytes than not shipping the indentation of a source file to
# every reader of a feed.
#
# Usage: strip_xsl_space.sh [public-dir]

set -e

pub="${1:-public}"

if [ ! -d "$pub" ]; then
	echo "strip_xsl_space: no such directory: $pub" >&2
	exit 1
fi

if ! command -v xsltproc >/dev/null 2>&1; then
	echo "strip_xsl_space: xsltproc not found (FreeBSD: textproc/libxslt)" >&2
	exit 1
fi

# An identity transform, with the whitespace rules doing all the work.
# cdata-section-elements keeps the inline scripts in CDATA sections rather than
# re-escaping them, which would be correct but unreadable.
strip="${TMPDIR:-/tmp}/strip-xsl-space.$$.xsl"
trap 'rm -f "$strip"' EXIT INT TERM
cat >"$strip" <<'XSLT'
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="utf-8" indent="no"
              cdata-section-elements="script" omit-xml-declaration="no" />
  <xsl:strip-space elements="*" />
  <xsl:preserve-space elements="xsl:text" />
  <xsl:template match="comment()" priority="1" />
  <xsl:template match="@*|node()">
    <xsl:copy><xsl:apply-templates select="@*|node()" /></xsl:copy>
  </xsl:template>
</xsl:stylesheet>
XSLT

find "$pub" -type f -name '*.xsl' -print | while IFS= read -r xsl; do
	# xsl:strip-space does not honour xml:space, so a stylesheet that relies
	# on it has to be left as it is rather than silently flattened.
	if grep -q "xml:space[[:space:]]*=[[:space:]]*['\"]preserve" "$xsl"; then
		echo "strip_xsl_space: $xsl: uses xml:space=\"preserve\", left unchanged" >&2
		continue
	fi

	tmp="$xsl.$$"
	if ! xsltproc --nonet -o "$tmp" "$strip" "$xsl"; then
		rm -f "$tmp"
		exit 1
	fi
	before=$(wc -c <"$xsl")
	after=$(wc -c <"$tmp")
	mv "$tmp" "$xsl"
	echo "strip_xsl_space: $xsl $before -> $after bytes"
done
