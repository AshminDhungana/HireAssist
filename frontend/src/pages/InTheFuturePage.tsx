import { Card } from '../components/ui'

interface FeatureItem {
  id: string
  title: string
  description: string
  icon: string
  status: 'planned' | 'in-progress' | 'soon'
  eta?: string
}

export default function InTheFuturePage() {
  const upcomingFeatures: FeatureItem[] = [
    {
      id: '1',
      title: 'Mobile App (iOS & Android)',
      description: 'React Native mobile application for on-the-go resume screening and candidate management',
      icon: '📱',
      status: 'planned',
      eta: 'Q2 2026',
    },
    {
      id: '2',
      title: 'AI Chat Assistant',
      description: 'Conversational AI to help with candidate queries, resume questions, and job recommendations',
      icon: '🤖',
      status: 'planned',
      eta: 'Q1 2026',
    },
    {
      id: '3',
      title: 'Advanced Video Interview',
      description: 'Conduct and analyze video interviews with AI-powered candidate assessment',
      icon: '🎥',
      status: 'soon',
      eta: 'Q2 2026',
    },
    {
      id: '4',
      title: 'Skill Assessment Platform',
      description: 'Automated coding tests, technical assessments, and skill verification',
      icon: '✍️',
      status: 'planned',
      eta: 'Q3 2026',
    },
    {
      id: '5',
      title: 'Multi-Language Support',
      description: 'Support for 20+ languages for global recruitment needs',
      icon: '🌍',
      status: 'soon',
      eta: 'Q2 2026',
    },
    {
      id: '6',
      title: 'Predictive Analytics',
      description: 'Machine learning models to predict candidate success and retention rates',
      icon: '🔮',
      status: 'planned',
      eta: 'Q3 2026',
    },
    {
      id: '7',
      title: 'Integration Marketplace',
      description: 'Connect with ATS, HRIS, Slack, Teams, and 50+ third-party tools',
      icon: '🔗',
      status: 'soon',
      eta: 'Q2 2026',
    },
    {
      id: '8',
      title: 'Employer Branding Portal',
      description: 'Showcase company culture, benefits, and team stories to attract talent',
      icon: '🏢',
      status: 'planned',
      eta: 'Q4 2026',
    },
    {
      id: '9',
      title: 'Candidate Community',
      description: 'Networking platform for candidates to connect, learn, and grow',
      icon: '👨‍👩‍👧‍👦',
      status: 'planned',
      eta: '2026',
    },
    {
      id: '10',
      title: 'Advanced Reporting',
      description: 'Custom reports, dashboards, and data export with BI tool integration',
      icon: '📊',
      status: 'soon',
      eta: 'Q1 2026',
    },
    {
      id: '11',
      title: 'Blockchain Verification',
      description: 'Verify credentials, certifications, and work history on blockchain',
      icon: '🔐',
      status: 'planned',
      eta: 'Q4 2026',
    },
    {
      id: '12',
      title: 'Global Payroll Integration',
      description: 'Seamless integration with payroll systems for hired candidates',
      icon: '💰',
      status: 'planned',
      eta: '2026',
    },
  ]

  const statusConfig = {
    planned: { color: 'bg-blue-100 text-blue-800 border-blue-300', label: 'Planned' },
    'in-progress': { color: 'bg-yellow-100 text-yellow-800 border-yellow-300', label: 'In Progress' },
    soon: { color: 'bg-green-100 text-green-800 border-green-300', label: 'Coming Soon' },
  }

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <section className="overflow-hidden rounded-3xl bg-white shadow-2xl ring-1 ring-gray-200">
        <div className="p-8 sm:p-12 text-center text-white bg-gradient-to-br from-purple-600 via-pink-600 to-red-600">
          <h2 className="mb-3 text-4xl font-extrabold tracking-tight drop-shadow-md sm:text-5xl">
            🚀 In The Future
          </h2>
          <p className="text-lg font-medium text-purple-100 opacity-90 sm:text-xl">
            Exciting features coming soon to HireAssist
          </p>
        </div>
      </section>

      {/* Roadmap Overview */}
      <Card className="bg-gradient-to-br from-purple-50 to-pink-50 border-t-4 border-purple-600">
        <h3 className="text-2xl font-bold text-gray-900 mb-4">📅 Product Roadmap</h3>
        <p className="text-gray-700 mb-4">
          We're constantly innovating and building new features to make recruitment easier, faster, and smarter. Check out what's coming next!
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-white rounded-lg border border-purple-200">
            <div className="text-3xl font-bold text-blue-600 mb-1">4</div>
            <p className="text-sm text-gray-600">Coming Soon</p>
          </div>
          <div className="text-center p-4 bg-white rounded-lg border border-purple-200">
            <div className="text-3xl font-bold text-green-600 mb-1">5</div>
            <p className="text-sm text-gray-600">Planned Q1-Q2</p>
          </div>
          <div className="text-center p-4 bg-white rounded-lg border border-purple-200">
            <div className="text-3xl font-bold text-orange-600 mb-1">3</div>
            <p className="text-sm text-gray-600">Planned Q3+</p>
          </div>
        </div>
      </Card>

      {/* Features Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {upcomingFeatures.map((feature) => (
          <Card
            key={feature.id}
            className={`border-t-4 hover:shadow-xl transition-all duration-300 ${
              feature.status === 'soon'
                ? 'border-t-green-600 bg-gradient-to-br from-green-50 to-emerald-50'
                : feature.status === 'in-progress'
                ? 'border-t-yellow-600 bg-gradient-to-br from-yellow-50 to-amber-50'
                : 'border-t-blue-600 bg-gradient-to-br from-blue-50 to-indigo-50'
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="text-4xl">{feature.icon}</div>
              <span
                className={`px-2 py-1 rounded-full text-xs font-bold border ${
                  statusConfig[feature.status].color
                }`}
              >
                {statusConfig[feature.status].label}
              </span>
            </div>

            <h3 className="text-lg font-bold text-gray-900 mb-2">{feature.title}</h3>
            <p className="text-sm text-gray-600 mb-3">{feature.description}</p>

            {feature.eta && (
              <div className="text-xs font-semibold text-gray-700 pt-3 border-t border-gray-200">
                📅 ETA: {feature.eta}
              </div>
            )}
          </Card>
        ))}
      </div>

      {/* Mobile App Highlight */}
      <section className="overflow-hidden rounded-3xl bg-white shadow-2xl ring-1 ring-gray-200">
        <div className="grid grid-cols-1 sm:grid-cols-2">
          {/* Left Side - Content */}
          <div className="p-8 sm:p-12 flex flex-col justify-center">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 mb-4">
              📱 Mobile App Coming Soon
            </h2>
            <p className="text-gray-600 mb-4 text-lg">
              Access HireAssist on the go with our upcoming React Native mobile app for iOS and Android.
            </p>

            <div className="space-y-3 mb-6">
              <div className="flex gap-3">
                <span className="text-2xl">✅</span>
                <p className="text-gray-700">
                  <strong>Resume Upload</strong> - Capture resumes with camera or file upload
                </p>
              </div>
              <div className="flex gap-3">
                <span className="text-2xl">✅</span>
                <p className="text-gray-700">
                  <strong>Instant Parsing</strong> - Get results in seconds on your phone
                </p>
              </div>
              <div className="flex gap-3">
                <span className="text-2xl">✅</span>
                <p className="text-gray-700">
                  <strong>Notifications</strong> - Get alerts for new matches and applications
                </p>
              </div>
              <div className="flex gap-3">
                <span className="text-2xl">✅</span>
                <p className="text-gray-700">
                  <strong>Offline Support</strong> - Work offline, sync when connected
                </p>
              </div>
            </div>

            <div className="bg-blue-100 border-l-4 border-blue-600 p-4 rounded">
              <p className="text-sm text-blue-900">
                <strong>🎯 Target Launch:</strong> Q2 2026
              </p>
            </div>
          </div>

          {/* Right Side - Visual */}
          <div className="bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 p-8 sm:p-12 flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-4">📱</div>
              <p className="text-white text-xl font-bold mb-2">HireAssist Mobile</p>
              <p className="text-blue-100">Available on iOS & Android</p>
              <div className="mt-6 flex gap-3 justify-center">
                <div className="px-4 py-2 bg-white bg-opacity-20 rounded-lg text-white text-sm font-semibold">
                  App Store
                </div>
                <div className="px-4 py-2 bg-white bg-opacity-20 rounded-lg text-white text-sm font-semibold">
                  Play Store
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* AI Assistant Highlight */}
      <section className="overflow-hidden rounded-3xl bg-white shadow-2xl ring-1 ring-gray-200">
        <div className="grid grid-cols-1 sm:grid-cols-2">
          {/* Left Side - Visual */}
          <div className="bg-gradient-to-br from-emerald-600 via-teal-600 to-cyan-600 p-8 sm:p-12 flex items-center justify-center order-2 sm:order-1">
            <div className="text-center">
              <div className="text-6xl mb-4">🤖</div>
              <p className="text-white text-xl font-bold mb-2">AI Chat Assistant</p>
              <p className="text-emerald-100">Available Q1 2026</p>
              <div className="mt-6 space-y-2">
                <div className="px-3 py-1 bg-white bg-opacity-20 rounded text-white text-xs font-semibold">
                  24/7 Support
                </div>
                <div className="px-3 py-1 bg-white bg-opacity-20 rounded text-white text-xs font-semibold">
                  Natural Language
                </div>
                <div className="px-3 py-1 bg-white bg-opacity-20 rounded text-white text-xs font-semibold">
                  Smart Recommendations
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Content */}
          <div className="p-8 sm:p-12 flex flex-col justify-center order-1 sm:order-2">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 mb-4">
              🤖 AI Chat Assistant
            </h2>
            <p className="text-gray-600 mb-4 text-lg">
              Talk to our AI assistant to get instant help with your recruitment tasks.
            </p>

            <div className="space-y-3 mb-6">
              <p className="text-gray-700">
                <strong>💬 Ask Questions:</strong> "Find senior developers matching our requirements"
              </p>
              <p className="text-gray-700">
                <strong>🔍 Get Insights:</strong> "What's the average match score this week?"
              </p>
              <p className="text-gray-700">
                <strong>⚡ Take Actions:</strong> "Send offers to top 5 candidates"
              </p>
              <p className="text-gray-700">
                <strong>📊 Get Reports:</strong> "Show me our hiring metrics"
              </p>
            </div>

            <div className="bg-emerald-100 border-l-4 border-emerald-600 p-4 rounded">
              <p className="text-sm text-emerald-900">
                <strong>🎯 Coming:</strong> Q1 2026
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Feedback Section */}
      <Card className="bg-gradient-to-br from-orange-50 to-red-50 border-t-4 border-orange-600 text-center">
        <h3 className="text-2xl font-bold text-gray-900 mb-3">💡 Have Ideas?</h3>
        <p className="text-gray-700 mb-4">
          We'd love to hear what features you'd like to see next! Your feedback shapes our roadmap.
        </p>
        <button className="px-6 py-3 bg-gradient-to-r from-orange-600 to-red-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all duration-300">
          📧 Share Your Feedback
        </button>
      </Card>

      {/* Newsletter Signup */}
      <Card className="bg-gradient-to-br from-indigo-50 to-purple-50 border-t-4 border-indigo-600">
        <h3 className="text-xl font-bold text-gray-900 mb-3">📬 Stay Updated</h3>
        <p className="text-gray-700 mb-4">
          Subscribe to our newsletter to get notified when new features launch.
        </p>
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="email"
            placeholder="your@email.com"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all">
            Subscribe
          </button>
        </div>
      </Card>
    </div>
  )
}
