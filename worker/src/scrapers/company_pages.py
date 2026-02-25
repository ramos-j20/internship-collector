import asyncio
from typing import List, Dict, Any
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class CompanyPagesScraper(BaseScraper):
    def __init__(self):
        super().__init__(name="CompanyPages", source="Direct Company")
        # List of pages to check (expanding for tech companies requested)
        self.companies = {
            "Feedzai": "https://feedzai.com/careers/open-roles/?location=Portugal",
            "Talkdesk": "https://www.talkdesk.com/careers/open-roles/",
            "Unbabel": "https://unbabel.com/careers/open-roles/",
            "Sword Health": "https://swordhealth.com/careers",
            "Volkswagen Digital Solutions": "https://www.vwds.pt/careers/",
            "Blip": "https://blip.pt/careers/",
            "Critical TechWorks": "https://www.criticaltechworks.com/careers",
            "Mindera": "https://mindera.com/careers/"
        }

    async def fetch(self) -> Any:
        # Fetch directly since each is just 1 page
        results = {}
        for company, url in self.companies.items():
            # Use JS render as many career pages use Greenhouse/Lever SPA
            html = await self.fetch_js_rendered_html(url) 
            if html:
                results[company] = {"html": html, "url": url}
        return results

    async def parse(self, raw_data: Dict[str, Dict[str, str]]) -> List[Dict[str, Any]]:
        jobs = []
        for company, data in raw_data.items():
            html = data["html"]
            soup = BeautifulSoup(html, 'html.parser')
            
            # Identify typical anchor tags that contain job references
            for link in soup.find_all('a'):
                text = link.get_text(strip=True).lower()
                href = link.get('href', '')
                if any(k in text for k in ['intern', 'trainee', 'estágio', 'junior', 'entry']):
                    if href.startswith('/'):
                        parsed = urlparse(data["url"])
                        href = f"{parsed.scheme}://{parsed.netloc}{href}"
                        
                    jobs.append({
                        "title": link.get_text(strip=True),
                        "company": company,
                        "location": "Portugal",
                        "url": href,
                        "type": "Trainee/Entry Level"
                    })
        return jobs
