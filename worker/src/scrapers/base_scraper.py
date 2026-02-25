import abc
import asyncio
import logging
import random
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
]

class BaseScraper(abc.ABC):
    """
    Abstract base class for all scrapers.
    Handles rate limiting, retry logic (exponential backoff), and standardizing output.
    """
    
    def __init__(self, name: str, source: str, rate_limit: float = 2.0, max_retries: int = 3):
        self.name = name
        self.source = source
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(headers={"User-Agent": random.choice(USER_AGENTS)}, timeout=30.0)

    async def close(self):
        await self.client.aclose()
        
    def _get_headers(self) -> Dict[str, str]:
        return {"User-Agent": random.choice(USER_AGENTS)}

    async def fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML content with retry and backoff logic using httpx."""
        retries = 0
        backoff = 1.0
        while retries <= self.max_retries:
            try:
                await asyncio.sleep(self.rate_limit + random.uniform(0, 1)) # Rate limiting with jitter
                response = await self.client.get(url, headers=self._get_headers())
                response.raise_for_status()
                return response.text
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                logger.warning(f"[{self.name}] Error fetching {url}: {e}. Retry {retries}/{self.max_retries}")
                retries += 1
                if retries <= self.max_retries:
                    await asyncio.sleep(backoff)
                    backoff *= 2 # Exponential backoff
        logger.error(f"[{self.name}] Max retries reached for {url}.")
        return None

    async def fetch_js_rendered_html(self, url: str, wait_selector: str = None) -> Optional[str]:
        """Fetch JS rendered HTML using Playwright."""
        retries = 0
        backoff = 1.0
        while retries <= self.max_retries:
            try:
                await asyncio.sleep(self.rate_limit + random.uniform(0, 1))
                async with async_playwright() as p:
                    # Launching chromium with specific args to bypass basic bot detection
                    browser = await p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
                    page = await browser.new_page(user_agent=random.choice(USER_AGENTS))
                    
                    # Instead of 'networkidle' which hangs on tracking scripts, wait for 'domcontentloaded' with a shorter timeout
                    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    
                    if wait_selector:
                        # Wait for specific element, timeout after 5s if it doesn't appear
                        await page.wait_for_selector(wait_selector, timeout=5000)
                    else:
                        # Just give it 2 seconds to run client-side JS
                        await page.wait_for_timeout(2000)
                        
                    content = await page.content()
                    await browser.close()
                    return content
            except Exception as e:
                logger.warning(f"[{self.name}] Playwright error fetching {url}: {e}. Retry {retries}/{self.max_retries}")
                retries += 1
                if retries <= self.max_retries:
                    await asyncio.sleep(backoff)
                    backoff *= 2
        logger.error(f"[{self.name}] Max retries reached for JS rendering {url}.")
        return None

    @abc.abstractmethod
    async def fetch(self) -> Any:
        """Fetch raw data (HTML pages, JSON responses, etc.)."""
        pass

    @abc.abstractmethod
    async def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse raw data into dictionaries representing jobs."""
        pass

    async def normalize(self, parsed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize the parsed data to canonical schema.
        Override if needed, else assumes parsed_data generally maps to schema, 
        but normalizer module handles the strict mapping.
        """
        from .normalizer import normalize_job # Lazy import to avoid circular dependency
        normalized = []
        for job in parsed_data:
            job['source'] = self.source
            normalized.append(normalize_job(job))
        return normalized

    async def run(self) -> List[Dict[str, Any]]:
        """Main execution flow for a scraper."""
        logger.info(f"[{self.name}] Starting scrape.")
        raw_data = await self.fetch()
        if not raw_data:
            logger.info(f"[{self.name}] No raw data fetched.")
            await self.close()
            return []
            
        parsed_data = await self.parse(raw_data)
        logger.info(f"[{self.name}] Parsed {len(parsed_data)} raw items.")
        
        normalized_data = await self.normalize(parsed_data)
        logger.info(f"[{self.name}] Normalized {len(normalized_data)} items.")
        
        await self.close()
        return normalized_data
