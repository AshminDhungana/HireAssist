import { useState, useEffect } from 'react'
import { Button, Card, Badge } from '../components/ui'
import { listResumes, uploadResume, deleteResume } from '../api/resumeService'

interface Resume {
  id: string
  filename: string
  skills: string[]
  experience_years?: number
  education_level?: string
  created_at?: string
}

export default function ResumeManagementPage() {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    loadResumes()
  }, [])

  const loadResumes = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await listResumes()
      if (result.success) {
        setResumes(result.data.resumes)
      } else {
        setError(result.error || 'Failed to load resumes')
      }
    } catch (err) {
      setError('Error loading resumes')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (file: File) => {
    if (!file) return

    setUploading(true)
    try {
      const result = await uploadResume(file)
      if (result.success) {
        alert('Resume uploaded successfully!')
        loadResumes()
      } else {
        alert(result.error || 'Upload failed')
      }
    } catch (err) {
      alert('Error uploading resume')
      console.error(err)
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (resumeId: string) => {
    if (window.confirm('Are you sure you want to delete this resume?')) {
      try {
        const result = await deleteResume(resumeId)
        if (result.success) {
          alert('Resume deleted successfully!')
          loadResumes()
        }
      } catch (err) {
        alert('Error deleting resume')
      }
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <section className="overflow-hidden rounded-3xl bg-white shadow-2xl ring-1 ring-gray-200">
        <div className="p-8 sm:p-12 text-center text-white bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600">
          <h2 className="mb-3 text-4xl font-extrabold tracking-tight drop-shadow-md sm:text-5xl">
            📄 Resume Management
          </h2>
          <p className="text-lg font-medium text-indigo-100 opacity-90 sm:text-xl">
            Upload, view, and manage your resumes
          </p>
        </div>
      </section>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Upload Section */}
      <Card>
        <h3 className="text-xl font-bold text-gray-900 mb-4">📤 Upload Resume</h3>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <input
            type="file"
            accept=".pdf,.doc,.docx,.txt"
            onChange={(e) => e.target.files && handleFileUpload(e.target.files[0])}
            disabled={uploading}
            className="hidden"
            id="resume-input"
          />
          <label
            htmlFor="resume-input"
            className="cursor-pointer inline-block"
          >
            <div className="text-4xl mb-2">📎</div>
            <p className="text-gray-700 font-semibold mb-1">
              {uploading ? 'Uploading...' : 'Click to upload resume'}
            </p>
            <p className="text-sm text-gray-600">
              Supported: PDF, DOC, DOCX, TXT (Max 10MB)
            </p>
          </label>
        </div>
      </Card>

      {/* Resumes List */}
      <Card>
        <h3 className="text-xl font-bold text-gray-900 mb-4">
          Your Resumes ({resumes.length})
        </h3>

        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading resumes...</div>
        ) : resumes.length > 0 ? (
          <div className="space-y-4">
            {resumes.map((resume) => (
              <div key={resume.id} className="border rounded-lg p-4 hover:shadow-md transition">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h4 className="text-lg font-bold text-gray-900">{resume.filename}</h4>
                    {resume.experience_years && (
                      <p className="text-sm text-gray-600">
                        📊 {resume.experience_years} years experience
                      </p>
                    )}
                    {resume.education_level && (
                      <p className="text-sm text-gray-600">
                        🎓 {resume.education_level}
                      </p>
                    )}
                  </div>
                  <Badge variant="primary">{resumes.indexOf(resume) + 1}</Badge>
                </div>

                {resume.skills && resume.skills.length > 0 && (
                  <div className="mb-3">
                    <p className="text-sm font-semibold text-gray-600 mb-2">Skills:</p>
                    <div className="flex flex-wrap gap-2">
                      {resume.skills.slice(0, 5).map((skill, i) => (
                        <Badge key={i} variant="primary">
                          {skill}
                        </Badge>
                      ))}
                      {resume.skills.length > 5 && (
                        <Badge variant="secondary">
                          +{resume.skills.length - 5} more
                        </Badge>
                      )}
                    </div>
                  </div>
                )}

                {resume.created_at && (
                  <p className="text-xs text-gray-500 mb-3">
                    Uploaded: {new Date(resume.created_at).toLocaleDateString()}
                  </p>
                )}

                <div className="flex gap-2">
                  <Button variant="secondary" size="sm">
                    👁️ View
                  </Button>
                  <Button
                    onClick={() => handleDelete(resume.id)}
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
          <div className="text-center py-8 text-gray-500">
            No resumes uploaded yet. Upload your first resume above!
          </div>
        )}
      </Card>
    </div>
  )
}
