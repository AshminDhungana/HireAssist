import React from 'react';
import { ParserMetrics } from '../../types/parser';

interface ComparisonCardProps {
  metrics: ParserMetrics;
  isWinner: boolean;
}

export const ComparisonCard: React.FC<ComparisonCardProps> = ({
  metrics,
  isWinner,
}) => {
  const getRatingStars = (isWinner: boolean) => {
    if (metrics.type === 'npl') {
      return '★★★★★';
    }
    return isWinner ? '★★★★☆' : '★★★☆☆';
  };

  const getBadgeColor = (isWinner: boolean) => {
    if (metrics.type === 'npl') {
      return 'bg-gradient-to-r from-blue-600 to-purple-600 text-white';
    }
    return isWinner
      ? 'bg-yellow-100 text-yellow-700'
      : 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow p-8 border-l-4 border-blue-600">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">{metrics.name}</h2>
        <div
          className={`px-4 py-2 rounded-full text-sm font-bold ${getBadgeColor(
            isWinner
          )}`}
        >
          {getRatingStars(isWinner)}
          {isWinner && metrics.type === 'npl' && ' WINNER'}
        </div>
      </div>

      <div className="space-y-4">
        <div className="border-b border-gray-200 pb-4">
          <p className="text-gray-600 text-sm font-medium">Skills Detected</p>
          <p className="text-4xl font-bold text-blue-600 mt-1">
            {metrics.skillsExtracted}
          </p>
        </div>

        <div className="border-b border-gray-200 pb-4">
          <p className="text-gray-600 text-sm font-medium">
            Experience Extracted
          </p>
          <p
            className={`text-4xl font-bold mt-1 ${
              metrics.experienceYears > 0
                ? 'text-green-600'
                : 'text-red-600'
            }`}
          >
            {metrics.experienceYears > 0
              ? `${metrics.experienceYears} years ✓`
              : '0 years ✗'}
          </p>
        </div>

        <div className="border-b border-gray-200 pb-4">
          <p className="text-gray-600 text-sm font-medium">Parsing Time</p>
          <p className="text-4xl font-bold text-orange-600 mt-1">
            {metrics.parsingTimeMs.toFixed(2)}ms
          </p>
        </div>

        <div className="border-b border-gray-200 pb-4">
          <p className="text-gray-600 text-sm font-medium">Success Rate</p>
          <p className="text-4xl font-bold text-green-600 mt-1">
            {metrics.successRate}%
          </p>
        </div>

        <div>
          <p className="text-gray-600 text-sm font-medium">Accuracy</p>
          <p className="text-4xl font-bold text-purple-600 mt-1">
            {metrics.accuracyEstimate}
          </p>
        </div>
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-gray-700">
          {metrics.type === 'npl' ? (
            <>
              <strong>Recommendation:</strong> Use as primary parser for
              production systems requiring high accuracy.
            </>
          ) : (
            <>
              <strong>Recommendation:</strong> Use as fallback or for
              high-volume, low-accuracy scenarios.
            </>
          )}
        </p>
      </div>
    </div>
  );
};
