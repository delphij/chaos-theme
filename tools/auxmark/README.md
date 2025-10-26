# auxmark - Auxiliary Markdown Processing Tool

A modular tool for automating content maintenance tasks in Hugo sites. Scans Markdown files under git control and performs preprocessing operations like caching external embeds, downloading remote images, and converting files to Hugo page bundles.

## Features

- **Git-aware scanning**: Only processes Markdown files tracked by git
- **Modular architecture**: Easy to extend with new processors
- **Intelligent caching**: Checks cache age before re-downloading
- **Dry-run mode**: Preview changes without modifying files
- **Hugo integration**: Auto-detects Hugo site configuration

### Available Modules

#### `tweet_downloader`
Detects Hugo X/Twitter shortcodes and pre-caches embed data locally.

- Finds `{{< x user="..." id="..." >}}` shortcodes
- Downloads oEmbed data from X's public API
- Saves to `data/x_embeds/` for offline use
- Auto-detects Hugo's `languageCode` for localized embeds
- Sanitizes HTML (removes tracking scripts)
- Respects cache age (default: 30 days)

## Requirements

- Python 3.11 or later
- Git repository
- Hugo site (for tweet_downloader module)

## Installation

The tool is included in the Chaos theme under `themes/chaos/tools/auxmark/`.

No additional installation required - it uses Python standard library only.

## Usage

### Basic Usage

Run from your Hugo site root:

```bash
python3 themes/chaos/tools/auxmark.py
```

This will:
1. Scan all `*.md` files under git control
2. Run all registered modules
3. Perform preprocessing (downloads, caching)
4. Execute post-processing (file rewrites)

### Command-Line Options

```bash
# Show what would be done without making changes
python3 themes/chaos/tools/auxmark.py --dry-run

# Enable verbose output
python3 themes/chaos/tools/auxmark.py --verbose

# Run specific module only
python3 themes/chaos/tools/auxmark.py --module tweet

# Use custom config file
python3 themes/chaos/tools/auxmark.py --config /path/to/.auxmark.toml

# Combine options
python3 themes/chaos/tools/auxmark.py --verbose --dry-run
```

### Configuration File

Create `.auxmark.toml` in your Hugo site root (alongside `hugo.toml` or `config.toml`) to customize module behavior:

```toml
[general]
verbose = false
dry_run = false

[modules.image_localizer]
enabled = true
convert_to_webp = true
max_retries = 3
retry_delay = 1.0
retry_backoff = 2.0
timeout = 30

[modules.tweet_downloader]
enabled = true
cache_max_age_days = 30
defang = true
lang = "auto"
data_dir = "data/x_embeds"

[worker]
max_workers = 4
rate_limit_delay = 1.0
```

**Config file discovery order:**
1. Hugo site root (e.g., `/path/to/site/.auxmark.toml`)
2. Theme directory (e.g., `/path/to/site/themes/chaos/.auxmark.toml`)
3. Built-in defaults

**Note:** Command-line options (`--verbose`, `--dry-run`) always override config file settings.

See `.auxmark.toml.example` in the theme directory for a complete example with comments.

### Module Selection

Run specific modules:
- `--module tweet` - Tweet downloader only
- `--module image` - Image localizer only
- `--module tweet,image` - Both modules

## How It Works

### Processing Pipeline

1. **Scan**: Find all `.md` files using `git ls-files`
2. **Parse**: Read each file line by line
3. **Probe**: Each module checks if it's interested in a line
4. **Action**: Module returns one of:
   - `IGNORE` - Not interested
   - `TAG` - Process later (postprocessing only)
   - `TAG_WITH_PREPROCESS_ONLY` - Download/fetch only, no rewrite
   - `TAG_WITH_PREPROCESS_AND_POSTPROCESS` - Download first, then rewrite
   - `EXPAND` - Convert `file.md` → `file/index.md` using `git mv` (Hugo page bundle)
5. **Preprocess**: Execute async jobs (downloads, API calls)
6. **Postprocess**: Rewrite files if needed

**Note on EXPAND action**: When a file is expanded from `post.md` to `post/index.md`, the tool:
- Uses `git mv` for better history tracking (git recognizes it as a rename)
- Marks the old path (`post.md`) as processed to skip it if encountered again
- Queues the new path (`post/index.md`) for normal processing
- Discards any pending jobs for the old path (requeued for new path)

