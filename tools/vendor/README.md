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
