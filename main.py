import json
from scraper import TravelOfferScraper
from analyzer import OfferAnalyzer

def run_pipeline():
    url = "https://www.wakacje.pl/oferty/cypr/cypr-poludniowy/protaras/anastasia-beach-protaras-916278.html?od-2026-10-03,7-dni,all-inclusive,z-katowic,srcx"
    
    print(f"[Info] Fetching raw text from: {url}")
    scraper = TravelOfferScraper(headless=False)
    raw_text = scraper.get_offer_text(url)
    
    if raw_text.startswith("Error"):
        print(f"[Error] Scraper failed: {raw_text}")
        return
        
    print(f"[Info] Successfully fetched {len(raw_text)} characters.")
    print("[Info] Extracting structured data using LLM...")
    
    analyzer = OfferAnalyzer()
    
    try:
        structured_data = analyzer.extract_information(raw_text)
        print("\n--- EXTRACTED DATA ---")
        print(json.dumps(structured_data, indent=4, ensure_ascii=False))
        print("----------------------")
    except Exception as e:
        print(f"[Error] Data extraction failed: {e}")

if __name__ == "__main__":
    run_pipeline()