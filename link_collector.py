import time
import argparse
from playwright.sync_api import sync_playwright
from storage import OfferStorage

class TravelHarvester:
    def __init__(self):
        self.storage = OfferStorage()

    def harvest_tui(self, max_links: int):
        collected_count = 0
        current_page = 0
        seen_urls = set()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            print("[INFO] Starting TUI harvester (pagination)...")
            
            page.goto("https://www.tui.pl/oferty-first-minute-lato", timeout=60000)
            try:
                page.get_by_role("button", name="Zgadzam się").click(timeout=3000)
                time.sleep(1)
            except:
                pass
            
            while collected_count < max_links:
                page_url = f"https://www.tui.pl/oferty-first-minute-lato?pm_source=FMS27&pm_name=oferty-baner&page={current_page}"
                
                print(f"[INFO] TUI - Loading page: {current_page}...")
                page.goto(page_url, timeout=60000)
                time.sleep(4)
                
                page.mouse.wheel(0, 4000)
                time.sleep(2)
                
                links_on_page = page.locator("a").all()
                added_on_page = 0
                
                for el in links_on_page:
                    href = el.get_attribute("href")
                    if href and "OfferCodeWS" in href:
                        clean_url = href.split("?")[0]
                        full_url = f"https://www.tui.pl{clean_url}" if not clean_url.startswith("http") else clean_url
                            
                        if full_url not in seen_urls:
                            seen_urls.add(full_url)
                            try:
                                self.storage.add_source(full_url, provider="TUI")
                                collected_count += 1
                                added_on_page += 1
                                if collected_count >= max_links:
                                    break
                            except Exception:
                                pass
                                
                print(f"[INFO] TUI - Found {added_on_page} new offers on this page. Total in database: {collected_count}/{max_links}")
                
                if added_on_page == 0:
                    print("[WARNING] No new offers on page (reached end of results).")
                    break
                    
                current_page += 1
                
            browser.close()
            print(f"[SUCCESS] Finished! Total TUI links in database: {collected_count}.")

    def harvest_wakacje(self, max_links: int):
        collected_count = 0
        current_page = 1
        seen_urls = set()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            print("[INFO] Starting Wakacje.pl harvester...")
            while collected_count < max_links:
                page_url = "https://www.wakacje.pl/wczasy/?firstminute" if current_page == 1 else f"https://www.wakacje.pl/wczasy/?str-{current_page},firstminute"
                page.goto(page_url, timeout=60000)
                time.sleep(4)
                page.mouse.wheel(0, 3000)
                time.sleep(2)
                
                for el in page.locator("a").all():
                    href = el.get_attribute("href")
                    if href and "/oferty/" in href and ".html" in href:
                        clean_url = href.split("?")[0]
                        full_url = f"https://www.wakacje.pl{clean_url}" if not clean_url.startswith("http") else clean_url
                            
                        if full_url not in seen_urls:
                            seen_urls.add(full_url)
                            try:
                                self.storage.add_source(full_url, provider="Wakacje.pl")
                                collected_count += 1
                                if collected_count >= max_links:
                                    break
                            except Exception:
                                pass
                
                print(f"[INFO] Wakacje.pl - Page {current_page}, Gathered links: {collected_count}/{max_links}")
                current_page += 1
            browser.close()
            print(f"[SUCCESS] Finished! Total Wakacje.pl links in database: {collected_count}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloads offer links from travel portals.")
    parser.add_argument("--provider", type=str, choices=["tui", "wakacje"], required=True)
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()
    
    harvester = TravelHarvester()
    if args.provider == "tui":
        harvester.harvest_tui(args.limit)
    elif args.provider == "wakacje":
        harvester.harvest_wakacje(args.limit)