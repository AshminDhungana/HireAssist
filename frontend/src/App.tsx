import { useState, lazy, Suspense } from 'react'
import ResumeUpload from './components/ResumeUpload'
import ApiStatus from './components/ApiStatus'

const ParserComparisonPage = lazy(() => import('./pages/ParserComparisonPage'))

export default function App() {
  const [currentPage, setCurrentPage] = useState<'home' | 'comparison'>('home')

  const isHomePage = currentPage === 'home'
  const isComparisonPage = currentPage === 'comparison'

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-gray-50 to-white text-gray-800 antialiased">
      {/* Navigation Bar */}
      <nav className="sticky top-0 z-50 w-full bg-white/95 backdrop-blur-md border-b border-gray-200 shadow-sm">
        <div className="flex items-center justify-between h-16 px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          {/* Logo/Title */}
          <h1 className="text-3xl font-black text-transparent bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text">
            HireAssist
          </h1>

          {/* Navigation Buttons */}
          <div className="flex items-center gap-3 sm:gap-4">
            <button
              onClick={() => setCurrentPage('home')}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-full transition-all duration-300 shadow-md hover:shadow-lg hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-blue-300 ${
                isHomePage ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white' : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <span className="text-lg">📤</span>
              <span className="hidden sm:inline">Resume Upload</span>
            </button>
            
            <button
              onClick={() => setCurrentPage('comparison')}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-full transition-all duration-300 shadow-md hover:shadow-lg hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-indigo-300 ${
                isComparisonPage ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white' : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <span className="text-lg">📊</span>
              <span className="hidden sm:inline">Parser Comparison</span>
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
              {/* Main Upload Card Section */}
              <section className="overflow-hidden rounded-3xl bg-white shadow-2xl ring-1 ring-gray-200 transition-all duration-300 hover:shadow-3xl">
                {/* Gradient Header */}
                <div className="p-8 sm:p-12 text-center text-white bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600">
                  <h2 className="mb-3 text-4xl font-extrabold tracking-tight drop-shadow-md sm:text-5xl">
                    📤 Resume Upload & Parsing
                  </h2>
                  <p className="text-lg font-medium text-blue-100 opacity-90 sm:text-xl">
                    Upload your resume and let our AI parse it instantly
                  </p>
                </div>

                {/* Upload Component Wrapper */}
                <div className="p-8 sm:p-10 flex justify-center bg-gradient-to-b from-gray-50 to-white">
                  <ResumeUpload />
                </div>
              </section>

              {/* Feature Cards Grid */}
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

          {/* COMPARISON PAGE: Lazy Loaded */}
          {isComparisonPage && (
            <Suspense
              fallback={
                <div className="flex items-center justify-center min-h-[60vh]">
                  <div className="text-center">
                    <div className="w-12 h-12 mx-auto mb-4 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                    <p className="font-medium text-gray-600">Loading dashboard...</p>
                  </div>
                </div>
              }
            >
              <ParserComparisonPage />
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