### Module Architecture

Each module inherits from `BaseModule`:

```python
class MyModule(BaseModule):
    name = "my_module"
    regex = re.compile(r".*")  # Pattern to match lines

    def probe(self, file_path, line_no, line):
        """
        Return (Action, metadata) for this line.
        Metadata is passed to preprocess/postprocess methods.
        """

    def preprocess(self, job):
        """
        Execute async work (download, fetch, API calls).
        Job contains: file_path, line_no, line, metadata.
        Returns: True if successful, False otherwise.
        """

    def postprocess(self, file_path, line_no, line, metadata):
        """
        Rewrite a single line (line-oriented postprocessing).
        Receives original line and metadata from probe phase.
        Returns: Modified line (or original if no changes).
        """
```

**Key Design**: Postprocessing is **line-oriented**, not file-oriented. Modules receive and return individual lines, making it easier to handle multiple matches per line (e.g., multiple images in one line).

## Examples

### Example 1: Cache All Tweets

```bash
# Dry-run to see what would be cached
python3 themes/chaos/tools/auxmark.py --dry-run --verbose --module tweet

# Actually cache the tweets
python3 themes/chaos/tools/auxmark.py --module tweet
```

Output:
```
[auxmark] Scanned 2068 files
[auxmark] Running 1 preprocessing jobs...
  Fetching tweet 404015814665195520...
  ✓ Tweet 404015814665195520 cached successfully
[auxmark] Done!
```

### Example 2: Check What Would Change

```bash
python3 themes/chaos/tools/auxmark.py --dry-run --verbose
```

This shows all detected patterns without making changes.

## Assumptions

1. **Git repository**: Tool must run inside a git repository
2. **Hugo site structure**: Expected directories:
   - `content/` - Markdown files
   - `data/` - Cache storage
   - Hugo config file at root (`hugo.toml` or `config.toml`)
3. **Running location**: Execute from Hugo site root, not theme directory

## Cache Management

### Tweet Cache

Location: `data/x_embeds/`

Files created:
- `{tweet_id}.json` - Full oEmbed response
- `{tweet_id}.html` - Sanitized HTML (scripts removed)

Cache age:
- Default: 30 days
- Automatically skips if cache is fresh
- Use standalone `fetch_x_embed.py --refresh` to force update

## Troubleshooting

### "Not in a git repository"
- Ensure you're running from inside a git repository
- Run `git status` to verify

### "No markdown files found"
- Check that files are tracked: `git ls-files '*.md'`
- Add files to git if needed: `git add content/`

### Module doesn't detect content
- Use `--verbose` to see what's being scanned
- Check regex pattern in module code
- Verify shortcode syntax matches expected format

## Development

### Adding a New Module

1. Create `auxmark/modules/your_module.py`
2. Inherit from `BaseModule`
3. Implement `probe()`, `preprocess()`, `postprocess()`
4. Register in `main.py`:
   ```python
   from .modules import YourModule
   ModuleRegistry.register(YourModule)
   ```

### Testing

Run the test suite to verify functionality without production data:

```bash
python3 themes/chaos/tools/auxmark/test_auxmark.py
```

The test suite:
- Creates temporary Hugo sites with sample content
- Generates Markdown files with tweet shortcodes
- Tests dry-run mode, module selection, git-awareness
- Cleans up automatically after each test

Manual testing with verbose and dry-run:

```bash
python3 themes/chaos/tools/auxmark.py --verbose --dry-run
```

### Directory Structure

```
tools/auxmark/
├── __init__.py         # Package initialization
├── core.py             # BaseModule, Action, ModuleRegistry
├── scanner.py          # Git-aware file discovery
├── processor.py        # Main processing loop
├── main.py             # CLI entrypoint
└── modules/
    ├── __init__.py
    └── tweet_downloader.py
```

## Related Tools

- `fetch_x_embed.py` - Standalone tweet caching tool
  - Can be used independently for manual caching
  - Integrated as module interface for auxmark
  - Supports batch processing from file

## License

Apache 2.0 License - see LICENSE file for details.

## See Also

- Hugo documentation: https://gohugo.io/
- Chaos theme README: `../../README.md`
