import asyncio
import logging
import datetime
from typing import List, Dict, Any

from .deduplicator import Deduplicator
from .linkedin import LinkedInScraper
from .indeed import IndeedScraper
from .sapo import SapoScraper
from .expresso import ExpressoScraper
from .company_pages import CompanyPagesScraper

logger = logging.getLogger(__name__)

class ScraperOrchestrator:
    def __init__(self):
        self.scrapers = [
            LinkedInScraper(),
            IndeedScraper(),
            SapoScraper(),
            ExpressoScraper(),
            CompanyPagesScraper()
        ]
        self.deduplicator = Deduplicator()
        
    async def run_all(self) -> List[Dict[str, Any]]:
        start_time = datetime.datetime.utcnow()
        logger.info(f"Orchestrator started at {start_time.isoformat()}")
        
        # Run all scrapers concurrently
        results = await asyncio.gather(
            *(scraper.run() for scraper in self.scrapers),
            return_exceptions=True
        )
        
        all_jobs = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Scraper {self.scrapers[i].name} failed with error: {result}")
            else:
                all_jobs.extend(result)
                
        total_fetched = len(all_jobs)
        
        # Deduplicate jobs by title+company+location
        unique_jobs = self.deduplicator.process_and_deduplicate(all_jobs)
        
        end_time = datetime.datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(
            f"Orchestrator finished in {duration:.2f} seconds.\n"
            f"Total fetched: {total_fetched}\n"
            f"Duplicates removed: {total_fetched - len(unique_jobs)}\n"
            f"New candidates to insert: {len(unique_jobs)}"
        )
        
        return unique_jobs
