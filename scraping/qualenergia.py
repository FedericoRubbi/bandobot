from .template import Scraper as ScraperTemplate

from bs4 import BeautifulSoup
import requests

URL = "https://www.qualenergia.it/pro/articoli-pro/bandi-e-appalti-del-giorno/"

class Scraper(ScraperTemplate):

    @ staticmethod
    def scrape() -> list[str]:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        })
        response = session.get(URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        return [soup.find(class_="sottotitolo-articolo").text]

    @staticmethod
    def format(results: list[str]) -> str:
        return f"""
        🌱 *Fonte:* [qualenergia.it](https://www.qualenergia.it)
        • {results[0]}
        🌐 [Leggi l'articolo completo]({URL})
        """


if __name__ == "__main__":
    scraper = Scraper("qualenergia")
    scraper.run()