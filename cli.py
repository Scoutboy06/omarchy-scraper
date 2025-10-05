#!/usr/bin/env python3
"""
Command-line interface for the Omarchy Manual Scraper.
"""

import argparse
import asyncio
import sys
from pathlib import Path

from omarchy_scraper import OmarchyScraper
import config


def setup_args():
    """Set up command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Scrape The Omarchy Manual and convert to Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run with default settings
  %(prog)s --url https://example.com/manual  # Use custom base URL
  %(prog)s --output-dir my_chapters # Use custom output directory
  %(prog)s --dry-run               # Test without saving files
        """
    )
    
    parser.add_argument(
        '--url', 
        default=config.BASE_URL,
        help=f'Base URL to scrape (default: {config.BASE_URL})'
    )
    
    parser.add_argument(
        '--query-param',
        default=config.QUERY_PARAM,
        help=f'Query parameter to append (default: {config.QUERY_PARAM})'
    )
    
    parser.add_argument(
        '--output-dir',
        default=config.OUTPUT_DIR,
        help=f'Directory for individual chapter files (default: {config.OUTPUT_DIR})'
    )
    
    parser.add_argument(
        '--combined-output',
        default=config.COMBINED_OUTPUT,
        help=f'Filename for combined output (default: {config.COMBINED_OUTPUT})'
    )
    
    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=config.MAX_CONCURRENT_REQUESTS,
        help=f'Maximum concurrent requests (default: {config.MAX_CONCURRENT_REQUESTS})'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test run without saving files'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--list-links-only',
        action='store_true',
        help='Only extract and display chapter links, then exit'
    )
    
    return parser


async def main():
    """Main CLI entry point."""
    parser = setup_args()
    args = parser.parse_args()
    
    # Update config with CLI arguments
    config.BASE_URL = args.url
    config.QUERY_PARAM = args.query_param
    config.OUTPUT_DIR = args.output_dir
    config.COMBINED_OUTPUT = args.combined_output
    config.MAX_CONCURRENT_REQUESTS = args.max_concurrent
    
    if args.verbose:
        print("🔧 Configuration:")
        print(f"   Base URL: {config.BASE_URL}")
        print(f"   Query param: {config.QUERY_PARAM}")
        print(f"   Output dir: {config.OUTPUT_DIR}")
        print(f"   Combined output: {config.COMBINED_OUTPUT}")
        print(f"   Max concurrent: {config.MAX_CONCURRENT_REQUESTS}")
        print(f"   Dry run: {args.dry_run}")
        print()
    
    scraper = OmarchyScraper(dry_run=args.dry_run)
    
    if args.list_links_only:
        # Just extract and show links
        try:
            await scraper.create_session()
            links = await scraper.extract_chapter_links()
            
            print(f"📋 Found {len(links)} chapter links:")
            for i, (title, url) in enumerate(links, 1):
                print(f"   {i:2d}. {title}")
                if args.verbose:
                    print(f"       {url}")
            
        except Exception as e:
            print(f"❌ Error extracting links: {e}")
            sys.exit(1)
        finally:
            await scraper.close_session()
    
    else:
        # Run full scraper
        if args.dry_run:
            print("🔍 DRY RUN MODE - No files will be saved")
            # For dry run, we'll just run normally but skip the actual file writing
            # The scraper will still process everything but we'll intercept saves
        
        try:
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