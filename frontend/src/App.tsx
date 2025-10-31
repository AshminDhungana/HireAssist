import { useState, lazy, Suspense } from 'react'
import ResumeUpload from './components/ResumeUpload'
import ApiStatus from './components/ApiStatus'
import './App.css'

const ParserComparisonPage = lazy(() => import('./pages/ParserComparisonPage'))

function App() {
  const [currentPage, setCurrentPage] = useState('home')

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Left: Brand */}
            <h1 className="text-2xl font-bold text-blue-600">HireAssist</h1>
            
            {/* Center: Nav Buttons */}
            <div className="flex gap-3">
              <button
                onClick={() => setCurrentPage('home')}
                className={
                  currentPage === 'home'
                    ? 'px-6 py-2 rounded-lg font-semibold bg-blue-600 text-white shadow-lg transition-all'
                    : 'px-6 py-2 rounded-lg font-semibold bg-gray-100 text-gray-800 hover:bg-gray-200 transition-all'
                }
              >
                📤 Resume Upload
              </button>
              
              <button
                onClick={() => setCurrentPage('comparison')}
                className={
                  currentPage === 'comparison'
                    ? 'px-6 py-2 rounded-lg font-semibold bg-blue-600 text-white shadow-lg transition-all'
                    : 'px-6 py-2 rounded-lg font-semibold bg-gray-100 text-gray-800 hover:bg-gray-200 transition-all'
                }
              >
                📊 Parser Comparison
              </button>
            </div>

            {/* Right: API Status Badge */}
            <ApiStatus />
          </div>
        </div>
      </nav>

      {/* Page Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        
        {/* HOME PAGE */}
        {currentPage === 'home' && (
          <div className="space-y-8">
            <section className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
                <h2 className="text-3xl font-bold">📤 Resume Upload</h2>
                <p className="text-blue-100 mt-2">Upload and parse your resume</p>
              </div>
              <div className="p-8">
                <ResumeUpload />
              </div>
            </section>
          </div>
        )}

        {/* COMPARISON PAGE */}
        {currentPage === 'comparison' && (
          <Suspense
            fallback={
              <div className="flex items-center justify-center min-h-[60vh]">
                <div className="text-center">
                  <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-gray-600 font-medium">Loading dashboard...</p>
                </div>
              </div>
            }
          >
            <ParserComparisonPage />
          </Suspense>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12 py-6">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600 text-sm">
          <p>© 2025 HireAssist - AI Resume Screening System</p>
        </div>
      </footer>
    </div>
  )
}

export default App
