import sys
import time
from scraper import TravelOfferScraper
from analyzer import OfferAnalyzer
from storage import OfferStorage

def run_pipeline():
    print("[INFO] Initializing batch pipeline...")
    
    storage = OfferStorage()
    active_sources = storage.get_pending_sources(limit=500)
    
    if not active_sources:
        print("[WARNING] No pending sources found in the database. Add some URLs first!")
        return

    print(f"[INFO] Found {len(active_sources)} source(s) to process in this batch.")

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

        print(f"[INFO] Fetched {len(html_content)} characters. Requesting Gemini API extraction...")

        try:
            extracted_data = analyzer.extract_information(html_content)
        except Exception as e:
            print(f"[ERROR] Extraction failed for {url}: {e}")
            storage.update_source_status(url, 'FAILED')
            continue

        if extracted_data and extracted_data.get('hotel_name') and extracted_data.get('price_per_person') is not None:
            if extracted_data['price_per_person'] > 0:
                try:
                    storage.save_offer(url, extracted_data)
                    storage.update_source_status(url, 'PROCESSED')
                    print(f"[SUCCESS] Saved: {extracted_data['hotel_name']} ({extracted_data['price_per_person']} PLN)")
                except Exception as db_err:
                    print(f"[ERROR] Database save error for {url}: {db_err}")
                    storage.update_source_status(url, 'FAILED')
            else:
                print(f"[WARNING] Extracted price is 0 for {url}. Marking as EXPIRED to protect dataset quality.")
                storage.update_source_status(url, 'EXPIRED')
        else:
            print(f"[WARNING] Missing essential data (hotel name or price) for {url}. Marking as EXPIRED.")
            storage.update_source_status(url, 'EXPIRED')

        if index < len(active_sources) - 1:
            print("[INFO] Waiting 4.5 seconds before next request...")
            time.sleep(4.5)

    print("\n[SUCCESS] Batch processing finished successfully!")

if __name__ == "__main__":
    run_pipeline()