import { useState, useEffect } from 'react'
import { skillsService } from '../services/skillsService'

interface SkillsAutocompleteProps {
  selectedSkills: string[]
  onSkillsChange: (skills: string[]) => void
}

export default function SkillsAutocomplete({
  selectedSkills,
  onSkillsChange
}: SkillsAutocompleteProps) {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [allSkills, setAllSkills] = useState<string[]>([])

  useEffect(() => {
    loadAllSkills()
  }, [])

  const loadAllSkills = async () => {
    const result = await skillsService.getAvailableSkills()
    if (result.success) {
      setAllSkills(result.data)
    }
  }

  const handleSearch = async (value: string) => {
    setQuery(value)
    
    if (value.length < 2) {
      setSuggestions(allSkills)
      return
    }

    const result = await skillsService.searchSkills(value)
    if (result.success) {
      setSuggestions(
        result.data.filter((s: string) => !selectedSkills.includes(s))
      )
    }
  }

  const addSkill = (skill: string) => {
    if (!selectedSkills.includes(skill)) {
      onSkillsChange([...selectedSkills, skill])
    }
    setQuery('')
    setSuggestions([])
  }

  const removeSkill = (skill: string) => {
    onSkillsChange(selectedSkills.filter(s => s !== skill))
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm font-semibold text-gray-900">
        Skills
      </label>

      {/* Input */}
      <div className="relative">
        <input
          type="text"
          placeholder="Search and add skills..."
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
            {suggestions.slice(0, 10).map((skill) => (
              <button
                key={skill}
                onClick={() => addSkill(skill)}
                className="w-full text-left px-3 py-2 hover:bg-gray-100 transition"
              >
                {skill}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Selected Skills */}
      <div className="flex flex-wrap gap-2">
        {selectedSkills.map((skill) => (
          <div
            key={skill}
            className="bg-blue-100 border border-blue-300 rounded-full px-3 py-1 flex items-center gap-2"
          >
            <span className="text-sm font-medium text-blue-900">{skill}</span>
            <button
              onClick={() => removeSkill(skill)}
              className="text-blue-600 hover:text-blue-800 font-bold"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
