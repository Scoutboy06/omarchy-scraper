#!/usr/bin/env python3
"""
Command-line interface for the Omarchy Manual Scraper.
This module serves as the entry point when installed as a package.
"""

import asyncio
import argparse
import sys
from pathlib import Path

from . import OmarchyScraper, Config


def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Scrape The Omarchy Manual and convert to Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  omarchy-scraper                    # Download all chapters
  omarchy-scraper --list-links       # Show available chapters
  omarchy-scraper --dry-run          # Test without saving files
  omarchy-scraper --output-dir docs  # Custom output directory
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test run without saving files'
    )
    
    parser.add_argument(
        '--list-links',
        action='store_true',
        help='Only extract and display chapter links'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path.cwd() / "omarchy_manual",
        help='Output directory (default: ./omarchy_manual/)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


async def async_main():
    """Async main function."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Create configuration
    config = Config(
        output_dir=args.output_dir,
        chapters_dir=args.output_dir / "chapters"
    )
    
    if args.verbose:
        print("🔧 Configuration:")
        print(f"   Base URL: {config.base_url}")
        print(f"   Output dir: {config.output_dir}")
        print(f"   Chapters dir: {config.chapters_dir}")
        print(f"   Dry run: {args.dry_run}")
        print()
    
    scraper = OmarchyScraper(config, dry_run=args.dry_run)
    
    try:
        if args.list_links:
            # Just show chapter links
            await scraper._create_session()
            links = await scraper.extract_chapter_links()
            
            print(f"📋 Found {len(links)} chapter links:")
            for i, (title, url) in enumerate(links, 1):
                print(f"   {i:2d}. {title}")
                if args.verbose:
                    print(f"       {url}")
            
            await scraper._close_session()
        else:
            # Run full scraper
            await scraper.run()
            
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()