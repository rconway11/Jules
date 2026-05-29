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

        for company, url in HOSPITALS.items():
            logger.info(f"Scraping {company}...")
            scraper = scrapers.get(company)
            if scraper:
                try:
                    jobs = await scraper.scrape(browser, url, company)
                    logger.info(f"Found {len(jobs)} total jobs for {company}")
                    all_jobs.extend(jobs)
                except Exception as e:
                    logger.error(f"Scraper failed for {company}: {e}")

        await browser.close()

    logger.info("Processing and filtering jobs...")
    filtered_jobs = filter_jobs(all_jobs)

    logger.info(f"Final count after filtering: {len(filtered_jobs)}")

    send_email(filtered_jobs)
    logger.info("Job search complete.")

if __name__ == "__main__":
    asyncio.run(run_finder())
