# Omarchy Manual Scraper

A clean, efficient Python scraper that downloads The Omarchy Manual, converts it to Markdown, and tracks changes between runs.

## Features

- 🔍 **Auto-discovery** - Automatically finds all chapter links
-  **Markdown conversion** - Converts HTML content to clean Markdown
- 📁 **Organized output** - Individual chapter files + combined manual
- 🔄 **Change tracking** - Detects content changes between runs
- 📊 **Progress bars** - Visual progress indicators
- ⚡ **Async processing** - Fast parallel downloads
- 🛡️ **Error handling** - Robust error recovery

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the scraper:**
   ```bash
   python main.py
   ```

3. **Check the results:**
   - Individual chapters: `output/chapters/`
   - Combined manual: `output/omarchy_manual_complete.md`

## Usage

```bash
# Basic usage
python main.py

# Show available chapters without downloading
python main.py --list-links

# Test run without saving files
python main.py --dry-run

# Use custom output directory
python main.py --output-dir /path/to/output

# Verbose output
python main.py --verbose

# Show help
python main.py --help
```

## Project Structure

```
omarchy-manual-scraper/
├── src/                    # Source code
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   └── scraper.py         # Main scraper logic
├── scripts/               # Utility scripts
│   ├── test_setup.py      # Test installation
│   ├── debug_request.py   # Debug HTTP requests
│   └── analyze_structure.py # Analyze webpage structure
├── output/                # Generated files
│   ├── chapters/          # Individual chapter files
│   ├── omarchy_manual_complete.md # Combined manual
│   └── chapter_metadata.json # Change tracking data
├── main.py               # Main entry point
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Configuration

The scraper can be configured by modifying `src/config.py`:

```python
@dataclass
class Config:
    base_url: str = "https://learn.omacom.io/2/the-omarchy-manual"
    query_param: str = ""
    output_dir: Path = Path("output")
    max_concurrent: int = 5
    request_timeout: int = 30
```

## Change Detection

The scraper tracks content changes using SHA-256 hashes:

- **First run**: All chapters marked as new
- **Subsequent runs**: Only changed chapters reported
- **Metadata**: Stored in `output/chapter_metadata.json`

Example output:
```
✨ No changes detected since last run
```

Or:
```
🔄 Changed chapters since last run (2):
   • Getting_Started.md
   • Configuration.md
```

## Requirements

- Python 3.7+
- aiohttp (async HTTP client)
- beautifulsoup4 (HTML parsing)
- markdownify (HTML to Markdown conversion)
- tqdm (progress bars)

## License

MIT License - feel free to use and modify as needed.