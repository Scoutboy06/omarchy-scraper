#!/usr/bin/env python3
"""
Omarchy Manual Scraper - Universal Entry Point

This script works both locally and remotely:
- Local usage: python run.py [options]
- Remote usage: curl -s https://raw.githubusercontent.com/Scoutboy06/omarchy-scraper/main/run.py | python3
"""

import asyncio
import sys
import tempfile
import urllib.request
import subprocess
from pathlib import Path


def is_remote_execution():
    """Check if this script is being executed remotely (piped from curl/wget)."""
    # When piped, stdin is not a TTY and __file__ might not be available
    try:
        # If we can get the file path and it exists, we're running locally
        return not Path(__file__).exists()
    except (NameError, OSError):
        # __file__ not available or path doesn't exist = remote execution
        return True


def check_dependencies():
    """Check if required packages are available."""
    required = ["aiohttp", "bs4", "markdownify", "tqdm"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing


def install_dependencies():
    """Install required packages."""
    packages = [
        "aiohttp>=3.8.0",
        "beautifulsoup4>=4.11.0", 
        "markdownify>=0.11.0",
        "tqdm>=4.64.0",
        "lxml>=4.9.0"
    ]
    
    print("📦 Installing dependencies...")
    
    try:
        for package in packages:
            print(f"   Installing {package.split('>=')[0]}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("💡 Try manually: pip install aiohttp beautifulsoup4 markdownify tqdm lxml")
        return False


def run_local_scraper():
    """Run the scraper using local source code."""
    try:
        # Import and run the local scraper
        from src import OmarchyScraper, Config
        
        # Parse arguments
        import argparse
        parser = argparse.ArgumentParser(description="Omarchy Manual Scraper")
        parser.add_argument("--dry-run", action="store_true", help="Test without saving")
        parser.add_argument("--list-links", action="store_true", help="Show chapter links only")
        parser.add_argument("--output-dir", default="omarchy_manual", help="Output directory")
        parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
        args = parser.parse_args()
        
        # Create configuration
        output_dir = Path(args.output_dir)
        config = Config(
            output_dir=output_dir,
            chapters_dir=output_dir / "chapters"
        )
        
        if args.verbose:
            print("🔧 Configuration:")
            print(f"   Base URL: {config.base_url}")
            print(f"   Output dir: {config.output_dir}")
            print(f"   Dry run: {args.dry_run}")
            print()
        
        async def main():
            scraper = OmarchyScraper(config, dry_run=args.dry_run)
            
            if args.list_links:
                await scraper._create_session()
                links = await scraper.extract_chapter_links()
                
                print(f"📋 Found {len(links)} chapter links:")
                for i, (title, url) in enumerate(links, 1):
                    print(f"   {i:2d}. {title}")
                    if args.verbose:
                        print(f"       {url}")
                
                await scraper._close_session()
            else:
                await scraper.run()
        
        asyncio.run(main())
        
    except ImportError:
        print("❌ Local source files not found. This might be a remote execution.")
        return False
    except Exception as e:
        print(f"❌ Error running local scraper: {e}")
        return False
    
    return True


def run_embedded_scraper():
    """Run the embedded scraper for remote execution."""
    
    # Embedded scraper code (compact version)
    scraper_code = '''
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

class OmarchyScraper:
    def __init__(self, output_dir="omarchy_manual", dry_run=False):
        self.output_dir = Path(output_dir)
        self.chapters_dir = self.output_dir / "chapters"
        self.dry_run = dry_run
        self.session = None
        self.base_url = "https://learn.omacom.io/2/the-omarchy-manual"
        
        if not dry_run:
            self.output_dir.mkdir(exist_ok=True)
            self.chapters_dir.mkdir(exist_ok=True)
    
    async def create_session(self):
        headers = {"Accept": "*/*"}
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
    
    async def close_session(self):
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url):
        async with self.session.get(url) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status} for {url}")
            return await response.text()
    
    async def extract_chapter_links(self):
        print("🔍 Extracting chapter links...")
        content = await self.fetch_page(self.base_url)
        soup = BeautifulSoup(content, "html.parser")
        
        chapter_links = []
        toc_links = soup.select("a.toc__link")
        
        for link in toc_links:
            href = link.get("href")
            text = link.get_text(strip=True)
            
            if href and text:
                clean_title = text.replace("Open ", "") if text.startswith("Open ") else text
                if href.startswith("/"):
                    full_href = urljoin(self.base_url, href)
                else:
                    full_href = href
                
                if "/the-omarchy-manual/" in full_href and clean_title not in ["", "Open"]:
                    chapter_links.append((clean_title, full_href))
        
        print(f"✅ Found {len(chapter_links)} chapters")
        return chapter_links
    
    def sanitize_filename(self, title):
        sanitized = re.sub(r'[<>:"/\\\\|?*]', "_", title)
        sanitized = re.sub(r"\\s+", "_", sanitized)
        return sanitized.strip("._")[:100]
    
    async def extract_content(self, html):
        soup = BeautifulSoup(html, "html.parser")
        main_element = soup.find("main") or soup.find("body")
        
        if not main_element:
            raise Exception("Could not find main content")
        
        for element in main_element.find_all(["script", "style", "nav", "header", "footer"]):
            element.decompose()
        
        markdown = md(str(main_element), heading_style="ATX")
        return re.sub(r"\\n\\s*\\n\\s*\\n", "\\n\\n", markdown).strip()
    
    async def process_chapter(self, title, url, semaphore):
        async with semaphore:
            html = await self.fetch_page(url)
            content = await self.extract_content(html)
            filename = f"{self.sanitize_filename(title)}.md"
            return filename, content
    
    async def run(self):
        print("🚀 Omarchy Manual Scraper")
        print(f"📁 Output: {self.output_dir.absolute()}")
        
        if self.dry_run:
            print("🔍 DRY RUN MODE")
        
        await self.create_session()
        
        try:
            chapter_links = await self.extract_chapter_links()
            print("\\n📖 Processing chapters...")
            
            semaphore = asyncio.Semaphore(5)
            tasks = [self.process_chapter(title, url, semaphore) for title, url in chapter_links]
            
            results_dict = {}
            with tqdm(total=len(tasks), desc="Processing") as pbar:
                for coro in asyncio.as_completed(tasks):
                    filename, content = await coro
                    
                    # Find original order
                    for j, (title, url) in enumerate(chapter_links):
                        if self.sanitize_filename(title) + ".md" == filename:
                            results_dict[j] = (filename, content)
                            break
                    
                    if not self.dry_run:
                        chapter_file = self.chapters_dir / filename
                        with open(chapter_file, "w", encoding="utf-8") as f:
                            f.write(content)
                    
                    pbar.update(1)
            
            # Create combined file
            results = [results_dict[i] for i in sorted(results_dict.keys())]
            combined_content = [
                "# The Omarchy Manual - Complete\\n",
                f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\\n",
                "---\\n"
            ]
            
            for filename, content in results:
                title = filename.replace(".md", "").replace("_", " ")
                combined_content.extend([f"\\n# {title}\\n", content, "\\n---\\n"])
            
            if not self.dry_run:
                combined_file = self.output_dir / "omarchy_manual_complete.md"
                with open(combined_file, "w", encoding="utf-8") as f:
                    f.write("\\n".join(combined_content))
            
            print(f"\\n✅ Successfully processed {len(results)} chapters")
            if not self.dry_run:
                print(f"📁 Files saved to: {self.output_dir.absolute()}")
            
        finally:
            await self.close_session()

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Omarchy Manual Scraper")
    parser.add_argument("--dry-run", action="store_true", help="Test without saving")
    parser.add_argument("--list-links", action="store_true", help="Show chapter links only")
    parser.add_argument("--output-dir", default="omarchy_manual", help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    scraper = OmarchyScraper(args.output_dir, args.dry_run)
    
    if args.list_links:
        await scraper.create_session()
        links = await scraper.extract_chapter_links()
        
        print(f"📋 Found {len(links)} chapter links:")
        for i, (title, url) in enumerate(links, 1):
            print(f"   {i:2d}. {title}")
            if args.verbose:
                print(f"       {url}")
        
        await scraper.close_session()
    else:
        await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    # Create temporary file and execute
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(scraper_code)
        temp_script = f.name
    
    try:
        subprocess.check_call([sys.executable, temp_script] + sys.argv[1:])
    except subprocess.CalledProcessError as e:
        print(f"❌ Scraper failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        sys.exit(1)
    finally:
        Path(temp_script).unlink(missing_ok=True)


def main():
    """Main entry point - works for both local and remote execution."""
    
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        sys.exit(1)
    
    # Determine execution mode
    remote = is_remote_execution()
    
    if remote:
        print("🌐 Remote execution detected")
        print("🚀 Omarchy Manual Scraper - Remote Mode")
        print("=" * 50)
        
        # Check and install dependencies if needed
        missing = check_dependencies()
        if missing:
            print(f"📦 Missing dependencies: {', '.join(missing)}")
            
            try:
                response = input("🤔 Install missing dependencies? (y/N): ").lower()
                if response in ['y', 'yes']:
                    if not install_dependencies():
                        sys.exit(1)
                else:
                    print("❌ Cannot proceed without dependencies")
                    sys.exit(1)
            except (KeyboardInterrupt, EOFError):
                print("\n❌ Installation cancelled")
                sys.exit(1)
        
        # Run embedded scraper
        run_embedded_scraper()
        
    else:
        print("💻 Local execution detected")
        
        # Check dependencies
        missing = check_dependencies()
        if missing:
            print(f"❌ Missing dependencies: {', '.join(missing)}")
            print("💡 Install with: pip install -r requirements.txt")
            sys.exit(1)
        
        # Try to run local scraper
        if not run_local_scraper():
            print("🔄 Falling back to embedded scraper...")
            run_embedded_scraper()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        sys.exit(1)