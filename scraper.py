from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

class TravelOfferScraper:
    def __init__(self, headless=False):
        self.headless = headless

    def get_offer_text(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
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
                page.wait_for_timeout(1500)

                raw_html = page.content()
                soup = BeautifulSoup(raw_html, "html.parser")

                tags_to_remove = ["script", "style", "nav", "footer", "header", "noscript", "iframe"]
                for element in soup(tags_to_remove):
                    element.decompose()

                cleaned_text = soup.get_text(separator="\n", strip=True)
                
                return cleaned_text

            except Exception as e:
                return f"Error fetching {url}: {e}"
            finally:
                browser.close()