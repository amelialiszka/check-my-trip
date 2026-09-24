import re
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

class TravelOfferScraper:
    def __init__(self, headless=True):
        self.headless = headless

    def get_offer_text(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, "height": 1080}
            )
            page = context.new_page()

            try:
                try:
                    page.goto(url, wait_until="networkidle", timeout=15000)
                except PlaywrightTimeoutError:
                    page.goto(url, wait_until="domcontentloaded", timeout=15000)

                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2);")
                page.wait_for_timeout(random.randint(2500, 4500))

                raw_html = page.content()
                soup = BeautifulSoup(raw_html, "html.parser")

                tags_to_remove = ["script", "style", "nav", "footer", "header", "noscript", "iframe", "form", "svg"]
                for element in soup(tags_to_remove):
                    element.decompose()

                for element in soup.select('.cookie-banner, [role="dialog"], .modal, #cookie-consent'):
                    element.decompose()

                cleaned_text = soup.get_text(separator=" ", strip=True)
                compressed_text = re.sub(r'\s{2,}', ' ', cleaned_text).strip()
                
                return compressed_text

            except Exception as e:
                return f"Error fetching {url}: {e}"
            finally:
                browser.close()