import { useState } from 'react'
import { Card, Select, Button, Badge } from '../components/ui'
import { LineChart, BarChart, PieChart } from '../components/charts'

interface AnalyticsData {
  totalJobs: number
  totalCandidates: number
  totalApplications: number
  hiredCount: number
  avgMatchScore: number
  conversionRate: number
  timeToHire: number
}

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState('30')

  // Mock analytics data
  const analyticsData: AnalyticsData = {
    totalJobs: 24,
    totalCandidates: 156,
    totalApplications: 428,
    hiredCount: 12,
    avgMatchScore: 78.5,
    conversionRate: 2.8,
    timeToHire: 18,
  }

  const chartData = {
    // Applications over time (30 days)
    applications: [
      { date: 'Oct 2', count: 12 },
      { date: 'Oct 3', count: 15 },
      { date: 'Oct 4', count: 10 },
      { date: 'Oct 5', count: 18 },
      { date: 'Oct 6', count: 22 },
      { date: 'Oct 7', count: 20 },
      { date: 'Oct 8', count: 25 },
      { date: 'Oct 9', count: 30 },
      { date: 'Oct 10', count: 28 },
      { date: 'Oct 11', count: 35 },
    ],
    // Match score distribution
    matchScores: [
      { range: '0-20%', count: 5 },
      { range: '20-40%', count: 12 },
      { range: '40-60%', count: 28 },
      { range: '60-80%', count: 65 },
      { range: '80-100%', count: 46 },
    ],
    // Candidate status breakdown
    candidateStatus: [
      { status: 'Active', count: 95, percentage: 61 },
      { status: 'Pending', count: 35, percentage: 22 },
      { status: 'Hired', count: 18, percentage: 11 },
      { status: 'Rejected', count: 8, percentage: 5 },
    ],
    // Jobs by category
    jobsByCategory: [
      { category: 'Engineering', count: 8 },
      { category: 'Sales', count: 5 },
      { category: 'Marketing', count: 4 },
      { category: 'HR', count: 3 },
      { category: 'Support', count: 4 },
    ],
  }

  const handleExportReport = () => {
    alert('Report exported successfully!')
  }

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <section className="overflow-hidden rounded-3xl bg-white shadow-2xl ring-1 ring-gray-200">
        <div className="p-8 sm:p-12 text-center text-white bg-gradient-to-br from-cyan-600 via-blue-600 to-indigo-600">
          <h2 className="mb-3 text-4xl font-extrabold tracking-tight drop-shadow-md sm:text-5xl">
            📈 Analytics & Insights
          </h2>
          <p className="text-lg font-medium text-cyan-100 opacity-90 sm:text-xl">
            Recruitment metrics and performance data
          </p>
        </div>

        {/* Date Range Filter */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="w-full sm:w-auto">
              <Select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                options={[
                  { value: '7', label: 'Last 7 Days' },
                  { value: '30', label: 'Last 30 Days' },
                  { value: '90', label: 'Last 90 Days' },
                  { value: '365', label: 'Last Year' },
                ]}
              />
            </div>
            <Button onClick={handleExportReport} variant="primary">
              📥 Export Report
            </Button>
          </div>
        </div>
      </section>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-t-4 border-blue-600">
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600 mb-2">
              {analyticsData.totalJobs}
            </div>
            <p className="text-gray-700 font-semibold">Active Jobs</p>
            <p className="text-sm text-gray-600 mt-1">Posted this period</p>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-t-4 border-purple-600">
          <div className="text-center">
            <div className="text-4xl font-bold text-purple-600 mb-2">
              {analyticsData.totalCandidates}
            </div>
            <p className="text-gray-700 font-semibold">Candidates</p>
            <p className="text-sm text-gray-600 mt-1">In system</p>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-t-4 border-green-600">
          <div className="text-center">
            <div className="text-4xl font-bold text-green-600 mb-2">
              {analyticsData.totalApplications}
            </div>
            <p className="text-gray-700 font-semibold">Applications</p>
            <p className="text-sm text-gray-600 mt-1">Received</p>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-t-4 border-orange-600">
          <div className="text-center">
            <div className="text-4xl font-bold text-orange-600 mb-2">
              {analyticsData.hiredCount}
            </div>
            <p className="text-gray-700 font-semibold">Hired</p>
            <p className="text-sm text-gray-600 mt-1">This period</p>
          </div>
        </Card>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <Card>
          <div className="text-center">
            <div className="text-5xl font-bold text-cyan-600 mb-2">
              {analyticsData.avgMatchScore}%
            </div>
            <p className="text-gray-700 font-semibold">Avg Match Score</p>
            <p className="text-sm text-gray-600 mt-1">Across all candidates</p>
            <div className="mt-4 bg-gray-200 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-cyan-500 to-blue-500 h-2 rounded-full"
                style={{ width: `${analyticsData.avgMatchScore}%` }}
              ></div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="text-center">
            <div className="text-5xl font-bold text-emerald-600 mb-2">
              {analyticsData.conversionRate}%
            </div>
            <p className="text-gray-700 font-semibold">Conversion Rate</p>
            <p className="text-sm text-gray-600 mt-1">Applications to hires</p>
            <div className="mt-4 bg-gray-200 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-emerald-500 to-green-500 h-2 rounded-full"
                style={{ width: `${analyticsData.conversionRate * 10}%` }}
              ></div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="text-center">
            <div className="text-5xl font-bold text-rose-600 mb-2">
              {analyticsData.timeToHire}
            </div>
            <p className="text-gray-700 font-semibold">Time to Hire</p>
            <p className="text-sm text-gray-600 mt-1">Average days</p>
            <div className="mt-4 bg-gray-200 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-rose-500 to-pink-500 h-2 rounded-full"
                style={{ width: `${(analyticsData.timeToHire / 30) * 100}%` }}
              ></div>
            </div>
          </div>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Applications Trend */}
        <Card>
          <h3 className="text-xl font-bold text-gray-900 mb-4">📊 Application Trends</h3>
          <LineChart data={chartData.applications} />
        </Card>

        {/* Match Score Distribution */}
        <Card>
          <h3 className="text-xl font-bold text-gray-900 mb-4">🎯 Match Score Distribution</h3>
          <BarChart data={chartData.matchScores} />
        </Card>

        {/* Candidate Status */}
        <Card>
          <h3 className="text-xl font-bold text-gray-900 mb-4">👥 Candidate Status</h3>
          <div className="space-y-3">
            {chartData.candidateStatus.map((item, idx) => (
              <div key={idx}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-semibold text-gray-700">{item.status}</span>
                  <Badge variant={
                    item.status === 'Active' ? 'primary' :
                    item.status === 'Hired' ? 'success' :
                    item.status === 'Pending' ? 'warning' : 'danger'
                  }>
                    {item.count}
                  </Badge>
                </div>
                <div className="bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      item.status === 'Active' ? 'bg-blue-500' :
                      item.status === 'Hired' ? 'bg-green-500' :
                      item.status === 'Pending' ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${item.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Jobs by Category */}
        <Card>
          <h3 className="text-xl font-bold text-gray-900 mb-4">💼 Jobs by Category</h3>
          <div className="space-y-3">
            {chartData.jobsByCategory.map((item, idx) => (
              <div key={idx} className="flex justify-between items-center">
                <span className="text-sm font-semibold text-gray-700">{item.category}</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-indigo-500 to-purple-500 h-2 rounded-full"
                      style={{ width: `${(item.count / 8) * 100}%` }}
                    ></div>
                  </div>
                  <Badge variant="primary">{item.count}</Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Summary Statistics */}
      <Card className="bg-gradient-to-br from-indigo-50 to-purple-50 border-t-4 border-indigo-600">
        <h3 className="text-xl font-bold text-gray-900 mb-4">📋 Summary</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-gray-600 mb-1">Total Match Score</p>
            <p className="text-2xl font-bold text-indigo-600">
              {(analyticsData.avgMatchScore * analyticsData.totalCandidates / 100).toFixed(0)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Success Rate</p>
            <p className="text-2xl font-bold text-purple-600">
              {((analyticsData.hiredCount / analyticsData.totalApplications) * 100).toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Avg Candidates per Job</p>
            <p className="text-2xl font-bold text-blue-600">
              {(analyticsData.totalApplications / analyticsData.totalJobs).toFixed(1)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Pending Applications</p>
            <p className="text-2xl font-bold text-orange-600">
              {analyticsData.totalApplications - (analyticsData.hiredCount * 15)}
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}
