import React from 'react';
import { Bar, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import type { ParserMetrics } from '../../types/parser';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface PerformanceChartProps {
  parserA: ParserMetrics;
  parserB: ParserMetrics;
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({
  parserA,
  parserB,
}) => {
  const skillsChartData = {
    labels: ['Parser A (NLP)', 'Parser B (Regex)'],
    datasets: [
      {
        label: 'Skills Detected',
        data: [parserA.skillsExtracted, parserB.skillsExtracted],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(249, 115, 22, 0.8)',
        ],
        borderColor: ['rgb(59, 130, 246)', 'rgb(249, 115, 22)'],
        borderWidth: 2,
        borderRadius: 8,
      },
    ],
  };

  const performanceChartData = {
    labels: ['Parser A (NLP)', 'Parser B (Regex)'],
    datasets: [
      {
        label: 'Parsing Time (ms)',
        data: [parserA.parsingTimeMs, parserB.parsingTimeMs],
        backgroundColor: [
          'rgba(59, 130, 246, 0.1)',
          'rgba(249, 115, 22, 0.1)',
        ],
        borderColor: ['rgb(59, 130, 246)', 'rgb(249, 115, 22)'],
        borderWidth: 2,
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
      },
      title: {
        display: true,
        font: { size: 14, weight: 'bold' as const },  // ✅ FIXED: Add 'as const'
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  } as const;  // ✅ FIXED: Add 'as const' at the end

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          Skills Detection Comparison
        </h3>
        <div style={{ height: '300px' }}>
          <Bar
            data={skillsChartData}
            options={{
              ...chartOptions,
              scales: {
                y: {
                  beginAtZero: true,
                  max: 50,
                },
              },
            }}
          />
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          Parsing Performance (Lower is Better)
        </h3>
        <div style={{ height: '300px' }}>
          <Line
            data={performanceChartData}
            options={{
              ...chartOptions,
              scales: {
                y: {
                  beginAtZero: true,
                  max: 150,
                },
              },
            }}
          />
        </div>
      </div>
    </div>
  );
};
