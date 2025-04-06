from gpt_researcher import GPTResearcher
from gpt_researcher.utils.enum import ReportType, Tone
import asyncio
from dotenv import load_dotenv
import logging
import os
import datetime

# Set up logging
def setup_logging():
    """Configure logging to log to both console and a file"""
    log_dir = "logs/linkedin_post_logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Create timestamp for the log filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"linkedin_posts_{timestamp}.log")
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler
            logging.FileHandler(log_file)
        ]
    )
    
    # Get the logger and log the start of the process
    logger = logging.getLogger(__name__)
    logger.info(f"Logging to file: {log_file}")
    
    return logger, log_file

# Set up logging
logger, log_file = setup_logging()

async def generate_linkedin_posts(query: str) -> str:
    try:
        # Load environment variables directly here to ensure they're loaded
        load_dotenv(override=True)  # Add override=True to ensure .env values take precedence
        
        # Check that environment variables are set
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        logger.info(f"Original Tavily API key from env: {tavily_api_key}")
        
        # Clean API key first
        if "'" in tavily_api_key or '"' in tavily_api_key or ' ' in tavily_api_key:
            logger.warning("API key contains quotes or spaces - cleaning API key")
            tavily_api_key = tavily_api_key.strip("' \"")
            os.environ["TAVILY_API_KEY"] = tavily_api_key
            logger.info(f"After cleaning, Tavily API key: {tavily_api_key}")
        
        # Double check the environment variable after cleaning
        logger.info(f"Environment variable after cleaning: {os.getenv('TAVILY_API_KEY')}")
        
        logger.info(f"Using Tavily API key: {tavily_api_key[:10]}...")
        logger.info(f"API key length: {len(tavily_api_key)}")
        logger.info(f"API key format check - starts with 'tvly-': {tavily_api_key.startswith('tvly-')}")
        
        logger.info("Starting LinkedIn post generation process...")
        logger.info(f"Starting research for query: {query}")
        
        # Initialize researcher with default config and cleaned API key
        researcher = GPTResearcher(
            query=query,
            report_type=ReportType.ResearchReport.value,
            report_source="web",
            config_path=None  # Use default config
        )

        # Double check the environment variable after researcher initialization
        logger.info(f"Environment variable after researcher init: {os.getenv('TAVILY_API_KEY')}")

        # Conduct research and generate report
        await researcher.conduct_research()
        logger.info("Research completed, generating LinkedIn posts...")
        report = await researcher.write_report()
        return report

    except Exception as e:
        logger.error(f"Error generating LinkedIn posts: {str(e)}")
        return f"Error: {str(e)}"

def save_to_file(content, topic, directory="outputs/linkedin_posts"):
    """Save the generated LinkedIn posts to a file"""
    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Create a filename with the topic and timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Clean the topic for use in a filename (remove special characters)
    clean_topic = "".join(c if c.isalnum() else "_" for c in topic)
    filename = f"{clean_topic}_{timestamp}.md"
    filepath = os.path.join(directory, filename)
    
    # Write the content to the file
    with open(filepath, "w") as f:
        f.write(f"# LinkedIn Posts on: {topic}\n\n")
        f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(content)
    
    logger.info(f"Saved LinkedIn posts to: {filepath}")
    return filepath

async def main():
    # Load environment variables from .env file with override to ensure they take precedence
    load_dotenv(override=True)
    
    # Define the topic
    topic = "Chemical-free household products"
    
    # Print all environment variables for debugging (redacting sensitive info)
    logger.info("Environment variables:")
    for key, value in os.environ.items():
        if "KEY" in key or "TOKEN" in key or "SECRET" in key:
            if value:
                logger.info(f"{key}: {value[:5]}...{value[-2:]} (length: {len(value)})")
            else:
                logger.info(f"{key}: <empty>")
    
    # Generate posts for the topic
    result = await generate_linkedin_posts(topic)
    
    # Save the posts to a file
    filepath = save_to_file(result, topic)
    
    # Log completion
    logger.info(f"LinkedIn post generation completed. Output saved to: {filepath}")
    logger.info(f"Log file saved to: {log_file}")
    
    # Print success message
    print(f"\nGenerated LinkedIn Posts saved to: {filepath}")
    print(f"Log file saved to: {log_file}")
    print("\nPreview of generated content:")
    print("------------------------")
    # Print just the first 500 characters as a preview
    preview_length = 500
    print(f"{result[:preview_length]}...")
    print(f"\nFull content saved to: {filepath}")

if __name__ == "__main__":
    asyncio.run(main()) 