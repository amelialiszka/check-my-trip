import json
import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class OfferDetails(BaseModel):
    # --- BASIC INFO ---
    total_price: float = Field(..., description="Total price of the trip in local currency. If not found, output 0.0")
    duration_days: int = Field(..., description="Duration of the trip in days.")
    country: str = Field(..., description="Destination country.")
    region: str = Field(..., description="Destination region or city.")
    
    # --- HOTEL & STANDARD ---
    hotel_stars: float = Field(..., description="Hotel category in stars (e.g., 4.0 or 5.0). If not found, output 0.0")
    average_rating: float = Field(..., description="Average customer review score on a 5-point scale (e.g., 4.6). Map descriptive labels (e.g., 'Znakomity', 'Excellent', 'Hervorragend') to a 5-point scale: Exceptional -> 4.9, Great/Excellent -> 4.6, Very Good -> 4.2, Good -> 3.8, Average -> 3.0, Poor -> 2.0. If not found, output 0.0")
    review_count: int = Field(..., description="Total number of customer reviews. If not found, output 0")
    
    # --- ROOM & TRANSPORT ---
    room_type: str = Field(..., description="Type of room, e.g., 'Standard', 'Apartment'. If not specified, output 'Unknown'")
    has_sea_view: bool = Field(..., description="Does the room have a sea view? True/False")
    meal_plan: str = Field(..., description="Type of meal plan, e.g., 'All Inclusive', 'HB', 'BB', 'RO'.")
    
    # --- AMENITIES ---
    number_of_restaurants: int = Field(..., description="Total number of restaurants. If not specified, output 1.")
    number_of_bars: int = Field(..., description="Total number of bars. If not specified, output 0.")
    number_of_pools: int = Field(..., description="Number of swimming pools. If not found, output 1 for resorts or 0.")
    is_wifi_free: bool = Field(..., description="Is Wi-Fi free? True/False")
    
    # --- LOCATION ---
    distance_to_beach_meters: int = Field(
        ..., 
        description=(
            "Distance to the beach in meters. "
            "CRITICAL RULES: "
            "1. If exact numeric meters are provided in the text, extract them. "
            "2. If terms indicating proximity are used (e.g., 'close to beach', 'blisko', 'strandnah', 'short walk'), output 200. DO NOT output 0 for these! "
            "3. Output 0 ONLY if explicitly waterfront or directly on the beach (e.g., 'przy plaży', 'beachfront', 'direkt am Strand'). "
            "4. If far away, output 1000. "
            "5. If completely unknown, output -1."
        )
    )
    distance_to_center_meters: int = Field(..., description="Distance to the city center in meters. If not found, output -1")
    is_direct_flight: bool = Field(..., description="Is the flight direct? True/False")
    is_transfer_included: bool = Field(..., description="Is the transfer included? True/False")


class OfferAnalyzer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("ERROR: GEMINI_API_KEY not found in environment variables!")
        
        self.client = genai.Client(api_key=api_key)

    def extract_information(self, text: str) -> dict:
        schema_json = json.dumps(OfferDetails.model_json_schema(), indent=2)
        
        prompt = f"""
        You are an advanced data extraction system for travel offers. 
        Analyze the following text and extract information strictly according to this JSON schema:
        {schema_json}
        
        Respond ONLY with a valid JSON object.
        """

        response = self.client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[prompt, text],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        
        extracted_dict = json.loads(response.text)
        validated_data = OfferDetails(**extracted_dict)
        
        return validated_data.model_dump()