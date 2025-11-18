'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import LoadingSpinner from '@/components/LoadingSpinner'
import { fetchSimbriefPlan } from '@/lib/api'
import { Plane, AlertCircle } from 'lucide-react'

export default function HomePage() {
  const router = useRouter()
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [processingStep, setProcessingStep] = useState<string>('')
  const [username, setUsername] = useState('')

  const handleSimbriefFetch = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!username.trim()) {
      setError('Please enter your SimBrief username')
      return
    }

    setError(null)
    setIsProcessing(true)

    try {
      // Fetch from SimBrief
      setProcessingStep('Fetching flight plan from SimBrief...')
      const analysisResponse = await fetchSimbriefPlan(username.trim())
      console.log('SimBrief fetch successful:', analysisResponse)

      // Store analysis data in sessionStorage for the next page
      sessionStorage.setItem('analysisData', JSON.stringify(analysisResponse))

      // Navigate to briefing dashboard
      router.push('/briefing')
    } catch (err: any) {
      console.error('Error fetching SimBrief plan:', err)
      setError(
        err.response?.data?.detail ||
          err.message ||
          'Failed to fetch flight plan from SimBrief. Please check your username and try again.'
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
              <h1 className="text-3xl font-bold text-gray-900">flyt.ai</h1>
              <p className="text-sm text-gray-600">
                AI-Powered Flight Briefing System
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
                Load Your Flight Plan from SimBrief
              </h2>
              <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                Enter your SimBrief username to fetch your latest flight plan and view a comprehensive flight briefing with all the details you need.
              </p>

              {/* SimBrief Username Form */}
              <form onSubmit={handleSimbriefFetch} className="max-w-md mx-auto mb-8">
                <div className="bg-white p-8 rounded-lg shadow-lg border">
                  <label htmlFor="username" className="block text-left text-sm font-medium text-gray-700 mb-2">
                    SimBrief Username
                  </label>
                  <input
                    type="text"
                    id="username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter your SimBrief username"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                    disabled={isProcessing}
                  />
                  <button
                    type="submit"
                    disabled={isProcessing || !username.trim()}
                    className="w-full mt-4 bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                  >
                    Fetch Flight Plan
                  </button>
                  <p className="text-xs text-gray-500 mt-3 text-left">
                    Don't have a SimBrief account? <a href="https://www.simbrief.com/system/register.php" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Register here</a>
                  </p>
                </div>
              </form>

              {/* Features */}
              <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <div className="text-2xl mb-3">🌐</div>
                  <h3 className="font-semibold text-gray-900 mb-2">SimBrief Integration</h3>
                  <p className="text-sm text-gray-600">
                    Directly fetch your flight plans from SimBrief with all the data you need
                  </p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <div className="text-2xl mb-3">📊</div>
                  <h3 className="font-semibold text-gray-900 mb-2">Comprehensive Dashboard</h3>
                  <p className="text-sm text-gray-600">
                    View flight data, route maps, weather, load sheet, and performance info
                  </p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <div className="text-2xl mb-3">✈️</div>
                  <h3 className="font-semibold text-gray-900 mb-2">Professional Briefing</h3>
                  <p className="text-sm text-gray-600">
                    Get a clean, organized briefing with all essential flight information
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
            flyt.ai v0.1 - Professional Flight Briefing System
          </p>
        </div>
      </footer>
    </div>
  )
}
