from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
import os
import uuid
import shutil
import asyncio
from typing import Dict
import logging

from app.models.schemas import (
    UploadResponse,
    AnalysisRequest,
    AnalysisResponse,
    GenerateRequest,
    GenerateResponse,
    ErrorResponse,
    FlightPlanSection
)
from app.services import PDFParser, AIAnalyzer, PDFGenerator

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for demo (use Redis or DB in production)
file_storage: Dict[str, dict] = {}

# Initialize services
pdf_parser = PDFParser()
ai_analyzer = AIAnalyzer()
pdf_generator = PDFGenerator()

# Get upload directory from environment
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 20971520))  # 20MB default

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a flight plan PDF file.

    - **file**: PDF file (max 20MB)
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    # Generate unique file ID
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()

            # Check file size
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes"
                )

            buffer.write(content)

        # Get total pages
        total_pages = pdf_parser.get_total_pages(file_path)

        # Store file metadata
        file_storage[file_id] = {
            "filename": file.filename,
            "file_path": file_path,
            "total_pages": total_pages,
            "analyzed": False
        }

        logger.info(f"Uploaded file {file.filename} with ID {file_id}")

        return UploadResponse(
            file_id=file_id,
            filename=file.filename,
            total_pages=total_pages
        )

    except HTTPException:
        # Clean up file on validation error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise

    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)

        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_pdf(request: AnalysisRequest):
    """
    Analyze uploaded PDF and identify sections with AI.

    - **file_id**: File ID from upload response
    """
    # Validate file exists
    if request.file_id not in file_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_info = file_storage[request.file_id]
    file_path = file_info["file_path"]

    try:
        # Extract text by page
        logger.info(f"Parsing PDF {request.file_id}")
        pages_text = pdf_parser.extract_text_by_page(file_path)

        # Identify sections
        logger.info(f"Identifying sections for {request.file_id}")
        identified_sections = pdf_parser.identify_sections(pages_text)

        # Analyze each section with AI (in parallel for speed)
        logger.info(f"Analyzing {len(identified_sections)} sections with AI")
        analysis_tasks = [
            ai_analyzer.analyze_section(section)
            for section in identified_sections
        ]
        analyzed_sections = await asyncio.gather(*analysis_tasks)

        # Generate overall summary
        logger.info(f"Generating overall summary")
        overall_summary = await ai_analyzer.generate_overall_summary(analyzed_sections)

        # Store analysis results
        file_storage[request.file_id]["sections"] = analyzed_sections
        file_storage[request.file_id]["overall_summary"] = overall_summary
        file_storage[request.file_id]["analyzed"] = True

        return AnalysisResponse(
            file_id=request.file_id,
            sections=analyzed_sections,
            total_pages=file_info["total_pages"],
            analysis_summary=overall_summary
        )

    except Exception as e:
        logger.error(f"Error analyzing PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze PDF: {str(e)}"
        )


@router.post("/generate", response_model=GenerateResponse)
async def generate_briefing(request: GenerateRequest):
    """
    Generate custom flight briefing PDF with selected sections.

    - **file_id**: File ID from upload response
    - **selected_sections**: List of sections to include
    - **briefing_type**: Type of briefing (custom, recommended, minimal)
    """
    # Validate file exists
    if request.file_id not in file_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_info = file_storage[request.file_id]

    # Validate file has been analyzed
    if not file_info.get("analyzed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be analyzed before generating briefing"
        )

    try:
        # Get selected section names
        selected_names = [
            s.section_name for s in request.selected_sections if s.selected
        ]

        if not selected_names:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one section must be selected"
            )

        # Generate output PDF
        output_filename = f"{request.file_id}_briefing.pdf"
        output_path = os.path.join(UPLOAD_DIR, output_filename)

        logger.info(f"Generating briefing PDF for {request.file_id}")
        pdf_generator.generate_briefing_pdf(
            original_pdf_path=file_info["file_path"],
            output_path=output_path,
            sections=file_info["sections"],
            selected_sections=selected_names,
            overall_summary=file_info["overall_summary"]
        )

        # Store output path
        file_storage[request.file_id]["output_path"] = output_path

        # Calculate total pages in output
        total_pages = pdf_parser.get_total_pages(output_path)

        return GenerateResponse(
            file_id=request.file_id,
            download_url=f"/api/download/{request.file_id}",
            included_sections=selected_names,
            total_pages=total_pages
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error generating briefing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate briefing: {str(e)}"
        )


@router.get("/download/{file_id}")
async def download_briefing(file_id: str):
    """
    Download generated flight briefing PDF.

    - **file_id**: File ID from upload response
    """
    # Validate file exists
    if file_id not in file_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_info = file_storage[file_id]

    # Validate output exists
    if "output_path" not in file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Briefing not generated yet"
        )

    output_path = file_info["output_path"]

    if not os.path.exists(output_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated file not found"
        )

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename=f"FlightBrief_{file_info['filename']}"
    )


@router.delete("/cleanup/{file_id}")
async def cleanup_files(file_id: str):
    """
    Clean up uploaded and generated files.

    - **file_id**: File ID to clean up
    """
    if file_id not in file_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_info = file_storage[file_id]

    # Remove original file
    if os.path.exists(file_info["file_path"]):
        os.remove(file_info["file_path"])

    # Remove generated file if exists
    if "output_path" in file_info and os.path.exists(file_info["output_path"]):
        os.remove(file_info["output_path"])

    # Remove from storage
    del file_storage[file_id]

    return {"message": "Files cleaned up successfully"}
