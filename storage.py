import os
import datetime
import libsql_client
from dotenv import load_dotenv
import time

try:
    import streamlit as st
except ImportError:
    st = None

load_dotenv()

class OfferStorage:
    def __init__(self):
        self.url = None
        self.token = None
        self.is_connected = False

        if st and hasattr(st, "secrets"):
            self.url = st.secrets.get("TURSO_DATABASE_URL")
            self.token = st.secrets.get("TURSO_AUTH_TOKEN")

        if not self.url:
            self.url = os.getenv("TURSO_DATABASE_URL")
        if not self.token:
            self.token = os.getenv("TURSO_AUTH_TOKEN")

        # 2. Bezpieczna próba połączenia z bazą
        if not self.url or not self.token:
            print("[WARNING] Brak TURSO_DATABASE_URL lub TURSO_AUTH_TOKEN. Baza danych działa w trybie OFFLINE (zapis wyłączony).")
        else:
            try:
                self.init_db()
                self.is_connected = True
            except Exception as e:
                print(f"[WARNING] Nie udało się połączyć z bazą Turso: {e}. Zapis został wyłączony.")

    def get_client(self):
        if not self.is_connected:
            return None
        return libsql_client.create_client_sync(
            url=self.url,
            auth_token=self.token
        )

    def init_db(self):
        client = libsql_client.create_client_sync(url=self.url, auth_token=self.token)
        with client:
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
        if not self.is_connected:
            return []
            
        try:
            with self.get_client() as client:
                result = client.execute(
                    "SELECT url, provider FROM sources WHERE status IN ('PENDING', 'FAILED') LIMIT ?", 
                    [limit]
                )
                return [{"url": row[0], "provider": row[1]} for row in result.rows]
        except Exception as e:
            print(f"[WARNING] Failed to fetch pending sources: {e}")
            return []

    def add_source(self, url: str, provider: str):
        if not self.is_connected:
            return
            
        try:
            with self.get_client() as client:
                client.execute(
                    "INSERT OR IGNORE INTO sources (url, provider) VALUES (?, ?)", 
                    [url, provider]
                )
                print(f"[INFO] Added source URL for {provider}: {url}")
        except Exception as e:
            print(f"[WARNING] Failed to add source {url}: {e}")

    def update_source_status(self, url: str, status: str, max_retries: int = 3):
        if not self.is_connected:
            return

        for attempt in range(1, max_retries + 1):
            try:
                with self.get_client() as client:
                    client.execute("UPDATE sources SET status = ? WHERE url = ?", [status, url])
                    print(f"[INFO] Source status updated to {status} for {url}")
                    return
            except Exception as e:
                if attempt == max_retries:
                    print(f"[WARNING] Failed to update status for {url} after {max_retries} attempts: {e}")
                else:
                    time.sleep(2)

    def save_offer(self, url: str, offer_data: dict):
        if not self.is_connected:
            print(f"[INFO] Storage is in OFFLINE mode. Skipping database save for offer: {offer_data.get('hotel_name', 'Unknown')}")
            return

        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        scraped_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
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
                        offer_data.get('price_per_person'), 
                        offer_data.get('average_rating'), 
                        offer_data.get('review_count'), 
                        offer_id
                    ])
                    print(f"[INFO] Offer for {offer_data.get('hotel_name')} already exists for today. Updated existing record.")
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
                        offer_data.get('hotel_name'), offer_data.get('price_per_person'), offer_data.get('duration_days'), 
                        offer_data.get('country'), offer_data.get('region'), offer_data.get('departure_date'),
                        offer_data.get('hotel_stars'), offer_data.get('average_rating'), offer_data.get('review_count'),
                        offer_data.get('room_type'), offer_data.get('has_sea_view'), offer_data.get('meal_plan'),
                        offer_data.get('flight_departure_time'), offer_data.get('flight_return_time'),
                        offer_data.get('number_of_restaurants'), offer_data.get('number_of_bars'), offer_data.get('number_of_pools'), 
                        offer_data.get('is_wifi_free'), offer_data.get('is_sunbed_included'),
                        offer_data.get('distance_to_beach_meters'), offer_data.get('distance_to_center_meters'), 
                        offer_data.get('is_direct_flight'), offer_data.get('is_transfer_included'), offer_data.get('is_public_transport_nearby')
                    ])
                    print(f"[INFO] Successfully saved new offer for {offer_data.get('hotel_name')} to Turso cloud.")
        except Exception as e:
            print(f"[WARNING] Failed to save offer to Turso: {e}")