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
    print(f"[DEBUG] Extracted data: {extracted_data}")
    
    storage = OfferStorage()
    storage.save_offer(url, extracted_data)
    
    print("[INFO] Pipeline finished successfully.")

if __name__ == "__main__":
    test_url = "https://www.itaka.pl/wczasy/wyspy-kanaryjskie/fuerteventura/hotel-r2-rio-calma,FUERIOC/?id%5B0%5D=CgVJdGFrYRIEVklUWBoDUExOIgdGVUVSSU9DKAQ6BFo2MDBCBgiAt5DaBkoGCICstdoGUAJiBQoDV1JPagUKA0ZVRXIDCgExegUKA0ZVRYIBBQoDV1JPigEDCgExkgEGCIC3kNoGmgEGCICstdoGogEFCgNEQkyqAQMKAUjiAQkKB1Jlc2FiZWXqAQkKB1Jlc2FiZWXyAQkKB1Jlc2FiZWU%3D&adults%5B0%5D=2"
    
    run_pipeline(test_url)