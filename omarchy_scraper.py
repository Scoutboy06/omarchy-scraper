#!/usr/bin/env python3
"""
Omarchy Manual Scraper

This script scrapes The Omarchy Manual, extracts chapter content,
converts to Markdown, and tracks changes between runs.
"""

import asyncio
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from tqdm import tqdm

# Import configuration
from config import (
    BASE_URL, QUERY_PARAM, OUTPUT_DIR, COMBINED_OUTPUT, METADATA_FILE,
    MAX_CONCURRENT_REQUESTS, REQUEST_TIMEOUT, USER_AGENT
)

# Convert OUTPUT_DIR to Path object
OUTPUT_DIR = Path(OUTPUT_DIR)

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)


class OmarchyScraperError(Exception):
    """Custom exception for scraper errors."""
    pass


class OmarchyScraper:
    def __init__(self, dry_run: bool = False):
        self.session: Optional[aiohttp.ClientSession] = None
        self.chapter_metadata: Dict = {}
        self.dry_run = dry_run
        self.load_metadata()
    
    def load_metadata(self):
        """Load previously saved chapter metadata."""
        if Path(METADATA_FILE).exists():
            try:
                with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                    self.chapter_metadata = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load metadata file: {e}")
                self.chapter_metadata = {}
        else:
            self.chapter_metadata = {}
    
    def save_metadata(self):
        """Save chapter metadata to file."""
        try:
            with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.chapter_metadata, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save metadata file: {e}")
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content for change detection."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    async def create_session(self):
        """Create aiohttp session with appropriate headers."""
        # Use minimal headers - the server rejects complex browser headers
        headers = {
            'Accept': '*/*',
        }
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
    
    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str) -> str:
        """Fetch a single page and return its content."""
        if not self.session:
            raise OmarchyScraperError("Session not initialized")
        
        try:
            async with self.session.get(url) as response:
                # Print more detailed error information
                if response.status != 200:
                    error_text = await response.text()
                    raise OmarchyScraperError(
                        f"HTTP {response.status} {response.reason} for {url}. "
                        f"Response: {error_text[:200]}..."
                    )
                return await response.text()
        except aiohttp.ClientError as e:
            raise OmarchyScraperError(f"Failed to fetch {url}: {e}")
        except Exception as e:
            raise OmarchyScraperError(f"Unexpected error fetching {url}: {e}")
    
    async def extract_chapter_links(self) -> List[Tuple[str, str]]:
        """
        Extract chapter links from the base URL.
        Returns list of (chapter_title, chapter_url) tuples.
        """
        print("🔍 Extracting chapter links from base URL...")
        
        full_url = f"{BASE_URL}{QUERY_PARAM}"
        try:
            content = await self.fetch_page(full_url)
        except OmarchyScraperError as e:
            raise OmarchyScraperError(f"Failed to fetch base page: {e}")
        
        soup = BeautifulSoup(content, 'html.parser')
        
        chapter_links = []
        
        # Look for TOC links with class 'toc__link' - these are the real chapters
        toc_links = soup.select('a.toc__link')
        
        if toc_links:
            print(f"🎯 Found {len(toc_links)} TOC links, filtering for chapters...")
            
            for link in toc_links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if href and text:
                    # Clean up the chapter title (remove "Open " prefix)
                    clean_title = text.replace('Open ', '') if text.startswith('Open ') else text
                    
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        full_href = urljoin(BASE_URL, href)
                    elif href.startswith('http'):
                        full_href = href
                    else:
                        full_href = urljoin(full_url, href)
                    
                    # Filter out duplicates and ensure it's a chapter page
                    if (full_href not in [url for _, url in chapter_links] and 
                        '/the-omarchy-manual/' in full_href and
                        clean_title not in ['', 'Open']):
                        chapter_links.append((clean_title, full_href))
        
        # Fallback: if no TOC links found, use original logic
        if not chapter_links:
            print("⚠️  No TOC links found, falling back to general link detection...")
            
            # Common patterns for chapter links
            link_selectors = [
                'a[href*="chapter"]',
                'a[href*="section"]',
                '.chapter-link a',
                '.toc a',
                'nav a',
                'main a[href^="/manual/"]'
            ]
            
            for selector in link_selectors:
                links = soup.select(selector)
                if links:
                    for link in links:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        
                        if href and text:
                            # Convert relative URLs to absolute
                            if href.startswith('/'):
                                full_href = urljoin(BASE_URL, href)
                            elif href.startswith('http'):
                                full_href = href
                            else:
                                full_href = urljoin(full_url, href)
                            
                            # Basic filtering to avoid duplicates and irrelevant links
                            if full_href not in [url for _, url in chapter_links]:
                                chapter_links.append((text, full_href))
                    break  # Use first successful selector
            
            if not chapter_links:
                # Final fallback: look for any links in main content
                main_content = soup.find('main') or soup.find('body')
                if main_content:
                    for link in main_content.find_all('a', href=True):
                        href = link['href']
                        text = link.get_text(strip=True)
                        
                        if href and text and len(text) > 5:  # Filter very short text
                            if href.startswith('/'):
                                full_href = urljoin(BASE_URL, href)
                            elif href.startswith('http'):
                                full_href = href
                            else:
                                full_href = urljoin(full_url, href)
                            
                            if full_href not in [url for _, url in chapter_links]:
                                chapter_links.append((text, full_href))
        
        if not chapter_links:
            raise OmarchyScraperError("No chapter links found. You may need to adjust the link extraction logic.")
        
        print(f"✅ Found {len(chapter_links)} chapter links")
        return chapter_links
    
    def sanitize_filename(self, title: str) -> str:
        """Convert chapter title to safe filename."""
        # Remove or replace invalid filename characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', title)
        sanitized = re.sub(r'\s+', '_', sanitized)
        sanitized = sanitized.strip('._')
        
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized
    
    async def extract_main_content(self, html: str) -> str:
        """Extract content from <main> element and convert to Markdown."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to find main content
        main_element = soup.find('main')
        if not main_element:
            # Fallback selectors
            main_element = (
                soup.find('div', class_=re.compile(r'main|content|article')) or
                soup.find('article') or
                soup.find('div', id=re.compile(r'main|content|article')) or
                soup.find('body')
            )
        
        if not main_element:
            raise OmarchyScraperError("Could not find main content element")
        
        # Remove unwanted elements
        for element in main_element.find_all(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Convert to markdown
        markdown_content = md(str(main_element), heading_style="ATX")
        
        # Clean up markdown
        markdown_content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)
        markdown_content = markdown_content.strip()
        
        return markdown_content
    
    async def process_chapter(self, title: str, url: str, semaphore: asyncio.Semaphore) -> Tuple[str, str, bool]:
        """
        Process a single chapter: fetch, extract, convert to markdown.
        Returns (filename, content, changed).
        """
        async with semaphore:
            try:
                # Fetch chapter content
                html_content = await self.fetch_page(url)
                
                # Extract and convert to markdown
                markdown_content = await self.extract_main_content(html_content)
                
                # Calculate content hash
                content_hash = self.calculate_content_hash(markdown_content)
                
                # Create filename
                filename = f"{self.sanitize_filename(title)}.md"
                
                # Check if content has changed
                chapter_key = url
                old_hash = self.chapter_metadata.get(chapter_key, {}).get('hash', '')
                changed = content_hash != old_hash
                
                # Update metadata
                self.chapter_metadata[chapter_key] = {
                    'title': title,
                    'filename': filename,
                    'hash': content_hash,
                    'last_updated': datetime.now().isoformat(),
                    'url': url
                }
                
                return filename, markdown_content, changed
                
            except Exception as e:
                raise OmarchyScraperError(f"Error processing chapter '{title}': {e}")
    
    async def run(self):
        """Main execution method."""
        print("🚀 Starting Omarchy Manual Scraper")
        print(f"📁 Output directory: {OUTPUT_DIR.absolute()}")
        
        try:
            await self.create_session()
            
            # Step 1: Extract chapter links
            chapter_links = await self.extract_chapter_links()
            
            # Step 2: Process chapters with progress bar and concurrency control
            print("\n📖 Processing chapters...")
            
            # Limit concurrent requests
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
            
            # Create tasks for parallel processing
            tasks = [
                self.process_chapter(title, url, semaphore)
                for title, url in chapter_links
            ]
            
            # Execute with progress bar
            results_dict = {}  # Store results with original order info
            changed_chapters = []
            
            # Use asyncio.as_completed with tqdm
            with tqdm(total=len(tasks), desc="Processing chapters") as pbar:
                for coro in asyncio.as_completed(tasks):
                    try:
                        filename, content, changed = await coro
                        
                        # Find the original index to preserve order
                        original_index = None
                        for i, (title, url) in enumerate(chapter_links):
                            if self.sanitize_filename(title) + ".md" == filename:
                                original_index = i
                                break
                        
                        if original_index is not None:
                            results_dict[original_index] = (filename, content)
                        
                        if changed:
                            changed_chapters.append(filename)
                        
                        # Save individual chapter file
                        chapter_file = OUTPUT_DIR / filename
                        if self.dry_run:
                            print(f"   Would save: {chapter_file}")
                        else:
                            with open(chapter_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                        
                        pbar.update(1)
                        
                    except OmarchyScraperError as e:
                        print(f"\n⚠️  {e}")
                        pbar.update(1)
                        continue
            
            # Sort results by original order
            results = [results_dict[i] for i in sorted(results_dict.keys())]
            
            # Step 3: Create combined file
            print(f"\n📝 Creating combined Markdown file: {COMBINED_OUTPUT}")
            
            combined_content = []
            combined_content.append("# The Omarchy Manual - Complete\n")
            combined_content.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            combined_content.append("---\n")
            
            for filename, content in results:
                chapter_title = filename.replace('.md', '').replace('_', ' ')
                combined_content.append(f"\n# {chapter_title}\n")
                combined_content.append(content)
                combined_content.append("\n---\n")
            
            if self.dry_run:
                print(f"   Would save combined file: {Path(COMBINED_OUTPUT).absolute()}")
                print(f"   Combined content length: {len(''.join(combined_content))} characters")
            else:
                with open(COMBINED_OUTPUT, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(combined_content))
            
            # Step 4: Save metadata and report changes
            if not self.dry_run:
                self.save_metadata()
            else:
                print(f"   Would save metadata: {METADATA_FILE}")
            
            # Report results
            print(f"\n✅ Successfully processed {len(results)} chapters")
            print(f"📁 Individual chapters saved to: {OUTPUT_DIR.absolute()}")
            print(f"📄 Combined file saved as: {Path(COMBINED_OUTPUT).absolute()}")
            
            if changed_chapters:
                print(f"\n🔄 Changed chapters since last run ({len(changed_chapters)}):")
                for chapter in changed_chapters:
                    print(f"   • {chapter}")
            else:
                print("\n✨ No changes detected since last run")
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Scraping interrupted by user")
        except Exception as e:
            print(f"\n❌ Error during scraping: {e}")
            raise
        finally:
            await self.close_session()


async def main():
    """Entry point for the scraper."""
    scraper = OmarchyScraper()
    await scraper.run()


if __name__ == "__main__":
    asyncio.run(main())