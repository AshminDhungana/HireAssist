import { useState } from 'react'
import { Button, Select, Card, Table, Badge } from '../components/ui'

interface MatchResult {
  id: string
  candidateName: string
  score: number
  skillMatch: number
  experienceMatch: number
  educationMatch: number
  status: 'excellent' | 'good' | 'fair' | 'poor'
}

export default function JobMatchingPage() {
  const [selectedJob, setSelectedJob] = useState('')
  const [matchResults, setMatchResults] = useState<MatchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [filterScore, setFilterScore] = useState(0)

  // Mock data - replace with API calls later
  const jobs = [
    { value: '1', label: 'Senior React Developer' },
    { value: '2', label: 'Full Stack Engineer' },
    { value: '3', label: 'Data Science Manager' },
  ]

  const mockResults: MatchResult[] = [
    {
      id: '1',
      candidateName: 'John Doe',
      score: 92,
      skillMatch: 95,
      experienceMatch: 88,
      educationMatch: 90,
      status: 'excellent',
    },
    {
      id: '2',
      candidateName: 'Jane Smith',
      score: 85,
      skillMatch: 88,
      experienceMatch: 82,
      educationMatch: 85,
      status: 'good',
    },
    {
      id: '3',
      candidateName: 'Mike Johnson',
      score: 72,
      skillMatch: 75,
      experienceMatch: 70,
      educationMatch: 72,
      status: 'fair',
    },
  ]

  const handleMatchCandidates = () => {
    if (!selectedJob) {
      alert('Please select a job')
      return
    }

    setIsLoading(true)
    // Simulate API call
    setTimeout(() => {
      setMatchResults(mockResults)
      setIsLoading(false)
    }, 1500)
  }

  const filteredResults = matchResults.filter((r) => r.score >= filterScore)

  const statusColors = {
    excellent: 'success',
    good: 'primary',
    fair: 'warning',
    poor: 'danger',
  } as const

  const tableColumns = [
    { key: 'candidateName', label: 'Candidate Name' },
    { key: 'score', label: 'Overall Score' },
    { key: 'skillMatch', label: 'Skills' },
    { key: 'experienceMatch', label: 'Experience' },
    { key: 'educationMatch', label: 'Education' },
    { key: 'status', label: 'Status' },
  ]

  const tableData = filteredResults.map((r) => ({
    ...r,
    score: `${r.score}%`,
    skillMatch: `${r.skillMatch}%`,
    experienceMatch: `${r.experienceMatch}%`,
    educationMatch: `${r.educationMatch}%`,
    status: <Badge variant={statusColors[r.status]}>{r.status}</Badge>,
  }))

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <section className="overflow-hidden rounded-3xl bg-white shadow-2xl ring-1 ring-gray-200">
        <div className="p-8 sm:p-12 text-center text-white bg-gradient-to-br from-green-600 via-teal-600 to-cyan-600">
          <h2 className="mb-3 text-4xl font-extrabold tracking-tight drop-shadow-md sm:text-5xl">
            🎯 Job-to-Resume Matching
          </h2>
          <p className="text-lg font-medium text-green-100 opacity-90 sm:text-xl">
            Match resumes to job descriptions and find the best candidates
          </p>
        </div>

        {/* Matching Controls */}
        <div className="p-8 sm:p-12">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-6">
            <Select
              label="Select Job"
              value={selectedJob}
              onChange={(e) => setSelectedJob(e.target.value)}
              options={jobs}
            />
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Minimum Score: {filterScore}%
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={filterScore}
                onChange={(e) => setFilterScore(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          </div>

          <Button
            onClick={handleMatchCandidates}
            isLoading={isLoading}
            className="w-full sm:w-auto"
          >
            🔍 Find Matching Candidates
          </Button>
        </div>
      </section>

      {/* Results Section */}
      {matchResults.length > 0 && (
        <section className="space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <Card>
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">
                  {matchResults.length}
                </div>
                <p className="text-gray-600 font-semibold">Total Candidates</p>
              </div>
            </Card>

            <Card>
              <div className="text-center">
                <div className="text-4xl font-bold text-green-600 mb-2">
                  {matchResults.filter((r) => r.score >= 80).length}
                </div>
                <p className="text-gray-600 font-semibold">Excellent Matches</p>
              </div>
            </Card>

            <Card>
              <div className="text-center">
                <div className="text-4xl font-bold text-yellow-600 mb-2">
                  {(
                    matchResults.reduce((acc, r) => acc + r.score, 0) /
                    matchResults.length
                  ).toFixed(1)}
                  %
                </div>
                <p className="text-gray-600 font-semibold">Average Score</p>
              </div>
            </Card>
          </div>

          {/* Results Table */}
          <Card>
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              Candidate Matches (Filtered: {filteredResults.length})
            </h3>
            <Table columns={tableColumns} data={tableData} />
          </Card>

          {/* Top Candidate Detail */}
          {filteredResults.length > 0 && (
            <Card className="bg-gradient-to-br from-green-50 to-teal-50 border-t-4 border-green-600">
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                🏆 Top Match: {filteredResults[0].candidateName}
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Overall Score</p>
                  <p className="text-2xl font-bold text-green-600">
                    {filteredResults[0].score}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Skills Match</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {filteredResults[0].skillMatch}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Experience</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {filteredResults[0].experienceMatch}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Education</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {filteredResults[0].educationMatch}%
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
                <Button variant="primary">📧 Send Offer</Button>
                <Button variant="secondary">📄 View Resume</Button>
              </div>
            </Card>
          )}

          {filteredResults.length === 0 && matchResults.length > 0 && (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <p className="text-gray-600 text-lg">
                No candidates match the minimum score filter. Try lowering the threshold.
              </p>
            </div>
          )}
        </section>
      )}

      {/* Empty State */}
      {matchResults.length === 0 && (
        <Card className="text-center py-12">
          <div className="text-6xl mb-4">🔍</div>
          <p className="text-gray-600 text-lg">
            Select a job and click "Find Matching Candidates" to see results
          </p>
        </Card>
      )}
    </div>
  )
}
