# Omarchy Manual Scraper

A Python script that downloads The Omarchy Manual, converts it to Markdown, and tracks changes between runs.

## 🚀 Quick Start

### One-liner (No Installation Required)
```bash
curl -s https://raw.githubusercontent.com/Scoutboy06/omarchy-scraper/main/run.py | python3
```

### Local Usage
```bash
git clone https://github.com/Scoutboy06/omarchy-scraper.git
cd omarchy-scraper
pip install -r requirements.txt
python run.py
```

### Install as Package
```bash
git clone https://github.com/Scoutboy06/omarchy-scraper.git
cd omarchy-scraper
python install.py
omarchy-scraper  # Use anywhere
```

## Examples

```bash
# Basic usage
python run.py

# Show available chapters
python run.py --list-links

# Custom output directory
python run.py --output-dir docs

# Test without saving
python run.py --dry-run

# Remote execution with options
curl -s https://raw.githubusercontent.com/Scoutboy06/omarchy-scraper/main/run.py | python3 - --dry-run
```

## Output

- `📁 omarchy_manual/chapters/` - Individual chapter Markdown files
- `📄 omarchy_manual/omarchy_manual_complete.md` - Combined manual (1400+ lines)

## Features

- ✅ Auto-discovers all 36 chapters
- ✅ Fast parallel processing (~20 chapters/second)
- ✅ Change detection between runs
- ✅ Progress bars and error handling
- ✅ Works locally or remotely

## Requirements

- Python 3.7+
- Dependencies: `aiohttp`, `beautifulsoup4`, `markdownify`, `tqdm`, `lxml`