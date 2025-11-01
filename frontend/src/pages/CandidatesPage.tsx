import { useState, useEffect } from 'react'
import { Button, Input, Select, Card, Modal, Badge } from '../components/ui'
import { candidateService } from '../services/candidateService'

interface Candidate {
  id: string
  name: string
  email: string
  phone: string
  location: string
  resumesCount: number
  status: 'active' | 'hired' | 'rejected' | 'pending'
  appliedJobs: number
  lastUpdate: string
}

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null)
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false)
  const [selectedCandidates, setSelectedCandidates] = useState<string[]>([])
  const [skip, setSkip] = useState(0)
  const [limit] = useState(20)

  // Load candidates from backend
  useEffect(() => {
    loadCandidates()
  }, [skip])

  const loadCandidates = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await candidateService.listCandidates(skip, limit)
      
      if (result.success && result.data) {
        // Transform API response to match UI interface
        const transformedCandidates: Candidate[] = result.data.candidates.map((c: any) => ({
          id: c.id,
          name: c.name,
          email: c.email,
          phone: c.phone || 'N/A',
          location: c.location || 'N/A',
          resumesCount: c.resume_count || 0,
          status: 'active' as const, // Default status (you can update via API later)
          appliedJobs: 0, // This would come from applications table if available
          lastUpdate: new Date().toISOString().split('T')[0],
        }))
        setCandidates(transformedCandidates)
      } else {
        setError(result.error || 'Failed to load candidates')
      }
    } catch (err) {
      setError('Error loading candidates')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const filteredCandidates = candidates.filter((c) => {
    const matchesSearch =
      c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.email.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = !filterStatus || c.status === filterStatus
    return matchesSearch && matchesStatus
  })

  const statusColors = {
    active: 'primary',
    hired: 'success',
    rejected: 'danger',
    pending: 'warning',
  } as const

  const tableColumns = [
    { key: 'name', label: 'Name' },
    { key: 'email', label: 'Email' },
    { key: 'location', label: 'Location' },
    { key: 'appliedJobs', label: 'Applications' },
    { key: 'status', label: 'Status' },
  ]

  const handleSelectCandidate = (id: string) => {
    setSelectedCandidates((prev) =>
      prev.includes(id) ? prev.filter((cid) => cid !== id) : [...prev, id]
    )
  }

  const handleSelectAll = () => {
    setSelectedCandidates(
      selectedCandidates.length === filteredCandidates.length
        ? []
        : filteredCandidates.map((c) => c.id)
    )
  }

  const handleViewDetails = (candidate: Candidate) => {
    setSelectedCandidate(candidate)
    setIsDetailModalOpen(true)
  }

  const handleStatusChange = (candidateId: string, newStatus: Candidate['status']) => {
    setCandidates(
      candidates.map((c) =>
        c.id === candidateId ? { ...c, status: newStatus } : c
      )
    )
  }

  const handleDeleteCandidate = async (candidateId: string) => {
    if (window.confirm('Are you sure you want to delete this candidate?')) {
      // Delete via API if needed
      setCandidates(candidates.filter((c) => c.id !== candidateId))
    }
  }

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <section className="overflow-hidden rounded-3xl bg-white shadow-2xl ring-1 ring-gray-200">
        <div className="p-8 sm:p-12 text-center text-white bg-gradient-to-br from-orange-600 via-red-600 to-pink-600">
          <h2 className="mb-3 text-4xl font-extrabold tracking-tight drop-shadow-md sm:text-5xl">
            👥 Candidate Management
          </h2>
          <p className="text-lg font-medium text-orange-100 opacity-90 sm:text-xl">
            View and manage all uploaded candidates
          </p>
        </div>
      </section>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600 mb-2">
              {candidates.length}
            </div>
            <p className="text-gray-600 font-semibold">Total Candidates</p>
          </div>
        </Card>

        <Card>
          <div className="text-center">
            <div className="text-4xl font-bold text-green-600 mb-2">
              {candidates.filter((c) => c.status === 'active').length}
            </div>
            <p className="text-gray-600 font-semibold">Active</p>
          </div>
        </Card>

        <Card>
          <div className="text-center">
            <div className="text-4xl font-bold text-yellow-600 mb-2">
              {candidates.filter((c) => c.status === 'pending').length}
            </div>
            <p className="text-gray-600 font-semibold">Pending Review</p>
          </div>
        </Card>

        <Card>
          <div className="text-center">
            <div className="text-4xl font-bold text-purple-600 mb-2">
              {candidates.filter((c) => c.status === 'hired').length}
            </div>
            <p className="text-gray-600 font-semibold">Hired</p>
          </div>
        </Card>
      </div>

      {/* Search & Filter Section */}
      <Card>
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-gray-900">🔍 Search & Filter</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              placeholder="Search by name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              options={[
                { value: '', label: 'All Status' },
                { value: 'active', label: 'Active' },
                { value: 'pending', label: 'Pending' },
                { value: 'hired', label: 'Hired' },
                { value: 'rejected', label: 'Rejected' },
              ]}
            />
          </div>

          {selectedCandidates.length > 0 && (
            <div className="flex flex-wrap gap-2 items-center pt-4 border-t border-gray-200">
              <p className="text-sm font-semibold text-gray-600">
                {selectedCandidates.length} selected
              </p>
              <Button variant="primary" size="sm">
                📧 Send Email
              </Button>
              <Button variant="secondary" size="sm">
                ⬇️ Export
              </Button>
              <Button variant="danger" size="sm">
                🗑️ Delete
              </Button>
            </div>
          )}
        </div>
      </Card>

      {/* Candidates Table */}
      <Card>
        <h3 className="text-xl font-bold text-gray-900 mb-4">
          Candidates ({filteredCandidates.length})
        </h3>

        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading candidates...</div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-gray-100 border-b-2 border-gray-300">
                    <th className="px-4 py-3 text-left">
                      <input
                        type="checkbox"
                        checked={
                          selectedCandidates.length === filteredCandidates.length &&
                          filteredCandidates.length > 0
                        }
                        onChange={handleSelectAll}
                        className="w-4 h-4 cursor-pointer"
                      />
                    </th>
                    {tableColumns.map((col) => (
                      <th
                        key={col.key}
                        className="px-4 py-3 text-left text-sm font-semibold text-gray-900"
                      >
                        {col.label}
                      </th>
                    ))}
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCandidates.map((candidate) => (
                    <tr
                      key={candidate.id}
                      className="border-b border-gray-200 hover:bg-gray-50 transition"
                    >
                      <td className="px-4 py-3">
                        <input
                          type="checkbox"
                          checked={selectedCandidates.includes(candidate.id)}
                          onChange={() => handleSelectCandidate(candidate.id)}
                          className="w-4 h-4 cursor-pointer"
                        />
                      </td>
                      <td className="px-4 py-3 text-sm font-semibold text-gray-900">
                        {candidate.name}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {candidate.email}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {candidate.location}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 font-semibold">
                        {candidate.appliedJobs}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <Badge variant={statusColors[candidate.status]}>
                          {candidate.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleViewDetails(candidate)}
                            className="text-blue-600 hover:text-blue-800 font-semibold text-xs"
                          >
                            View
                          </button>
                          <button
                            onClick={() => handleDeleteCandidate(candidate.id)}
                            className="text-red-600 hover:text-red-800 font-semibold text-xs"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {filteredCandidates.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <p className="text-lg">No candidates found</p>
              </div>
            )}

            {/* Pagination */}
            <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-200">
              <button
                onClick={() => setSkip(Math.max(0, skip - limit))}
                disabled={skip === 0}
                className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-sm text-gray-600">Page {Math.floor(skip / limit) + 1}</span>
              <button
                onClick={() => setSkip(skip + limit)}
                className="px-4 py-2 bg-gray-200 rounded"
              >
                Next
              </button>
            </div>
          </>
        )}
      </Card>

      {/* Candidate Detail Modal */}
      <Modal
        isOpen={isDetailModalOpen}
        onClose={() => setIsDetailModalOpen(false)}
        title={selectedCandidate?.name || ''}
      >
        {selectedCandidate && (
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600">Email</p>
              <p className="text-lg font-semibold text-gray-900">
                {selectedCandidate.email}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-600">Phone</p>
              <p className="text-lg font-semibold text-gray-900">
                {selectedCandidate.phone}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-600">Location</p>
              <p className="text-lg font-semibold text-gray-900">
                {selectedCandidate.location}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-600">Resumes</p>
              <p className="text-lg font-semibold text-gray-900">
                {selectedCandidate.resumesCount} uploaded
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-600">Applications</p>
              <p className="text-lg font-semibold text-gray-900">
                {selectedCandidate.appliedJobs} applied
              </p>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Change Status
              </label>
              <Select
                value={selectedCandidate.status}
                onChange={(e) =>
                  handleStatusChange(
                    selectedCandidate.id,
                    e.target.value as Candidate['status']
                  )
                }
                options={[
                  { value: 'active', label: 'Active' },
                  { value: 'pending', label: 'Pending' },
                  { value: 'hired', label: 'Hired' },
                  { value: 'rejected', label: 'Rejected' },
                ]}
              />
            </div>

            <div className="grid grid-cols-2 gap-3 pt-4">
              <Button variant="primary">📄 View Resume</Button>
              <Button variant="secondary" onClick={() => setIsDetailModalOpen(false)}>
                Close
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
