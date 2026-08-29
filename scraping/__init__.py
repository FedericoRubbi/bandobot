import scraping.cdp
import scraping.gazzettaufficiale
import scraping.incentivigov
import scraping.lazioinnova
import scraping.obiettivoeuropa
import scraping.qualenergia


ScrapersList = [
    cdp.Scraper(),
    # gazzettaufficiale.Scraper(),  # not implemented yet (empty module)
    incentivigov.Scraper(),
    lazioinnova.Scraper(),
    obiettivoeuropa.Scraper(),
    qualenergia.Scraper(),
]
