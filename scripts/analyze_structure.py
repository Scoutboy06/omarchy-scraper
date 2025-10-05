#!/usr/bin/env python3
"""
Analyze the HTML structure to better understand the chapter links.
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from config import BASE_URL, QUERY_PARAM


async def analyze_html_structure():
    """Analyze the HTML structure of the page."""
    url = f"{BASE_URL}{QUERY_PARAM}"
    print(f"🔍 Analyzing HTML structure of: {url}")
    
    headers = {'Accept': '*/*'}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"❌ Failed to fetch page: {response.status}")
                return
            
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            
            print(f"📄 Page title: {soup.title.string if soup.title else 'No title'}")
            print(f"📊 Total content length: {len(content)} characters")
            print()
            
            # Look for main content structure
            main_element = soup.find('main')
            if main_element:
                print("✅ Found <main> element")
                print(f"   Main content length: {len(str(main_element))}")
            else:
                print("❌ No <main> element found")
            
            # Look for navigation or table of contents
            nav_elements = soup.find_all('nav')
            print(f"🧭 Found {len(nav_elements)} <nav> elements")
            
            # Look for common TOC patterns
            toc_selectors = [
                '.toc', '.table-of-contents', '#toc', '#table-of-contents',
                '.sidebar', '.navigation', '.menu', '.contents'
            ]
            
            for selector in toc_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"📑 Found TOC-like element: {selector} ({len(elements)} elements)")
            
            # Analyze all links
            all_links = soup.find_all('a', href=True)
            print(f"🔗 Total links found: {len(all_links)}")
            
            # Categorize links
            internal_links = []
            external_links = []
            chapter_like_links = []
            
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if not text or len(text) < 3:
                    continue
                
                if href.startswith('http') and 'learn.omacom.io' not in href:
                    external_links.append((text, href))
                elif href.startswith('/') or href.startswith('#') or 'learn.omacom.io' in href:
                    internal_links.append((text, href))
                    
                    # Look for chapter-like patterns
                    if any(keyword in text.lower() for keyword in ['chapter', 'section', 'part', 'open ']):
                        chapter_like_links.append((text, href))
            
            print(f"🏠 Internal links: {len(internal_links)}")
            print(f"🌐 External links: {len(external_links)}")
            print(f"📚 Chapter-like links: {len(chapter_like_links)}")
            print()
            
            # Show first few chapter-like links
            print("📖 First 10 chapter-like links:")
            for i, (text, href) in enumerate(chapter_like_links[:10], 1):
                print(f"   {i:2d}. {text[:50]}{'...' if len(text) > 50 else ''}")
                print(f"       → {href}")
            
            # Look for specific patterns that might indicate real chapters
            print("\n🔍 Looking for better chapter detection patterns...")
            
            # Check for numbered sections or specific structure
            for link in all_links[:20]:  # Check first 20 links for patterns
                text = link.get_text(strip=True)
                href = link.get('href', '')
                classes = link.get('class', [])
                parent_classes = link.parent.get('class', []) if link.parent else []
                
                print(f"   Link: '{text[:30]}...' href='{href[:40]}...' classes={classes} parent_classes={parent_classes}")


if __name__ == "__main__":
    asyncio.run(analyze_html_structure())