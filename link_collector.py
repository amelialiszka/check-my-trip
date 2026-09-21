import time
from playwright.sync_api import sync_playwright
from storage import OfferStorage

def harvest_wakacje_pl(max_links: int = 1000):
    storage = OfferStorage()
    domain = "https://www.wakacje.pl"
    
    collected_count = 0
    current_page = 1
    seen_urls = set()  
    
    with sync_playwright() as p:
        print("[INFO] Launching browser for Wakacje.pl collection...")
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        while collected_count < max_links:
            if current_page == 1:
                page_url = "https://www.wakacje.pl/wczasy/?firstminute"
            else:
                page_url = f"https://www.wakacje.pl/wczasy/?str-{current_page},firstminute"
                
            print(f"\n[INFO] Scraping listing page {current_page}: {page_url}")
            
            try:
                page.goto(page_url, timeout=60000)
                time.sleep(4)
                
                page.mouse.wheel(0, 3000)
                time.sleep(2)
                
                links_on_page = page.locator("a").all()
                page_added = 0
                
                for el in links_on_page:
                    href = el.get_attribute("href")
                    
                    if href and "/oferty/" in href and ".html" in href:
                        clean_url = href.split("?")[0]
                        full_url = f"{domain}{clean_url}" if not clean_url.startswith("http") else clean_url
                            
                        if full_url in seen_urls:
                            continue
                            
                        seen_urls.add(full_url)
                            
                        try:
                            storage.add_source(full_url, provider="Wakacje.pl")
                            collected_count += 1
                            page_added += 1
                            if collected_count >= max_links:
                                break
                        except Exception:
                            pass
                
                print(f"[INFO] Added {page_added} unique offer links from page {current_page}. Total collected: {collected_count}")
                
                if page_added == 0:
                    print("[WARNING] No more new offer links found on this page. Stopping harvester.")
                    break
                    
                current_page += 1
                time.sleep(3)
                
            except Exception as e:
                print(f"[ERROR] Failed to process page {current_page}: {e}")
                break
                
        browser.close()
        print(f"\n[SUCCESS] Harvesting finished! Total clean and unique offer links in queue: {collected_count}")

if __name__ == "__main__":
    harvest_wakacje_pl(max_links=1000)