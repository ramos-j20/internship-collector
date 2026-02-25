from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class IndeedScraper(BaseScraper):
    def __init__(self):
        super().__init__(name="Indeed", source="Indeed", rate_limit=5.0)

    async def fetch(self) -> Any:
        # Indeed frequently blocks simple HTTP requests; Playwright JS rendering helps bypass basic blocks
        url = "https://pt.indeed.com/jobs?q=internship+OR+trainee+OR+%22entry+level%22&l=Portugal"
        html = await self.fetch_js_rendered_html(url)
        return [html] if html else []

    async def parse(self, raw_data: List[str]) -> List[Dict[str, Any]]:
        jobs = []
        for html in raw_data:
            soup = BeautifulSoup(html, 'html.parser')
            cards = soup.find_all("div", class_="job_seen_beacon")
            for card in cards:
                try:
                    title_elem = card.find("h2", class_="jobTitle")
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    company_elem = card.find("span", {"data-testid": "company-name"})
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                    
                    location_elem = card.find("div", {"data-testid": "text-location"})
                    location = location_elem.get_text(strip=True) if location_elem else "Portugal"
                    
                    url_elem = title_elem.find("a")
                    url = "https://pt.indeed.com" + url_elem['href'] if url_elem and 'href' in url_elem.attrs else ""
                    
                    # Remove hidden visually-hidden text from Indeed titles
                    title = title.replace("new", "").replace("nova", "").strip()

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
