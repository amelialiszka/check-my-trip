import os
import datetime
import libsql_client
from dotenv import load_dotenv

load_dotenv()

class OfferStorage:
    def __init__(self):
        self.url = os.getenv("TURSO_DATABASE_URL")
        self.token = os.getenv("TURSO_AUTH_TOKEN")
        
        if not self.url or not self.token:
            raise ValueError("[ERROR] Missing TURSO_DATABASE_URL or TURSO_AUTH_TOKEN in .env file!")
            
        self.init_db()

    def get_client(self):
        return libsql_client.create_client_sync(
            url=self.url,
            auth_token=self.token
        )

    def init_db(self):
        with self.get_client() as client:
            client.execute("""
                CREATE TABLE IF NOT EXISTS offers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    scraped_at TIMESTAMP NOT NULL,
                    
                    hotel_name TEXT NOT NULL,
                    price_per_person REAL,
                    duration_days INTEGER,
                    country TEXT,
                    region TEXT,
                    departure_date TEXT,
                    
                    hotel_stars REAL,
                    average_rating REAL,
                    review_count INTEGER,
                    
                    room_type TEXT,
                    has_sea_view BOOLEAN,
                    meal_plan TEXT,
                    
                    flight_departure_time TEXT,
                    flight_return_time TEXT,
                    
                    number_of_restaurants INTEGER,
                    number_of_bars INTEGER,
                    number_of_pools INTEGER,
                    is_wifi_free BOOLEAN,
                    is_sunbed_included BOOLEAN,
                    
                    distance_to_beach_meters INTEGER,
                    distance_to_center_meters INTEGER,
                    is_direct_flight BOOLEAN,
                    is_transfer_included BOOLEAN,
                    is_public_transport_nearby BOOLEAN
                )
            """)
            
            client.execute("""
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    provider TEXT NOT NULL,
                    status TEXT DEFAULT 'PENDING'
                )
            """)
            print("[INFO] Connected to Turso cloud. Tables 'offers' and 'sources' are ready.")

    def get_pending_sources(self, limit: int = 20):
        with self.get_client() as client:
            result = client.execute(
                "SELECT url, provider FROM sources WHERE status IN ('PENDING', 'FAILED') LIMIT ?", 
                [limit]
            )
            return [{"url": row[0], "provider": row[1]} for row in result.rows]

    def add_source(self, url: str, provider: str):
        with self.get_client() as client:
            client.execute(
                "INSERT OR IGNORE INTO sources (url, provider) VALUES (?, ?)", 
                [url, provider]
            )
            print(f"[INFO] Added source URL for {provider}: {url}")

    def update_source_status(self, url: str, status: str):
        with self.get_client() as client:
            client.execute("UPDATE sources SET status = ? WHERE url = ?", [status, url])
            print(f"[INFO] Source status updated to {status} for {url}")

    def save_offer(self, url: str, offer_data: dict):
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        scraped_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with self.get_client() as client:
            existing = client.execute("""
                SELECT id FROM offers 
                WHERE url = ? AND DATE(scraped_at) = ?
            """, [url, today_date])
            
            if len(existing.rows) > 0:
                offer_id = existing.rows[0][0]
                client.execute("""
                    UPDATE offers 
                    SET scraped_at = ?, price_per_person = ?, average_rating = ?, review_count = ?
                    WHERE id = ?
                """, [
                    scraped_at, 
                    offer_data['price_per_person'], 
                    offer_data['average_rating'], 
                    offer_data['review_count'], 
                    offer_id
                ])
                print(f"[INFO] Offer for {offer_data['hotel_name']} already exists for today. Updated existing record.")
            else:
                client.execute("""
                    INSERT INTO offers (
                        url, scraped_at, hotel_name, price_per_person, duration_days, country, region, departure_date,
                        hotel_stars, average_rating, review_count, room_type, has_sea_view, meal_plan,
                        flight_departure_time, flight_return_time,
                        number_of_restaurants, number_of_bars, number_of_pools, is_wifi_free, is_sunbed_included,
                        distance_to_beach_meters, distance_to_center_meters, is_direct_flight, is_transfer_included, is_public_transport_nearby
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                """, [
                    url, scraped_at, 
                    offer_data['hotel_name'], offer_data['price_per_person'], offer_data['duration_days'], 
                    offer_data['country'], offer_data['region'], offer_data['departure_date'],
                    offer_data['hotel_stars'], offer_data['average_rating'], offer_data['review_count'],
                    offer_data['room_type'], offer_data['has_sea_view'], offer_data['meal_plan'],
                    offer_data['flight_departure_time'], offer_data['flight_return_time'],
                    offer_data['number_of_restaurants'], offer_data['number_of_bars'], offer_data['number_of_pools'], 
                    offer_data['is_wifi_free'], offer_data['is_sunbed_included'],
                    offer_data['distance_to_beach_meters'], offer_data['distance_to_center_meters'], 
                    offer_data['is_direct_flight'], offer_data['is_transfer_included'], offer_data['is_public_transport_nearby']
                ])
                print(f"[INFO] Successfully saved new offer for {offer_data['hotel_name']} to Turso cloud.")