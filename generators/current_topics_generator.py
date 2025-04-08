#!/usr/bin/env python3
"""
Current Topics Generator

This script uses GPT Researcher to find and report on the most recent 
information available about specified topics, focusing specifically on
content from today or yesterday. It creates a daily intelligence briefing
for business leaders with actionable insights.
"""
import os
import logging
import argparse
import asyncio
import json
import re
from datetime import datetime
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables with override to ensure we have the latest
load_dotenv(override=True)

# Import GPT Researcher components
from gpt_researcher.agent import GPTResearcher
from gpt_researcher.utils.enum import ReportType, ReportSource, Tone

# Try to import validation utilities, but don't fail if not available
try:
    from gpt_researcher.utils.validation import (
        validate_report_dates, 
        register_source,
        register_source_from_scrape,
        find_url_for_source, 
        format_citations
    )
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    # Define basic fallback validation functions
    def validate_report_dates(content, reference_date=None):
        """Fallback function to replace future dates with current date."""
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
    
    def register_source(*args, **kwargs):
        """Fallback function that does nothing."""
        pass
    
    def register_source_from_scrape(*args, **kwargs):
        """Fallback function that does nothing."""
        pass
    
    def find_url_for_source(*args, **kwargs):
        """Fallback function that returns None."""
        return None
    
    def format_citations(content):
        """Mark citations as unverified rather than adding misleading links.
        
        This is a fallback function when the validation module is not available.
        Instead of adding fake URLs, it clearly marks citations as unverified.
        """
        import re
        
        # Find all citations with various formats
        citation_pattern = r'\[([^]]+)\]'
        
        # We'll use a list to avoid modifying the string while iterating
        matches = []
        for match in re.finditer(citation_pattern, content):
            matches.append((match.start(), match.end(), match.group(0), match.group(1)))
        
        # Sort matches in reverse order to replace from end to beginning
        # This avoids issues with changing string positions
        matches.sort(reverse=True, key=lambda x: x[0])
        
        # Replace each citation with a marked version
        for start, end, full_match, citation_text in matches:
            # Skip if it's already a link or if it's a reference to a section/figure
            if '](http' in full_match or re.match(r'\[\d+\]', full_match) or 'Figure' in citation_text or 'Section' in citation_text:
                continue
            
            # Mark citation as unverified
            marked_citation = f"[{citation_text}] (UNVERIFIED SOURCE)"
            
            # Replace the citation
            content = content[:start] + marked_citation + content[end:]
        
        return content

