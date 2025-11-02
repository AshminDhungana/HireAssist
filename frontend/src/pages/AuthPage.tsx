import { useState } from 'react'
import { Button, Input, Card } from '../components/ui'
import ApiStatus from '../components/ApiStatus'
import axios from 'axios'

interface AuthPageProps {
  onLoginSuccess: (token: string, user: any) => void
}

export default function AuthPage({ onLoginSuccess }: AuthPageProps) {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [isGuestUpload, setIsGuestUpload] = useState(false)
  const [guestEmail, setGuestEmail] = useState('')
  const [guestFile, setGuestFile] = useState<File | null>(null)

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

  const handleGuestUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

    if (!guestFile) {
      setError('Please select a resume file')
      setLoading(false)
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', guestFile)
      formData.append('email', guestEmail.trim())

      const response = await axios.post(
        `${API_BASE_URL}/api/v1/resumes/guest-upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )

      if (response.data.success) {
        setSuccess('✅ Resume uploaded successfully! Our team will review it shortly.')
        setGuestEmail('')
        setGuestFile(null)
      } else {
        setError(response.data.error)
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      if (isLogin) {
        const response = await axios.post(`${API_BASE_URL}/api/v1/auth/login`, {
          email: email.trim(),
          password: password.trim()
        })

        if (response.data.access_token) {
          setSuccess('Login successful! Redirecting...')
          localStorage.setItem('access_token', response.data.access_token)
          localStorage.setItem('user', JSON.stringify(response.data.user))
          
          setTimeout(() => {
            onLoginSuccess(response.data.access_token, response.data.user)
          }, 500)
        }
      } else {
        const response = await axios.post(`${API_BASE_URL}/api/v1/auth/register`, {
          email: email.trim(),
          password: password.trim(),
          first_name: firstName.trim(),
          last_name: lastName.trim(),
          role: 'candidate'
        })

        if (response.data.access_token) {
          setSuccess('✅ Account created! Waiting for admin approval...')
          setTimeout(() => {
            setIsLogin(true)
            setEmail('')
            setPassword('')
            setFirstName('')
            setLastName('')
          }, 2000)
        }
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Authentication failed'
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 p-4">
      {/* ✅ API Status Button - Top Right */}
      <div className="fixed top-4 right-4 z-50">
        <ApiStatus />
      </div>

      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-black text-white mb-2 drop-shadow-lg">
            HireAssist
          </h1>
          <p className="text-blue-100 text-lg">AI-Powered Resume Screening</p>
        </div>

        {/* Toggle Tabs */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => {
              setIsGuestUpload(false)
              setError(null)
              setSuccess(null)
            }}
            className={`flex-1 py-2 px-4 rounded-lg font-semibold transition ${
              !isGuestUpload
                ? 'bg-white text-blue-600 shadow-md'
                : 'bg-white/20 text-white hover:bg-white/30'
            }`}
          >
            🔐 Login
          </button>
          <button
            onClick={() => {
              setIsGuestUpload(true)
              setError(null)
              setSuccess(null)
            }}
            className={`flex-1 py-2 px-4 rounded-lg font-semibold transition ${
              isGuestUpload
                ? 'bg-white text-blue-600 shadow-md'
                : 'bg-white/20 text-white hover:bg-white/30'
            }`}
          >
            📤 Guest Upload
          </button>
        </div>

        <Card className="shadow-2xl">
          {/* GUEST UPLOAD */}
          {isGuestUpload ? (
            <form onSubmit={handleGuestUpload} className="space-y-4">
              <div className="text-center mb-6 pb-6 border-b border-gray-200">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">📄 Upload Resume</h2>
                <p className="text-gray-600 text-sm">
                  Upload 1 resume without creating an account
                </p>
              </div>

              {error && (
                <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded">
                  <p className="font-semibold">❌ Error</p>
                  <p className="text-sm mt-1">{error}</p>
                </div>
              )}

              {success && (
                <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded">
                  <p className="font-semibold">✅ Success</p>
                  <p className="text-sm mt-1">{success}</p>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  Email Address
                </label>
                <Input
                  type="email"
                  placeholder="you@example.com"
                  value={guestEmail}
                  onChange={(e) => setGuestEmail(e.target.value)}
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-2">
                  Resume File (PDF, DOC, DOCX, TXT)
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={(e) => setGuestFile(e.target.files?.[0] || null)}
                    className="hidden"
                    id="guest-file"
                    required
                  />
                  <label htmlFor="guest-file" className="cursor-pointer block">
                    <div className="text-4xl mb-2">📎</div>
                    <p className="text-gray-700 font-semibold mb-1">
                      {guestFile ? guestFile.name : 'Click to upload resume'}
                    </p>
                    <p className="text-sm text-gray-600">Max 10MB</p>
                  </label>
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                variant="primary"
                className="w-full mt-6"
              >
                {loading ? 'Uploading...' : '📤 Upload Resume'}
              </Button>
            </form>
          ) : (
            /* LOGIN/REGISTER */
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="text-center mb-6 pb-6 border-b border-gray-200">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  {isLogin ? '👋 Welcome Back' : '🚀 Get Started'}
                </h2>
                <p className="text-gray-600">
                  {isLogin ? 'Login to your account' : 'Create your account to begin'}
                </p>
              </div>

              {error && (
                <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded">
                  <p className="font-semibold">❌ Error</p>
                  <p className="text-sm mt-1">{error}</p>
                </div>
              )}

              {success && (
                <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded">
                  <p className="font-semibold">✅ Success</p>
                  <p className="text-sm mt-1">{success}</p>
                </div>
              )}

              {!isLogin && (
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">
                      First Name
                    </label>
                    <Input
                      type="text"
                      placeholder="John"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">
                      Last Name
                    </label>
                    <Input
                      type="text"
                      placeholder="Doe"
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                      required
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  Email Address
                </label>
                <Input
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  Password
                </label>
                <Input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              <Button
                type="submit"
                disabled={loading}
                variant="primary"
                className="w-full mt-6"
              >
                {loading
                  ? isLogin
                    ? 'Logging in...'
                    : 'Creating account...'
                  : isLogin
                  ? '🔓 Login'
                  : '✨ Create Account'}
              </Button>

              <div className="mt-6 pt-6 border-t border-gray-200 text-center">
                <p className="text-gray-600 text-sm mb-3">
                  {isLogin ? "Don't have an account?" : 'Already have an account?'}
                </p>
                <button
                  type="button"
                  onClick={() => {
                    setIsLogin(!isLogin)
                    setError(null)
                    setSuccess(null)
                    setEmail('')
                    setPassword('')
                    setFirstName('')
                    setLastName('')
                  }}
                  className="text-blue-600 hover:text-blue-800 font-semibold transition"
                >
                  {isLogin ? '📝 Sign Up' : '🔓 Login'}
                </button>
              </div>
            </form>
          )}
        </Card>

        <div className="text-center mt-8 text-blue-100 text-sm">
          <p>© 2025 HireAssist. All rights reserved.</p>
        </div>
      </div>
    </div>
  )
}
