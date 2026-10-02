# Vendorized Dependencies

This directory contains vendored third-party dependencies used by theme build and indexing tools.

## fxsjy/jieba

- **Project**: [fxsjy/jieba](https://github.com/fxsjy/jieba)
- **Version**: 0.42.1
- **License**: MIT License (see `themes/chaos/tools/vendor/jieba/LICENSE`)
- **Purpose**: Chinese word segmentation for generating static offline search indexes (`build_search_index.py`).
- **Rationale for Vendoring**:
  Avoids requiring users or CI environments to install Python packages via `pip` or manage virtual environments. It is pure Python with zero compiled dependencies or runtime build hooks.

### How to Update

To update or re-vendor `jieba` from upstream:

```bash
python3 -c "
import urllib.request, tarfile, tempfile, shutil, os

VERSION = '0.42.1'
url = f'https://github.com/fxsjy/jieba/archive/refs/tags/v{VERSION}.tar.gz'
target_dir = 'themes/chaos/tools/vendor/jieba'

with tempfile.TemporaryDirectory() as tmpdir:
    tar_path = os.path.join(tmpdir, 'jieba.tar.gz')
    urllib.request.urlretrieve(url, tar_path)
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(path=tmpdir)
    pkg = os.path.join(tmpdir, f'jieba-{VERSION}', 'jieba')
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    shutil.copytree(pkg, target_dir)
    license_src = os.path.join(tmpdir, f'jieba-{VERSION}', 'LICENSE')
    if os.path.exists(license_src):
        shutil.copy2(license_src, os.path.join(target_dir, 'LICENSE'))
print('Updated jieba to version', VERSION)
"
```

## BYVoid/OpenCC (character table only)

- **Project**: [BYVoid/OpenCC](https://github.com/BYVoid/OpenCC)
- **Version**: 1.4.2 (tag `ver.1.4.2`, commit `025f371dc76b598d77384fbdab90c937471844d8`), recorded in `opencc/VERSION`
- **License**: Apache License 2.0 (see `themes/chaos/tools/vendor/opencc/LICENSE`)
- **Purpose**: `build_search_index.py` indexes Traditional Chinese characters as their Simplified forms, so that a search in either script finds a post in either.
- **What is vendored**: one data file and what its license needs beside it. None of OpenCC's code, phrase tables or other dictionaries is here, and nothing imports `opencc`.

| File | Upstream path | Changes |
| :--- | :--- | :--- |
| `opencc/TSCharacters.txt` | `data/dictionary/TSCharacters.txt` | None |
| `opencc/LICENSE` | `LICENSE` | None |
| `opencc/AUTHORS` | `AUTHORS` | None |
| `opencc/VERSION` | — | Ours: the upstream version the three files above are from |

Upstream has no `NOTICE` file.

### How the license is met

- The copy of the license and the table's own header, which names its license and source, are kept as they came.
- No vendored file is modified, so none carries a notice of changes.
- `build_search_index.py` reads the first Simplified form of each character and writes a part of those pairs into the search index a site publishes. That part is a derivative of the table, so each index that has it carries a `foldCredit` string naming OpenCC, the version, its authors' copyright and the license with its URL.
- The theme's `NOTICE` lists OpenCC with the other third-party software.

### How to Update

```bash
python3 -c "
import urllib.request, tarfile, tempfile, shutil, os

VERSION = '1.4.2'
url = f'https://github.com/BYVoid/OpenCC/archive/refs/tags/ver.{VERSION}.tar.gz'
target_dir = 'themes/chaos/tools/vendor/opencc'

with tempfile.TemporaryDirectory() as tmpdir:
    tar_path = os.path.join(tmpdir, 'opencc.tar.gz')
    urllib.request.urlretrieve(url, tar_path)
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(path=tmpdir)
    src = os.path.join(tmpdir, f'OpenCC-ver.{VERSION}')
    os.makedirs(target_dir, exist_ok=True)
    shutil.copy2(os.path.join(src, 'data', 'dictionary', 'TSCharacters.txt'), target_dir)
    for name in ('LICENSE', 'AUTHORS'):
        shutil.copy2(os.path.join(src, name), target_dir)
    with open(os.path.join(target_dir, 'VERSION'), 'w') as f:
        f.write(VERSION + '\\n')
print('Updated the OpenCC character table to version', VERSION)
"
```

Then update the version and commit above, in `NOTICE`, and in the dependency lists of `README.md`, `AGENTS.md` and `CLAUDE.md`, and check upstream for a `NOTICE` file, which would have to be vendored too. Rebuild the search index: a site's index holds pairs from the table it was built with.
