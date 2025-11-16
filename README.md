# FlightBrief AI - MVP v0.1

AI-powered flight plan analysis and briefing generation tool. Upload your aviation flight plan PDF, let AI analyze it, select the sections you need, and generate a customized briefing PDF.

## Features

- **Smart PDF Parsing**: Automatically identifies aviation sections (OFP, NOTAMs, Weather, Fuel Planning, etc.)
- **AI Analysis**: GPT-4o-mini evaluates section criticality and provides concise summaries
- **Custom Briefing**: Generate tailored PDFs with only the sections you need
- **Quick Selection**: Pre-configured selection modes (All, Recommended, Minimal)
- **Modern UI**: Clean, responsive interface built with Next.js and Tailwind CSS

## Tech Stack

### Backend
- **FastAPI** (Python 3.11) - Modern async web framework
- **PyPDF2** - PDF parsing and manipulation
- **OpenAI GPT-4o-mini** - AI analysis
- **ReportLab** - PDF generation
- **PostgreSQL** - Metadata storage
- **Docker** - Containerization

### Frontend
- **Next.js 14** (App Router) - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Dropzone** - File upload

## Project Structure

```
flightbrief-mvp/
├── docker-compose.yml          # Docker orchestration
├── .env.example                # Environment variables template
├── .env                        # Local environment variables
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py            # FastAPI application
│   │   ├── models/
│   │   │   └── schemas.py     # Pydantic models
│   │   ├── services/
│   │   │   ├── pdf_parser.py  # PDF parsing logic
│   │   │   ├── ai_analyzer.py # OpenAI integration
│   │   │   └── pdf_generator.py # PDF generation
│   │   └── api/
│   │       └── routes.py      # API endpoints
│   └── tests/
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── app/
    │   ├── layout.tsx         # Root layout
    │   ├── page.tsx           # Homepage (upload)
    │   ├── globals.css        # Global styles
    │   └── select/
    │       └── page.tsx       # Section selection page
    ├── components/
    │   ├── FileUpload.tsx     # Drag & drop upload
    │   ├── SectionSelector.tsx # Section table
    │   ├── CriticalityBadge.tsx # Priority badges
    │   └── LoadingSpinner.tsx  # Loading indicator
    └── lib/
        ├── api.ts             # API client
        └── utils.ts           # Utilities
```

## Prerequisites

- **Docker Desktop** (Windows 10/11)
- **OpenAI API Key** (GPT-4o-mini access)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd flightbrief-mvp
```

### 2. Configure Environment Variables

Edit the `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Start the Application

```bash
docker-compose up --build
```

This will:
- Build and start 3 containers (PostgreSQL, Backend, Frontend)
- Backend will be available at `http://localhost:8000`
- Frontend will be available at `http://localhost:3000`
- API docs at `http://localhost:8000/docs`

### 4. Access the Application

Open your browser and navigate to:

```
http://localhost:3000
```

## Usage

### 1. Upload Flight Plan
- Drag & drop or click to select your flight plan PDF
- Maximum file size: 20MB
- Only PDF files are accepted

### 2. AI Analysis
- The system automatically parses the PDF
- AI analyzes each section and assigns criticality levels:
  - 🔴 **CRITICAL**: Essential for flight safety (OFP, runway analysis, fuel planning)
  - 🟡 **WARNING**: Important information (NOTAMs, weather, alternates)
  - 🟢 **NORMAL**: Useful reference (charts, route details, flight log)
  - 🔵 **INFO**: Supplementary information

### 3. Select Sections
- Choose sections individually with checkboxes
- Or use quick selection modes:
  - **Select All**: Include all sections
  - **Recommended Selection**: CRITICAL + WARNING sections
  - **Minimal Briefing**: Only CRITICAL sections

### 4. Generate & Download
- Click "Generate & Download Briefing"
- Your custom PDF will be generated with:
  - Professional cover page
  - AI summary
  - Section list
  - Selected pages from original PDF

## API Endpoints

### POST `/api/upload`
Upload a flight plan PDF file.

**Request:** `multipart/form-data` with PDF file
**Response:** File ID, filename, total pages

### POST `/api/analyze`
Analyze uploaded PDF with AI.

**Request:**
```json
{
  "file_id": "uuid"
}
```

**Response:**
```json
{
  "file_id": "uuid",
  "sections": [...],
  "total_pages": 25,
  "analysis_summary": "..."
}
```

### POST `/api/generate`
Generate custom briefing PDF.

**Request:**
```json
{
  "file_id": "uuid",
  "selected_sections": [
    {"section_name": "OFP", "selected": true},
    ...
  ],
  "briefing_type": "custom"
}
```

**Response:**
```json
{
  "file_id": "uuid",
  "download_url": "/api/download/uuid",
  "included_sections": [...],
  "total_pages": 15
}
```

### GET `/api/download/{file_id}`
Download generated briefing PDF.

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests (if configured)
cd frontend
npm test
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `UPLOAD_DIR` | Upload directory path | `/tmp/uploads` |
| `MAX_FILE_SIZE` | Max upload size in bytes | `20971520` (20MB) |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## Troubleshooting

### Docker Issues

**Problem:** Containers won't start
**Solution:** Ensure Docker Desktop is running, check logs with `docker-compose logs`

**Problem:** Port already in use
**Solution:** Stop conflicting services or change ports in `docker-compose.yml`

### API Issues

**Problem:** 500 Internal Server Error
**Solution:** Check backend logs: `docker-compose logs backend`

**Problem:** OpenAI API errors
**Solution:** Verify your API key in `.env` and check OpenAI account status

### Upload Issues

**Problem:** File upload fails
**Solution:** Ensure file is PDF, under 20MB, and backend is running

**Problem:** Analysis timeout
**Solution:** Large PDFs may take 20-30 seconds, wait for completion

## Limitations (MVP)

This is an MVP and has the following limitations:

- No user authentication
- No persistent storage of flight history
- No real-time weather API integration
- No manual section editing
- In-memory file storage (use Redis/S3 for production)
- Basic error handling

## Future Enhancements

- User authentication and accounts
- Flight history and saved briefings
- Real-time weather integration
- Manual section editing
- Multi-language support
- Mobile app
- Collaborative briefings
- Integration with flight planning software

## License

MIT License - See LICENSE file for details

## Support

For issues and feature requests, please create an issue in the GitHub repository.

## Acknowledgments

- Built with FastAPI, Next.js, and OpenAI
- Designed for aviation professionals
- MVP for demonstration purposes

---

**Note:** This is a demonstration MVP. Always verify critical flight information with official sources before flight operations.
