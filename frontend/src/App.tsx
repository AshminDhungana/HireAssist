import { useState, lazy, Suspense, useEffect } from 'react'
import ResumeUpload from './components/ResumeUpload'
import ApiStatus from './components/ApiStatus'
import AuthPage from './pages/AuthPage'

const ParserComparisonPage = lazy(() => import('./pages/ParserComparisonPage'))
const JobMatchingPage = lazy(() => import('./pages/JobMatchingPage'))
const CandidatesPage = lazy(() => import('./pages/CandidatesPage'))
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'))
const InTheFuturePage = lazy(() => import('./pages/InTheFuturePage'))
const JobManagementPage = lazy(() => import('./pages/JobManagementPage'))
const ResumeManagementPage = lazy(() => import('./pages/ResumeManagementPage'))

type PageType = 'home' | 'comparison' | 'matching' | 'candidates' | 'analytics' | 'future' | 'jobs' | 'resumes'

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageType>('home')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState<any>(null)

  // Check if user is already logged in on mount
  useEffect(() => {
    const _token = localStorage.getItem('access_token')
    const userData = localStorage.getItem('user')
    if (_token && userData) {
      setIsAuthenticated(true)
      setUser(JSON.parse(userData))
    }
  }, [])

  const handleLoginSuccess = (token: string, userData: any) => {
    localStorage.setItem('access_token', token);
    setIsAuthenticated(true)
    setUser(userData)
    setCurrentPage('home')
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setIsAuthenticated(false)
    setUser(null)
    setCurrentPage('home')
  }

  // 🔐 If not authenticated, show login page
  if (!isAuthenticated) {
    return <AuthPage onLoginSuccess={handleLoginSuccess} />
  }

  const isHomePage = currentPage === 'home'
  const isComparisonPage = currentPage === 'comparison'
  const isMatchingPage = currentPage === 'matching'
  const isCandidatesPage = currentPage === 'candidates'
  const isAnalyticsPage = currentPage === 'analytics'
  const isJobsPage = currentPage === 'jobs'
  const isResumesPage = currentPage === 'resumes'

  // Navigation button component (reusable)
  const NavButton = ({
    isActive,
    onClick,
    icon,
    label,
    color,
  }: {
    isActive: boolean
    onClick: () => void
    icon: string
    label: string
    color: string
  }) => (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-3 sm:px-4 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-all duration-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-offset-2 ${
        isActive
          ? `bg-gradient-to-r ${color} text-white`
          : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
      }`}
    >
      <span className="text-lg">{icon}</span>
      <span className="hidden sm:inline">{label}</span>
    </button>
  )

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-gray-50 to-white text-gray-800 antialiased">
      {/* Navigation Bar */}
      <nav className="sticky top-0 z-50 w-full bg-white/95 backdrop-blur-md border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Top row: Logo + Search + User */}
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <h1 className="text-2xl sm:text-3xl font-black text-transparent bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text whitespace-nowrap">
              HireAssist
            </h1>

            {/* User Info & Logout */}
            <div className="flex items-center gap-3">
              {user && (
                <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-lg border border-blue-200">
                  <span className="text-sm font-semibold text-blue-900">👤 {user.email}</span>
                </div>
              )}
              <button
                onClick={handleLogout}
                className="px-3 sm:px-4 py-2 text-xs sm:text-sm font-semibold rounded-lg bg-red-100 text-red-700 hover:bg-red-200 transition-colors"
              >
                🚪 Logout
              </button>
              <ApiStatus />
            </div>
          </div>

          {/* Bottom row: Navigation buttons */}
          <div className="flex items-center gap-1.5 sm:gap-2 pb-4 overflow-x-auto scrollbar-hide">
            <NavButton
              isActive={isHomePage}
              onClick={() => setCurrentPage('home')}
              icon="📤"
              label="Upload"
              color="from-blue-600 to-indigo-600"
            />
            <NavButton
              isActive={isComparisonPage}
              onClick={() => setCurrentPage('comparison')}
              icon="📊"
              label="Compare"
              color="from-indigo-600 to-purple-600"
            />
            <NavButton
              isActive={isMatchingPage}
              onClick={() => setCurrentPage('matching')}
              icon="🎯"
              label="Matching"
              color="from-green-600 to-teal-600"
            />
            <NavButton
              isActive={isCandidatesPage}
              onClick={() => setCurrentPage('candidates')}
              icon="👥"
              label="Candidates"
              color="from-orange-600 to-red-600"
            />
            <NavButton
              isActive={isJobsPage}
              onClick={() => setCurrentPage('jobs')}
              icon="💼"
              label="Jobs"
              color="from-purple-600 to-pink-600"
            />
            <NavButton
              isActive={isResumesPage}
              onClick={() => setCurrentPage('resumes')}
              icon="📄"
              label="Resumes"
              color="from-pink-600 to-red-600"
            />
            <NavButton
              isActive={isAnalyticsPage}
              onClick={() => setCurrentPage('analytics')}
              icon="📈"
              label="Analytics"
              color="from-cyan-600 to-blue-600"
            />
            <NavButton
              isActive={currentPage === 'future'}
              onClick={() => setCurrentPage('future')}
              icon="🚀"
              label="Future"
              color="from-purple-600 to-pink-600"
            />
          </div>
        </div>
      </nav>

      {/* Page Content Area */}
      <main className="flex-1 w-full py-12 sm:py-16 lg:py-20">
        <div className="px-4 mx-auto max-w-6xl sm:px-6 lg:px-8">
          {/* HOME PAGE: Resume Upload */}
          {isHomePage && (
            <div className="space-y-12 sm:space-y-16">
              <section className="overflow-hidden rounded-3xl bg-white shadow-2xl ring-1 ring-gray-200 transition-all duration-300 hover:shadow-3xl">
                <div className="p-8 sm:p-12 text-center text-white bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600">
                  <h2 className="mb-3 text-4xl font-extrabold tracking-tight drop-shadow-md sm:text-5xl">
                    📤 Resume Upload & Parsing
                  </h2>
                  <p className="text-lg font-medium text-blue-100 opacity-90 sm:text-xl">
                    Upload your resume and let our AI parse it instantly
                  </p>
                </div>

                <div className="p-8 sm:p-10 flex justify-center bg-gradient-to-b from-gray-50 to-white">
                  <ResumeUpload />
                </div>
              </section>

              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                <div className="group p-8 transition-all duration-300 rounded-2xl bg-white shadow-md hover:shadow-xl hover:-translate-y-1 border-t-4 border-blue-600">
                  <div className="mb-3 text-4xl text-blue-600">⚡</div>
                  <p className="text-lg font-bold text-gray-900">Fast Parsing</p>
                  <p className="mt-1 text-sm text-gray-600">Process resumes in seconds</p>
                </div>

                <div className="group p-8 transition-all duration-300 rounded-2xl bg-white shadow-md hover:shadow-xl hover:-translate-y-1 border-t-4 border-indigo-600">
                  <div className="mb-3 text-4xl text-indigo-600">🎯</div>
                  <p className="text-lg font-bold text-gray-900">Accurate Extraction</p>
                  <p className="mt-1 text-sm text-gray-600">Extract skills, experience & more</p>
                </div>

                <div className="group p-8 transition-all duration-300 rounded-2xl bg-white shadow-md hover:shadow-xl hover:-translate-y-1 border-t-4 border-green-600">
                  <div className="mb-3 text-4xl text-green-600">🔒</div>
                  <p className="text-lg font-bold text-gray-900">Secure & Private</p>
                  <p className="mt-1 text-sm text-gray-600">Your data is safe with us</p>
                </div>
              </div>
            </div>
          )}

          {/* COMPARISON PAGE: Parser Comparison */}
          {isComparisonPage && (
            <Suspense fallback={<LoadingSpinner />}>
              <ParserComparisonPage />
            </Suspense>
          )}

          {/* MATCHING PAGE: Job Matching */}
          {isMatchingPage && (
            <Suspense fallback={<LoadingSpinner />}>
              <JobMatchingPage />
            </Suspense>
          )}

          {/* CANDIDATES PAGE */}
          {isCandidatesPage && (
            <Suspense fallback={<LoadingSpinner />}>
              <CandidatesPage />
            </Suspense>
          )}

          {/* JOBS PAGE */}
          {isJobsPage && (
            <Suspense fallback={<LoadingSpinner />}>
              <JobManagementPage />
            </Suspense>
          )}

          {/* RESUMES PAGE */}
          {isResumesPage && (
            <Suspense fallback={<LoadingSpinner />}>
              <ResumeManagementPage />
            </Suspense>
          )}

          {/* ANALYTICS PAGE */}
          {isAnalyticsPage && (
            <Suspense fallback={<LoadingSpinner />}>
              <AnalyticsPage />
            </Suspense>
          )}

          {/* FUTURE PAGE */}
          {currentPage === 'future' && (
            <Suspense fallback={<LoadingSpinner />}>
              <InTheFuturePage />
            </Suspense>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full mt-auto bg-gradient-to-r from-gray-900 to-gray-800 text-gray-300 border-t border-gray-700">
        <div className="px-6 py-8 mx-auto max-w-7xl md:py-12 text-center">
          <h2 className="text-2xl font-bold text-white leading-snug xl:text-3xl">
            HireAssist — AI Resume Screening System
          </h2>
          <p className="mt-3 text-sm text-gray-400">
            Developed with ❤️ by Ashmin Dhungana
          </p>
          <p className="mt-7 text-sm text-gray-500">© {new Date().getFullYear()} HireAssist. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center">
        <div className="w-12 h-12 mx-auto mb-4 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="font-medium text-gray-600">Loading page...</p>
      </div>
    </div>
  )
}
