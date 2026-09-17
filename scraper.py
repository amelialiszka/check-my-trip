from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

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
                    print(f"[Warn] Network idle timeout on {url}. Retrying with domcontentloaded...")
                    page.goto(url, wait_until="domcontentloaded", timeout=15000)

                # Trigger lazy loading for elements below the fold
                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2);")
                page.wait_for_timeout(1500)

                return page.locator("body").inner_text()

            except Exception as e:
                return f"Error fetching {url}: {e}"
            finally:
                browser.close()