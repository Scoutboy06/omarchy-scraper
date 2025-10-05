# Omarchy Manual Scraper

A Python script to scrape The Omarchy Manual, extract chapter content, convert to Markdown, and track changes between runs.

## Features

- 🔍 **Auto-discovery**: Finds all chapter links from the base URL
- 📖 **Content extraction**: Extracts only the `<main>` element content
- 📝 **Markdown conversion**: Converts HTML to clean Markdown format
- 📁 **Individual chapters**: Saves each chapter as a separate file
- 📄 **Combined output**: Creates one big Markdown file with all chapters
- 🔄 **Change detection**: Tracks content changes between runs
- 📊 **Progress bars**: Shows progress for fetching and processing
- ⚡ **Async processing**: Processes multiple chapters concurrently

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Before running, update the configuration in `omarchy_scraper.py`:

```python
# Configuration
BASE_URL = "https://omarchy.com/manual"  # Replace with actual base URL
QUERY_PARAM = "?view=all"  # Static query parameter
```

## Usage

### Basic Usage

Run the scraper with default settings:

```bash
python omarchy_scraper.py
```

### CLI Interface

For more control, use the command-line interface:

```bash
python cli.py --help
```

Available options:
- `--url` - Custom base URL
- `--query-param` - Custom query parameter
- `--output-dir` - Custom output directory
- `--combined-output` - Custom combined file name
- `--max-concurrent` - Maximum concurrent requests
- `--dry-run` - Test run without saving files
- `--verbose` - Detailed output
- `--list-links-only` - Only show found chapter links

### Examples

```bash
# Use custom URL
python cli.py --url https://example.com/manual

# Dry run to test without saving files
python cli.py --dry-run

# Only list chapter links
python cli.py --list-links-only

# Verbose output with custom settings
python cli.py --verbose --max-concurrent 3 --output-dir my_chapters
```

The script will:
1. Fetch the base URL and find all chapter links
2. Download and process each chapter
3. Save individual Markdown files to the `chapters/` directory
4. Create a combined file `omarchy_manual_complete.md`
5. Report any changes since the last run

## Output

- `chapters/` - Directory containing individual chapter Markdown files
- `omarchy_manual_complete.md` - Combined Markdown file with all chapters
- `chapter_metadata.json` - Metadata file for change tracking (don't delete this)

## Change Detection

The script tracks content changes by calculating SHA-256 hashes of the chapter content. On subsequent runs, it will report which chapters have changed since the last execution.

## Customization

### Adjusting Chapter Link Detection

If the script doesn't find chapter links correctly, you may need to adjust the link extraction logic in the `extract_chapter_links()` method. The script tries several common selectors:

- `a[href*="chapter"]`
- `a[href*="section"]`
- `.chapter-link a`
- `.toc a`
- `nav a`
- `main a[href^="/manual/"]`

### Adjusting Content Extraction

If the main content isn't extracted correctly, you may need to modify the `extract_main_content()` method to use different selectors for your specific website structure.

### Concurrency Control

The script limits concurrent requests to 5 by default. You can adjust this in the `run()` method:

```python
semaphore = asyncio.Semaphore(5)  # Change this number
```

## Error Handling

The script includes comprehensive error handling:
- Network errors are caught and reported
- Individual chapter failures don't stop the entire process
- Graceful handling of interrupted runs (Ctrl+C)

## Requirements

- Python 3.7+
- aiohttp (async HTTP client)
- beautifulsoup4 (HTML parsing)
- markdownify (HTML to Markdown conversion)
- tqdm (progress bars)
- lxml (XML/HTML parser)