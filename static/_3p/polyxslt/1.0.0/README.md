# polyxslt

- **Project**: [polyxslt](https://github.com/delphij/polyxslt)
- **Version**: 1.0.0 (release tag `v1.0.0`)
- **License**: MIT (see `LICENSE`)
- **Purpose**: renders the Atom and RSS feeds through `feed.xsl` in a browser
  that no longer runs XSLT itself. Loaded by `layouts/index.atom.xml` and
  `layouts/index.rss.xml`; a browser that still has XSLT never requests it.

`xslt-polyfill.min.js` is the release asset of the same name, unmodified:

```
a0003273f787c459466bcaec0e1910c0acbefdd397e4b9c8e227831225a103be  xslt-polyfill.min.js
```

## How to Update

```bash
VERSION=1.0.0
DEST="themes/chaos/static/_3p/polyxslt/${VERSION}"

mkdir -p "${DEST}"
gh release download "v${VERSION}" -R delphij/polyxslt \
  -p xslt-polyfill.min.js -p SHA256SUMS -D "${DEST}"
(cd "${DEST}" && grep ' xslt-polyfill.min.js$' SHA256SUMS | shasum -a 256 -c - && rm SHA256SUMS)
curl -sSL -o "${DEST}/LICENSE" \
  "https://raw.githubusercontent.com/delphij/polyxslt/v${VERSION}/LICENSE"
```

Then change the version in the two feed templates (`grep -rl polyxslt/ layouts`)
and update this file, `NOTICE` and the dependency lists.
