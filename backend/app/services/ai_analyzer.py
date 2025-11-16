import openai
import os
import json
import logging
from typing import Dict, List
from app.models.schemas import FlightPlanSection, CriticalityLevel

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Analyze flight plan sections using OpenAI GPT-4o-mini."""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        openai.api_key = api_key
        self.model = "gpt-4o-mini"

    async def analyze_section(self, section: Dict) -> FlightPlanSection:
        """
        Analyze a single flight plan section using AI.

        Args:
            section: Dictionary containing section name, pages, and text

        Returns:
            FlightPlanSection with AI-determined criticality and summary
        """
        section_name = section["name"]
        section_text = section["text"][:4000]  # Limit text to avoid token limits
        pages = section["pages"]

        prompt = f"""Analyze this section from an aviation flight plan document.

Section Name: {section_name}
Content: {section_text}

Return ONLY a valid JSON object with this exact structure:
{{
    "section_name": "string (keep original or improve)",
    "criticality": "CRITICAL|WARNING|NORMAL|INFO",
    "one_line_summary": "string (concise summary for pilots)",
    "pages": {pages}
}}

Criticality guidelines:
- CRITICAL: Essential for flight safety (OFP, runway analysis, critical NOTAMs, fuel planning)
- WARNING: Important but not immediately critical (standard NOTAMs, weather, alternates)
- NORMAL: Useful reference information (charts, route details, flight log)
- INFO: Supplementary information (general notices, optional data)

Keep the summary professional and aviation-focused. Maximum 100 characters."""

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an aviation expert analyzing flight plan documents. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )

            # Extract and parse JSON response
            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            analysis = json.loads(content)

            # Validate and create FlightPlanSection
            return FlightPlanSection(
                section_name=analysis["section_name"],
                criticality=CriticalityLevel(analysis["criticality"]),
                one_line_summary=analysis["one_line_summary"],
                pages=analysis["pages"]
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            # Fallback to default values
            return self._create_fallback_section(section_name, pages)

        except Exception as e:
            logger.error(f"Error analyzing section '{section_name}': {str(e)}")
            return self._create_fallback_section(section_name, pages)

    def _create_fallback_section(self, section_name: str, pages: List[int]) -> FlightPlanSection:
        """Create a fallback section when AI analysis fails."""
        # Determine default criticality based on section name
        criticality_map = {
            "OFP": CriticalityLevel.CRITICAL,
            "Fuel Planning": CriticalityLevel.CRITICAL,
            "Runway Analysis": CriticalityLevel.CRITICAL,
            "NOTAM": CriticalityLevel.WARNING,
            "Weather": CriticalityLevel.WARNING,
            "Charts": CriticalityLevel.NORMAL,
            "Route": CriticalityLevel.NORMAL,
            "Flight Log": CriticalityLevel.NORMAL,
        }

        criticality = CriticalityLevel.NORMAL
        for key, value in criticality_map.items():
            if key.lower() in section_name.lower():
                criticality = value
                break

        return FlightPlanSection(
            section_name=section_name,
            criticality=criticality,
            one_line_summary=f"Flight plan section: {section_name}",
            pages=pages
        )

    async def generate_overall_summary(self, sections: List[FlightPlanSection]) -> str:
        """
        Generate an overall summary of the flight plan analysis.

        Args:
            sections: List of analyzed sections

        Returns:
            Overall summary string
        """
        sections_info = "\n".join([
            f"- {s.section_name} ({s.criticality.value}): {s.one_line_summary}"
            for s in sections
        ])

        prompt = f"""Analyze this flight plan brief based on the identified sections:

{sections_info}

Provide a 2-3 sentence professional summary for the pilot covering:
1. Flight plan completeness
2. Key critical items to review
3. Overall readiness assessment

Keep it concise and actionable."""

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an aviation expert providing flight briefing summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=200
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Flight plan analysis complete. Please review all critical sections before departure."
