'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import FileUpload from '@/components/FileUpload'
import LoadingSpinner from '@/components/LoadingSpinner'
import { uploadPDF, analyzePDF } from '@/lib/api'
import { Plane, AlertCircle } from 'lucide-react'

export default function HomePage() {
  const router = useRouter()
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [processingStep, setProcessingStep] = useState<string>('')

  const handleFileSelect = async (file: File) => {
    setError(null)
    setIsProcessing(true)

    try {
      // Step 1: Upload
      setProcessingStep('Uploading flight plan...')
      const uploadResponse = await uploadPDF(file)
      console.log('Upload successful:', uploadResponse)

      // Step 2: Analyze
      setProcessingStep('Analyzing with AI (this may take up to 30 seconds)...')
      const analysisResponse = await analyzePDF(uploadResponse.file_id)
      console.log('Analysis successful:', analysisResponse)

      // Store analysis data in sessionStorage for the next page
      sessionStorage.setItem('analysisData', JSON.stringify(analysisResponse))

      // Navigate to selection page
      router.push('/select')
    } catch (err: any) {
      console.error('Error processing file:', err)
      setError(
        err.response?.data?.detail ||
          err.message ||
          'Failed to process flight plan. Please try again.'
      )
      setIsProcessing(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3">
            <Plane className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">FlightBrief AI</h1>
              <p className="text-sm text-gray-600">
                AI-Powered Flight Plan Analysis & Briefing
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
        <div className="w-full max-w-4xl">
          {!isProcessing ? (
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Upload Your Flight Plan
              </h2>
              <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                Upload your flight plan PDF and let our AI analyze it for you. Select the
                sections you need and generate a customized briefing in seconds.
              </p>

              <FileUpload onFileSelect={handleFileSelect} isUploading={isProcessing} />

              {/* Features */}
              <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <div className="text-2xl mb-3">📄</div>
                  <h3 className="font-semibold text-gray-900 mb-2">Smart Parsing</h3>
                  <p className="text-sm text-gray-600">
                    Automatically identifies OFP, NOTAMs, weather, fuel planning, and more
                  </p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <div className="text-2xl mb-3">🤖</div>
                  <h3 className="font-semibold text-gray-900 mb-2">AI Analysis</h3>
                  <p className="text-sm text-gray-600">
                    GPT-4 evaluates section criticality and provides concise summaries
                  </p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <div className="text-2xl mb-3">✈️</div>
                  <h3 className="font-semibold text-gray-900 mb-2">Custom Briefing</h3>
                  <p className="text-sm text-gray-600">
                    Generate a tailored PDF with only the sections you need
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-lg p-8">
              <LoadingSpinner message={processingStep} />
            </div>
          )}

          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Error</p>
                <p className="text-sm text-red-800 mt-1">{error}</p>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            FlightBrief AI MVP v0.1 - For demonstration purposes only
          </p>
        </div>
      </footer>
    </div>
  )
}
