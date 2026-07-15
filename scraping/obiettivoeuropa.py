import logging
import json
import requests
from .template import Scraper as ScraperTemplate

logger = logging.getLogger(__name__)

URL = "https://www.obiettivoeuropa.com/api/call/?page=1&ordering=-published&sectors=24,135,130,86,45,141,107,83,127,115,85,46&regions=13,12,10"
BASE_SITE_URL = "https://www.obiettivoeuropa.com"

class Scraper(ScraperTemplate):

    @staticmethod
    def scrape() -> list[str]:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        })
        
        try:
            response = session.get(URL)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error("Failed to fetch or parse API data: %s", e)
            return []

        results = []
        # Extract individual calls and serialize them to a string representation
        # so the template.py hash check works seamlessly.
        for item in data.get("results", []):
            results.append(json.dumps(item))
            
        return results

    @staticmethod
    def format(results: list[str]) -> str:
        messages = []
        messages.append("🇪🇺 *Nuovi Bandi da Obiettivo Europa* 🇪🇺\n")
        
        for json_str in results:
            try:
                item = json.loads(json_str)
                title = item.get("title", "Senza Titolo")
                deadline = item.get("deadline_label", "N/A")
                days_left = item.get("deadline_days_left", "N/A")
                budget_raw = item.get("budget")
                
                # Format budget with thousands separators if it exists
                if budget_raw is not None:
                    budget = f"€ {budget_raw:,.0f}".replace(",", ".")
                else:
                    value = "Non specificato"
                
                relative_url = item.get("url", "")
                full_url = f"{BASE_SITE_URL}{relative_url}" if relative_url else BASE_SITE_URL
                
                item_md = (
                    f"📌 *{title}*\n"
                    f"💰 *Budget:* {budget}\n"
                    f"📅 *Scadenza:* {deadline} ({days_left} giorni rimasti)\n"
                    f"🔗 [Leggi il bando completo]({full_url})\n"
                )
                messages.append(item_md)
            except Exception as e:
                logger.error("Failed to format item: %s", e)
                continue
                
        return "\n---\n\n".join(messages)


if __name__ == "__main__":
    # Standard standalone debugging block
    logging.basicConfig(level=logging.INFO)
    scraper = Scraper()
    output = scraper.run()
    if output:
        print("--- Generated Message ---")
        print(output)
    else:
        print("No new updates found.")