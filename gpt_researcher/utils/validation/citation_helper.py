"""
Citation and Validation Utilities for GPT Researcher

This module provides standardized functions for source validation, citation formatting,
and evidence verification to enhance report reliability.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Tuple
import re
import logging

logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Enumeration of confidence levels for cited information."""
    HIGH = "High Confidence"
    MEDIUM = "Medium Confidence"
    LOW = "Low Confidence"
    SPECULATIVE = "Speculative"


class TimeHorizon(Enum):
    """Enumeration of time horizons for trends and projections."""
    CURRENT = "Current Trend"
    NEAR_TERM = "Near-term Development (0-6 months)"
    MID_TERM = "Mid-term Projection (6-18 months)"
    LONG_TERM = "Long-term Forecast (18+ months)"


class SourceValidator:
    """Validates and formats source citations."""
    
    @staticmethod
    def validate_source_date(date_str: str) -> Tuple[bool, str]:
        """
        Validates if the source date is recent enough (within last 6 months).
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Handle multiple date formats
            date_formats = [
                "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y",
                "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y"
            ]
            
            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            
            if not parsed_date:
                return False, "Invalid date format"
            
            # Check if date is within last 6 months
            six_months_ago = datetime.now() - timedelta(days=180)
            
            if parsed_date < six_months_ago:
                return False, f"Source date ({date_str}) is older than 6 months"
            
            # Check if date is in the future
            if parsed_date > datetime.now():
                return False, f"Source date ({date_str}) is in the future"
                
            return True, "Source date is valid and recent"
            
        except Exception as e:
            logger.error(f"Error validating source date: {e}")
            return False, f"Error validating date: {str(e)}"
    
    @staticmethod
    def format_citation(
        title: str,
        source: str,
        date: str,
        author: Optional[str] = None,
        url: Optional[str] = None
    ) -> str:
        """
        Formats a citation in a standardized way.
        
        Args:
            title: Title of the publication
            source: Source name (journal, website, etc.)
            date: Publication date
            author: Author name(s)
            url: URL to the source
            
        Returns:
            Formatted citation string
        """
        citation = f"\"{title}\", {source}, {date}"
        
        if author:
            citation = f"{citation}, by {author}"
        
        if url:
            citation = f"{citation} [URL: {url}]"
            
        return citation
    
    @staticmethod
    def evaluate_confidence(
        num_sources: int,
        source_types: List[str],
        contradictions: bool,
        recency: bool
    ) -> ConfidenceLevel:
        """
        Evaluates the confidence level of information based on sources.
        
        Args:
            num_sources: Number of corroborating sources
            source_types: Types of sources (academic, news, company report, etc.)
            contradictions: Whether there are contradicting sources
            recency: Whether sources are recent
            
        Returns:
            ConfidenceLevel enum value
        """
        # High confidence requires multiple recent sources without contradictions
        if num_sources >= 3 and not contradictions and recency and 'academic' in source_types:
            return ConfidenceLevel.HIGH
            
        # Medium confidence requires at least 2 sources
        elif num_sources >= 2 and recency and not contradictions:
            return ConfidenceLevel.MEDIUM
            
        # Low confidence for limited or contradictory sources
        elif num_sources >= 1 and recency:
            return ConfidenceLevel.LOW
            
        # Speculative for very limited evidence
        else:
            return ConfidenceLevel.SPECULATIVE
    
    @staticmethod
    def classify_time_horizon(forecast_months: int) -> TimeHorizon:
        """
        Classifies information based on time horizon.
        
        Args:
            forecast_months: Number of months in the future for the forecast
            
        Returns:
            TimeHorizon enum value
        """
        if forecast_months <= 0:
            return TimeHorizon.CURRENT
        elif forecast_months <= 6:
            return TimeHorizon.NEAR_TERM
        elif forecast_months <= 18:
            return TimeHorizon.MID_TERM
        else:
            return TimeHorizon.LONG_TERM


class EvidenceVerifier:
    """Verifies and formats evidence for claims in reports."""
    
    @staticmethod
    def format_case_study(
        company: Optional[str],
        industry: str,
        implementation_date: str,
        metrics: Dict[str, Union[str, float, int]],
        is_anonymous: bool = False
    ) -> str:
        """
        Formats a case study in a standardized way.
        
        Args:
            company: Company name (or None if anonymous)
            industry: Industry name
            implementation_date: Date of implementation
            metrics: Dictionary of metrics with before/after values
            is_anonymous: Whether the case study is anonymized
            
        Returns:
            Formatted case study string
        """
        if is_anonymous or not company:
            company_str = f"[Anonymous {industry} company]"
        else:
            company_str = company
            
        case_study = f"**Case Study**: {company_str} ({implementation_date})\n\n"
        case_study += "**Results**:\n"
        
        for metric, value in metrics.items():
            if isinstance(value, dict) and 'before' in value and 'after' in value:
                if isinstance(value['before'], (int, float)) and isinstance(value['after'], (int, float)):
                    percent_change = ((value['after'] - value['before']) / value['before']) * 100
                    case_study += f"- {metric}: {value['before']} → {value['after']} ({percent_change:.1f}% change)\n"
                else:
                    case_study += f"- {metric}: {value['before']} → {value['after']}\n"
            else:
                case_study += f"- {metric}: {value}\n"
                
        return case_study
    
    @staticmethod
    def format_market_data(
        metric: str,
        value: Union[str, float, int],
        source: str,
        sample_size: Optional[int] = None,
        confidence_interval: Optional[str] = None,
        methodology: Optional[str] = None
    ) -> str:
        """
        Formats market data with methodology information.
        
        Args:
            metric: Name of the market metric
            value: Value of the metric
            source: Source of the data
            sample_size: Sample size (if applicable)
            confidence_interval: Confidence interval (if applicable)
            methodology: Research methodology
            
        Returns:
            Formatted market data string
        """
        market_data = f"**{metric}**: {value}"
        
        methodology_parts = []
        if source:
            methodology_parts.append(f"Source: {source}")
        if sample_size:
            methodology_parts.append(f"Sample size: {sample_size}")
        if confidence_interval:
            methodology_parts.append(f"CI: {confidence_interval}")
        if methodology:
            methodology_parts.append(f"Methodology: {methodology}")
            
        if methodology_parts:
            market_data += f" ({'; '.join(methodology_parts)})"
            
        return market_data


def validate_report_dates(report_content: str) -> str:
    """
    Corrects any future dates in the report and standardizes date formatting.
    
    Args:
        report_content: The full report content
        
    Returns:
        Corrected report content
    """
    today = datetime.now()
    
    # Replace any dates in the future
    future_date_pattern = r"(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, (2024|2025|2026)"
    
    def replace_future_date(match):
        # Replace future dates with today's date
        return today.strftime("%B %d, %Y")
    
    corrected_content = re.sub(future_date_pattern, replace_future_date, report_content)
    
    # Add a disclaimer about dates and projections
    date_disclaimer = f"""
---

**Date Disclaimer**: This report was generated on {today.strftime('%B %d, %Y')}. All temporal references are relative to this date. Trends labeled as "Current" are supported by recent data, while those with future time horizons represent projections based on available evidence.
"""
    
    # Add the disclaimer before the conclusion
    if "## Conclusion" in corrected_content:
        corrected_content = corrected_content.replace("## Conclusion", f"{date_disclaimer}\n\n## Conclusion")
    else:
        corrected_content += f"\n\n{date_disclaimer}"
    
    return corrected_content 