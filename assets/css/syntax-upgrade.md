# Syntax highlighting and Hugo upgrades

Last verified against Chroma v2.27.0 (Hugo v0.166.0).

Chaos does not ship a generated Chroma stylesheet. The colours are roles
(`--syntax-keyword`, `--syntax-string`, …) defined once per mode in
`tokens.css`, and `syntax.css` maps every Chroma token class onto one of
them. A Hugo upgrade can therefore break highlighting only through Chroma's
class names or markup, never through its colours, and `hugo gen chromastyles`
output is used as a reference to check against, never pasted in.

## What an upgrade can change

| Change in Chroma | Symptom on the site | Caught by |
| :--- | :--- | :--- |
| A new token class | Those tokens render as plain text | `check_chroma.py`: unmapped |
| A class dropped | Nothing visible; dead CSS | `check_chroma.py`: stale |
| A short name moved to another token | Tokens coloured as the wrong role | `check_chroma.py`: renamed |
| Line-number or line wrapper markup | Misaligned or doubled line numbers, hanging indent broken | `check_chroma.py`: structural, then the visual pass |
| Lexer changes | Different tokens for the same code | Visual pass only |

## Procedure

1. Before upgrading, render the sample below with the current Hugo and keep
   screenshots of it in light and dark mode.
2. Upgrade Hugo, then from the site root run:

   ```sh
   python3 themes/chaos/tools/check_chroma.py
   ```

3. For each **unmapped** class, look the token up in Chroma's `types.go` and
   add the class to the role it belongs to in `syntax.css`, with its token
   name as the comment. The roles follow GitHub's grouping; when unsure, use
   the role `hugo gen chromastyles --style=github` gives the token. A class
   that should stay body text still goes in the body-text rule, so the next
   check knows it was decided rather than forgotten.
4. Delete **stale** classes, and fix **renamed** ones by moving the class to
   the role of its new token.
5. For a **structural** report, compare `hugo gen chromastyles` output for
   `lntable`, `lntd`, `lnlinks` and `line` with the `.chroma` block in
   `prose.css`, which the site and the feed share.
6. Rebuild and compare the sample with the screenshots from step 1, in both
   modes, on a wide screen (hanging line numbers) and a narrow one (numbers
   hidden), and in print preview (light colours whatever the mode).
7. When the checker is clean and the pages look right, update the version
   line at the top of this file. The checker reports a mismatch until then.

## Changing colours

Edit only the `--syntax-*` roles in `tokens.css`. Keep to traditional colours
at the values 和色大辞典 publishes (see the palette section of the README),
keep each role near its GitHub hue so code reads as it does there, and run
the checker: it fails any ink below 4.5:1 on the code ground or on a
highlighted line, in either mode.

## Sample

A post with these fences exercises most roles:

````markdown
```c {linenos=table,hl_lines=[3]}
#include <sys/param.h>
#define NBUF 16 /* buffers */
static int
foo(struct buf *bp, const char *s)
{
	if (bp == NULL || s[0] != '\n')
		return (EINVAL);
	return (0);
}
```

```python
@cache
class Node(Base):
    def walk(self, depth=0x10):
        return [f"{n!r}" for n in self.children if n is not None]
```

```html
<a href="/posts/" class="cat-link">&amp; more</a>
```

```diff
- old line
+ new line
```

```console
$ uname -r
15.0-RELEASE
```
````
