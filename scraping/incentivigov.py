import logging
import csv
import io
import requests
from datetime import datetime
from .template import Scraper as ScraperTemplate

logger = logging.getLogger(__name__)

# The Solr Endpoint returning CSV data for all incentives
URL = "https://www.incentivi.gov.it/solr/coredrupal/select?q.op=OR&wt=csv&rows=8000&fl=ID_Incentivo:zs_nid,Titolo:zs_title,Descrizione:zs_body,Obiettivo_Finalita:zm_field_scopes_value,Data_apertura:zs_field_open_date,Data_chiusura:zs_field_close_date,Note_di_apertura_chiusura:zs_field_close_date_descriptor,Dimensioni:zm_field_dimensions_value,Tipologia_Soggetto:zm_field_subject_type_value,Forma_agevolazione:zm_field_support_form_value,Costi_Ammessi:zm_field_granted_costs_value,Spesa_Ammessa_min:zs_field_cost_min,Spesa_Ammessa_max:zs_field_cost_max,Agevolazione_Concedibile_min:zs_field_support_grant_type_min,Agevolazione_Concedibile_max:zs_field_support_grant_type_max,Settore_Attivita:zm_field_activity_sector_value,Codici_ATECO:zs_field_ateco,Regioni:zm_field_regions_value,Comuni:zs_field_comuni,Ambito_territoriale:zm_field_special_territory_value,Soggetto_Concedente:zs_field_subject_grant,Base_normativa_primaria:zs_field_primary_ruleset,Base_normativa_secondaria:zs_field_secondary_ruleset,Provvedimento_attuativo:zs_field_implementation_ruleset,Gazzetta_ufficiale:zs_field_official_references,Stanziamento_incentivo:zs_field_budget_allocation,Link_istituzionale:zs_field_link,Altre_caratteristiche:zs_field_other_characteristic,Data_ultimo_aggiornamento:ds_last_update,&q=index_id:incentivi"

BASE_SITE_URL = "https://www.incentivi.gov.it/it/catalogo"

# Targeted filter sets
TARGET_REGIONS = {"lazio", "umbria", "abruzzo"}
TARGET_GOALS = {"innovazione e ricerca", "transizione ecologica"}

