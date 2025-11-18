'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  AnalysisResponse,
  generateBriefing,
  downloadBriefing,
  SectionSelection,
} from '@/lib/api'
import { ArrowLeft, Download, AlertCircle, CheckCircle, Plane, FileText } from 'lucide-react'
import LoadingSpinner from '@/components/LoadingSpinner'
import CriticalityBadge from '@/components/CriticalityBadge'
import { CheckSquare, Square } from 'lucide-react'

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

      // Initialize all sections as selected
      const initial: Record<string, boolean> = {}
      parsed.sections.forEach((section: any) => {
        initial[section.section_name] = true
      })
      setSelectedSections(initial)
    } catch (err) {
      console.error('Failed to parse analysis data:', err)
      router.push('/')
    }
  }, [router])

  const handleToggle = (sectionName: string) => {
    setSelectedSections(prev => ({
      ...prev,
      [sectionName]: !prev[sectionName]
    }))
  }

  const handleSelectAll = () => {
    const newSelected: Record<string, boolean> = {}
    analysisData?.sections.forEach((section) => {
      newSelected[section.section_name] = true
    })
    setSelectedSections(newSelected)
  }

  const handleSelectRecommended = () => {
    const newSelected: Record<string, boolean> = {}
    analysisData?.sections.forEach((section) => {
      newSelected[section.section_name] =
        section.criticality === 'CRITICAL' || section.criticality === 'WARNING'
    })
    setSelectedSections(newSelected)
  }

  const handleSelectMinimal = () => {
    const newSelected: Record<string, boolean> = {}
    analysisData?.sections.forEach((section) => {
      newSelected[section.section_name] = section.criticality === 'CRITICAL'
    })
    setSelectedSections(newSelected)
  }

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
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
        <LoadingSpinner message="Loading sections..." />
      </div>
    )
  }

  const selectedCount = Object.values(selectedSections).filter(Boolean).length

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => router.push('/briefing')}
              className="flex items-center gap-2 text-blue-300 hover:text-blue-100 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="text-sm font-medium">Back to Briefing</span>
            </button>
            <div className="flex items-center gap-3">
              <FileText className="w-6 h-6 text-blue-400" />
              <div>
                <h1 className="text-xl font-bold text-white">Section Selection</h1>
                <p className="text-sm text-blue-300">Choose sections for your PDF</p>
              </div>
            </div>
            <div className="w-32"></div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Selection Buttons */}
        <div className="mb-6 flex flex-wrap items-center gap-3">
          <button
            onClick={handleSelectAll}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-medium shadow-lg"
          >
            Select All
          </button>
          <button
            onClick={handleSelectRecommended}
            className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors text-sm font-medium shadow-lg"
          >
            Recommended
          </button>
          <button
            onClick={handleSelectMinimal}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors text-sm font-medium shadow-lg"
          >
            Minimal
          </button>
          <div className="ml-auto flex items-center gap-2 text-sm text-blue-200 bg-white/5 px-4 py-2 rounded-lg border border-white/10">
            <CheckSquare className="w-4 h-4" />
            <span className="font-medium">
              {selectedCount} of {analysisData.sections.length} selected
            </span>
          </div>
        </div>

        {/* Sections Table */}
        <div className="bg-white/10 backdrop-blur-md rounded-xl overflow-hidden border border-white/20 shadow-2xl mb-8">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-black/40 border-b border-white/10">
                <tr>
                  <th className="px-4 py-4 text-left text-sm font-semibold text-white w-12"></th>
                  <th className="px-4 py-4 text-left text-sm font-semibold text-white">Section</th>
                  <th className="px-4 py-4 text-left text-sm font-semibold text-white w-32">Priority</th>
                  <th className="px-4 py-4 text-left text-sm font-semibold text-white">Summary</th>
                  <th className="px-4 py-4 text-left text-sm font-semibold text-white w-24">Pages</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {analysisData.sections.map((section, index) => (
                  <tr
                    key={section.section_name}
                    className={`${
                      selectedSections[section.section_name]
                        ? 'bg-blue-500/10 hover:bg-blue-500/20'
                        : 'bg-transparent hover:bg-white/5'
                    } transition-colors cursor-pointer`}
                    onClick={() => handleToggle(section.section_name)}
                  >
                    <td className="px-4 py-4">
                      <button
                        className="focus:outline-none"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleToggle(section.section_name)
                        }}
                      >
                        {selectedSections[section.section_name] ? (
                          <CheckSquare className="w-5 h-5 text-blue-400" />
                        ) : (
                          <Square className="w-5 h-5 text-gray-500" />
                        )}
                      </button>
                    </td>
                    <td className="px-4 py-4">
                      <span className="font-medium text-white">
                        {section.section_name}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <CriticalityBadge level={section.criticality} />
                    </td>
                    <td className="px-4 py-4 text-sm text-gray-300">
                      {section.one_line_summary}
                    </td>
                    <td className="px-4 py-4 text-sm text-gray-400 font-mono">
                      {section.pages.length > 3
                        ? `${section.pages.slice(0, 3).join(', ')}...`
                        : section.pages.join(', ')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Generate Button */}
        <div className="flex justify-center mb-6">
          <button
            onClick={handleGenerateBriefing}
            disabled={isGenerating || selectedCount === 0}
            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl font-semibold text-lg shadow-2xl hover:shadow-blue-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3"
          >
            {isGenerating ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Generating PDF...</span>
              </>
            ) : (
              <>
                <Download className="w-5 h-5" />
                <span>Generate & Download PDF</span>
              </>
            )}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-2xl mx-auto p-4 bg-red-500/20 backdrop-blur-md border border-red-500/50 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-200">Error</p>
              <p className="text-sm text-red-300 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Success Message */}
        {downloadUrl && (
          <div className="max-w-2xl mx-auto p-4 bg-green-500/20 backdrop-blur-md border border-green-500/50 rounded-lg flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-green-200">Success!</p>
              <p className="text-sm text-green-300 mt-1">
                Your briefing has been generated and should download automatically.
              </p>
              <a
                href={downloadUrl}
                className="text-sm text-green-400 underline hover:text-green-300 mt-2 inline-block"
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
