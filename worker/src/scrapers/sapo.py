from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class SapoScraper(BaseScraper):
    def __init__(self):
        super().__init__(name="Sapo", source="SAPO Emprego")

    async def fetch(self) -> Any:
        url = "https://emprego.sapo.pt/offers?q=trainee%20OR%20estagio"
        html = await self.fetch_js_rendered_html(url)
        return [html] if html else []

    async def parse(self, raw_data: List[str]) -> List[Dict[str, Any]]:
        jobs = []
        for html in raw_data:
            soup = BeautifulSoup(html, 'html.parser')
            # Their list item blocks often use class 'offer-list-item'
            cards = soup.find_all("div", class_="offer-list-item")
            for card in cards:
                try:
                    title_elem = card.find("h2", class_="title")
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    company_elem = card.find("div", class_="company")
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                    
                    location_elem = card.find("div", class_="location")
                    location = location_elem.get_text(strip=True) if location_elem else "Portugal"
                    
                    link_elem = title_elem.find("a")
                    url = "https://emprego.sapo.pt" + link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "url": url,
                        "type": "Internship/Trainee"
                    })
                except Exception:
                    continue
        return jobs
