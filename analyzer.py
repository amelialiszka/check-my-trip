import json
import os
import time
from typing import Optional
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class OfferDetails(BaseModel):
    reasoning_and_search: str = Field(
        ..., 
        description="Before filling out the JSON, write a step-by-step analysis. Explicitly search the text for hotel name, price per person, stars, rating, beach distance, amenities, sunbeds (verify carefully if they are free or require extra payment), departure date, and flight times. Point out where you found them or state explicitly that you searched the whole text and it's missing."
    )
    hotel_name: str = Field(..., description="Name of the hotel.")
    price_per_person: float = Field(..., description="Price per person in local currency.")
    duration_days: int = Field(..., description="Duration of the trip in days.")
    country: str = Field(..., description="Destination country.")
    region: str = Field(..., description="Destination region or city.")
    departure_date: Optional[str] = Field(default=None, description="Departure date in YYYY-MM-DD format.")
    hotel_stars: Optional[float] = Field(default=None, description="Hotel category in stars. Search thoroughly. Output null ONLY if absolutely missing.")
    average_rating: Optional[float] = Field(default=None, description="Average customer review score. Search carefully. Output null ONLY if absolutely missing.")
    review_count: Optional[int] = Field(default=None, description="Total number of customer reviews. Output null ONLY if absolutely missing.")
    room_type: Optional[str] = Field(
        default=None, 
        description=(
            "Categorize the room type into strictly ONE of these English categories: "
            "'Standard', 'Family', 'Apartment', 'Suite', 'Studio', 'Economy'. "
            "Map regular rooms (e.g., 'Pokój 2 os.', 'Pokój dwuosobowy', 'Standardowy') to 'Standard'. "
            "Map 'Rodzinny' to 'Family'. Map 'Promocyjny' to 'Economy'."
        )
    )
    has_sea_view: Optional[bool] = Field(default=None, description="Does the room have a sea view? True/False.")
    meal_plan: Optional[str] = Field(
        default=None, 
        description="Type of meal plan. ALWAYS use standard abbreviations: 'BB', 'HB', 'FB', 'AI', 'RO'."
    )
    flight_departure_time: Optional[str] = Field(default=None, description="Time of the departure flight (e.g. '06:30'). Output null if missing.")
    flight_return_time: Optional[str] = Field(default=None, description="Time of the return flight (e.g. '23:15'). Output null if missing.")
    number_of_restaurants: Optional[int] = Field(default=None, description="Total number of restaurants.")
    number_of_bars: Optional[int] = Field(default=None, description="Total number of bars.")
    number_of_pools: Optional[int] = Field(default=None, description="Number of swimming pools. Search for 'basen' or 'pools'.")
    is_wifi_free: Optional[bool] = Field(default=None, description="Is Wi-Fi free? True/False.")
    is_sunbed_included: Optional[bool] = Field(
        default=None, 
        description="Are sunbeds included for free? Output True ONLY if explicitly 'bezpłatne' or 'w cenie'. Output False if 'płatne', 'za opłatą', or cost money. Output null if not mentioned."
    )
    distance_to_beach_meters: Optional[int] = Field(
        default=None, 
        description="Distance to the beach in meters. Search thoroughly for keywords like 'plaża', 'morze', 'beach'. 1. Extract exact numbers. 2. 'Bezpośrednio przy plaży' or 'Beachfront' -> 0. Output null ONLY if completely absent."
    )
    distance_to_center_meters: Optional[int] = Field(default=None, description="Distance to city center in meters. Search thoroughly.")
    is_direct_flight: Optional[bool] = Field(default=None, description="Is the flight direct? True/False.")
    is_transfer_included: Optional[bool] = Field(default=None, description="Is the transfer included? True/False.")
    is_public_transport_nearby: Optional[bool] = Field(default=None, description="Is there public transport (bus, train) nearby? True/False.")


class OfferAnalyzer:
    def __init__(self):
        api_key_env = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEYS")
        if not api_key_env:
            raise ValueError("[ERROR] API key not found in .env variables!")
        
        self.api_key = api_key_env.split(",")[0].strip()
        
        print("[INFO] Loaded API key. Initializing Gemini Client.")
        self.client = genai.Client(api_key=self.api_key)


    def extract_information(self, text: str, max_retries: int = 2) -> dict:
        schema_json = json.dumps(OfferDetails.model_json_schema(), indent=2)
        
        prompt = f"""
        You are an advanced data extraction system for travel offers. 
        Analyze the following text and extract information strictly according to this JSON schema:
        {schema_json}
        
        Respond ONLY with a valid JSON object.
        """

        target_model = 'gemini-3.5-flash-lite'

        for attempt in range(1, max_retries + 1):
            try:
                print(f"[INFO] Requesting extraction using {target_model} (Attempt {attempt}/{max_retries})...")
                
                response = self.client.models.generate_content(
                    model=target_model,
                    contents=[prompt, text],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0
                    )
                )
                
                extracted_dict = json.loads(response.text)
                validated_data = OfferDetails(**extracted_dict)
                
                final_data = validated_data.model_dump()
                final_data.pop("reasoning_and_search", None)
                
                return final_data

            except Exception as e:
                error_str = str(e).upper()
                
                if "429" in error_str or "QUOTA" in error_str or "EXHAUSTED" in error_str:
                    if attempt < max_retries:
                        print("[WARNING] API limit hit. Waiting 60 seconds before retry...")
                        time.sleep(60)
                        continue
                        
                elif "503" in error_str or "UNAVAILABLE" in error_str:
                    if attempt < max_retries:
                        print("[WARNING] Google servers overloaded (503). Waiting 30s before retry...")
                        time.sleep(30)
                        continue
                
                raise RuntimeError(f"[ERROR] Extraction failed after {attempt} attempts: {e}")