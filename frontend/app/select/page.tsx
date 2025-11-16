'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import SectionSelector from '@/components/SectionSelector'
import LoadingSpinner from '@/components/LoadingSpinner'
import {
  AnalysisResponse,
  generateBriefing,
  downloadBriefing,
  SectionSelection,
} from '@/lib/api'
import { ArrowLeft, Download, AlertCircle, CheckCircle } from 'lucide-react'

export default function SelectPage() {
  const router = useRouter()
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null)
  const [selectedSections, setSelectedSections] = useState<Record<string, boolean>>({})
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null)

  useEffect(() => {
    // Load analysis data from sessionStorage
    const data = sessionStorage.getItem('analysisData')
    if (!data) {
      router.push('/')
      return
    }

    try {
      const parsed = JSON.parse(data)
      setAnalysisData(parsed)
    } catch (err) {
      console.error('Failed to parse analysis data:', err)
      router.push('/')
    }
  }, [router])

  const handleGenerateBriefing = async () => {
    if (!analysisData) return

    setError(null)
    setIsGenerating(true)

    try {
      // Convert selected sections to API format
      const selections: SectionSelection[] = analysisData.sections.map((section) => ({
        section_name: section.section_name,
        selected: selectedSections[section.section_name] ?? true,
      }))

      // Check if at least one section is selected
      const hasSelection = selections.some((s) => s.selected)
      if (!hasSelection) {
        setError('Please select at least one section')
        setIsGenerating(false)
        return
      }

      // Generate briefing
      const response = await generateBriefing({
        file_id: analysisData.file_id,
        selected_sections: selections,
        briefing_type: 'custom',
      })

      // Set download URL
      const url = downloadBriefing(analysisData.file_id)
      setDownloadUrl(url)

      // Auto-download
      window.location.href = url
    } catch (err: any) {
      console.error('Error generating briefing:', err)
      setError(
        err.response?.data?.detail ||
          err.message ||
          'Failed to generate briefing. Please try again.'
      )
    } finally {
      setIsGenerating(false)
    }
  }

  if (!analysisData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner message="Loading analysis data..." />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => router.push('/')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="text-sm font-medium">Back</span>
            </button>
            <h1 className="text-xl font-bold text-gray-900">Select Sections</h1>
            <div className="w-20"></div> {/* Spacer for centering */}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Card */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Analysis Summary</h2>
          <p className="text-gray-700 leading-relaxed">{analysisData.analysis_summary}</p>
          <div className="mt-4 flex items-center gap-4 text-sm text-gray-600">
            <span>
              <strong>Total Sections:</strong> {analysisData.sections.length}
            </span>
            <span>
              <strong>Total Pages:</strong> {analysisData.total_pages}
            </span>
          </div>
        </div>

        {/* Section Selector */}
        <SectionSelector
          sections={analysisData.sections}
          onSelectionChange={setSelectedSections}
        />

        {/* Actions */}
        <div className="mt-8 flex flex-col sm:flex-row gap-4 items-center justify-center">
          <button
            onClick={handleGenerateBriefing}
            disabled={isGenerating}
            className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isGenerating ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Generating Briefing...</span>
              </>
            ) : (
              <>
                <Download className="w-5 h-5" />
                <span>Generate & Download Briefing</span>
              </>
            )}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-6 max-w-2xl mx-auto p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-900">Error</p>
              <p className="text-sm text-red-800 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Success Message */}
        {downloadUrl && (
          <div className="mt-6 max-w-2xl mx-auto p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-green-900">Success!</p>
              <p className="text-sm text-green-800 mt-1">
                Your briefing has been generated and should download automatically.
              </p>
              <a
                href={downloadUrl}
                className="text-sm text-green-700 underline hover:text-green-900 mt-2 inline-block"
              >
                Click here if download doesn&apos;t start
              </a>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
