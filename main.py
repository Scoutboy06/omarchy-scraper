#!/usr/bin/env python3
"""
Main entry point for the Omarchy Manual Scraper.

Usage:
    python main.py [options]

Options:
    --help              Show this help message
    --dry-run           Run without saving files
    --list-links        Only show chapter links
    --output-dir DIR    Set output directory
    --verbose           Show detailed output
"""

import asyncio
import argparse
import sys
from pathlib import Path

from src import OmarchyScraper, Config, default_config


def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Scrape The Omarchy Manual and convert to Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter
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
        default=default_config.output_dir,
        help=f'Output directory (default: {default_config.output_dir})'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )
    
    return parser


async def main():
    """Main entry point."""
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


if __name__ == "__main__":
    asyncio.run(main())