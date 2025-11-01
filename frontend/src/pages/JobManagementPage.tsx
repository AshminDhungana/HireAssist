import { useState, useEffect } from 'react'
import { Button, Input, Card, Modal, Badge, Textarea } from '../components/ui'
import { jobService } from '../services/jobService'

interface Job {
  id: string
  title: string
  description: string
  requirements: string
  location: string
  salary_min?: number
  salary_max?: number
  status: 'active' | 'closed'
  created_at?: string
}

export default function JobManagementPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingJob, setEditingJob] = useState<Job | null>(null)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    requirements: '',
    location: '',
    salary_min: '',
    salary_max: '',
  })
  const [searchTerm, setSearchTerm] = useState('')
  const [skip, setSkip] = useState(0)

  useEffect(() => {
    loadJobs()
  }, [skip])

  const loadJobs = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await jobService.listJobs(skip, 20)
      if (result.success && result.data) {
        setJobs(result.data.jobs)
      } else {
        setError(result.error || 'Failed to load jobs')
      }
    } catch (err) {
      setError('Error loading jobs')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleOpenModal = (job?: Job) => {
    if (job) {
      setEditingJob(job)
      setFormData({
        title: job.title,
        description: job.description,
        requirements: job.requirements,
        location: job.location,
        salary_min: job.salary_min?.toString() || '',
        salary_max: job.salary_max?.toString() || '',
      })
    } else {
      setEditingJob(null)
      setFormData({
        title: '',
        description: '',
        requirements: '',
        location: '',
        salary_min: '',
        salary_max: '',
      })
    }
    setIsModalOpen(true)
  }

  const handleSubmit = async () => {
    if (!formData.title || !formData.description || !formData.requirements) {
      alert('Please fill in all required fields')
      return
    }

    try {
      if (editingJob) {
        // Update job
        await jobService.updateJob(editingJob.id, {
          title: formData.title,
          description: formData.description,
          requirements: formData.requirements,
          location: formData.location,
          salary_min: formData.salary_min ? parseInt(formData.salary_min) : undefined,
          salary_max: formData.salary_max ? parseInt(formData.salary_max) : undefined,
        })
        alert('Job updated successfully!')
      } else {
        // Create job
        await jobService.createJob({
          title: formData.title,
          description: formData.description,
          requirements: formData.requirements,
          location: formData.location,
          salary_min: formData.salary_min ? parseInt(formData.salary_min) : undefined,
          salary_max: formData.salary_max ? parseInt(formData.salary_max) : undefined,
        })
        alert('Job created successfully!')
      }
      setIsModalOpen(false)
      loadJobs()
    } catch (err) {
      alert('Error saving job')
      console.error(err)
    }
  }

  const handleDelete = async (jobId: string) => {
    if (window.confirm('Are you sure you want to delete this job?')) {
      try {
        await jobService.deleteJob(jobId)
        alert('Job deleted successfully!')
        loadJobs()
      } catch (err) {
        alert('Error deleting job')
      }
    }
  }

  const filteredJobs = jobs.filter(job =>
    job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    job.location.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="space-y-8">
      {/* Header */}
      <section className="overflow-hidden rounded-3xl bg-white shadow-2xl ring-1 ring-gray-200">
        <div className="p-8 sm:p-12 text-center text-white bg-gradient-to-br from-purple-600 via-pink-600 to-red-600">
          <h2 className="mb-3 text-4xl font-extrabold tracking-tight drop-shadow-md sm:text-5xl">
            💼 Job Management
          </h2>
          <p className="text-lg font-medium text-purple-100 opacity-90 sm:text-xl">
            Create and manage job postings
          </p>
        </div>
      </section>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Search & Create */}
      <Card>
        <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
          <Input
            placeholder="Search jobs by title or location..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1"
          />
          <Button
            onClick={() => handleOpenModal()}
            variant="primary"
          >
            ➕ Create Job
          </Button>
        </div>
      </Card>

      {/* Jobs List */}
      <Card>
        <h3 className="text-xl font-bold text-gray-900 mb-4">
          Active Jobs ({filteredJobs.length})
        </h3>

        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading jobs...</div>
        ) : filteredJobs.length > 0 ? (
          <div className="space-y-4">
            {filteredJobs.map((job) => (
              <div key={job.id} className="border rounded-lg p-4 hover:shadow-md transition">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <h4 className="text-lg font-bold text-gray-900">{job.title}</h4>
                    <p className="text-gray-600">{job.location}</p>
                  </div>
                  <Badge variant="success">{job.status}</Badge>
                </div>

                <p className="text-gray-700 mb-2 line-clamp-2">{job.description}</p>

                {job.salary_min && job.salary_max && (
                  <p className="text-sm text-gray-600 mb-3">
                    💰 ${job.salary_min} - ${job.salary_max}
                  </p>
                )}

                <div className="flex gap-2">
                  <Button
                    onClick={() => handleOpenModal(job)}
                    variant="secondary"
                    size="sm"
                  >
                    ✏️ Edit
                  </Button>
                  <Button
                    onClick={() => handleDelete(job.id)}
                    variant="danger"
                    size="sm"
                  >
                    🗑️ Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">No jobs found</div>
        )}
      </Card>

      {/* Pagination */}
      {!loading && (
        <div className="flex justify-between items-center">
          <button
            onClick={() => setSkip(Math.max(0, skip - 20))}
            disabled={skip === 0}
            className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
          >
            Previous
          </button>
          <button
            onClick={() => setSkip(skip + 20)}
            className="px-4 py-2 bg-gray-200 rounded"
          >
            Next
          </button>
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingJob ? 'Edit Job' : 'Create New Job'}
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-1">
              Job Title *
            </label>
            <Input
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g., Senior React Developer"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-1">
              Description *
            </label>
            <Textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Job description..."
              rows={4}
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-1">
              Requirements *
            </label>
            <Textarea
              value={formData.requirements}
              onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
              placeholder="Required skills and experience..."
              rows={4}
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-1">
              Location
            </label>
            <Input
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              placeholder="e.g., San Francisco, CA"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-1">
                Min Salary
              </label>
              <Input
                type="number"
                value={formData.salary_min}
                onChange={(e) => setFormData({ ...formData, salary_min: e.target.value })}
                placeholder="e.g., 80000"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-1">
                Max Salary
              </label>
              <Input
                type="number"
                value={formData.salary_max}
                onChange={(e) => setFormData({ ...formData, salary_max: e.target.value })}
                placeholder="e.g., 120000"
              />
            </div>
          </div>

          <div className="flex gap-2 pt-4">
            <Button onClick={handleSubmit} variant="primary" className="flex-1">
              {editingJob ? 'Update Job' : 'Create Job'}
            </Button>
            <Button onClick={() => setIsModalOpen(false)} variant="secondary" className="flex-1">
              Cancel
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
