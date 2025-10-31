import { useState, lazy, Suspense } from 'react'
import ResumeUpload from './components/ResumeUpload'
import ApiStatus from './components/ApiStatus'

const ParserComparisonPage = lazy(() => import('./pages/ParserComparisonPage'))
const JobMatchingPage = lazy(() => import('./pages/JobMatchingPage'))
const CandidatesPage = lazy(() => import('./pages/CandidatesPage'))
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'))
const InTheFuturePage = lazy(() => import('./pages/InTheFuturePage'))


type PageType = 'home' | 'comparison' | 'matching' | 'candidates' | 'analytics' | 'future'

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageType>('home')

  const isHomePage = currentPage === 'home'
  const isComparisonPage = currentPage === 'comparison'
  const isMatchingPage = currentPage === 'matching'
  const isCandidatesPage = currentPage === 'candidates'
  const isAnalyticsPage = currentPage === 'analytics'

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-gray-50 to-white text-gray-800 antialiased">
      {/* Navigation Bar */}
      <nav className="sticky top-0 z-50 w-full bg-white/95 backdrop-blur-md border-b border-gray-200 shadow-sm">
        <div className="flex items-center justify-between h-16 px-4 mx-auto max-w-7xl sm:px-6 lg:px-8 gap-3">
          {/* Logo/Title */}
          <h1 className="text-3xl font-black text-transparent bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text">
            HireAssist
          </h1>

          {/* Navigation Buttons */}
          <div className="flex items-center gap-2 sm:gap-3 flex-wrap justify-center">
            <button
              onClick={() => setCurrentPage('home')}
              className={`flex items-center gap-2 px-3 sm:px-4 py-2 text-xs sm:text-sm font-semibold rounded-full transition-all duration-300 shadow-md hover:shadow-lg hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-blue-300 ${
                isHomePage ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white' : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <span className="text-lg">📤</span>
              <span className="hidden sm:inline">Upload</span>
            </button>

            <button
              onClick={() => setCurrentPage('comparison')}
              className={`flex items-center gap-2 px-3 sm:px-4 py-2 text-xs sm:text-sm font-semibold rounded-full transition-all duration-300 shadow-md hover:shadow-lg hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-indigo-300 ${
                isComparisonPage ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white' : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <span className="text-lg">📊</span>
              <span className="hidden sm:inline">Compare</span>
            </button>

            <button
              onClick={() => setCurrentPage('matching')}
              className={`flex items-center gap-2 px-3 sm:px-4 py-2 text-xs sm:text-sm font-semibold rounded-full transition-all duration-300 shadow-md hover:shadow-lg hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-green-300 ${
                isMatchingPage ? 'bg-gradient-to-r from-green-600 to-teal-600 text-white' : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <span className="text-lg">🎯</span>
              <span className="hidden sm:inline">Matching</span>
            </button>

            <button
              onClick={() => setCurrentPage('candidates')}
              className={`flex items-center gap-2 px-3 sm:px-4 py-2 text-xs sm:text-sm font-semibold rounded-full transition-all duration-300 shadow-md hover:shadow-lg hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-orange-300 ${
                isCandidatesPage ? 'bg-gradient-to-r from-orange-600 to-red-600 text-white' : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <span className="text-lg">👥</span>
              <span className="hidden sm:inline">Candidates</span>
            </button>

            <button
              onClick={() => setCurrentPage('analytics')}
              className={`flex items-center gap-2 px-3 sm:px-4 py-2 text-xs sm:text-sm font-semibold rounded-full transition-all duration-300 shadow-md hover:shadow-lg hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-cyan-300 ${
                isAnalyticsPage ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white' : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <span className="text-lg">📈</span>
              <span className="hidden sm:inline">Analytics</span>
            </button>
            <button
              onClick={() => setCurrentPage('future')}
              className={`flex items-center gap-2 px-3 sm:px-4 py-2 text-xs sm:text-sm font-semibold rounded-full transition-all duration-300 shadow-md hover:shadow-lg hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-purple-300 ${
                currentPage === 'future' ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <span className="text-lg">🚀</span>
              <span className="hidden sm:inline">Future</span>
            </button>
            <ApiStatus />
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
      <footer className="w-full mt-auto bg-gray-900 text-gray-300 border-t border-gray-800">
        <div className="px-6 py-8 mx-auto max-w-7xl md:py-12 text-center">
          <h2 className="text-2xl font-bold text-white leading-snug xl:text-3xl">
            HireAssist — AI Resume Screening System
          </h2>
          <a className="inline-block mt-3 text-sm text-blue-400 hover:text-blue-300 transition" href="#">
            Developed By Ashmin Dhungana
          </a>
          <p className="mt-7 text-sm">© {new Date().getFullYear()} HireAssist</p>
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
