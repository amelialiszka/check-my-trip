import sys
import time
from scraper import TravelOfferScraper
from analyzer import OfferAnalyzer
from storage import OfferStorage

def run_pipeline():
    print("[INFO] Initializing pipeline...")
    
    storage = OfferStorage()
    active_sources = storage.get_pending_sources(limit=20)
    
    if not active_sources:
        print("[WARNING] No pending sources found in the database. Add some seed URLs first!")
        return

    print(f"[INFO] Found {len(active_sources)} pending source(s) in this batch.")

    scraper = TravelOfferScraper()
    analyzer = OfferAnalyzer()

    for index, source in enumerate(active_sources):
        url = source["url"]
        provider = source["provider"]
        
        print(f"\n[INFO] Processing URL [{index + 1}/{len(active_sources)}] from [{provider}]: {url}")
        
        html_content = scraper.get_offer_text(url)
        if not html_content or html_content.startswith("Error fetching"):
            print(f"[ERROR] Failed to retrieve page content for {url}. Marking as FAILED.")
            storage.update_source_status(url, 'FAILED')
            continue
            
        expired_keywords = ["oferta nieaktualna", "wyprzedane", "brak miejsc", "nie znaleziono oferty", "przepraszamy, oferta"]
        html_lower = html_content.lower()
        
        if any(keyword in html_lower for keyword in expired_keywords):
            print(f"[WARNING] Offer expired ({url}). Marking as EXPIRED. Skipping API call.")
            storage.update_source_status(url, 'EXPIRED')
            continue

        print(f"[INFO] Fetched {len(html_content)} characters.")
        print("[INFO] Extracting data via Gemini API...")
        
        try:
            extracted_data = analyzer.extract_information(html_content)
        except Exception as e:
            print(f"[ERROR] Extraction failed for {url}: {e}")
            storage.update_source_status(url, 'FAILED')
            continue

        if extracted_data and extracted_data.get('hotel_name'):
            storage.save_offer(url, extracted_data)
            storage.update_source_status(url, 'PROCESSED')
        else:
            print(f"[WARNING] Extracted data was empty or invalid for {url}. Marking as FAILED.")
            storage.update_source_status(url, 'FAILED')

        if index < len(active_sources) - 1:
            print("[INFO] Waiting 2.5 seconds before the next request to respect rate limits...")
            time.sleep(2.5)

    print("\n[INFO] Batch finished successfully.")

if __name__ == "__main__":
    run_pipeline()