interface PieChartProps {
  data: { label: string; value: number }[]
}

export default function PieChart({ data }: PieChartProps) {
  const total = data.reduce((sum, item) => sum + item.value, 0)
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

  let currentAngle = -90

  return (
    <div className="flex items-center justify-center">
      <svg width="200" height="200" viewBox="0 0 200 200">
        {data.map((item, idx) => {
          const sliceAngle = (item.value / total) * 360
          const endAngle = currentAngle + sliceAngle

          const x1 = 100 + 80 * Math.cos((currentAngle * Math.PI) / 180)
          const y1 = 100 + 80 * Math.sin((currentAngle * Math.PI) / 180)
          const x2 = 100 + 80 * Math.cos((endAngle * Math.PI) / 180)
          const y2 = 100 + 80 * Math.sin((endAngle * Math.PI) / 180)

          const largeArc = sliceAngle > 180 ? 1 : 0

          const pathData = [
            `M 100 100`,
            `L ${x1} ${y1}`,
            `A 80 80 0 ${largeArc} 1 ${x2} ${y2}`,
            'Z',
          ].join(' ')

          currentAngle = endAngle

          return (
            <path
              key={idx}
              d={pathData}
              fill={colors[idx % colors.length]}
              stroke="white"
              strokeWidth="2"
            />
          )
        })}
      </svg>
    </div>
  )
}
