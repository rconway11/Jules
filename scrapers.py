import asyncio
from playwright.async_api import async_playwright
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self, user_agent=None):
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    async def get_page(self, browser, url):
        context = await browser.new_context(
            user_agent=self.user_agent,
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        await page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/"
        })
        try:
            await page.goto(url, wait_until="load", timeout=60000)
            return page, context
        except Exception as e:
            logger.error(f"Error loading {url}: {e}")
            await context.close()
            return None, None

class PhenomScraper(BaseScraper):
    async def scrape(self, browser, url, company):
        page, context = await self.get_page(browser, url)
        if not page: return []

        jobs = []
        try:
            await page.wait_for_selector(".jobs-list-item", timeout=20000)
            items = await page.query_selector_all(".jobs-list-item")
            for item in items:
                title_elem = await item.query_selector("[role='heading'], .job-title")
                location_elem = await item.query_selector(".job-location")
                link_elem = await item.query_selector("a")

                title = (await title_elem.inner_text()).strip() if title_elem else "N/A"
                location = (await location_elem.inner_text()).strip() if location_elem else "N/A"
                link = await link_elem.get_attribute("href") if link_elem else url

                jobs.append({
                    "title": title,
                    "location": location,
                    "link": link,
                    "company": company
                })
        except Exception as e:
            logger.info(f"No jobs found or timeout for {company} at {url}")
        finally:
            await context.close()
        return jobs

class WorkdayScraper(BaseScraper):
    async def scrape(self, browser, url, company):
        page, context = await self.get_page(browser, url)
        if not page: return []

        jobs = []
        try:
            await page.wait_for_timeout(5000)
            items = await page.query_selector_all("li[data-automation-id='searchResultsListItem']")

            for item in items:
                title_elem = await item.query_selector("a[data-automation-id='jobTitle']")
                location_elem = await item.query_selector("[data-automation-id='locations']")

                title = (await title_elem.inner_text()).strip() if title_elem else "N/A"
                location = (await location_elem.inner_text()).strip() if location_elem else "N/A"
                link_path = await title_elem.get_attribute("href") if title_elem else ""
                link = f"https://{url.split('/')[2]}{link_path}" if link_path else url

                jobs.append({
                    "title": title,
                    "location": location,
                    "link": link,
                    "company": company
                })
        except Exception as e:
            logger.info(f"No jobs found or error for {company} at {url}")
        finally:
            await context.close()
        return jobs

class UCSFScraper(BaseScraper):
    async def scrape(self, browser, url, company):
        page, context = await self.get_page(browser, url)
        if not page: return []

        jobs = []
        try:
            await page.wait_for_timeout(5000)
            items = await page.query_selector_all("tr[id*='row_']")
            for item in items:
                title_elem = await item.query_selector("a")
                tds = await item.query_selector_all("td")

                title = (await title_elem.inner_text()).strip() if title_elem else "N/A"
                location = (await tds[2].inner_text()).strip() if len(tds) > 2 else "N/A"
                link = await title_elem.get_attribute("href") if title_elem else url

                jobs.append({
                    "title": title,
                    "location": location,
                    "link": link,
                    "company": company
                })
        except Exception as e:
            logger.info(f"No jobs found or error for {company} at {url}")
        finally:
            await context.close()
        return jobs

class KaiserScraper(BaseScraper):
    async def scrape(self, browser, url, company):
        page, context = await self.get_page(browser, url)
        if not page: return []

        jobs = []
        try:
            await page.wait_for_timeout(5000)
            items = await page.query_selector_all("#search-results-list ul li")
            for item in items:
                title_elem = await item.query_selector("h2")
                location_elem = await item.query_selector(".job-location")
                link_elem = await item.query_selector("a")

                title = (await title_elem.inner_text()).strip() if title_elem else "N/A"
                location = (await location_elem.inner_text()).strip() if location_elem else "N/A"
                link_path = await link_elem.get_attribute("href") if link_elem else ""
                link = f"https://www.kaiserpermanentejobs.org{link_path}" if link_path.startswith('/') else link_path

                jobs.append({
                    "title": title,
                    "location": location,
                    "link": link,
                    "company": company
                })
        except Exception as e:
            logger.info(f"No jobs found or error for {company} at {url}")
        finally:
            await context.close()
        return jobs

class UniversalScraper(BaseScraper):
    async def scrape(self, browser, url, company):
        page, context = await self.get_page(browser, url)
        if not page: return []

        jobs = []
        try:
            await page.wait_for_timeout(7000)

            selectors = [
                ".job-item", ".list-group-item", "li.job", ".job-listing",
                "tr.job", ".jobs-list-item", ".direct_joblisting"
            ]

            items = []
            for selector in selectors:
                items = await page.query_selector_all(selector)
                if items: break

            if not items:
                links = await page.query_selector_all("a")
                for link in links:
                    text = await link.inner_text()
                    if any(kw in text.upper() for kw in ["EMT", "ER TECH", "TECHNICIAN", "AMBULANCE"]):
                        jobs.append({
                            "title": text.strip(),
                            "location": "See Link",
                            "link": await link.get_attribute("href"),
                            "company": company
                        })
                return jobs

            for item in items:
                title_elem = await item.query_selector("a, h2, h3, .title")
                location_elem = await item.query_selector(".location, .job-location, .city")

                title = (await title_elem.inner_text()).strip() if title_elem else "N/A"
                location = (await location_elem.inner_text()).strip() if location_elem else "N/A"
                link = await title_elem.get_attribute("href") if title_elem and await title_elem.get_attribute("href") else url

                if not link.startswith("http"):
                    base = "/".join(url.split("/")[:3])
                    link = base + (link if link.startswith("/") else "/" + link)

                jobs.append({
                    "title": title,
                    "location": location,
                    "link": link,
                    "company": company
                })
        except Exception as e:
            logger.info(f"No jobs found or error for {company} at {url}")
        finally:
            await context.close()
        return jobs
