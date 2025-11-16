from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
import PyPDF2
from datetime import datetime
import os
import logging
from typing import List
from app.models.schemas import FlightPlanSection, CriticalityLevel

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generate customized flight briefing PDFs."""

    def __init__(self):
        self.page_size = A4
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Create custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1,  # Center
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
        ))

    def generate_briefing_pdf(
        self,
        original_pdf_path: str,
        output_path: str,
        sections: List[FlightPlanSection],
        selected_sections: List[str],
        overall_summary: str
    ) -> str:
        """
        Generate a custom flight briefing PDF.

        Args:
            original_pdf_path: Path to the original uploaded PDF
            output_path: Path where the generated PDF will be saved
            sections: List of all analyzed sections
            selected_sections: List of section names to include
            overall_summary: AI-generated overall summary

        Returns:
            Path to the generated PDF
        """
        try:
            # Create cover page first
            cover_path = output_path.replace('.pdf', '_cover.pdf')
            self._create_cover_page(
                cover_path,
                sections,
                selected_sections,
                overall_summary
            )

            # Extract selected pages from original PDF
            selected_pages = self._get_selected_pages(sections, selected_sections)

            # Merge cover page with selected pages
            self._merge_pdfs(
                cover_path,
                original_pdf_path,
                output_path,
                selected_pages
            )

            # Clean up temporary cover page
            if os.path.exists(cover_path):
                os.remove(cover_path)

            logger.info(f"Generated briefing PDF: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise Exception(f"Failed to generate PDF: {str(e)}")

    def _create_cover_page(
        self,
        output_path: str,
        sections: List[FlightPlanSection],
        selected_sections: List[str],
        overall_summary: str
    ):
        """Create the cover page with summary and section list."""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=self.page_size,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch
        )

        story = []

        # Title
        title = Paragraph("FlightBrief AI", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3 * inch))

        # Subtitle with date
        date_str = datetime.now().strftime("%B %d, %Y - %H:%M UTC")
        subtitle = Paragraph(
            f"<b>Custom Flight Briefing</b><br/>{date_str}",
            self.styles['Normal']
        )
        story.append(subtitle)
        story.append(Spacer(1, 0.4 * inch))

        # Overall Summary
        story.append(Paragraph("<b>Executive Summary</b>", self.styles['SectionHeader']))
        summary_para = Paragraph(overall_summary, self.styles['Normal'])
        story.append(summary_para)
        story.append(Spacer(1, 0.3 * inch))

        # Included Sections Table
        story.append(Paragraph("<b>Included Sections</b>", self.styles['SectionHeader']))

        # Filter only selected sections
        included = [s for s in sections if s.section_name in selected_sections]

        # Create table data
        table_data = [['Section', 'Priority', 'Summary', 'Pages']]

        for section in included:
            criticality_badge = self._get_criticality_badge(section.criticality)
            table_data.append([
                section.section_name,
                criticality_badge,
                section.one_line_summary[:50] + '...' if len(section.one_line_summary) > 50 else section.one_line_summary,
                ', '.join(map(str, section.pages[:3])) + ('...' if len(section.pages) > 3 else '')
            ])

        # Create table
        table = Table(table_data, colWidths=[1.8 * inch, 0.8 * inch, 2.8 * inch, 0.8 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))

        story.append(table)
        story.append(Spacer(1, 0.3 * inch))

        # Footer
        footer = Paragraph(
            "<i>This briefing was generated by FlightBrief AI. Always verify critical information with official sources.</i>",
            self.styles['Normal']
        )
        story.append(Spacer(1, 0.5 * inch))
        story.append(footer)

        # Build PDF
        doc.build(story)

    def _get_criticality_badge(self, criticality: CriticalityLevel) -> str:
        """Get text representation of criticality level."""
        badges = {
            CriticalityLevel.CRITICAL: "CRITICAL",
            CriticalityLevel.WARNING: "WARNING",
            CriticalityLevel.NORMAL: "NORMAL",
            CriticalityLevel.INFO: "INFO",
        }
        return badges.get(criticality, "NORMAL")

    def _get_selected_pages(
        self,
        sections: List[FlightPlanSection],
        selected_sections: List[str]
    ) -> List[int]:
        """Get list of page numbers from selected sections."""
        pages = set()

        for section in sections:
            if section.section_name in selected_sections:
                pages.update(section.pages)

        return sorted(list(pages))

    def _merge_pdfs(
        self,
        cover_path: str,
        original_path: str,
        output_path: str,
        selected_pages: List[int]
    ):
        """Merge cover page with selected pages from original PDF."""
        pdf_writer = PyPDF2.PdfWriter()

        # Add cover page
        with open(cover_path, 'rb') as cover_file:
            cover_reader = PyPDF2.PdfReader(cover_file)
            for page in cover_reader.pages:
                pdf_writer.add_page(page)

        # Add selected pages from original
        with open(original_path, 'rb') as original_file:
            original_reader = PyPDF2.PdfReader(original_file)

            for page_num in selected_pages:
                if 0 < page_num <= len(original_reader.pages):
                    page = original_reader.pages[page_num - 1]  # Convert to 0-indexed
                    pdf_writer.add_page(page)

        # Write output
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