class Scraper(ScraperTemplate):

    @staticmethod
    def scrape() -> list[str]:
        session = requests.Session()
        
        # 1. Set up headers to perfectly mimic the real browser request you provided
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:152.0) Gecko/20100101 Firefox/152.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.incentivi.gov.it/it/open-data",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        })
        
        try:
            # 2. Step 1: Hit the landing page first to initialize cookies
            logger.info("Initializing session cookies from landing page...")
            landing_response = session.get("https://www.incentivi.gov.it/it/open-data", timeout=10)
            landing_response.raise_for_status()
            
            # Update headers to match Ajax/Fetch requirements of the API call
            session.headers.update({
                "Accept": "*/*",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            })
            
            # 3. Step 2: Fetch the actual dataset using the validated session
            clean_url = (
                "https://www.incentivi.gov.it/solr/coredrupal/select"
                "?q.op=OR&wt=csv&rows=8000"
                "&fl=ID_Incentivo:zs_nid,Titolo:zs_title,Descrizione:zs_body,"
                "Obiettivo_Finalita:zm_field_scopes_value,Data_apertura:zs_field_open_date,"
                "Data_chiusura:zs_field_close_date,Note_di_apertura_chiusura:zs_field_close_date_descriptor,"
                "Dimensioni:zm_field_dimensions_value,Tipologia_Soggetto:zm_field_subject_type_value,"
                "Forma_agevolazione:zm_field_support_form_value,Costi_Ammessi:zm_field_granted_costs_value,"
                "Spesa_Ammessa_min:zs_field_cost_min,Spesa_Ammessa_max:zs_field_cost_max,"
                "Agevolazione_Concedibile_min:zs_field_support_grant_type_min,"
                "Agevolazione_Concedibile_max:zs_field_support_grant_type_max,"
                "Settore_Attivita:zm_field_activity_sector_value,Codici_ATECO:zs_field_ateco,"
                "Regioni:zm_field_regions_value,Comuni:zs_field_comuni,"
                "Ambito_territoriale:zm_field_special_territory_value,Soggetto_Concedente:zs_field_subject_grant,"
                "Base_normativa_primaria:zs_field_primary_ruleset,Base_normativa_secondaria:zs_field_secondary_ruleset,"
                "Provvedimento_attuativo:zs_field_implementation_ruleset,Gazzetta_ufficiale:zs_field_official_references,"
                "Stanziamento_incentivo:zs_field_budget_allocation,Link_istituzionale:zs_field_link,"
                "Altre_caratteristiche:zs_field_other_characteristic,Data_ultimo_aggiornamento:ds_last_update"
                "&q=index_id:incentivi"
            )
            
            logger.info("Requesting Solr data extract...")
            response = session.get(clean_url, timeout=20)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
        except Exception as e:
            logger.error("Failed to fetch open data from incentivi.gov.it: %s", e)
            return []

        results = []
        now = datetime.now()

        csv_file = io.StringIO(response.text)
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            # 1. Skip expired incentives
            close_date_str = row.get("Data_chiusura", "").strip()
            if close_date_str:
                try:
                    date_part = close_date_str.split("T")[0]
                    close_date = datetime.strptime(date_part, "%Y-%m-%d")
                    if close_date < now:
                        continue
                except ValueError:
                    pass

            # 2. Filter by regions
            regions_field = row.get("Regioni", "").lower()
            if regions_field:
                has_target_region = any(r in regions_field for r in TARGET_REGIONS)
                is_national = "nazionale" in regions_field or "tutto il territorio" in regions_field
                if not (has_target_region or is_national):
                    continue

            # 3. Filter by objective
            goals_field = row.get("Obiettivo_Finalita", "").lower()
            if not any(g in goals_field for g in TARGET_GOALS):
                continue

            results.append(
                f"{row.get('ID_Incentivo','')}||"
                f"{row.get('Titolo','')[:100]}||"
                f"{row.get('Data_chiusura','')}||"
                f"{row.get('Link_istituzionale','')}"
            )
            
        return results
    
    @staticmethod
    def format(results: list[str]) -> str:
        messages = []
        messages.append("🇮🇹 *Nuovi Incentivi Selezionati* (Incentivi.gov.it) 🇮🇹\n"
                        "🎯 _Filtro applicato: Lazio/Umbria/Abruzzo & Innovazione/Green_\n")
        
        for record in results:
            try:
                parts = record.split("||")
                if len(parts) < 4:
                    continue
                incentive_id, title, close_date, ext_link = parts
                
                formatted_close = "Senza scadenza"
                if close_date:
                    try:
                        date_part = close_date.split("T")[0]
                        dt = datetime.strptime(date_part, "%Y-%m-%d")
                        formatted_close = dt.strftime("%d/%m/%Y")
                    except Exception:
                        formatted_close = close_date
                
                platform_link = f"{BASE_SITE_URL}/{title.lower().replace(' ', '-').replace('/', '-')}" if title else BASE_SITE_URL
                target_url = ext_link if ext_link else platform_link

                item_md = (
                    f"🔸 *{title}*\n"
                    f"📅 *Scadenza:* {formatted_close}\n"
                    f"🔗 [Accedi all'incentivo]({target_url})\n"
                )
                messages.append(item_md)
            except Exception as e:
                logger.error("Failed to format record: %s", e)
                continue
                
        return "\n---\n\n".join(messages)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = Scraper()
    output = scraper.run()
    if output:
        print("--- Generated Message ---")
        print(output)
    else:
        print("No new/active incentives found matching criteria.")