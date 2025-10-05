"""
Configuration module for the Omarchy Manual Scraper.
"""

from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration settings for the scraper."""
    
    # Source settings
    base_url: str = "https://learn.omacom.io/2/the-omarchy-manual"
    query_param: str = ""
    
    # Output settings
    output_dir: Path = Path("output")
    chapters_dir: Path = Path("output/chapters")
    combined_output: str = "omarchy_manual_complete.md"
    metadata_file: str = "chapter_metadata.json"
    
    # Performance settings
    max_concurrent: int = 5
    request_timeout: int = 30
    
    def __post_init__(self):
        """Ensure paths are Path objects and directories exist."""
        self.output_dir = Path(self.output_dir)
        self.chapters_dir = Path(self.chapters_dir)
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.chapters_dir.mkdir(exist_ok=True)


# Default configuration instance
default_config = Config()