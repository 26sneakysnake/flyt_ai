import openai
import os
import json
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
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
    "departure_time": "string or null (HHMM format like 1430 for 2:30 PM UTC)",
    "arrival_time": "string or null (HHMM format like 2315 for 11:15 PM UTC)",
    "flight_time": "string or null (leave as null, will be calculated)",
    "route": "string or null (waypoints)",
    "cruise_altitude": "string or null (e.g., 'FL350')",
    "fuel_planned": "string or null (BLOCK FUEL value with unit, e.g., '45000 KG' or '99200 LBS')"
}}

IMPORTANT INSTRUCTIONS:
- For departure_time and arrival_time: Extract in HHMM format (e.g., 1430, 0845, 2315)
- For fuel_planned: Look specifically for "BLOCK FUEL" or "BLOCK" in the fuel section
- Leave flight_time as null (it will be calculated automatically)
- Use null for any field you cannot find
- Be precise and extract exact values from the OFP"""

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

            # Post-process the data
            data = self._post_process_flight_data(data)

            # Create FlightData object
            return FlightData(**data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse flight data JSON: {e}")
            return FlightData()  # Return empty flight data

        except Exception as e:
            logger.error(f"Error extracting flight data: {str(e)}")
            return FlightData()  # Return empty flight data

    def _post_process_flight_data(self, data: dict) -> dict:
        """
        Post-process extracted flight data:
        - Format times to readable format (HH:MM UTC)
        - Calculate flight time from departure and arrival times

        Args:
            data: Raw extracted data dictionary

        Returns:
            Processed data dictionary
        """
        # Format departure and arrival times
        if data.get("departure_time"):
            data["departure_time"] = self._format_time(data["departure_time"])

        if data.get("arrival_time"):
            data["arrival_time"] = self._format_time(data["arrival_time"])

        # Calculate flight time if both departure and arrival are available
        if data.get("departure_time") and data.get("arrival_time"):
            data["flight_time"] = self._calculate_flight_time(
                data["departure_time"],
                data["arrival_time"]
            )

        return data

    def _format_time(self, time_str: str) -> str:
        """
        Format time from HHMM to HH:MM UTC.

        Args:
            time_str: Time in HHMM format (e.g., "1430", "0845")

        Returns:
            Formatted time string (e.g., "14:30 UTC", "08:45 UTC")
        """
        try:
            # Remove any non-digit characters
            time_clean = ''.join(filter(str.isdigit, str(time_str)))

            if len(time_clean) >= 4:
                hours = time_clean[:2]
                minutes = time_clean[2:4]
                return f"{hours}:{minutes} UTC"
            elif len(time_clean) == 3:
                # Handle times like 845 (8:45)
                hours = time_clean[0]
                minutes = time_clean[1:3]
                return f"0{hours}:{minutes} UTC"
            else:
                return time_str  # Return as-is if format is unexpected
        except Exception as e:
            logger.warning(f"Failed to format time '{time_str}': {e}")
            return str(time_str)

    def _calculate_flight_time(self, departure: str, arrival: str) -> str:
        """
        Calculate flight time from departure and arrival times.

        Args:
            departure: Departure time in "HH:MM UTC" format
            arrival: Arrival time in "HH:MM UTC" format

        Returns:
            Flight time string (e.g., "8h 30m", "12h 45m")
        """
        try:
            # Extract HH:MM from "HH:MM UTC"
            dep_time = departure.replace(" UTC", "").strip()
            arr_time = arrival.replace(" UTC", "").strip()

            # Parse times
            dep_hour, dep_min = map(int, dep_time.split(":"))
            arr_hour, arr_min = map(int, arr_time.split(":"))

            # Create datetime objects for today
            dep_dt = datetime.now().replace(hour=dep_hour, minute=dep_min, second=0, microsecond=0)
            arr_dt = datetime.now().replace(hour=arr_hour, minute=arr_min, second=0, microsecond=0)

            # If arrival is before departure, it means we crossed midnight
            if arr_dt < dep_dt:
                arr_dt += timedelta(days=1)

            # Calculate difference
            duration = arr_dt - dep_dt

            # Convert to hours and minutes
            total_minutes = int(duration.total_seconds() / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60

            return f"{hours}h {minutes:02d}m"

        except Exception as e:
            logger.warning(f"Failed to calculate flight time from {departure} to {arrival}: {e}")
            return None

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
