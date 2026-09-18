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
    # --- BASIC INFO (Required) ---
    total_price: float = Field(..., description="Total price of the trip in local currency.")
    duration_days: int = Field(..., description="Duration of the trip in days.")
    country: str = Field(..., description="Destination country.")
    region: str = Field(..., description="Destination region or city.")
    
    # --- HOTEL & STANDARD (Optional) ---
    hotel_stars: Optional[float] = Field(default=None, description="Hotel category in stars. If not found, output null.")
    average_rating: Optional[float] = Field(default=None, description="Average customer review score on a 5-point scale. If not found, output null.")
    review_count: Optional[int] = Field(default=None, description="Total number of customer reviews. If not found, output null.")
    
    # --- ROOM & TRANSPORT (Optional) ---
    room_type: Optional[str] = Field(default=None, description="Type of room, e.g., 'Standard', 'Apartment'. If not specified, output null.")
    has_sea_view: Optional[bool] = Field(default=None, description="Does the room have a sea view? True/False. If not specified, output null.")
    meal_plan: Optional[str] = Field(default=None, description="Type of meal plan, e.g., 'All Inclusive', 'HB', 'BB', 'RO'. If not specified, output null.")
    
    # --- AMENITIES (Optional) ---
    number_of_restaurants: Optional[int] = Field(default=None, description="Total number of restaurants. If not specified, output null.")
    number_of_bars: Optional[int] = Field(default=None, description="Total number of bars. If not specified, output null.")
    number_of_pools: Optional[int] = Field(default=None, description="Number of swimming pools. If not found, output null.")
    is_wifi_free: Optional[bool] = Field(default=None, description="Is Wi-Fi free? True/False. If not specified, output null.")
    
    # --- LOCATION (Optional) ---
    distance_to_beach_meters: Optional[int] = Field(
        default=None, 
        description=(
            "Distance to the beach in meters. "
            "1. Extract exact numbers. "
            "2. 'Close to beach' -> 200. "
            "3. 'Beachfront' -> 0. "
            "4. Far away -> 1000. "
            "5. Unknown -> null."
        )
    )
    distance_to_center_meters: Optional[int] = Field(default=None, description="Distance to the city center in meters. If not found, output null.")
    is_direct_flight: Optional[bool] = Field(default=None, description="Is the flight direct? True/False. If not specified, output null.")
    is_transfer_included: Optional[bool] = Field(default=None, description="Is the transfer included? True/False. If not specified, output null.")


class OfferAnalyzer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("ERROR: GEMINI_API_KEY not found in environment variables!")
        
        self.client = genai.Client(api_key=api_key)

    def extract_information(self, text: str, max_retries: int = 5) -> dict:
        schema_json = json.dumps(OfferDetails.model_json_schema(), indent=2)
        
        prompt = f"""
        You are an advanced data extraction system for travel offers. 
        Analyze the following text and extract information strictly according to this JSON schema:
        {schema_json}
        
        Respond ONLY with a valid JSON object.
        """

        target_model = 'gemini-3.6-flash'

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
                return validated_data.model_dump()

            except Exception as e:
                error_str = str(e)
                if any(err in error_str for err in ["503", "UNAVAILABLE", "429"]):
                    if attempt < max_retries:
                        # Exponential backoff: 10s, 20s, 40s, 80s
                        sleep_time = 10 * (2 ** (attempt - 1))
                        print(f"[WARNING] API congested. Retrying in {sleep_time}s...")
                        time.sleep(sleep_time)
                        continue
                
                raise e