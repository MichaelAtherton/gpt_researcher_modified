#!/usr/bin/env python3
"""
Current Topics Generator

This script uses GPT Researcher to find and report on the most recent 
information available about specified topics, focusing specifically on
content from today or yesterday.
"""
import os
import logging
import argparse
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables with override to ensure we have the latest
load_dotenv(override=True)

# Import GPT Researcher components
from gpt_researcher.agent import GPTResearcher
from gpt_researcher.utils.enum import ReportType, ReportSource
from gpt_researcher.prompts import (
    generate_current_topics_search_queries_prompt,
    generate_current_topics_report_prompt
)

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
    
    logging.info(f"Logging to {log_file}")
    return log_file

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate reports on current topics")
    parser.add_argument(
        "--query", 
        type=str, 
        help="Research query for current topics", 
        default="Latest developments in artificial intelligence"
    )
    parser.add_argument(
        "--words", 
        type=int, 
        help="Approximate word count for the report", 
        default=1000
    )
    parser.add_argument(
        "--language", 
        type=str, 
        help="Language for the report", 
        default="english"
    )
    return parser.parse_args()

async def generate_current_topics(query: str, total_words: int = 1000, language: str = "english") -> str:
    """Generate current topics report for a given query."""
    # Initialize GPTResearcher
    researcher = GPTResearcher(
        query=query,
        report_type=ReportType.CustomReport.value,  # Use CustomReport to allow custom prompts
        report_format="default",
        report_source="web",
        config_path=None  # Use default config
    )
    
    # Conduct research (properly awaited)
    await researcher.conduct_research()
    
    # Generate custom prompt using the current_topics_report_prompt function
    custom_prompt = generate_current_topics_report_prompt(
        question=query,
        context="", # This will be filled by the researcher
        report_source="web",
        report_format="default",
        total_words=total_words,
        language=language
    )
    
    # Generate report (properly awaited) with the custom prompt
    report = await researcher.write_report(custom_prompt=custom_prompt)
    
    return report

async def async_main():
    """Async main function to handle coroutines properly."""
    args = parse_arguments()
    log_file = setup_logging()
    logging.info("Starting Current Topics search")
    
    # Use the query from command line arguments
    query = args.query
    logging.info(f"Query: {query}")
    
    # Check for environment variables
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        logging.warning("TAVILY_API_KEY not found in environment variables")
    else:
        logging.info(f"Using Tavily API key: {tavily_api_key[:5]}...")
    
    try:
        # Generate report with proper async handling
        logging.info(f"Conducting research on current topics for: {query}")
        report = await generate_current_topics(
            query, 
            total_words=args.words,
            language=args.language
        )
        
        # Save the output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join("outputs", "current_topics")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a sanitized filename from the query
        sanitized_query = "".join(c if c.isalnum() else "_" for c in query)[:50]
        output_path = os.path.join(output_dir, f"{sanitized_query}_{timestamp}.md")
        with open(output_path, "w") as f:
            f.write(report)
        
        logging.info(f"Current topics report generated and saved to {output_path}")
        print(f"\nCurrent topics report saved to: {output_path}")
        print(f"Log file: {log_file}")
        
        return output_path
        
    except Exception as e:
        logging.error(f"Error in current topics generation: {str(e)}")
        print(f"Error: {str(e)}")
        raise

def main():
    """Main function to run the async event loop."""
    return asyncio.run(async_main())
        
if __name__ == "__main__":
    main() 