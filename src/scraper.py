#!/usr/bin/env python3
"""
Omarchy Manual Scraper

A clean, efficient scraper for The Omarchy Manual that converts content to Markdown
and tracks changes between runs.
"""

import asyncio
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from tqdm import tqdm

from .config import Config


class ScraperError(Exception):
    """Custom exception for scraper errors."""
    pass


class OmarchyScraper:
    """Main scraper class for The Omarchy Manual."""
    
    def __init__(self, config: Config, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.session: Optional[aiohttp.ClientSession] = None
        self.metadata: Dict = {}
        self._load_metadata()
    
    def _load_metadata(self):
        """Load previously saved chapter metadata."""
        metadata_file = self.config.output_dir / self.config.metadata_file
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load metadata file: {e}")
                self.metadata = {}
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """Save chapter metadata to file."""
        if self.dry_run:
            print(f"   Would save metadata: {self.config.metadata_file}")
            return
            
        metadata_file = self.config.output_dir / self.config.metadata_file
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save metadata file: {e}")
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content for change detection."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _sanitize_filename(self, title: str) -> str:
        """Convert chapter title to safe filename."""
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', title)
        sanitized = re.sub(r'\s+', '_', sanitized)
        sanitized = sanitized.strip('._')
        
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized
    
    async def _create_session(self):
        """Create HTTP session with appropriate headers."""
        # Use minimal headers - the server rejects complex browser headers
        headers = {'Accept': '*/*'}
        timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
        self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
    
    async def _close_session(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
    
    async def _fetch_page(self, url: str) -> str:
        """Fetch a single page and return its content."""
        if not self.session:
            raise ScraperError("Session not initialized")
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ScraperError(
                        f"HTTP {response.status} {response.reason} for {url}. "
                        f"Response: {error_text[:200]}..."
                    )
                return await response.text()
        except aiohttp.ClientError as e:
            raise ScraperError(f"Failed to fetch {url}: {e}")
        except Exception as e:
            raise ScraperError(f"Unexpected error fetching {url}: {e}")
    
    async def extract_chapter_links(self) -> List[Tuple[str, str]]:
        """
        Extract chapter links from the base URL.
        Returns list of (chapter_title, chapter_url) tuples.
        """
        print("🔍 Extracting chapter links from base URL...")
        
        full_url = f"{self.config.base_url}{self.config.query_param}"
        try:
            content = await self._fetch_page(full_url)
        except ScraperError as e:
            raise ScraperError(f"Failed to fetch base page: {e}")
        
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
                        full_href = urljoin(self.config.base_url, href)
                    elif href.startswith('http'):
                        full_href = href
                    else:
                        full_href = urljoin(full_url, href)
                    
                    # Filter for actual chapters
                    if (full_href not in [url for _, url in chapter_links] and 
                        '/the-omarchy-manual/' in full_href and
                        clean_title not in ['', 'Open']):
                        chapter_links.append((clean_title, full_href))
        
        if not chapter_links:
            raise ScraperError("No chapter links found. The website structure may have changed.")
        
        print(f"✅ Found {len(chapter_links)} chapter links")
        return chapter_links
    
    async def _extract_content(self, html: str) -> str:
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
            raise ScraperError("Could not find main content element")
        
        # Remove unwanted elements
        for element in main_element.find_all(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Convert to markdown
        markdown_content = md(str(main_element), heading_style="ATX")
        
        # Clean up markdown
        markdown_content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)
        return markdown_content.strip()
    
    async def _process_chapter(self, title: str, url: str, semaphore: asyncio.Semaphore) -> Tuple[str, str, bool]:
        """
        Process a single chapter: fetch, extract, convert to markdown.
        Returns (filename, content, changed).
        """
        async with semaphore:
            try:
                # Fetch and process content
                html_content = await self._fetch_page(url)
                markdown_content = await self._extract_content(html_content)
                
                # Calculate content hash and check for changes
                content_hash = self._calculate_hash(markdown_content)
                filename = f"{self._sanitize_filename(title)}.md"
                
                old_hash = self.metadata.get(url, {}).get('hash', '')
                changed = content_hash != old_hash
                
                # Update metadata
                self.metadata[url] = {
                    'title': title,
                    'filename': filename,
                    'hash': content_hash,
                    'last_updated': datetime.now().isoformat(),
                    'url': url
                }
                
                return filename, markdown_content, changed
                
            except Exception as e:
                raise ScraperError(f"Error processing chapter '{title}': {e}")
    
    async def run(self) -> None:
        """Main execution method."""
        print("🚀 Starting Omarchy Manual Scraper")
        print(f"📁 Output directory: {self.config.output_dir.absolute()}")
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be saved")
        
        try:
            # Ensure output directories exist
            self.config.output_dir.mkdir(parents=True, exist_ok=True)
            self.config.chapters_dir.mkdir(parents=True, exist_ok=True)
            
            await self._create_session()
            
            # Step 1: Extract chapter links
            chapter_links = await self.extract_chapter_links()
            
            # Step 2: Process chapters with progress bar
            print("\n📖 Processing chapters...")
            
            semaphore = asyncio.Semaphore(self.config.max_concurrent)
            tasks = [
                self._process_chapter(title, url, semaphore)
                for title, url in chapter_links
            ]
            
            # Execute with progress bar, preserving order
            results_dict = {}
            changed_chapters = []
            
            with tqdm(total=len(tasks), desc="Processing chapters") as pbar:
                for coro in asyncio.as_completed(tasks):
                    try:
                        filename, content, changed = await coro
                        
                        # Find original index to preserve order
                        for i, (title, url) in enumerate(chapter_links):
                            if self._sanitize_filename(title) + ".md" == filename:
                                results_dict[i] = (filename, content)
                                break
                        
                        if changed:
                            changed_chapters.append(filename)
                        
                        # Save individual chapter file
                        chapter_file = self.config.chapters_dir / filename
                        if self.dry_run:
                            print(f"   Would save: {chapter_file}")
                        else:
                            with open(chapter_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                        
                        pbar.update(1)
                        
                    except ScraperError as e:
                        print(f"\n⚠️  {e}")
                        pbar.update(1)
                        continue
            
            # Sort results by original order
            results = [results_dict[i] for i in sorted(results_dict.keys())]
            
            # Step 3: Create combined file
            print(f"\n📝 Creating combined Markdown file: {self.config.combined_output}")
            await self._create_combined_file(results)
            
            # Step 4: Save metadata and report
            self._save_metadata()
            self._report_results(len(results), changed_chapters)
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Scraping interrupted by user")
        except Exception as e:
            print(f"\n❌ Error during scraping: {e}")
            raise
        finally:
            await self._close_session()
    
    async def _create_combined_file(self, results: List[Tuple[str, str]]) -> None:
        """Create the combined Markdown file."""
        combined_content = [
            "# The Omarchy Manual - Complete\n",
            f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
            "---\n"
        ]
        
        for filename, content in results:
            chapter_title = filename.replace('.md', '').replace('_', ' ')
            combined_content.extend([
                f"\n# {chapter_title}\n",
                content,
                "\n---\n"
            ])
        
        combined_file = self.config.output_dir / self.config.combined_output
        if self.dry_run:
            print(f"   Would save combined file: {combined_file.absolute()}")
            print(f"   Combined content length: {len(''.join(combined_content))} characters")
        else:
            with open(combined_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(combined_content))
    
    def _report_results(self, num_chapters: int, changed_chapters: List[str]) -> None:
        """Report the results of the scraping operation."""
        print(f"\n✅ Successfully processed {num_chapters} chapters")
        
        if not self.dry_run:
            print(f"📁 Individual chapters saved to: {self.config.chapters_dir.absolute()}")
            print(f"📄 Combined file saved as: {(self.config.output_dir / self.config.combined_output).absolute()}")
        
        if changed_chapters:
            print(f"\n🔄 Changed chapters since last run ({len(changed_chapters)}):")
            for chapter in changed_chapters:
                print(f"   • {chapter}")
        else:
            print("\n✨ No changes detected since last run")