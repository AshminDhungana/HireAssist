import React from 'react';
import { ParserMetrics } from '../../types/parser';

interface ComparisonTableProps {
  parserA: ParserMetrics;
  parserB: ParserMetrics;
  winner: 'A' | 'B' | 'tie';
}

export const ComparisonTable: React.FC<ComparisonTableProps> = ({
  parserA,
  parserB,
  winner,
}) => {
  const getWinnerColor = (isWinner: boolean) => {
    if (isWinner) return 'text-blue-600 font-bold';
    return 'text-gray-600';
  };

  const metrics = [
    {
      name: 'Skills Detected',
      a: parserA.skillsExtracted,
      b: parserB.skillsExtracted,
      winner: parserA.skillsExtracted > parserB.skillsExtracted ? 'A' : 'B',
    },
    {
      name: 'Experience Extraction',
      a: parserA.experienceYears > 0 ? `${parserA.experienceYears} years ✓` : '0 years ✗',
      b: parserB.experienceYears > 0 ? `${parserB.experienceYears} years ✓` : '0 years ✗',
      winner: parserA.experienceYears > parserB.experienceYears ? 'A' : 'B',
    },
    {
      name: 'Parsing Time (ms)',
      a: parserA.parsingTimeMs.toFixed(2),
      b: parserB.parsingTimeMs.toFixed(2),
      winner: parserA.parsingTimeMs < parserB.parsingTimeMs ? 'A' : 'B',
    },
    {
      name: 'Success Rate',
      a: `${parserA.successRate}%`,
      b: `${parserB.successRate}%`,
      winner: 'tie',
    },
    {
      name: 'Accuracy Estimate',
      a: parserA.accuracyEstimate,
      b: parserB.accuracyEstimate,
      winner: 'A',
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-100 border-b-2 border-gray-300">
            <tr>
              <th className="text-left py-4 px-6 font-bold text-gray-800">
                Metric
              </th>
              <th className="text-center py-4 px-6 font-bold text-blue-600">
                Parser A (NLP)
              </th>
              <th className="text-center py-4 px-6 font-bold text-orange-600">
                Parser B (Regex)
              </th>
              <th className="text-center py-4 px-6 font-bold text-green-600">
                Winner
              </th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((metric, index) => (
              <tr
                key={index}
                className="border-b border-gray-200 hover:bg-gray-50 transition-colors"
              >
                <td className="py-4 px-6 font-semibold text-gray-900">
                  {metric.name}
                </td>
                <td
                  className={`text-center py-4 px-6 ${getWinnerColor(
                    metric.winner === 'A'
                  )}`}
                >
                  {metric.a}
                </td>
                <td
                  className={`text-center py-4 px-6 ${getWinnerColor(
                    metric.winner === 'B'
                  )}`}
                >
                  {metric.b}
                </td>
                <td className="text-center py-4 px-6 font-bold text-green-600">
                  {metric.winner === 'A' && 'Parser A ✓'}
                  {metric.winner === 'B' && 'Parser B ✓'}
                  {metric.winner === 'tie' && 'Tie ═'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
