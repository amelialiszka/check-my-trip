from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class TravelOfferScraper:
    def __init__(self, headless=True):
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
                page.goto(url, wait_until="networkidle", timeout=15000)

                raw_text = page.locator("body").inner_text()
                return raw_text

            except PlaywrightTimeoutError:
                return "Error: Page load timed out."
            except Exception as e:
                return f"Error during fetching: {str(e)}"
            finally:
                browser.close()