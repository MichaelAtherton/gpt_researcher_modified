"""
Validation utilities for the gpt-researcher package.

This module provides tools for validating sources, formatting citations,
and verifying evidence in generated research reports.
"""

from enum import Enum, auto
import re
from datetime import datetime
from typing import Tuple, Optional, List

# Import source manager
try:
    from .source_manager import (
        SourceManager, 
        register_source, 
        register_source_from_scrape,
        find_url_for_source, 
        format_citations,
        global_source_manager
    )
except ImportError:
    # Define fallbacks if source manager is not available
    def register_source(*args, **kwargs): pass
    def register_source_from_scrape(*args, **kwargs): pass
    def find_url_for_source(*args, **kwargs): return None
    def format_citations(text): return text
    global_source_manager = None
    SourceManager = None

class ConfidenceLevel(Enum):
    """Enumeration of confidence levels for sources and evidence."""
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()

class TimeHorizon(Enum):
    """Enumeration of time horizons for insights and predictions."""
    CURRENT = auto()     # Already established
    NEAR_TERM = auto()   # 0-6 months
    MID_TERM = auto()    # 6-18 months
    LONG_TERM = auto()   # 18+ months

class SourceValidator:
    """
    Validates sources for credibility, recency, and relevance.
    """
    
    def validate_source(self, source_url: str, 
                         publication_date: Optional[str] = None) -> Tuple[ConfidenceLevel, str]:
        """
        Validate a source based on URL and publication date.
        
        Args:
            source_url: URL of the source
            publication_date: Date of publication (if available)
            
        Returns:
            Tuple of (confidence_level, message)
        """
        # This is a simplified implementation and would be expanded
        # with more sophisticated validation logic in production
        
        # Basic checks
        if not source_url:
            return ConfidenceLevel.LOW, "Missing source URL"
            
        # Check for reputable domains (simplified example)
        reputable_domains = [
            "nature.com", "science.org", "springer.com", "ieee.org",
            "acm.org", "sciencedirect.com", "forbes.com", "wsj.com",
            "nytimes.com", "washingtonpost.com", "harvard.edu", "mit.edu"
        ]
        
        # Check domain reputation
        if any(domain in source_url.lower() for domain in reputable_domains):
            return ConfidenceLevel.HIGH, "Source from reputable publisher"
        
        # Check recency if date provided
        if publication_date:
            try:
                # Parse the date (simplified)
                if "," in publication_date:
                    date_obj = datetime.strptime(publication_date, "%B %d, %Y")
                else:
                    date_obj = datetime.strptime(publication_date, "%Y-%m-%d")
                
                # Check if date is recent (within last 6 months)
                months_old = (datetime.now() - date_obj).days / 30
                if months_old <= 6:
                    return ConfidenceLevel.MEDIUM, "Recent source, moderate reputation"
                else:
                    return ConfidenceLevel.LOW, "Dated source (>6 months old)"
            except ValueError:
                pass  # Fall through to default return
        
        # Default case
        return ConfidenceLevel.MEDIUM, "Source with standard credibility"

class EvidenceVerifier:
    """
    Verifies evidence by checking multiple sources and consistency.
    """
    
    def verify_claim(self, claim: str, sources: List[str]) -> Tuple[ConfidenceLevel, str]:
        """
        Verify a claim based on provided sources.
        
        Args:
            claim: The claim to verify
            sources: List of source URLs supporting the claim
            
        Returns:
            Tuple of (confidence_level, message)
        """
        # This is a simplified implementation and would be expanded
        # with more sophisticated verification logic in production
        
        # Check number of sources
        if not sources:
            return ConfidenceLevel.LOW, "No sources provided"
        
        source_count = len(sources)
        
        if source_count >= 3:
            return ConfidenceLevel.HIGH, f"Well-supported by {source_count} sources"
        elif source_count == 2:
            return ConfidenceLevel.MEDIUM, "Supported by 2 sources"
        else:
            return ConfidenceLevel.LOW, "Limited support (single source)"

def validate_report_dates(content: str, reference_date: Optional[datetime] = None) -> str:
    """
    Validate and correct dates in a report to avoid future dates.
    
    Args:
        content: The report content to validate
        reference_date: The reference date (default: current date)
        
    Returns:
        Corrected report content
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    current_year = reference_date.year
    
    # This regex matches date patterns like "January 1, 2026"
    future_date_pattern = r'(\w+ \d{1,2}, )(\d{4})'
    
    def replace_future_date(match):
        date_prefix = match.group(1)
        year = int(match.group(2))
        
        if year > current_year:
            return f"{date_prefix}{current_year}"
        return match.group(0)
    
    return re.sub(future_date_pattern, replace_future_date, content)

# Define what's available when importing from this package
__all__ = [
    'ConfidenceLevel',
    'TimeHorizon',
    'SourceValidator',
    'EvidenceVerifier',
    'validate_report_dates',
    'register_source',
    'register_source_from_scrape',
    'find_url_for_source',
    'format_citations',
    'SourceManager',
    'global_source_manager'
] 