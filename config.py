# Configuration file for Omarchy Manual Scraper

# The base URL of The Omarchy Manual
BASE_URL = "https://learn.omacom.io/2/the-omarchy-manual"

# Query parameter to append to the base URL
QUERY_PARAM = ""

# Output settings
OUTPUT_DIR = "chapters"
COMBINED_OUTPUT = "omarchy_manual_complete.md"
METADATA_FILE = "chapter_metadata.json"

# Scraping settings
MAX_CONCURRENT_REQUESTS = 5
REQUEST_TIMEOUT = 30

# User agent for HTTP requests
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"