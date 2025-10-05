#!/usr/bin/env python3
"""
Example usage of the Omarchy scraper with a test URL.

This demonstrates the scraper functionality using a test website.
For real usage, update the BASE_URL in config.py to point to The Omarchy Manual.
"""

import asyncio
import tempfile
from pathlib import Path

# Update config for demo
import config
original_base_url = config.BASE_URL
original_query_param = config.QUERY_PARAM
original_output_dir = config.OUTPUT_DIR

# Use a test URL for demonstration
config.BASE_URL = "https://httpbin.org"
config.QUERY_PARAM = "/html"
config.OUTPUT_DIR = "demo_chapters"

from omarchy_scraper import OmarchyScraper


async def demo_scraper():
    """Demonstrate the scraper with a simple test."""
    print("🎯 Running Omarchy Scraper Demo")
    print(f"🔗 Using test URL: {config.BASE_URL}{config.QUERY_PARAM}")
    print("📝 Note: This is just a demo. For real usage, update config.py with the actual Omarchy Manual URL.\n")
    
    # Create a simple mock scraper for demo
    scraper = OmarchyScraper()
    
    try:
        await scraper.create_session()
        
        # Test basic HTTP functionality
        test_content = await scraper.fetch_page(f"{config.BASE_URL}{config.QUERY_PARAM}")
        
        if test_content:
            print("✅ Successfully fetched test page")
            print(f"📄 Content length: {len(test_content)} characters")
            
            # Test content extraction
            try:
                markdown = await scraper.extract_main_content(test_content)
                print("✅ Successfully extracted and converted content to Markdown")
                print(f"📝 Markdown length: {len(markdown)} characters")
                
                # Show first few lines
                lines = markdown.split('\n')[:5]
                print("📋 First few lines of converted content:")
                for line in lines:
                    if line.strip():
                        print(f"   {line}")
                
            except Exception as e:
                print(f"⚠️  Content extraction demo failed: {e}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    
    finally:
        await scraper.close_session()
    
    print("\n" + "="*50)
    print("🎯 Demo Complete!")
    print("\n📖 To use with The Omarchy Manual:")
    print("   1. Update config.py with the correct BASE_URL")
    print("   2. Run: python omarchy_scraper.py")
    print("\n📚 The scraper will:")
    print("   • Find all chapter links automatically")
    print("   • Download and convert each chapter to Markdown") 
    print("   • Save individual files and a combined file")
    print("   • Track changes between runs")
    print("   • Show progress bars during processing")


if __name__ == "__main__":
    asyncio.run(demo_scraper())