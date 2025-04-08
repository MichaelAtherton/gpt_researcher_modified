"""
Utility functions for the gpt-researcher package.
"""

from gpt_researcher.utils.enum import ReportFormat, ReportSource, ReportType, Tone

# Expose validation utilities if they exist
try:
    from gpt_researcher.utils.validation import (
        ConfidenceLevel,
        TimeHorizon,
        SourceValidator,
        EvidenceVerifier,
        validate_report_dates
    )
    has_validation = True
except ImportError:
    has_validation = False

__all__ = ["ReportFormat", "ReportSource", "ReportType", "Tone"]

if has_validation:
    __all__.extend([
        "ConfidenceLevel",
        "TimeHorizon",
        "SourceValidator",
        "EvidenceVerifier",
        "validate_report_dates"
    ])
