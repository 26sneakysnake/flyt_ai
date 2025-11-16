import openai
import os
import json
import logging
from typing import Dict, Optional
from app.models.schemas import FlightData

logger = logging.getLogger(__name__)


class FlightDataExtractor:
    """Extract key flight information from OFP using AI"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        openai.api_key = api_key
        self.model = "gpt-4o-mini"

    async def extract_flight_data(self, ofp_text: str) -> FlightData:
        """
        Extract structured flight data from the OFP section.

        Args:
            ofp_text: Text content from the OFP (Operational Flight Plan) section

        Returns:
            FlightData object with extracted information
        """
        # Limit text to avoid token limits (first 6000 chars of OFP usually contains all key info)
        text_sample = ofp_text[:6000]

        prompt = f"""Extract flight information from this Operational Flight Plan (OFP).

OFP Content:
{text_sample}

Return ONLY valid JSON with this structure:
{{
    "flight_number": "string or null",
    "aircraft_type": "string or null (e.g., B777-300ER, A320)",
    "aircraft_registration": "string or null",
    "airline": "string or null",
    "airline_icao": "string or null (e.g., AFR, UAL)",
    "departure_icao": "string or null (4-letter ICAO)",
    "departure_name": "string or null",
    "arrival_icao": "string or null (4-letter ICAO)",
    "arrival_name": "string or null",
    "alternate_icao": "string or null",
    "departure_time": "string or null (UTC format)",
    "arrival_time": "string or null (UTC format)",
    "flight_time": "string or null (e.g., '08:30')",
    "route": "string or null (waypoints)",
    "cruise_altitude": "string or null (e.g., 'FL350')",
    "fuel_planned": "string or null (e.g., '45000 KG')"
}}

Use null for any field you cannot find. Be precise and extract exact values from the OFP."""

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an aviation expert specialized in reading Operational Flight Plans. Extract data accurately. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for precise extraction
                max_tokens=500
            )

            # Extract and parse JSON response
            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.rsplit("```", 1)[0]

            data = json.loads(content)

            # Create FlightData object
            return FlightData(**data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse flight data JSON: {e}")
            return FlightData()  # Return empty flight data

        except Exception as e:
            logger.error(f"Error extracting flight data: {str(e)}")
            return FlightData()  # Return empty flight data

    def get_aircraft_image_url(self, aircraft_type: Optional[str], airline_icao: Optional[str]) -> str:
        """
        Generate aircraft image URL using placeholder service.
        In production, use aviation APIs like Planespotters or JetPhotos.

        Args:
            aircraft_type: Aircraft type (e.g., B777)
            airline_icao: Airline ICAO code (e.g., AFR)

        Returns:
            URL to aircraft image
        """
        if not aircraft_type:
            # Default generic aircraft
            return "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=800&h=600&fit=crop"

        # Use Unsplash as placeholder (in production, use aviation photo APIs)
        # Clean aircraft type for search
        aircraft_clean = aircraft_type.replace("-", " ").replace("ER", "").strip()

        # Map common types to search terms
        aircraft_map = {
            "B777": "Boeing 777",
            "B787": "Boeing 787 Dreamliner",
            "B737": "Boeing 737",
            "A320": "Airbus A320",
            "A330": "Airbus A330",
            "A350": "Airbus A350",
            "A380": "Airbus A380",
        }

        aircraft_search = aircraft_clean
        for key, value in aircraft_map.items():
            if key in aircraft_type.upper():
                aircraft_search = value
                break

        # Add airline if available
        search_term = aircraft_search
        if airline_icao:
            search_term = f"{airline_icao} {aircraft_search}"

        # Return Unsplash placeholder (replace with real aviation API)
        return f"https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=800&h=600&fit=crop&q=80"
