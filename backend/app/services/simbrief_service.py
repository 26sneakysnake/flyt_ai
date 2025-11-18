"""
SimBrief API integration service for fetching flight plan data.
"""
import httpx
from typing import Optional, Dict, Any
from ..models.schemas import FlightData


class SimbriefService:
    """Service for fetching and processing SimBrief flight plans."""

    BASE_URL = "https://www.simbrief.com/api/xml.fetcher.php"

    async def fetch_flight_plan(self, username: str) -> Dict[Any, Any]:
        """
        Fetch the latest flight plan from SimBrief for a given username.

        Args:
            username: SimBrief username

        Returns:
            Dict containing the flight plan data

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                self.BASE_URL,
                params={
                    "username": username,
                    "json": "1"
                }
            )
            response.raise_for_status()
            return response.json()

    def _safe_get(self, data: Dict, *keys: str, default: Optional[str] = None) -> Optional[str]:
        """
        Safely navigate nested dictionary and return value or default.

        Args:
            data: The dictionary to navigate
            *keys: The keys to traverse
            default: Default value if key not found

        Returns:
            The value if found, otherwise default
        """
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return str(current) if current is not None else default

    def _format_time(self, time_str: Optional[str]) -> Optional[str]:
        """
        Format time from HHMM or HH:MM to HH:MM UTC format.

        Args:
            time_str: Time string in HHMM or HH:MM format

        Returns:
            Formatted time string with UTC suffix
        """
        if not time_str:
            return None

        # Remove any existing colons
        time_clean = str(time_str).replace(":", "")

        # Ensure we have at least 4 digits
        if len(time_clean) >= 4:
            hours = time_clean[:2]
            minutes = time_clean[2:4]
            return f"{hours}:{minutes} UTC"

        return None

    def _calculate_flight_time(self, departure_time: Optional[str], arrival_time: Optional[str]) -> Optional[str]:
        """
        Calculate flight time from departure and arrival times.

        Args:
            departure_time: Departure time in HHMM format
            arrival_time: Arrival time in HHMM format

        Returns:
            Flight time in "XhYYm" format or None
        """
        if not departure_time or not arrival_time:
            return None

        try:
            # Parse times
            dep_clean = str(departure_time).replace(":", "")
            arr_clean = str(arrival_time).replace(":", "")

            if len(dep_clean) < 4 or len(arr_clean) < 4:
                return None

            dep_hours = int(dep_clean[:2])
            dep_minutes = int(dep_clean[2:4])
            arr_hours = int(arr_clean[:2])
            arr_minutes = int(arr_clean[2:4])

            # Convert to minutes
            dep_total_minutes = dep_hours * 60 + dep_minutes
            arr_total_minutes = arr_hours * 60 + arr_minutes

            # Handle midnight crossover
            if arr_total_minutes < dep_total_minutes:
                arr_total_minutes += 24 * 60

            # Calculate difference
            diff_minutes = arr_total_minutes - dep_total_minutes
            hours = diff_minutes // 60
            minutes = diff_minutes % 60

            return f"{hours}h{minutes:02d}m"
        except (ValueError, IndexError):
            return None

    def map_to_flight_data(self, simbrief_data: Dict[Any, Any]) -> FlightData:
        """
        Map SimBrief API response to FlightData model.

        Args:
            simbrief_data: Raw SimBrief API response

        Returns:
            FlightData object with mapped fields
        """
        # Extract main sections
        general = simbrief_data.get("general", {})
        origin = simbrief_data.get("origin", {})
        destination = simbrief_data.get("destination", {})
        aircraft = simbrief_data.get("aircraft", {})
        fuel = simbrief_data.get("fuel", {})
        weights = simbrief_data.get("weights", {})
        weather = simbrief_data.get("weather", {})
        times = simbrief_data.get("times", {})

        # Extract route (first waypoint to last waypoint)
        navlog = simbrief_data.get("navlog", {})
        fixes = navlog.get("fix", []) if isinstance(navlog.get("fix"), list) else [navlog.get("fix", {})]

        # Build route string from waypoints
        route_waypoints = []
        cruise_altitude = None
        max_fl = 0

        for fix in fixes:
            if isinstance(fix, dict):
                ident = fix.get("ident", "")
                altitude = fix.get("altitude_feet", "")

                if ident:
                    route_waypoints.append(ident)

                # Extract highest FL for cruise altitude
                if altitude:
                    try:
                        alt_ft = int(altitude)
                        fl = alt_ft // 100
                        if fl > max_fl:
                            max_fl = fl
                    except (ValueError, TypeError):
                        pass

        route = " ".join(route_waypoints) if route_waypoints else None

        # Set cruise altitude from max FL if found
        if max_fl > 0:
            cruise_altitude = f"FL{max_fl}"

        # Extract times
        departure_time = self._safe_get(origin, "plan_rwy_time")
        arrival_time = self._safe_get(destination, "plan_rwy_time")

        # Calculate flight time
        flight_time = self._calculate_flight_time(departure_time, arrival_time)

        # Format date
        flight_date = self._safe_get(general, "date")
        if flight_date:
            # SimBrief format is typically DDMMMYY (e.g., 18NOV25)
            try:
                from datetime import datetime
                date_obj = datetime.strptime(flight_date, "%d%b%y")
                flight_date = date_obj.strftime("%d %b %Y").upper()
            except (ValueError, ImportError):
                pass

        # Build FlightData object
        return FlightData(
            # Basic Info
            flight_number=self._safe_get(general, "icao_airline") + self._safe_get(general, "flight_number"),
            flight_date=flight_date,
            aircraft_type=self._safe_get(aircraft, "icaocode"),
            aircraft_registration=self._safe_get(aircraft, "reg"),
            airline=self._safe_get(general, "icao_airline"),

            # Route Info
            departure_icao=self._safe_get(origin, "icao_code"),
            departure_name=self._safe_get(origin, "name"),
            arrival_icao=self._safe_get(destination, "icao_code"),
            arrival_name=self._safe_get(destination, "name"),
            alternate_icao=self._safe_get(simbrief_data.get("alternate", {}), "icao_code"),

            # Timing
            departure_time=self._format_time(departure_time),
            arrival_time=self._format_time(arrival_time),
            flight_time=flight_time,
            air_time=self._safe_get(times, "est_time_enroute"),
            block_time=self._safe_get(times, "est_block"),

            # Route & Performance
            route=route,
            route_distance=self._safe_get(general, "route_distance"),
            cruise_altitude=cruise_altitude or self._safe_get(general, "initial_altitude"),
            ci_value=self._safe_get(general, "costindex"),
            average_wind=self._safe_get(general, "avg_wind_dir") + "/" + self._safe_get(general, "avg_wind_spd"),

            # Fuel
            fuel_planned=self._safe_get(fuel, "plan_ramp"),  # Block fuel

            # Load Sheet
            passenger_count=self._safe_get(weights, "pax_count"),
            baggage=self._safe_get(weights, "cargo"),
            payload=self._safe_get(weights, "payload"),
            ezfw=self._safe_get(weights, "est_zfw"),
            etow=self._safe_get(weights, "est_tow"),
            elw=self._safe_get(weights, "est_ldw"),

            # Weather
            metar_departure=self._safe_get(weather, "orig_metar"),
            metar_arrival=self._safe_get(weather, "dest_metar"),

            # Additional Info
            remarks=self._safe_get(general, "dx_rmk"),
        )
