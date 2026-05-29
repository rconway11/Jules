import asyncio
from playwright.async_api import async_playwright
from config import HOSPITALS
from scrapers import PhenomScraper, WorkdayScraper, UCSFScraper, KaiserScraper, UniversalScraper
from processor import filter_jobs
from notifier import send_email
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_finder():
    logger.info("Starting daily job search...")

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        scrapers = {
            "Stanford Health Care": PhenomScraper(),
            "Sutter Health": PhenomScraper(),
            "John Muir Health": WorkdayScraper(),
            "El Camino Health": WorkdayScraper(),
            "UCSF": UCSFScraper(),
            "Kaiser Permanente": KaiserScraper(),
            "Dignity Health": UniversalScraper(),
            "AMR": UniversalScraper(),
            "Royal Ambulance": UniversalScraper()
        }

        all_jobs = []

        # Primary search terms to ensure wide coverage
        search_terms = ["EMT", "ER Tech", "Emergency Room Technician", "Emergency Department"]

        for company, url in HOSPITALS.items():
            scraper = scrapers.get(company)
            if not scraper: continue

            for term in search_terms:
                logger.info(f"Scraping {company} for '{term}'...")
                # Adjust URL for search term if needed
                search_url = url
                if "SearchJobs" in url: # UCSF
                    search_url = f"{url}?keywords={term}"
                elif "search-results" in url or "search-jobs" in url: # Phenom/Taleo
                    search_url = f"{url}?keywords={term}"
                elif "wd5" in url: # Workday
                    search_url = f"{url}?q={term}"

                try:
                    jobs = await scraper.scrape(browser, search_url, company)
                    logger.info(f"Found {len(jobs)} total jobs for {company} with '{term}'")
                    all_jobs.extend(jobs)
                except Exception as e:
                    logger.error(f"Scraper failed for {company} with '{term}': {e}")

        await browser.close()

    logger.info("Processing and filtering jobs...")
    filtered_jobs = filter_jobs(all_jobs)

    logger.info(f"Final count after filtering: {len(filtered_jobs)}")

    send_email(filtered_jobs)
    logger.info("Job search complete.")

if __name__ == "__main__":
    asyncio.run(run_finder())
