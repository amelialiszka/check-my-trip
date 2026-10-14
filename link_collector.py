import time
import argparse
from playwright.sync_api import sync_playwright
from storage import OfferStorage

class TravelScraper:
    def __init__(self):
        self.storage = OfferStorage()

    def scrape_tui(self, max_links: int):
        collected_count = 0
        current_page = 0
        seen_urls = set()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            print("[INFO] Starting TUI scraper (pagination)...")
            
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

    def scrape_wakacje(self, max_links: int):
        collected_count = 0
        current_page = 1
        seen_urls = set()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            print("[INFO] Starting Wakacje.pl scraper...")
            while collected_count < max_links:
                page_url = "https://www.wakacje.pl/wczasy/?firstminute,2-28-dni,od-5000zl&src=fromFilters" if current_page == 1 else f"https://www.wakacje.pl/wczasy/?str-{current_page},firstminute,2-28-dni,od-5000zl&src=fromFilters"
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

    def scrape_itaka(self, max_links: int):
        collected_count = 0
        current_page = 1
        seen_urls = set()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            print("[INFO] Starting Itaka scraper...")
            
            page.goto("https://www.itaka.pl/wyniki-wyszukiwania/wakacje/?promotion=lato27", timeout=60000)
            try:
                page.get_by_role("button", name="Akceptuję").click(timeout=3000)
                time.sleep(1)
            except:
                pass
            
            while collected_count < max_links:
                page_url = f"https://www.itaka.pl/wyniki-wyszukiwania/wakacje/?promotion=lato27&page={current_page}"
                
                print(f"[INFO] Itaka - Loading page {current_page}...")
                page.goto(page_url, timeout=60000)
                time.sleep(4)
                
                page.mouse.wheel(0, 4000)
                time.sleep(2)
                
                links_on_page = page.locator("a").all()
                added_on_page = 0
                
                for el in links_on_page:
                    href = el.get_attribute("href")
                    if href and "/wczasy/" in href and "," in href:
                        clean_url = href.split("?")[0]
                        full_url = f"https://www.itaka.pl{clean_url}" if not clean_url.startswith("http") else clean_url
                            
                        if full_url not in seen_urls:
                            seen_urls.add(full_url)
                            try:
                                self.storage.add_source(full_url, provider="Itaka")
                                collected_count += 1
                                added_on_page += 1
                                if collected_count >= max_links:
                                    break
                            except Exception:
                                pass
                                
                print(f"[INFO] Itaka - Found {added_on_page} new offers on this page. Total in database: {collected_count}/{max_links}")
                
                if added_on_page == 0:
                    print("[WARNING] No new offers on page (reached end of results).")
                    break
                    
                current_page += 1
                
            browser.close()
            print(f"[SUCCESS] Finished! Total Itaka links in database: {collected_count}.")

    def scrape_rainbow(self, max_links: int):
        collected_count = 0
        current_page = 1
        seen_urls = set()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            print("[INFO] Starting Rainbow scraper...")
            
            page.goto("https://r.pl/szukaj?sezon=lato-2027", timeout=60000, wait_until="domcontentloaded")
            try:
                page.locator("button:has-text('Akceptuj'), button:has-text('Zgadzam się'), button:has-text('Przejdź')").first.click(timeout=5000)
            except:
                pass
            
            while collected_count < max_links:
                page_url = f"https://r.pl/szukaj?sezon=lato-2027&strona={current_page}"
                
                print(f"[INFO] Rainbow - Loading page {current_page}...")
                
                page.goto(page_url, timeout=60000, wait_until="networkidle")
                
                try:
                    page.wait_for_selector("a[href*='unikalnyKluczOferty'], a[href*='-wczasy']", timeout=10000)
                except:
                    print("[WARNING] Offers didn't render in time. The page might be empty or blocked.")
                
                for _ in range(3):
                    page.mouse.wheel(0, 2000)
                    time.sleep(1)
                
                extracted_hrefs = page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a'))
                                .map(a => a.href)
                                .filter(href => href.includes('unikalnyKluczOferty') || href.includes('-wczasy'));
                }""")
                
                extracted_hrefs = list(set(extracted_hrefs))
                added_on_page = 0
                
                for href in extracted_hrefs:
                    clean_url = href.split("&wiek")[0]
                    
                    if clean_url not in seen_urls:
                        seen_urls.add(clean_url)
                        try:
                            self.storage.add_source(clean_url, provider="Rainbow")
                            collected_count += 1
                            added_on_page += 1
                            if collected_count >= max_links:
                                break
                        except Exception:
                            pass
                                
                print(f"[INFO] Rainbow - Found {added_on_page} new offers on this page. Total in database: {collected_count}/{max_links}")
                
                if added_on_page == 0:
                    print("[WARNING] No new offers on page (reached end of results).")
                    break
                    
                current_page += 1
                
            browser.close()
            print(f"[SUCCESS] Finished! Total Rainbow links in database: {collected_count}.")

    def scrape_travelplanet(self, max_links: int):
        collected_count = 0
        current_page = 1
        seen_urls = set()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            print("[INFO] Starting Travelplanet scraper...")
            
            page.goto("https://www.travelplanet.pl/", timeout=60000)
            try:
                page.locator("button:has-text('Akceptuję'), button:has-text('Zgadzam się')").first.click(timeout=3000)
                time.sleep(1)
            except:
                pass
            
            while collected_count < max_links:
                page_url = f"https://www.travelplanet.pl/wakacje/?s_action=TRIPS_FM&d_start_from=01.01.2027&d_end_to=31.12.2027&nl_transportation_id%5B%5D=3_PL&duration=Flexible&nl_length_from=0&nl_length_to=0&nl_occupancy_adults=2&sort=nl_sell&page={current_page}"
                
                print(f"[INFO] Travelplanet - Loading page {current_page}...")
                page.goto(page_url, timeout=60000, wait_until="networkidle")
                
                try:
                    page.wait_for_selector("a[href*='/oferta/']", timeout=10000)
                except:
                    print("[WARNING] Offers didn't render in time. The page might be empty.")
                
                for _ in range(4):
                    page.mouse.wheel(0, 2000)
                    time.sleep(1)
                
                extracted_hrefs = page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a'))
                                .map(a => a.href)
                                .filter(href => href.includes('/hotele/') && href.includes('/oferta/'));
                }""")
                
                extracted_hrefs = list(set(extracted_hrefs))
                added_on_page = 0
                
                for href in extracted_hrefs:
                    clean_url = href.split("&c_price")[0]
                    
                    if clean_url not in seen_urls:
                        seen_urls.add(clean_url)
                        try:
                            self.storage.add_source(clean_url, provider="Travelplanet")
                            collected_count += 1
                            added_on_page += 1
                            if collected_count >= max_links:
                                break
                        except Exception:
                            pass
                                
                print(f"[INFO] Travelplanet - Found {added_on_page} new offers on this page. Total in database: {collected_count}/{max_links}")
                
                if added_on_page == 0:
                    print("[WARNING] No new offers on page (reached end of results).")
                    break
                    
                current_page += 1
                
            browser.close()
            print(f"[SUCCESS] Finished! Total Travelplanet links in database: {collected_count}.")


    def scrape_rainbow_luxury(self, max_links: int):
        collected_count = 0
        current_page = 1
        seen_urls = set()
        
        base_search_url = (
            "https://r.pl/szukaj?sezon=lato-2027"
            "&cena.od=10000"
            "&typTransportu=AIR"
            "&sortowanie=cena-asc"
        )
        
        print("[INFO] Starting Rainbow LUXURY scraper (min. 10 000 PLN)...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            # Pierwsze wejście w celu zaakceptowania cookie bannerów
            page.goto(base_search_url, timeout=60000, wait_until="domcontentloaded")
            try:
                page.locator("button:has-text('Akceptuj'), button:has-text('Zgadzam się'), button:has-text('Przejdź')").first.click(timeout=5000)
                time.sleep(1)
            except Exception:
                pass
            
            while collected_count < max_links:
                page_url = f"{base_search_url}&strona={current_page}"
                
                print(f"[INFO] Rainbow LUXURY - Loading page {current_page}...")
                page.goto(page_url, timeout=60000, wait_until="networkidle")
                
                try:
                    page.wait_for_selector("a[href*='unikalnyKluczOferty'], a[href*='-wczasy']", timeout=10000)
                except Exception:
                    print("[WARNING] Luxury offers didn't render in time. The page might be empty or blocked.")
                
                for _ in range(3):
                    page.mouse.wheel(0, 2000)
                    time.sleep(1)
                
                extracted_hrefs = page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a'))
                                .map(a => a.href)
                                .filter(href => href.includes('unikalnyKluczOferty') || href.includes('-wczasy'));
                }""")
                
                extracted_hrefs = list(set(extracted_hrefs))
                added_on_page = 0
                
                for href in extracted_hrefs:
                    clean_url = href.split("&wiek")[0]
                    
                    if clean_url not in seen_urls:
                        seen_urls.add(clean_url)
                        try:
                            # Zapisujemy w bazie pod poddostawcą "Rainbow Luxury" dla czytelności w DB
                            self.storage.add_source(clean_url, provider="Rainbow Luxury")
                            collected_count += 1
                            added_on_page += 1
                            if collected_count >= max_links:
                                break
                        except Exception:
                            pass
                                
                print(f"[INFO] Rainbow LUXURY - Page {current_page}, Found {added_on_page} new links. Total in database: {collected_count}/{max_links}")
                
                if added_on_page == 0:
                    print("[WARNING] No new luxury offers on page (reached end of results).")
                    break
                    
                current_page += 1
                
            browser.close()
            print(f"[SUCCESS] Finished! Total Rainbow LUXURY links in database: {collected_count}.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloads offer links from travel portals.")
    parser.add_argument("--provider", type=str, choices=["tui", "wakacje", "itaka", "rainbow", "rainbow_luxury", "travelplanet"], required=True)
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()
    
    scraper = TravelScraper()
    if args.provider == "tui":
        scraper.scrape_tui(args.limit)
    elif args.provider == "wakacje":
        scraper.scrape_wakacje(args.limit)
    elif args.provider == "itaka":
        scraper.scrape_itaka(args.limit)
    elif args.provider == "rainbow":
        scraper.scrape_rainbow(args.limit)
    elif args.provider == "rainbow_luxury":
        scraper.scrape_rainbow_luxury(args.limit)
    elif args.provider == "travelplanet":
        scraper.scrape_travelplanet(args.limit)


