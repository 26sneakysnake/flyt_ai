import PyPDF2
from typing import Dict, List, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """Parse flight plan PDFs and extract text content by page."""

    def __init__(self):
        self.section_keywords = {
            "OFP": ["operational flight plan", "ofp", "flight plan"],
            "NOTAM - Departure": ["notam", "departure", "adep"],
            "NOTAM - Destination": ["notam", "destination", "ades"],
            "NOTAM - Alternate": ["notam", "alternate", "altn"],
            "Weather - METAR": ["metar", "weather"],
            "Weather - TAF": ["taf", "terminal aerodrome forecast"],
            "Flight Log": ["flight log", "flt log", "navigation log"],
            "Route": ["route", "routing", "flight route"],
            "Fuel Planning": ["fuel", "fuel plan", "fuel calculation"],
            "Runway Analysis": ["runway", "runway analysis", "takeoff performance"],
            "Charts": ["chart", "sid", "star", "approach"],
        }

    def extract_text_by_page(self, pdf_path: str) -> Dict[int, str]:
        """
        Extract text from PDF, organized by page number.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary mapping page numbers (1-indexed) to text content
        """
        pages_text = {}

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)

                logger.info(f"Processing PDF with {total_pages} pages")

                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    pages_text[page_num + 1] = text  # 1-indexed

            return pages_text

        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            raise Exception(f"Failed to parse PDF: {str(e)}")

    def identify_sections(self, pages_text: Dict[int, str]) -> List[Dict]:
        """
        Identify potential sections in the flight plan based on keywords.
        This provides initial section candidates for AI analysis.

        Args:
            pages_text: Dictionary of page numbers to text content

        Returns:
            List of identified sections with page ranges
        """
        sections = []
        current_section = None

        for page_num, text in pages_text.items():
            text_lower = text.lower()

            # Check for section keywords
            for section_name, keywords in self.section_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    # If we found a new section
                    if current_section and current_section["name"] != section_name:
                        sections.append(current_section)
                        current_section = None

                    # Start or continue current section
                    if not current_section:
                        current_section = {
                            "name": section_name,
                            "pages": [page_num],
                            "text": text
                        }
                    else:
                        current_section["pages"].append(page_num)
                        current_section["text"] += "\n\n" + text
                    break
            else:
                # No keyword match - continue current section if exists
                if current_section:
                    current_section["pages"].append(page_num)
                    current_section["text"] += "\n\n" + text

        # Add the last section
        if current_section:
            sections.append(current_section)

        # If no sections identified, create a single "Unknown" section
        if not sections and pages_text:
            all_pages = sorted(pages_text.keys())
            sections.append({
                "name": "Flight Plan",
                "pages": all_pages,
                "text": "\n\n".join(pages_text.values())
            })

        logger.info(f"Identified {len(sections)} sections")
        return sections

    def get_total_pages(self, pdf_path: str) -> int:
        """Get total number of pages in PDF."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except Exception as e:
            logger.error(f"Error reading PDF page count: {str(e)}")
            raise Exception(f"Failed to read PDF: {str(e)}")
