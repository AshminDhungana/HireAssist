import { useState, useEffect } from 'react'
import { Button, Select, Card, Badge } from '../components/ui'
import { jobService } from '../services/jobService'
import { matchingService } from '../services/matchingService'

interface MatchResult {
  id: string
  candidateName: string
  resumeFilename: string
  score: number
  skillMatch: number
  experienceMatch: number
  educationMatch: number
  status: 'excellent' | 'good' | 'fair' | 'poor'
}

export default function JobMatchingPage() {
  const [jobs, setJobs] = useState<{ value: string; label: string }[]>([])
  const [selectedJob, setSelectedJob] = useState('')
  const [matchResults, setMatchResults] = useState<MatchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [jobsLoading, setJobsLoading] = useState(true)
  const [filterScore, setFilterScore] = useState(0)
  const [error, setError] = useState<string | null>(null)

  // Load jobs on mount
  useEffect(() => {
    loadJobs()
  }, [])

  const loadJobs = async () => {
    setJobsLoading(true)
    setError(null)
    try {
      const result = await jobService.listJobs(0, 100)
      if (result.success && result.data.jobs) {
        const jobOptions = result.data.jobs.map((job: any) => ({
          value: job.id,
          label: job.title
        }))
        setJobs(jobOptions)
      } else {
        setError('Failed to load jobs')
      }
    } catch (err) {
      setError('Error loading jobs')
      console.error(err)
    } finally {
      setJobsLoading(false)
    }
  }

  const handleMatchCandidates = async () => {
    if (!selectedJob) {
      alert('Please select a job')
      return
    }

    setIsLoading(true)
    setError(null)
    try {
      // Get match results from backend
      const result = await matchingService.getMatchResults(selectedJob, 0, 100, 0)
      
      if (result.success && result.data.results) {
        // Transform API response to match UI interface
        const transformedResults: MatchResult[] = result.data.results.map((r: any) => ({
          id: r.screening_result_id,
          candidateName: r.candidate_name,
          resumeFilename: r.resume_filename,
          score: Math.round(r.overall_score * 100),
          skillMatch: Math.round(r.skill_match_score * 100),
          experienceMatch: Math.round(r.experience_score * 100),
          educationMatch: Math.round(r.education_score * 100),
          status:
            r.overall_score >= 0.8 ? 'excellent' :
            r.overall_score >= 0.6 ? 'good' :
            r.overall_score >= 0.4 ? 'fair' : 'poor'
        }))
        
        // Sort by score descending
        transformedResults.sort((a, b) => b.score - a.score)
        setMatchResults(transformedResults)
      } else {
        setError(result.error || 'Failed to get match results')
      }
    } catch (err) {
      setError('Error matching candidates')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
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

  // const tableData = filteredResults.map((r) => ({
  //   ...r,
  //   score: `${r.score}%`,
  //   skillMatch: `${r.skillMatch}%`,
  //   experienceMatch: `${r.experienceMatch}%`,
  //   educationMatch: `${r.educationMatch}%`,
  //   status: <Badge variant={statusColors[r.status]}>{r.status}</Badge>,
  // }))


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
          {error && (
            <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Select Job
              </label>
              <Select
                value={selectedJob}
                onChange={(e) => setSelectedJob(e.target.value)}
                options={[
                  { value: '', label: 'Choose a job...' },
                  ...jobs
                ]}
                disabled={jobsLoading}
              />
            </div>
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
            disabled={!selectedJob || isLoading}
            className="w-full sm:w-auto"
          >
            {isLoading ? '🔄 Finding Candidates...' : '🔍 Find Matching Candidates'}
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
            {filteredResults.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="bg-gray-100 border-b-2 border-gray-300">
                      {tableColumns.map((col) => (
                        <th
                          key={col.key}
                          className="px-4 py-3 text-left text-sm font-semibold text-gray-900"
                        >
                          {col.label}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {filteredResults.map((result) => (
                      <tr
                        key={result.id}
                        className="border-b border-gray-200 hover:bg-gray-50 transition"
                      >
                        <td className="px-4 py-3 text-sm font-semibold text-gray-900">
                          {result.candidateName}
                        </td>
                        <td className="px-4 py-3 text-sm font-bold text-green-600">
                          {result.score}%
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {result.skillMatch}%
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {result.experienceMatch}%
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {result.educationMatch}%
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <Badge variant={statusColors[result.status]}>
                            {result.status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No candidates match the filter criteria
              </div>
            )}
          </Card>

          {/* Top Candidate Detail */}
          {filteredResults.length > 0 && (
            <Card className="bg-gradient-to-br from-green-50 to-teal-50 border-t-4 border-green-600">
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                🏆 Top Match: {filteredResults[0].candidateName}
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
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

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Button variant="primary">📧 Send Offer</Button>
                <Button variant="secondary">📄 View Resume</Button>
              </div>
            </Card>
          )}
        </section>
      )}

      {/* Empty State */}
      {matchResults.length === 0 && !isLoading && (
        <Card className="text-center py-12">
          <div className="text-6xl mb-4">🔍</div>
          <p className="text-gray-600 text-lg">
            Select a job and click "Find Matching Candidates" to see results
          </p>
        </Card>
      )}

      {/* Loading State */}
      {isLoading && (
        <Card className="text-center py-12">
          <div className="text-4xl mb-4">⏳</div>
          <p className="text-gray-600 text-lg">Finding matching candidates...</p>
        </Card>
      )}
    </div>
  )
}