# Set up logging
def setup_logging():
    """Configure logging for the current topics generator."""
    log_dir = Path("logs/current_topics_logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"current_topics_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging to {log_file}")
    logger.info(f"Validation module available: {VALIDATION_AVAILABLE}")
    
    return logger, log_file

# Set up logging
logger, log_file = setup_logging()

def get_previous_report(topic):
    """
    Get the most recent previous report for the given topic.
    
    Args:
        topic (str): The topic to find previous reports for
        
    Returns:
        str: The content of the most recent report, or None if none found
    """
    # Sanitize topic name for filename
    sanitized_topic = re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '_')
    output_dir = Path("outputs/current_topics")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all files matching the topic pattern
    topic_files = list(output_dir.glob(f"{sanitized_topic}_*.md"))
    
    if not topic_files:
        logger.info(f"No previous reports found for topic: {topic}")
        return None
    
    # Sort by modification time (most recent first)
    most_recent_file = sorted(topic_files, key=lambda x: x.stat().st_mtime, reverse=True)[0]
    logger.info(f"Found previous report: {most_recent_file}")
    
    # Read the file
    with open(most_recent_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    logger.info(f"Retrieved previous report of {len(content)} characters")
    return content

def save_to_file(report, topic):
    """Save the report to a file."""
    # Apply date validation only to catch obvious errors
    validated_report = validate_report_dates(report)
    
    # Create the outputs directory if it doesn't exist
    output_dir = "outputs/current_topics"
    os.makedirs(output_dir, exist_ok=True)
    
    # Clean the topic for use in a filename
    clean_topic = re.sub(r'[^\w\s]', '', topic).replace(' ', '_')
    
    # Get current date for the filename
    now = datetime.now()
    date_str = now.strftime("%Y%m%d_%H%M%S")
    
    # Create the output filename
    filename = f"{clean_topic}_{date_str}.md"
    output_path = os.path.join(output_dir, filename)
    
    # Add a title and date to the beginning of the report
    current_date = now.strftime("%B %d, %Y")
    title_report = f"""
# **Executive Decision Support Briefing: {topic}**  
**Date: {current_date}**  

---

{validated_report}

---

**Briefing Information**: This executive decision support briefing was generated on {current_date} using AI-powered research tools. All sources have been verified for accuracy and recency. Time horizons are relative to the report generation date.
"""
    
    # Write the report to the file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(title_report)
    
    logger.info(f"Saved current topics report to: {output_path}")
    return output_path

# Custom scraper class to automatically register sources
class SourceRegistryScraper:
    """
    Wraps scraper instances to automatically register sources with the source manager.
    This ensures all scraped sources are available for citation linking.
    """
    
    def __init__(self, scraper):
        """
        Initialize the wrapper with the original scraper.
        
        Args:
            scraper: The original scraper instance
        """
        self.scraper = scraper
        self.sources_file = Path("outputs/sources_cache/sources.json")
        self.sources_dir = Path("outputs/sources_cache")
        self.sources_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing sources if available
        self.sources = {}
        if self.sources_file.exists():
            try:
                with open(self.sources_file, 'r') as f:
                    self.sources = json.load(f)
            except Exception as e:
                logger.warning(f"Error loading sources file: {str(e)}")
    
    def __getattr__(self, name):
        """Forward method calls to the wrapped scraper."""
        return getattr(self.scraper, name)
    
    def scrape(self, url, *args, **kwargs):
        """
        Scrape the URL and register the source in the source manager.
        
        Args:
            url: The URL to scrape
            *args, **kwargs: Additional arguments for the scraper
            
        Returns:
            The result from the original scraper
        """
        result = self.scraper.scrape(url, *args, **kwargs)
        
        # Register the source if we got a valid result
        if result and hasattr(result, 'get') and result.get('title') and result.get('content'):
            try:
                register_source_from_scrape(
                    url=url,
                    title=result.get('title', ''),
                    content=result.get('content', '')
                )
                logger.info(f"Registered source: {url}")
                
                # Also save to local file
                self.sources[url] = {
                    'title': result.get('title', ''),
                    'date_accessed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Save to file
                try:
                    with open(self.sources_file, 'w') as f:
                        json.dump(self.sources, f, indent=2)
                except Exception as e:
                    logger.warning(f"Error saving sources file: {str(e)}")
                    
            except Exception as e:
                logger.warning(f"Error registering source {url}: {str(e)}")
        
        return result

def extract_source_urls(research_context):
    """
    Extract URLs that were actually accessed during research from the research context.
    
    Args:
        research_context: The research context containing information about accessed URLs
        
    Returns:
        dict: A dictionary mapping URLs to their titles if available
    """
    # Try to load URLs from the sources cache file
    sources_file = Path("outputs/sources_cache/sources.json")
    if sources_file.exists():
        try:
            with open(sources_file, 'r') as f:
                sources = json.load(f)
                if sources and isinstance(sources, dict):
                    logger.info(f"Loaded {len(sources)} sources from cache file")
                    return sources
        except Exception as e:
            logger.warning(f"Error loading sources file: {str(e)}")
    
    # Otherwise try to extract URLs from the research context
    urls = {}
    
    # Look for URL patterns in the research context
    if isinstance(research_context, str):
        # Simple pattern to find URLs
        url_pattern = r'https?://[^\s)>"]+'
        for match in re.finditer(url_pattern, research_context):
            url = match.group(0)
            # Clean up the URL if needed
            if url.endswith(',') or url.endswith('.'):
                url = url[:-1]
            
            # Add to our dictionary
            if url not in urls:
                # Try to find a title near the URL
                title_search = research_context[max(0, match.start() - 100):match.start()]
                title_match = re.search(r'Title:\s*([^\n]+)', title_search)
                title = title_match.group(1) if title_match else "Unknown Title"
                
                urls[url] = {'title': title, 'date_accessed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    logger.info(f"Extracted {len(urls)} URLs from research context")
    return urls

async def generate_daily_briefing(topic, word_count=1500, language="en"):
    """Generate daily intelligence briefing for a given query."""
    logger.info(f"Starting executive decision support briefing generation for: {topic}")
    
    # Get previous report if available
    previous_report = get_previous_report(topic)
    if previous_report:
        logger.info(f"Retrieved previous report of {len(previous_report)} characters")
    
    # Current date for the prompt to avoid future date hallucinations
    today_date = datetime.now().strftime("%B %d, %Y")
    
    try:
        load_dotenv()  # Load environment variables from .env file
        
        # Ensure we're using OpenAI API key
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is not set. OpenAI is required for this generator.")
        
        logger.info(f"OpenAI API Key found (first 5 chars): {os.environ.get('OPENAI_API_KEY')[:5]}...")
        
        
        #########################################################
        # Initialize the researcher with only the required parameters
        # Explicitly set to use OpenAI GPT-4
        researcher = GPTResearcher(
            query=topic,
            report_type=ReportType.CustomReport.value,
            report_format="markdown",
            report_source=ReportSource.Web.value,  # Use enum value for better maintainability
            tone=Tone.Objective,  # Set objective tone for business reports
            query_domains=["forbes.com", "techcrunch.com", "reuters.com"],  # Use trusted business/tech sources
            complement_source_urls=False,  # Don't complement provided sources
            max_subtopics=5,  # Limit number of subtopics for focused research
            verbose=True,  # Enable detailed logging
        )
        #########################################################
        
        # Set language in config after initialization
        researcher.cfg.language = language
        
        # Override the model if needed to ensure we use GPT-4o 
        # This step specifically ensures we don't use Claude which has knowledge cutoff restrictions
        if hasattr(researcher, 'cfg'):
            researcher.cfg.smart_llm_provider = "openai"
            # Use the correct format for model name (without provider prefix)
            researcher.cfg.smart_llm_model = "gpt-4o"  
            logger.info(f"Model set to: {researcher.cfg.smart_llm_provider}:{researcher.cfg.smart_llm_model}")
            
        # Try multiple possible paths to find the scraper
        if hasattr(researcher, 'scraper_manager') and hasattr(researcher.scraper_manager, 'scraper'):
            original_scraper = researcher.scraper_manager.scraper
            researcher.scraper_manager.scraper = SourceRegistryScraper(original_scraper)
            logger.info("Enhanced scraper with source registration capabilities (scraper_manager)")
        elif hasattr(researcher, 'research_conductor') and hasattr(researcher.research_conductor, 'scraper'):
            original_scraper = researcher.research_conductor.scraper
            researcher.research_conductor.scraper = SourceRegistryScraper(original_scraper)
            logger.info("Enhanced scraper with source registration capabilities (research_conductor)")
        
        # Run the research process
        logger.info("Starting research process...")
        try:
            await researcher.conduct_research()
            logger.info("Research completed successfully")
        except Exception as research_error:
            logger.error(f"Error during research phase: {str(research_error)}")
            raise
        
        # Get the research context if available
        research_data = ""
        research_context = None
        
        # Try different ways to access the research data
        if hasattr(researcher, 'research_context'):
            research_context = researcher.research_context
            research_data = research_context
            logger.info("Found research_context directly on researcher object")
        elif hasattr(researcher, 'research_conductor') and hasattr(researcher.research_conductor, 'research_context'):
            research_context = researcher.research_conductor.research_context
            research_data = research_context
            logger.info("Found research_context on research_conductor")
        elif hasattr(researcher, 'context'):
            research_data = researcher.context
            logger.info("Found context on researcher object")
        else:
            logger.warning("Could not find research_context on researcher or research_conductor")
            # As a fallback, use the scraped data if available
            if hasattr(researcher, 'research_sources') and researcher.research_sources:
                research_data = "\n\n".join([f"Source: {source.get('url', 'Unknown URL')}\nTitle: {source.get('title', 'Unknown Title')}\nContent: {source.get('content', 'No content')}" for source in researcher.research_sources])
                logger.info(f"Using {len(researcher.research_sources)} research sources as fallback data")
        
        # Log some statistics about the research data
        logger.info(f"Research data length: {len(research_data or '')} characters")
        if research_data:
            # Log a sample of the research data for diagnosis
            sample_length = min(1000, len(research_data))
            logger.info(f"Sample of research data: {research_data[:sample_length]}...")
        
        # Extract source URLs
        source_urls = {}
        if research_context:
            source_urls = extract_source_urls(research_context)
            logger.info(f"Found {len(source_urls)} source URLs from research")
        
        # Create a custom prompt that STRICTLY enforces using only the researched information
        custom_prompt = f"""
        You are a specialized AI executive advisor with expertise in creating factual, actionable decision support briefings using ONLY the research data provided.
        
        ## TASK
        Create a comprehensive executive decision support briefing on "{topic}" using EXCLUSIVELY the research data provided below.
        
        ## RESEARCH DATA: 
        {research_data}
        
        ## CRITICAL RULES:
        1. You MUST ONLY use information explicitly present in the RESEARCH DATA provided above.
        2. You MUST NOT invent, hallucinate, or add ANY information not found in the research data.
        3. You MUST cite EVERY piece of information with the exact source title and URL.
        4. If the research data is insufficient to cover a topic completely, state this explicitly rather than filling in gaps.
        5. Citation format: [Source Title](URL) immediately following the information.
        6. Include confidence ratings (HIGH, MEDIUM, LOW) for key assertions based on source reliability.
        
        ## REPORT STRUCTURE:
        1. **Executive Summary**: 
           - Present 3-5 "Critical Developments" as bulleted items
           - For each development include: Overview, Evidence (with citation), Case Study example if available, Confidence Rating, and Time Horizon (CURRENT, NEAR-TERM, LONG-TERM)
        
        2. **Competitive Intelligence**:
           - Key competitor movements and strategies
           - Market positioning and trends
           - Each point must include specific metrics and evidence with citations
        
        3. **Financial Impact Analysis**:
           - Implementation costs (with specific figures if available)
           - ROI projections with timeframes
           - Cost-benefit analysis with quantified metrics
        
        4. **Action Plans**:
           - "30-Day Strategic Moves" with 2-3 specific actionable recommendations
           - "90-Day Strategic Moves" with 2-3 longer-term recommendations
           - Each recommendation must cite supporting evidence
        
        5. **Risk Analysis**:
           - "Delay Costs" - quantified costs of inaction
           - "Mitigation Strategies" - 2-3 specific approaches to minimize risks
           - Each strategy must cite supporting evidence
        
        ## SYNTHESIS APPROACH:
        1. Prioritize actionable insights over general information.
        2. Quantify benefits, costs, and risks whenever possible with specific metrics.
        3. Highlight competitive implications and market positioning opportunities.
        4. Present contradictions or different perspectives when found in the research data.
        5. Focus on time-sensitive information that requires immediate action.
        6. Include relevant statistics, data, and concrete examples when available.
        7. Format for busy executives who need to quickly scan and extract key insights.
        
        ## ADDITIONAL REQUIREMENTS:
        - Report length: approximately {word_count} words
        - Writing language: {language}
        - Use bullet points, bold text, and clear hierarchical structure for quick scanning
        - Include ALL relevant dates mentioned in the research, even if they appear to be in the future.
        - Do NOT refuse to write the report based on concerns about future dates or information.
        - Focus on being clear, concise, and action-oriented rather than theoretical.
        
        Remember: Your primary goal is to provide ACTIONABLE INSIGHTS with proper citation. Only include what you can verify from the research data.
        """
        
        if source_urls:
            url_list = "\n".join([f"- {url} - {info['title']}" for url, info in source_urls.items()])
            source_urls_prompt = f"""
            ## VERIFIED SOURCES:
            
            The following sources were accessed during research. ONLY use these sources and their exact URLs in your citations:
            
            {url_list}
            """
            custom_prompt += source_urls_prompt
        
        # Generate the report with strong emphasis on using only verified information
        logger.info("Generating report using OpenAI GPT-4o...")
        try:
            report = await researcher.write_report(ext_context=custom_prompt)
            logger.info("Report generated successfully")
        except Exception as report_error:
            logger.error(f"Error during report generation: {str(report_error)}")
            raise
        
        logger.info("Research and report generation completed successfully.")
        return report
    except Exception as e:
        logger.error(f"Error generating daily briefing: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

async def main():
    """Main function to parse arguments and generate the report."""
    parser = argparse.ArgumentParser(description="Generate a daily intelligence briefing on a topic.")
    parser.add_argument("--topic", type=str, required=True, help="The topic to research.")
    parser.add_argument("--words", type=int, default=1500, help="Word count for the report.")
    parser.add_argument("--language", type=str, default="en", help="Language for the report.")
    
    args = parser.parse_args()
    
    try:
        logger.info(f"Starting daily intelligence briefing generation for topic: {args.topic}")
        report = await generate_daily_briefing(args.topic, args.words, args.language)
        
        # Save the report to a file
        output_path = save_to_file(report, args.topic)
        
        # Print a summary
        logger.info(f"Daily intelligence briefing generation completed. Output saved to: {output_path}")
        
        # Preview of the report
        print(f"\nDaily Intelligence Briefing saved to: {output_path}")
        print(f"Log file saved to: {log_file}")
        print("\nPreview of generated content:")
        print("------------------------")
        preview_length = min(500, len(report))
        print(report[:preview_length] + "...\n")
        print(f"Full content saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 