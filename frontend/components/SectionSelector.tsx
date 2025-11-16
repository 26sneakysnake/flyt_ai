'use client'

import { useState } from 'react'
import { FlightPlanSection } from '@/lib/api'
import CriticalityBadge from './CriticalityBadge'
import { CheckSquare, Square } from 'lucide-react'

interface SectionSelectorProps {
  sections: FlightPlanSection[]
  onSelectionChange: (selectedSections: Record<string, boolean>) => void
}

export default function SectionSelector({
  sections,
  onSelectionChange,
}: SectionSelectorProps) {
  // Initialize all sections as selected
  const [selected, setSelected] = useState<Record<string, boolean>>(() => {
    const initial: Record<string, boolean> = {}
    sections.forEach((section) => {
      initial[section.section_name] = true
    })
    return initial
  })

  const handleToggle = (sectionName: string) => {
    const newSelected = {
      ...selected,
      [sectionName]: !selected[sectionName],
    }
    setSelected(newSelected)
    onSelectionChange(newSelected)
  }

  const handleSelectAll = () => {
    const newSelected: Record<string, boolean> = {}
    sections.forEach((section) => {
      newSelected[section.section_name] = true
    })
    setSelected(newSelected)
    onSelectionChange(newSelected)
  }

  const handleSelectRecommended = () => {
    const newSelected: Record<string, boolean> = {}
    sections.forEach((section) => {
      // Select CRITICAL and WARNING sections
      newSelected[section.section_name] =
        section.criticality === 'CRITICAL' || section.criticality === 'WARNING'
    })
    setSelected(newSelected)
    onSelectionChange(newSelected)
  }

  const handleSelectMinimal = () => {
    const newSelected: Record<string, boolean> = {}
    sections.forEach((section) => {
      // Select only CRITICAL sections
      newSelected[section.section_name] = section.criticality === 'CRITICAL'
    })
    setSelected(newSelected)
    onSelectionChange(newSelected)
  }

  const selectedCount = Object.values(selected).filter(Boolean).length

  return (
    <div className="w-full">
      {/* Quick selection buttons */}
      <div className="mb-6 flex flex-wrap gap-3">
        <button
          onClick={handleSelectAll}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
        >
          Select All
        </button>
        <button
          onClick={handleSelectRecommended}
          className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm font-medium"
        >
          Recommended Selection
        </button>
        <button
          onClick={handleSelectMinimal}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
        >
          Minimal Briefing
        </button>
        <div className="ml-auto flex items-center gap-2 text-sm text-gray-600">
          <span className="font-medium">
            {selectedCount} of {sections.length} selected
          </span>
        </div>
      </div>

      {/* Sections table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-800 text-white">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold w-12"></th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Section</th>
                <th className="px-4 py-3 text-left text-sm font-semibold w-32">Priority</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Summary</th>
                <th className="px-4 py-3 text-left text-sm font-semibold w-24">Pages</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {sections.map((section, index) => (
                <tr
                  key={section.section_name}
                  className={`${
                    index % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                  } hover:bg-blue-50 transition-colors cursor-pointer`}
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
                      {selected[section.section_name] ? (
                        <CheckSquare className="w-5 h-5 text-blue-600" />
                      ) : (
                        <Square className="w-5 h-5 text-gray-400" />
                      )}
                    </button>
                  </td>
                  <td className="px-4 py-4">
                    <span className="font-medium text-gray-900">
                      {section.section_name}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <CriticalityBadge level={section.criticality} />
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-600">
                    {section.one_line_summary}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-500">
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
    </div>
  )
}
