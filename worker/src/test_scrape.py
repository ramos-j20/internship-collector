import asyncio
import logging
import json
from src.scrapers.orchestrator import ScraperOrchestrator

# Configure logging to see the output in the terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    logger = logging.getLogger("TestScraper")
    logger.info("Starting test run of the Scraper Orchestrator...")
    
    orchestrator = ScraperOrchestrator()
    
    # Run the orchestrator
    jobs = await orchestrator.run_all()
    
    logger.info(f"Test run completed. Total unique jobs found: {len(jobs)}")
    
    # Print the first 5 jobs nicely formatted
    if jobs:
        logger.info("Here are the first 5 jobs scraped:")
        print(json.dumps(jobs[:5], indent=2, ensure_ascii=False))
    else:
        logger.info("No jobs were found during this run.")

if __name__ == "__main__":
    asyncio.run(main())
