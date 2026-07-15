from .template import Scraper as ScraperTemplate

from bs4 import BeautifulSoup
import requests

URL = "https://www.lazioinnova.it/bandi/?cerca=&stati=&f_tematiche[]=1230&f_tematiche[]=1234&f_tematiche[]=1308&f_tematiche[]=1309&f_tematiche[]=1252&action=Cerca"

class Scraper(ScraperTemplate):

    @staticmethod
    def scrape() -> list[str]:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:152.0) Gecko/20100101 Firefox/152.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Referer": "https://www.lazioinnova.it/bandi/"
        })
        
        response = session.get(URL)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', class_='bandi')
        
        active_bandi = []
        for article in articles:
            # Locate the status indicator
            status_div = article.find('div', class_='status-bando')
            if not status_div:
                continue
                
            status = status_div.get_text(strip=True).lower()
            
            # Skip closed opportunities
            if status == 'chiuso':
                continue
                
            # Extract title and absolute link
            header = article.find('header', class_='entry-header')
            title_tag = header.find('a') if header else None
            
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href', '')
                
                # Combine title and link to form a unique text entry for parsing
                active_bandi.append(f"[{title}]({link})")
                
        return active_bandi

    @staticmethod
    def format(results: list[str]) -> str:
        bullet_points = "\n".join([f"• {item}" for item in results])
        return f"""
🌱 *Fonte:* [Lazio Innova](https://www.lazioinnova.it)
{bullet_points}
🌐 [Vedi tutti i bandi]({URL})
"""


if __name__ == "__main__":
    scraper = Scraper("lazioinnova")
    scraper.run()