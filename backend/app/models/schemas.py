from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class CriticalityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    NORMAL = "NORMAL"
    INFO = "INFO"


class FlightPlanSection(BaseModel):
    section_name: str = Field(..., description="Name of the section (e.g., 'OFP', 'NOTAM - Departure')")
    criticality: CriticalityLevel = Field(..., description="Criticality level of this section")
    one_line_summary: str = Field(..., description="One-line summary of the section content")
    pages: List[int] = Field(..., description="List of page numbers this section spans")


class UploadResponse(BaseModel):
    file_id: str = Field(..., description="Unique identifier for the uploaded file")
    filename: str = Field(..., description="Original filename")
    total_pages: int = Field(..., description="Total number of pages in the PDF")
    message: str = Field(default="File uploaded successfully")


class AnalysisRequest(BaseModel):
    file_id: str = Field(..., description="File ID from upload response")


class FlightData(BaseModel):
    """Core flight information extracted from the plan"""
    # Basic Info
    flight_number: Optional[str] = Field(None, description="Flight number (e.g., AF447)")
    flight_date: Optional[str] = Field(None, description="Flight date (e.g., 18 NOV 2025)")
    aircraft_type: Optional[str] = Field(None, description="Aircraft type (e.g., B777-300ER)")
    aircraft_registration: Optional[str] = Field(None, description="Aircraft registration (e.g., F-GZNE)")
    airline: Optional[str] = Field(None, description="Airline name")
    airline_icao: Optional[str] = Field(None, description="Airline ICAO code")

    # Route Info
    departure_icao: Optional[str] = Field(None, description="Departure airport ICAO")
    departure_name: Optional[str] = Field(None, description="Departure airport name")
    arrival_icao: Optional[str] = Field(None, description="Arrival airport ICAO")
    arrival_name: Optional[str] = Field(None, description="Arrival airport name")
    alternate_icao: Optional[str] = Field(None, description="Alternate airport ICAO")

    # Timing
    departure_time: Optional[str] = Field(None, description="Scheduled departure time")
    arrival_time: Optional[str] = Field(None, description="Estimated arrival time")
    flight_time: Optional[str] = Field(None, description="Total flight time")
    air_time: Optional[str] = Field(None, description="Air time (wheels up to wheels down)")
    block_time: Optional[str] = Field(None, description="Block time (gate to gate)")

    # Route & Performance
    route: Optional[str] = Field(None, description="Flight route")
    route_distance: Optional[str] = Field(None, description="Route distance (e.g., '3450 NM')")
    cruise_altitude: Optional[str] = Field(None, description="Cruise altitude (FL)")
    ci_value: Optional[str] = Field(None, description="Cost Index value")
    average_wind: Optional[str] = Field(None, description="Average wind (e.g., 'H045/25')")

    # Fuel
    fuel_planned: Optional[str] = Field(None, description="Block fuel")

    # Load Sheet
    passenger_count: Optional[str] = Field(None, description="Passenger count")
    baggage: Optional[str] = Field(None, description="Baggage weight")
    payload: Optional[str] = Field(None, description="Payload weight")
    ezfw: Optional[str] = Field(None, description="Estimated Zero Fuel Weight")
    etow: Optional[str] = Field(None, description="Estimated Take-Off Weight")
    elw: Optional[str] = Field(None, description="Estimated Landing Weight")

    # Weather
    metar_departure: Optional[str] = Field(None, description="METAR for departure airport")
    metar_arrival: Optional[str] = Field(None, description="METAR for arrival airport")


class AnalysisResponse(BaseModel):
    file_id: str
    sections: List[FlightPlanSection]
    total_pages: int
    analysis_summary: str = Field(..., description="Overall AI-generated summary")
    flight_data: Optional[FlightData] = Field(None, description="Extracted flight information")


class SectionSelection(BaseModel):
    section_name: str
    selected: bool = Field(default=True)


class GenerateRequest(BaseModel):
    file_id: str = Field(..., description="File ID from upload response")
    selected_sections: List[SectionSelection] = Field(..., description="List of sections to include")
    briefing_type: Optional[str] = Field(default="custom", description="Type of briefing (custom, recommended, minimal)")


class GenerateResponse(BaseModel):
    file_id: str
    download_url: str = Field(..., description="URL to download the generated PDF")
    included_sections: List[str]
    total_pages: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
