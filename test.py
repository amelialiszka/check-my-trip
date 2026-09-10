from scraper import TravelOfferScraper

scraper = TravelOfferScraper(headless=False)

url = "https://www.tui.pl/wypoczynek/cypr/larnaka/splashworld-tofinis-apartments-lca20137/OfferCodeWS/POZLCA20260930180020260930202610071415L07LCA20137DZX1AA02ROADZX1A02FCYY"

print("Fetching data from the website..")
text = scraper.get_offer_text(url)

print(f"Successfully fetched! Totarl text length: {len(text)} characters")

file_name = 'scraped_offer.txt'
with open(file_name, "w", encoding="utf-8") as file:
    file.write(text)