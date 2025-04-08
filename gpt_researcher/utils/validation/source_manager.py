"""
Source Manager

This module provides utilities for managing source information during research,
allowing for proper citation linking and validation in generated reports.
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import logging

logger = logging.getLogger(__name__)

class SourceManager:
    """
    Tracks and manages sources used during research to enable proper citation 
    linking and validation in generated reports.
    """
    
    def __init__(self, cache_dir: str = None):
        """
        Initialize the SourceManager.
        
        Args:
            cache_dir: Directory to store source cache files. Defaults to 
                      .source_cache in the current working directory.
        """
        self.sources = {}  # Dict to store source information
        self.cache_dir = Path(cache_dir or ".source_cache")
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.load_cache()
        
    def load_cache(self) -> None:
        """Load previously cached sources."""
        try:
            cache_file = self.cache_dir / "sources.json"
            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    self.sources = json.load(f)
                logger.info(f"Loaded {len(self.sources)} sources from cache")
        except Exception as e:
            logger.warning(f"Error loading source cache: {str(e)}")
            self.sources = {}
    
    def save_cache(self) -> None:
        """Save current sources to cache."""
        try:
            cache_file = self.cache_dir / "sources.json"
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(self.sources, f, indent=2)
            logger.info(f"Saved {len(self.sources)} sources to cache")
        except Exception as e:
            logger.warning(f"Error saving source cache: {str(e)}")
    
    def register_source(self, url: str, title: str, publisher: str, 
                        date: Optional[str] = None, author: Optional[str] = None) -> None:
        """
        Register a source with the manager.
        
        Args:
            url: The URL of the source
            title: The title of the content
            publisher: The name of the publisher
            date: Publication date (if available)
            author: Author name (if available)
        """
        key = self._create_source_key(publisher, title)
        self.sources[key] = {
            "url": url,
            "title": title,
            "publisher": publisher,
            "date": date,
            "author": author,
            "last_accessed": datetime.now().isoformat()
        }
        self.save_cache()
    
    def register_source_from_scrape(self, url: str, title: str, content: str) -> None:
        """
        Register a source from scraped data.
        
        Args:
            url: The URL of the source
            title: The title of the content
            content: The content of the page (used to extract publisher/date if possible)
        """
        publisher = self._extract_publisher(url, title, content)
        date = self._extract_date(content)
        author = self._extract_author(content)
        
        self.register_source(url, title, publisher, date, author)
    
    def get_source_url(self, publisher: str, title: str) -> Optional[str]:
        """
        Retrieve a source URL based on publisher and title.
        
        Args:
            publisher: The name of the publisher
            title: The title of the content
            
        Returns:
            The URL if found, None otherwise
        """
        key = self._create_source_key(publisher, title)
        if key in self.sources:
            return self.sources[key]["url"]
        
        # Try fuzzy matching if exact match fails
        return self._fuzzy_match_source(publisher, title)
    
    def find_sources_in_text(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Find and extract source citations from text.
        
        Args:
            text: The text to search for citations
            
        Returns:
            List of (publisher, date, title) tuples
        """
        # Pattern to match common citation formats
        patterns = [
            r'\*Source(?:\s+\d+)?\*:\s+([^,]+),\s+([^,]+),\s+[""]([^""]+)[""](?: by (.+))?',  # *Source N*: Publisher, Date, "Title" by Author
            r'\[([^,]+),\s+([^,]+),\s+[""]([^""]+)[""](?: by (.+))?\]',  # [Publisher, Date, "Title" by Author]
        ]
        
        sources = []
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                publisher = match.group(1).strip()
                date = match.group(2).strip()
                title = match.group(3).strip()
                author = match.group(4).strip() if len(match.groups()) > 3 and match.group(4) else None
                sources.append((publisher, date, title, author))
        
        return sources
    
    def format_citations_in_text(self, text: str) -> str:
        """
        Format citations in text to include clickable links.
        
        Args:
            text: Text containing citations to format
            
        Returns:
            Text with formatted citations
        """
        # Extract citations
        citations = self.find_sources_in_text(text)
        
        # Process text with replacements
        for publisher, date, title, author in citations:
            url = self.get_source_url(publisher, title)
            if url:
                # Create pattern to match this specific citation
                escaped_publisher = re.escape(publisher)
                escaped_date = re.escape(date)
                escaped_title = re.escape(title)
                author_pattern = f" by {re.escape(author)}" if author else r"(?:\s+by\s+[^\.]+)?"
                
                pattern = rf'\*Source(?:\s+\d+)?\*:\s+{escaped_publisher},\s+{escaped_date},\s+[""]{escaped_title}[""]{author_pattern}'
                
                # Create replacement with clickable link
                if author:
                    replacement = f'*Source*: [{publisher}, {date}, "{title}" by {author}]({url}) ({url})'
                else:
                    replacement = f'*Source*: [{publisher}, {date}, "{title}"]({url}) ({url})'
                
                # Replace in text
                text = re.sub(pattern, replacement, text)
        
        return text
    
    def _create_source_key(self, publisher: str, title: str) -> str:
        """Create a key for the source dictionary."""
        publisher_key = re.sub(r'[^\w]', '', publisher.lower())
        title_key = re.sub(r'[^\w]', '', title.lower())
        return f"{publisher_key}:{title_key}"
    
    def _fuzzy_match_source(self, publisher: str, title: str) -> Optional[str]:
        """Try to find a source with fuzzy matching."""
        publisher_words = set(re.findall(r'\w+', publisher.lower()))
        title_words = set(re.findall(r'\w+', title.lower()))
        
        best_match = None
        best_score = 0
        
        for key, source in self.sources.items():
            src_publisher_words = set(re.findall(r'\w+', source['publisher'].lower()))
            src_title_words = set(re.findall(r'\w+', source['title'].lower()))
            
            # Calculate similarity scores
            publisher_score = len(publisher_words.intersection(src_publisher_words)) / max(len(publisher_words), len(src_publisher_words))
            title_score = len(title_words.intersection(src_title_words)) / max(len(title_words), len(src_title_words))
            
            # Combined score with more weight on title
            score = (title_score * 0.7) + (publisher_score * 0.3)
            
            if score > 0.6 and score > best_score:  # Threshold for a good match
                best_score = score
                best_match = source['url']
        
        return best_match
    
    def _extract_publisher(self, url: str, title: str, content: str) -> str:
        """Extract publisher information from URL and content."""
        # Try to extract from URL
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if domain_match:
            domain = domain_match.group(1)
            # Convert domain to publisher name
            parts = domain.split('.')
            if len(parts) >= 2:
                return parts[-2].capitalize()
        
        # Fallback to domain
        return domain_match.group(1) if domain_match else "Unknown Source"
    
    def _extract_date(self, content: str) -> Optional[str]:
        """Extract publication date from content if possible."""
        # Common date patterns
        date_patterns = [
            r'Published(?:\s+on)?\s+([A-Z][a-z]+ \d{1,2},? \d{4})',
            r'Date[:\s]+([A-Z][a-z]+ \d{1,2},? \d{4})',
            r'(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        # Default to today's date
        return datetime.now().strftime("%B %d, %Y")
    
    def _extract_author(self, content: str) -> Optional[str]:
        """Extract author information from content if possible."""
        # Common author patterns
        author_patterns = [
            r'By\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'Author[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return None


# Create a global instance for easy access
global_source_manager = SourceManager()

def register_source(url: str, title: str, publisher: str, date: Optional[str] = None, author: Optional[str] = None) -> None:
    """Register a source with the global source manager."""
    global_source_manager.register_source(url, title, publisher, date, author)

def register_source_from_scrape(url: str, title: str, content: str) -> None:
    """Register a source from scraped data with the global source manager."""
    global_source_manager.register_source_from_scrape(url, title, content)

def find_url_for_source(publisher: str, title: str) -> Optional[str]:
    """Find a source URL based on publisher and title using the global source manager."""
    return global_source_manager.get_source_url(publisher, title)

def format_citations(text: str) -> str:
    """Format citations in text to include clickable links using the global source manager."""
    return global_source_manager.format_citations_in_text(text) 