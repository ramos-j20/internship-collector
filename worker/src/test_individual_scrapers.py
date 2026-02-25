import asyncio
import logging
import json
import sys

from src.scrapers.indeed import IndeedScraper
from src.scrapers.sapo import SapoScraper
from src.scrapers.expresso import ExpressoScraper
from src.scrapers.company_pages import CompanyPagesScraper

# Configure logging to see the output in the terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_scraper(scraper_class, scraper_name):
    logger = logging.getLogger(f"Test{scraper_name}")
    logger.info(f"Starting test run for {scraper_name}...")
    
    scraper = scraper_class()
    
    try:
        jobs = await scraper.run()
        logger.info(f"Test run completed. Total jobs found: {len(jobs)}")
        
        if jobs:
            logger.info(f"First 2 jobs from {scraper_name}:")
            print(json.dumps(jobs[:2], indent=2, ensure_ascii=False))
        else:
            logger.warning(f"No jobs were found by {scraper_name}.")
    except Exception as e:
        logger.error(f"Error running {scraper_name}: {e}")

async def main():
    if len(sys.argv) > 1:
        target = sys.argv[1].lower()
        if target == "indeed":
            await test_scraper(IndeedScraper, "Indeed")
        elif target == "sapo":
            await test_scraper(SapoScraper, "Sapo")
        elif target == "expresso":
            await test_scraper(ExpressoScraper, "Expresso")
        elif target == "companies":
            await test_scraper(CompanyPagesScraper, "CompanyPages")
        else:
            print("Unknown target. Use: indeed, sapo, expresso, or companies")
    else:
        # Test all non-LinkedIn scrapers one by one to avoid overwhelming output
        await test_scraper(IndeedScraper, "Indeed")
        print("\n" + "="*50 + "\n")
        await test_scraper(SapoScraper, "Sapo")
        print("\n" + "="*50 + "\n")
        await test_scraper(ExpressoScraper, "Expresso")
        print("\n" + "="*50 + "\n")
        await test_scraper(CompanyPagesScraper, "CompanyPages")

if __name__ == "__main__":
    asyncio.run(main())
