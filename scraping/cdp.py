import time

from .template import Scraper as ScraperTemplate

from bs4 import BeautifulSoup
import requests

URL = "https://www.cdp.it/sitointernet/it/fondazione_bandi.page"
PAGE_FETCH_DELAY_SECONDS = 2.0
MAX_ATTEMPTS_PER_PAGE = 5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:152.0) Gecko/20100101 Firefox/152.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

class Scraper(ScraperTemplate):

    @staticmethod
    def _fetch_page(page: int) -> BeautifulSoup | None:
        # The site's edge cache/WAF serves a stale page (usually page 1) when
        # two requests hit it back-to-back too quickly, regardless of the
        # "1_item" query param or session state. Spacing requests out avoids it.
        params = {"1_item": page, "searchPagination": ""} if page > 1 else {}
        response = requests.get(URL, params=params, headers=HEADERS)
        if response.status_code != 200:
            return None
        return BeautifulSoup(response.text, 'html.parser')

    @staticmethod
    def _extract_slides(soup: BeautifulSoup) -> list[str]:
        slider = soup.find(id="raccoltapubblicazioni-slider")
        if not slider:
            return []

        bandi = []
        for slide in slider.find_all(class_="slide"):
            link_tag = slide.find("a")
            title_tag = slide.find(class_="text-blue")
            if not link_tag or not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = link_tag.get("href", "")
            bandi.append(f"[{title}]({link})")

        return bandi

    @staticmethod
    def _last_page(soup: BeautifulSoup) -> int:
        dots = soup.find(class_="dots-wrapper")
        if not dots:
            return 1

        pages = [1]
        for anchor in dots.find_all(class_="page-number"):
            text = anchor.get_text(strip=True)
            if text.isdigit():
                pages.append(int(text))

        return max(pages)

    @staticmethod
    def scrape() -> list[str]:
        soup = Scraper._fetch_page(1)
        if not soup:
            return []

        last_page = Scraper._last_page(soup)

        seen_links = set()
        bandi = []
        for page in range(1, last_page + 1):
            page_soup = soup if page == 1 else None

            # The site occasionally serves a stale/duplicate page (a caching
            # race, unrelated to the "1_item" param) under rapid requests.
            # Retry with a delay until this page yields entries we haven't
            # already collected, or we exhaust the attempts.
            for attempt in range(MAX_ATTEMPTS_PER_PAGE):
                if page_soup is None:
                    time.sleep(PAGE_FETCH_DELAY_SECONDS)
                    page_soup = Scraper._fetch_page(page)
                if not page_soup:
                    break

                entries = Scraper._extract_slides(page_soup)
                links = {entry.rsplit("(", 1)[-1].rstrip(")") for entry in entries}
                if page == 1 or not links or not links.issubset(seen_links):
                    break

                page_soup = None  # force a retry fetch

            if not page_soup:
                continue

            for entry in Scraper._extract_slides(page_soup):
                link = entry.rsplit("(", 1)[-1].rstrip(")")
                if link not in seen_links:
                    seen_links.add(link)
                    bandi.append(entry)

        return bandi

    @staticmethod
    def format(results: list[str]) -> str:
        bullet_points = "\n".join([f"• {item}" for item in results])
        return f"""
🌱 *Fonte:* [CDP - Fondazione Cassa Depositi e Prestiti](https://www.cdp.it)
{bullet_points}
🌐 [Vedi tutti i bandi]({URL})
"""


if __name__ == "__main__":
    scraper = Scraper()
    scraper.run()
