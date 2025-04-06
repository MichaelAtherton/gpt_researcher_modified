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
        logger.info(f"Starting daily intelligence briefing generation for: {query}")
        
        # Get the previous report for this topic
        previous_report = get_previous_report(query)
        
        # Create previous report awareness section
        previous_report_section = "## Previous Report Awareness\n"
        if previous_report:
            previous_report_section += "In creating this briefing, be aware of the previous report on this topic. Focus on providing new or updated information not covered previously, and explicitly note any significant changes or developments since the last report.\n\n"
            previous_report_content = f"### Content from Previous Report:\n{previous_report}\n\n"
        else:
            previous_report_section += "This is the first intelligence briefing on this topic. Establish a comprehensive baseline of current developments that future reports can build upon.\n\n"
            previous_report_content = ""

        custom_prompt = f"""
# TASK: DAILY INTELLIGENCE BRIEFING

Generate a comprehensive, executive-level intelligence briefing on: {query}

{previous_report_section}
{previous_report_content}

## AUDIENCE
- C-suite executives and strategic decision-makers
- Requires actionable, business-relevant insights
- Values concise, high-impact assessment over general information

## FORMAT REQUIREMENTS
- Total length: approximately {total_words} words
- Use crisp, direct language optimized for busy executives
- Include a "Key Takeaways" section at the beginning
- Organize by theme rather than by source
- Break information into digestible sections with clear headings

## INTELLIGENCE STANDARDS
- VERIFY contradictory information and clearly note discrepancies
- PRIORITIZE authoritative and reliable sources
- SPECIFY levels of certainty for each insight (confirmed, likely, possible, etc.)
- DISTINGUISH between facts, analysis, and speculation
- FOCUS on business relevance over general interest

## FINAL REQUIREMENTS
- Write in {language}
- Use markdown format for clear structure
- Date this report {datetime.now().strftime('%B %d, %Y')}
"""
        
        # Create an instance of the researcher and conduct research
        researcher = GPTResearcher(
            query=query,
            report_type="custom_report",
            config_path=None,
            report_format="markdown",
            verbose=True,
        )
        
        logger.info("Conducting research...")
        await researcher.conduct_research()
        
        logger.info("Generating daily intelligence briefing...")
        try:
            # Instead of passing custom_prompt directly to write_report, modify the research context
            # to include our custom prompt instructions
            modified_context = researcher.context + "\n\n" + custom_prompt
            
            # Use write_report without the custom_prompt parameter
            report = await researcher.write_report(ext_context=modified_context)
            
            logger.info("Daily intelligence briefing generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating daily intelligence briefing: {str(e)}")
            return f"Error: {str(e)}"
        
    except Exception as e:
        logger.error(f"Error generating daily intelligence briefing: {str(e)}")
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