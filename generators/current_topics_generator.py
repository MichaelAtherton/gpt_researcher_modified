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
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables with override to ensure we have the latest
load_dotenv(override=True)

# Import GPT Researcher components
from gpt_researcher.agent import GPTResearcher
from gpt_researcher.utils.enum import ReportType, ReportSource, Tone

# Set up logging
def setup_logging():
    """Configure logging for the current topics generator."""
    log_dir = os.path.join("logs", "current_topics_logs")
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"current_topics_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging to {log_file}")
    
    return logger, log_file

# Set up logging
logger, log_file = setup_logging()

def get_previous_report(topic, directory="outputs/current_topics"):
    """
    Get the most recent previous report for the given topic.
    
    Args:
        topic (str): The topic to find previous reports for
        directory (str): The directory where reports are stored
        
    Returns:
        str: The content of the most recent report, or empty string if none found
    """
    if not os.path.exists(directory):
        logger.info(f"Output directory {directory} does not exist yet")
        return ""
    
    # Clean the topic for use in a filename
    sanitized_topic = "".join(c if c.isalnum() else "_" for c in topic)
    
    # Get all files matching the topic pattern
    matching_files = [
        os.path.join(directory, f) for f in os.listdir(directory)
        if f.startswith(sanitized_topic) and f.endswith(".md")
    ]
    
    if not matching_files:
        logger.info(f"No previous reports found for topic: {topic}")
        return ""
    
    # Sort by modification time (most recent first)
    matching_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
    
    # Get the most recent file
    most_recent = matching_files[0]
    logger.info(f"Found previous report: {most_recent}")
    
    # Read the file
    with open(most_recent, 'r') as f:
        content = f.read()
    
    logger.info(f"Retrieved previous report of {len(content)} characters")
    return content

def save_to_file(content, topic, directory="outputs/current_topics"):
    """Save the generated report to a file"""
    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Create a filename with the topic and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Clean the topic for use in a filename (remove special characters)
    clean_topic = "".join(c if c.isalnum() else "_" for c in topic)
    filename = f"{clean_topic}_{timestamp}.md"
    filepath = os.path.join(directory, filename)
    
    # Write the content to the file
    with open(filepath, "w") as f:
        f.write(content)
    
    logger.info(f"Saved current topics report to: {filepath}")
    return filepath

async def generate_daily_briefing(query: str, total_words: int = 1000, language: str = "english") -> str:
    """Generate daily intelligence briefing for a given query."""
    try:
        logger.info(f"Starting executive decision support briefing generation for: {query}")
        
        # Get the previous report for this topic
        previous_report = get_previous_report(query)
        
        # Create previous report awareness section
        previous_report_section = "## Previous Report Analysis\n"
        if previous_report:
            previous_report_section += "This briefing builds on previous intelligence, focusing on new developments and their strategic implications. Key changes and action items are highlighted for immediate decision-making.\n\n"
            previous_report_content = f"### Previous Report Context:\n{previous_report}\n\n"
        else:
            previous_report_section += "This is the initial strategic briefing on this topic. It establishes baseline metrics and action items for ongoing monitoring.\n\n"
            previous_report_content = ""

        custom_prompt = f"""
# TASK: EXECUTIVE DECISION SUPPORT BRIEFING

Generate a comprehensive, action-oriented strategic briefing on: {query}

{previous_report_section}
{previous_report_content}

## EXECUTIVE FOCUS
- Immediate decision points requiring CEO attention
- Competitive positioning and market dynamics
- Resource allocation and ROI considerations
- Risk assessment and mitigation strategies

## REQUIRED SECTIONS
1. Executive Summary
   - Critical developments (last 24-48 hours)
   - GO/NO-GO recommendations
   - Risk levels for each decision point

2. Competitive Intelligence
   - Competitor movements and strategies
   - Market share implications
   - First-mover opportunities
   - Defensive requirements

3. Financial Impact Analysis
   - Implementation costs
   - ROI projections
   - Resource requirements
   - Risk-adjusted returns

4. Action Plans
   - 30-day immediate actions
   - 90-day strategic moves
   - Success metrics
   - Key Performance Indicators

5. Risk Analysis
   - Delay costs
   - Competitive threats
   - Implementation challenges
   - Mitigation strategies

## INTELLIGENCE STANDARDS
- Verify all competitive claims
- Prioritize quantifiable data
- Note certainty levels
- Distinguish facts from speculation

## FORMAT
- Total length: approximately {total_words} words
- Language: {language}
- Style: Direct, action-oriented executive format
- Structure: Clear decision points and recommendations
"""
        
        # Create an instance of the researcher and conduct research
        researcher = GPTResearcher(
            query=query,
            report_type="custom_report",
            config_path=None,
            report_format="markdown",
            verbose=True,
        )
        
        logger.info("Conducting strategic research...")
        await researcher.conduct_research()
        
        logger.info("Generating executive decision support briefing...")
        try:
            # Modify research context to include competitive intelligence focus
            modified_context = f"""
COMPETITIVE INTELLIGENCE FOCUS:
The following research must be analyzed through a competitive lens, identifying:
1. Market positioning opportunities
2. Competitor vulnerabilities
3. First-mover advantages
4. Defensive necessities

RESEARCH CONTEXT:
{researcher.context}

BRIEFING REQUIREMENTS:
{custom_prompt}
"""
            
            # Generate the report with enhanced context
            report = await researcher.write_report(ext_context=modified_context)
            
            logger.info("Executive decision support briefing generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating executive briefing: {str(e)}")
            return f"Error: {str(e)}"
        
    except Exception as e:
        logger.error(f"Error in executive briefing generation: {str(e)}")
        return f"Error: {str(e)}"

async def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate daily intelligence briefing on current topics')
    parser.add_argument('--topic', type=str, default="Artificial Intelligence trends", 
                      help='Topic to research (default: "Artificial Intelligence trends")')
    parser.add_argument('--words', type=int, default=1000,
                      help='Target word count for the report (default: 1000)')
    parser.add_argument('--language', type=str, default="english",
                      help='Language for the report (default: english)')
    
    args = parser.parse_args()
    
    # Start the process
    logger.info(f"Starting daily intelligence briefing generation for topic: {args.topic}")
    
    # Generate the briefing
    result = await generate_daily_briefing(args.topic, args.words, args.language)
    
    # Save to file
    filepath = save_to_file(result, args.topic)
    
    # Log completion
    logger.info(f"Daily intelligence briefing generation completed. Output saved to: {filepath}")
    
    # Print success message
    print(f"\nDaily Intelligence Briefing saved to: {filepath}")
    print(f"Log file saved to: {log_file}")
    print("\nPreview of generated content:")
    print("------------------------")
    # Print just the first 500 characters as a preview
    preview_length = 500
    print(f"{result[:preview_length]}...")
    print(f"\nFull content saved to: {filepath}")

if __name__ == "__main__":
    asyncio.run(main()) 