import sqlite3
import datetime

class OfferStorage:
    def __init__(self, db_name: str = "travel_offers.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
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
            conn.commit()

    def save_offer(self, url: str, offer_data: dict):
        scraped_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO offers (
                    url, scraped_at, hotel_name, price_per_person, duration_days, country, region, departure_date,
                    hotel_stars, average_rating, review_count, room_type, has_sea_view, meal_plan,
                    flight_departure_time, flight_return_time,
                    number_of_restaurants, number_of_bars, number_of_pools, is_wifi_free, is_sunbed_included,
                    distance_to_beach_meters, distance_to_center_meters, is_direct_flight, is_transfer_included, is_public_transport_nearby
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
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
            ))
            conn.commit()
            print(f"[INFO] Successfully saved offer for {offer_data['hotel_name']} to {self.db_name}")