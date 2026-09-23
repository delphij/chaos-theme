#!/bin/sh
#
# Everything that has to happen to a built site after `hugo`, in order.
#
# A site's build script calls this one and nothing else, so a step added here
# reaches every site using the theme without each of them editing their own
# build script -- and so the ordering constraints between the steps stay in one
# place rather than being rediscovered.
#
# The steps, in the order they must run:
#
#   strip_xsl_space.sh        Removes the insignificant whitespace Hugo cannot
#                             (it has no minifier for application/xslt+xml, and
#                             the generic XML one corrupts XSLT). Runs first so
#                             the next step reads the smaller files.
#
#   render_xsl_companions.sh  Renders each XSLT-styled XML output to a static
#                             HTML companion, for a server to hand to browsers
#                             once they stop running XSLT themselves.
#
# Both are idempotent, so re-running this on an already-processed directory is
# harmless. Any step failing fails the build: nothing here is optional at the
# point where a site has chosen to call it.
#
# Usage: post_build.sh [public-dir]

set -e

pub="${1:-public}"
tools=$(dirname "$0")

if [ ! -d "$pub" ]; then
	echo "post_build: no such directory: $pub" >&2
	exit 1
fi

sh "$tools/strip_xsl_space.sh" "$pub"
sh "$tools/render_xsl_companions.sh" "$pub"
