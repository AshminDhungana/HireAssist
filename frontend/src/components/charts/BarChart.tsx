interface BarChartProps {
  data: { range: string; count: number }[]
}

export default function BarChart({ data }: BarChartProps) {
  const maxCount = Math.max(...data.map((d) => d.count))

  return (
    <div className="space-y-4">
      {data.map((item, idx) => (
        <div key={idx}>
          <div className="flex justify-between mb-1">
            <span className="text-sm font-semibold text-gray-700">{item.range}</span>
            <span className="text-sm font-bold text-gray-900">{item.count}</span>
          </div>
          <div className="bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-500 to-indigo-500 h-3 rounded-full transition-all"
              style={{ width: `${(item.count / maxCount) * 100}%` }}
            ></div>
          </div>
        </div>
      ))}
    </div>
  )
}
