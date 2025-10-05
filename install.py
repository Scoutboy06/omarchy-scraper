#!/usr/bin/env python3
"""
Installation script for Omarchy Scraper
"""

import subprocess
import sys
from pathlib import Path


def install_package():
    """Install the package in development mode."""
    try:
        # Install in editable mode
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-e", "."
        ])
        print("✅ Successfully installed omarchy-scraper!")
        print("🚀 You can now run: omarchy-scraper")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        sys.exit(1)


def main():
    """Main installation function."""
    print("🔧 Installing Omarchy Scraper...")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Run this from the project root.")
        sys.exit(1)
    
    install_package()


if __name__ == "__main__":
    main()