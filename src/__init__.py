"""
Omarchy Manual Scraper

A clean, efficient scraper for The Omarchy Manual.
"""

from .scraper import OmarchyScraper, ScraperError
from .config import Config, default_config

__version__ = "1.0.0"
__all__ = ["OmarchyScraper", "ScraperError", "Config", "default_config"]