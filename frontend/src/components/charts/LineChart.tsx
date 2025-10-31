interface LineChartProps {
  data: { date: string; count: number }[]
}

export default function LineChart({ data }: LineChartProps) {
  const maxCount = Math.max(...data.map((d) => d.count))
  const minCount = Math.min(...data.map((d) => d.count))
  const range = maxCount - minCount || 1

  return (
    <div className="h-64 relative">
      <svg className="w-full h-full" viewBox="0 0 800 200" preserveAspectRatio="none">
        {/* Grid lines */}
        {[0, 1, 2, 3, 4].map((i) => (
          <line
            key={`grid-${i}`}
            x1="0"
            y1={(i * 200) / 4}
            x2="800"
            y2={(i * 200) / 4}
            stroke="#e5e7eb"
            strokeWidth="1"
          />
        ))}

        {/* Line */}
        <polyline
          points={data
            .map(
              (d, i) =>
                `${(i / (data.length - 1)) * 800},${200 - ((d.count - minCount) / range) * 200}`
            )
            .join(' ')}
          fill="none"
          stroke="url(#gradient)"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Gradient */}
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="1" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.1" />
          </linearGradient>
        </defs>

        {/* Area under line */}
        <polygon
          points={`0,200 ${data
            .map(
              (d, i) =>
                `${(i / (data.length - 1)) * 800},${200 - ((d.count - minCount) / range) * 200}`
            )
            .join(' ')} 800,200`}
          fill="url(#gradient)"
        />

        {/* Points */}
        {data.map((d, i) => (
          <circle
            key={`point-${i}`}
            cx={(i / (data.length - 1)) * 800}
            cy={200 - ((d.count - minCount) / range) * 200}
            r="4"
            fill="#3b82f6"
          />
        ))}
      </svg>

      {/* Labels */}
      <div className="flex justify-between text-xs text-gray-600 mt-2">
        {data.map((d, i) => (
          i % Math.ceil(data.length / 5) === 0 && (
            <span key={`label-${i}`}>{d.date}</span>
          )
        ))}
      </div>
    </div>
  )
}
