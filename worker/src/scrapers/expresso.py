from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class ExpressoScraper(BaseScraper):
    def __init__(self):
        super().__init__(name="Expresso", source="Expresso Emprego")

    async def fetch(self) -> Any:
        url = "https://expressoemprego.pt/ofertas?q=est%C3%A1gio+OR+trainee"
        html = await self.fetch_js_rendered_html(url)
        return [html] if html else []

    async def parse(self, raw_data: List[str]) -> List[Dict[str, Any]]:
        jobs = []
        for html in raw_data:
            soup = BeautifulSoup(html, 'html.parser')
            # Select common classes or articles that might contain offers
            cards = soup.select(".offer-item, article")
            for card in cards:
                try:
                    title_elem = card.find(["h2", "h3"])
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    company_elem = card.select_one(".company-name")
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                    location = "Portugal"  # Specific element extraction can be refined
                    
                    link_elem = card.find("a")
                    href = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
                    if href.startswith("/"):
                        url = "https://expressoemprego.pt" + href 
                    else:
                        url = href
                    
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
