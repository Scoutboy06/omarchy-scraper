#!/usr/bin/env python3
"""
Test script to validate the scraper setup and configuration.
"""

import asyncio
import sys
from pathlib import Path

# Test imports
try:
    import aiohttp
    import bs4
    import markdownify
    import tqdm
    print("✅ All required packages are installed")
except ImportError as e:
    print(f"❌ Missing package: {e}")
    sys.exit(1)

# Test configuration
try:
    from config import BASE_URL, QUERY_PARAM, OUTPUT_DIR
    print(f"✅ Configuration loaded successfully")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Query param: {QUERY_PARAM}")
    print(f"   Output dir: {OUTPUT_DIR}")
except ImportError as e:
    print(f"❌ Configuration error: {e}")
    sys.exit(1)

# Test basic functionality
async def test_session():
    """Test that we can create an HTTP session."""
    try:
        async with aiohttp.ClientSession() as session:
            # Test with a simple request
            async with session.get("https://httpbin.org/get") as response:
                if response.status == 200:
                    print("✅ HTTP client working correctly")
                else:
                    print(f"⚠️  HTTP test returned status {response.status}")
    except Exception as e:
        print(f"❌ HTTP client error: {e}")

def test_html_parsing():
    """Test HTML parsing and markdown conversion."""
    try:
        html = "<main><h1>Test</h1><p>This is a test.</p></main>"
        soup = bs4.BeautifulSoup(html, 'html.parser')
        main_content = soup.find('main')
        markdown = markdownify.markdownify(str(main_content), heading_style="ATX")
        
        if "# Test" in markdown and "This is a test." in markdown:
            print("✅ HTML parsing and markdown conversion working")
        else:
            print("⚠️  HTML parsing test produced unexpected output:")
            print(f"   Generated markdown: {repr(markdown)}")
    except Exception as e:
        print(f"❌ HTML parsing error: {e}")

async def main():
    """Run all tests."""
    print("🧪 Testing Omarchy Scraper Setup\n")
    
    await test_session()
    test_html_parsing()
    
    print(f"\n✅ Setup validation complete!")
    print(f"📝 To run the scraper, execute: python omarchy_scraper.py")
    print(f"⚙️  To modify settings, edit: config.py")

if __name__ == "__main__":
    asyncio.run(main())