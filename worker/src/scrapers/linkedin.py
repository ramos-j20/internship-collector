from typing import List, Dict, Any
from bs4 import BeautifulSoup
import urllib.parse
from .base_scraper import BaseScraper

class LinkedInScraper(BaseScraper):
    def __init__(self):
        # Increased rate limit to respect LinkedIn a bit more
        super().__init__(name="LinkedIn", source="LinkedIn", rate_limit=3.0)
        self.base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        # Search query matching "internship OR trainee OR entry level" in Portugal
        keywords = "internship OR trainee OR \"entry level\""
        location = "Portugal"
        self.query_params = {
            "keywords": keywords,
            "location": location,
            "geoId": "100364837", # GeoID for Portugal
            "trk": "public_jobs_jobs-search-bar_search-submit",
            "position": 1,
            "pageNum": 0,
            "start": 0
        }

    async def fetch(self) -> Any:
        # Fetch a few pages for starting (2 pages * 25 jobs = 50 jobs)
        all_html = []
        for start in [0, 25]:
            params = self.query_params.copy()
            params["start"] = start
            query_string = urllib.parse.urlencode(params)
            url = f"{self.base_url}?{query_string}"
            
            html = await self.fetch_html(url)
            if html:
                all_html.append(html)
        return all_html

    async def parse(self, raw_data: List[str]) -> List[Dict[str, Any]]:
        jobs = []
        for html in raw_data:
            soup = BeautifulSoup(html, 'html.parser')
            job_cards = soup.find_all("li")
            for card in job_cards:
                try:
                    title_elem = card.find("h3", class_="base-search-card__title")
                    company_elem = card.find("h4", class_="base-search-card__subtitle")
                    location_elem = card.find("span", class_="job-search-card__location")
                    url_elem = card.find("a", class_="base-card__full-link")
                    
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                    location = location_elem.get_text(strip=True) if location_elem else "Portugal"
                    url = url_elem['href'] if url_elem else ""
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "url": url,
                        "type": "Entry Level/Internship"
                    })
                except Exception as e:
                    continue
        return jobs
