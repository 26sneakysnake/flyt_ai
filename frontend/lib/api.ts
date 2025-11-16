import axios from 'axios'
import { API_URL } from './utils'

export interface FlightPlanSection {
  section_name: string
  criticality: 'CRITICAL' | 'WARNING' | 'NORMAL' | 'INFO'
  one_line_summary: string
  pages: number[]
}

export interface UploadResponse {
  file_id: string
  filename: string
  total_pages: number
  message: string
}

export interface FlightData {
  flight_number?: string | null
  aircraft_type?: string | null
  aircraft_registration?: string | null
  airline?: string | null
  airline_icao?: string | null
  departure_icao?: string | null
  departure_name?: string | null
  arrival_icao?: string | null
  arrival_name?: string | null
  alternate_icao?: string | null
  departure_time?: string | null
  arrival_time?: string | null
  flight_time?: string | null
  route?: string | null
  cruise_altitude?: string | null
  fuel_planned?: string | null
}

export interface AnalysisResponse {
  file_id: string
  sections: FlightPlanSection[]
  total_pages: number
  analysis_summary: string
  flight_data?: FlightData | null
}

export interface SectionSelection {
  section_name: string
  selected: boolean
}

export interface GenerateRequest {
  file_id: string
  selected_sections: SectionSelection[]
  briefing_type?: string
}

export interface GenerateResponse {
  file_id: string
  download_url: string
  included_sections: string[]
  total_pages: number
}

const api = axios.create({
  baseURL: `${API_URL}/api`,
  timeout: 60000, // 60 second timeout for AI processing
})

export const uploadPDF = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

export const analyzePDF = async (fileId: string): Promise<AnalysisResponse> => {
  const response = await api.post<AnalysisResponse>('/analyze', {
    file_id: fileId,
  })

  return response.data
}

export const generateBriefing = async (
  request: GenerateRequest
): Promise<GenerateResponse> => {
  const response = await api.post<GenerateResponse>('/generate', request)

  return response.data
}

export const downloadBriefing = (fileId: string): string => {
  return `${API_URL}/api/download/${fileId}`
}
