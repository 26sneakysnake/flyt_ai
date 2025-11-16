'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { AnalysisResponse, FlightData } from '@/lib/api'
import {
  Plane,
  MapPin,
  Clock,
  Fuel,
  CloudRain,
  ArrowRight,
  Navigation,
  Settings,
  AlertCircle
} from 'lucide-react'
import LoadingSpinner from '@/components/LoadingSpinner'

export default function BriefingPage() {
  const router = useRouter()
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null)
  const [loading, setLoading] = useState(true)

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
      setLoading(false)
    } catch (err) {
      console.error('Failed to parse analysis data:', err)
      router.push('/')
    }
  }, [router])

  const handleContinueToSections = () => {
    router.push('/select')
  }

  if (loading || !analysisData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
        <LoadingSpinner message="Loading briefing..." />
      </div>
    )
  }

  const flight = analysisData.flight_data || {}

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Plane className="w-8 h-8 text-blue-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">flyt.ai</h1>
                <p className="text-sm text-blue-300">Flight Briefing Dashboard</p>
              </div>
            </div>
            <button
              onClick={handleContinueToSections}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              Continue to Sections
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Dashboard */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Flight Header Card */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-8 mb-6 shadow-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-4xl font-bold text-white mb-2">
                {flight.flight_number || 'Flight Plan'}
              </h2>
              <p className="text-blue-100 text-lg">
                {flight.airline || 'Airline'} • {flight.aircraft_type || 'Aircraft Type'}
              </p>
            </div>
            <div className="text-right">
              <div className="text-blue-100 text-sm">Registration</div>
              <div className="text-white text-2xl font-mono font-bold">
                {flight.aircraft_registration || 'N/A'}
              </div>
            </div>
          </div>
        </div>

        {/* Route Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Departure */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center">
                <MapPin className="w-6 h-6 text-green-400" />
              </div>
              <div>
                <div className="text-gray-300 text-sm">Departure</div>
                <div className="text-white text-2xl font-bold">{flight.departure_icao || 'XXXX'}</div>
              </div>
            </div>
            <p className="text-gray-300 text-sm">{flight.departure_name || 'Departure Airport'}</p>
            <div className="mt-4 flex items-center gap-2 text-blue-300">
              <Clock className="w-4 h-4" />
              <span className="font-mono">{flight.departure_time || '--:-- UTC'}</span>
            </div>
          </div>

          {/* Flight Info */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center">
                <Navigation className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <div className="text-gray-300 text-sm">Flight Time</div>
                <div className="text-white text-2xl font-bold">{flight.flight_time || '--:--'}</div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Cruise Altitude</span>
                <span className="text-blue-300 font-mono">{flight.cruise_altitude || 'FL---'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Fuel Planned</span>
                <span className="text-blue-300 font-mono">{flight.fuel_planned || '--- KG'}</span>
              </div>
            </div>
          </div>

          {/* Arrival */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-orange-500/20 rounded-full flex items-center justify-center">
                <MapPin className="w-6 h-6 text-orange-400" />
              </div>
              <div>
                <div className="text-gray-300 text-sm">Arrival</div>
                <div className="text-white text-2xl font-bold">{flight.arrival_icao || 'XXXX'}</div>
              </div>
            </div>
            <p className="text-gray-300 text-sm">{flight.arrival_name || 'Arrival Airport'}</p>
            <div className="mt-4 flex items-center gap-2 text-orange-300">
              <Clock className="w-4 h-4" />
              <span className="font-mono">{flight.arrival_time || '--:-- UTC'}</span>
            </div>
          </div>
        </div>

        {/* Maps and Aircraft Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Route Map */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl overflow-hidden border border-white/20">
            <div className="bg-black/30 px-6 py-4 border-b border-white/10">
              <h3 className="text-white font-semibold flex items-center gap-2">
                <Navigation className="w-5 h-5 text-blue-400" />
                Flight Route
              </h3>
            </div>
            <div className="aspect-video bg-gradient-to-br from-blue-950 to-slate-950 flex items-center justify-center relative overflow-hidden">
              {/* Simple route visualization */}
              <div className="absolute inset-0 opacity-20">
                <svg className="w-full h-full" viewBox="0 0 800 400">
                  <defs>
                    <linearGradient id="routeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" style={{ stopColor: '#10b981', stopOpacity: 1 }} />
                      <stop offset="100%" style={{ stopColor: '#f97316', stopOpacity: 1 }} />
                    </linearGradient>
                  </defs>
                  <path
                    d="M 100,200 Q 400,100 700,200"
                    fill="none"
                    stroke="url(#routeGradient)"
                    strokeWidth="4"
                    strokeDasharray="10,5"
                  />
                  <circle cx="100" cy="200" r="8" fill="#10b981" />
                  <circle cx="700" cy="200" r="8" fill="#f97316" />
                </svg>
              </div>
              <div className="text-center z-10">
                <MapPin className="w-16 h-16 text-blue-400 mx-auto mb-4" />
                <p className="text-gray-300 text-sm">
                  {flight.departure_icao && flight.arrival_icao
                    ? `${flight.departure_icao} → ${flight.arrival_icao}`
                    : 'Route Map Visualization'}
                </p>
                <p className="text-gray-500 text-xs mt-2">Interactive map coming soon</p>
              </div>
            </div>
          </div>

          {/* Aircraft Image */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl overflow-hidden border border-white/20">
            <div className="bg-black/30 px-6 py-4 border-b border-white/10">
              <h3 className="text-white font-semibold flex items-center gap-2">
                <Plane className="w-5 h-5 text-blue-400" />
                Aircraft
              </h3>
            </div>
            <div className="aspect-video bg-gradient-to-br from-slate-950 to-blue-950 flex items-center justify-center">
              <div className="text-center">
                <Plane className="w-24 h-24 text-blue-400 mx-auto mb-4 rotate-45" />
                <p className="text-white text-lg font-bold">{flight.aircraft_type || 'Aircraft Type'}</p>
                <p className="text-gray-400 text-sm">{flight.airline || 'Airline'}</p>
                <p className="text-gray-500 text-xs mt-4">Aircraft image with livery coming soon</p>
              </div>
            </div>
          </div>
        </div>

        {/* Wind Map (Placeholder) */}
        <div className="bg-white/10 backdrop-blur-md rounded-xl overflow-hidden border border-white/20 mb-6">
          <div className="bg-black/30 px-6 py-4 border-b border-white/10">
            <h3 className="text-white font-semibold flex items-center gap-2">
              <CloudRain className="w-5 h-5 text-blue-400" />
              Wind Analysis
            </h3>
          </div>
          <div className="aspect-[21/9] bg-gradient-to-br from-indigo-950 to-purple-950 flex items-center justify-center">
            <div className="text-center">
              <CloudRain className="w-16 h-16 text-purple-400 mx-auto mb-4" />
              <p className="text-gray-300">Wind pattern visualization along route</p>
              <p className="text-gray-500 text-sm mt-2">Real-time wind data integration coming soon</p>
            </div>
          </div>
        </div>

        {/* Route Details */}
        {flight.route && (
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 mb-6">
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              <Navigation className="w-5 h-5 text-blue-400" />
              Flight Route
            </h3>
            <div className="bg-black/30 rounded-lg p-4 font-mono text-sm text-blue-300 overflow-x-auto">
              {flight.route}
            </div>
          </div>
        )}

        {/* AI Summary */}
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <Settings className="w-5 h-5 text-blue-400" />
            AI Analysis Summary
          </h3>
          <p className="text-gray-300 leading-relaxed">{analysisData.analysis_summary}</p>
        </div>

        {/* Continue Button (Bottom) */}
        <div className="mt-8 flex justify-center">
          <button
            onClick={handleContinueToSections}
            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl font-semibold text-lg shadow-xl hover:shadow-2xl transition-all flex items-center gap-3"
          >
            Continue to Section Selection
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </main>
    </div>
  )
}
