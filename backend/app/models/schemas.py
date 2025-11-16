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


class AnalysisResponse(BaseModel):
    file_id: str
    sections: List[FlightPlanSection]
    total_pages: int
    analysis_summary: str = Field(..., description="Overall AI-generated summary")


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
