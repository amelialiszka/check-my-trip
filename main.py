import sys
from scraper import TravelOfferScraper
from analyzer import OfferAnalyzer
from storage import OfferStorage

def run_pipeline(url: str):
    print(f"[INFO] Starting pipeline for URL: {url}")
    
    # 1. Scrape
    scraper = TravelOfferScraper()
    print("[INFO] Scraping website...")
    html_content = scraper.get_offer_text(url)
    
    if not html_content or html_content.startswith("Error fetching"):
        print(f"[ERROR] Failed to retrieve page content. {html_content}.")
        sys.exit(1)
        
    print(f"[INFO] Fetched {len(html_content)} characters.")

    # 2. Extract
    analyzer = OfferAnalyzer()
    print("[INFO] Extracting data via Gemini API...")
    try:
        extracted_data = analyzer.extract_information(html_content)
    except Exception as e:
        print(f"[ERROR] Extraction failed: {e}")
        sys.exit(1)

    # 3. Save
    storage = OfferStorage()
    storage.save_offer(url, extracted_data)
    
    print("[INFO] Pipeline finished successfully.")

if __name__ == "__main__":
    test_url = "https://www.tui.pl/wypoczynek/gambia/holiday-beach-club-bjl30001/OfferCodeWS/POZBJL20261204101520261204202612111715L07BJL30001DZX5GA02ROGDZX5A02FCYY"
    
    run_pipeline(test_url)