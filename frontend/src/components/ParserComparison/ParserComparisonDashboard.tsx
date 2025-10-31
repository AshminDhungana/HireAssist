import React from 'react';
import { Loader } from 'lucide-react';
import { useParserComparison } from '../../hooks/useParserComparison';
import { ComparisonCard } from './ComparisonCard';
import { PerformanceChart } from './PerformanceChart';
import { ComparisonTable } from './ComparisonTable';

export const ParserComparisonDashboard: React.FC = () => {
  const { data: comparison, isLoading, error } = useParserComparison();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading parser comparison...</p>
        </div>
      </div>
    );
  }

  if (error || !comparison) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center p-8 bg-red-50 rounded-lg border border-red-200">
          <p className="text-red-600 font-semibold">
            Failed to load parser comparison data
          </p>
          <p className="text-red-500 text-sm mt-2">
            Please ensure the comparison script has been run
          </p>
        </div>
      </div>
    );
  }

  const isParserAWinner = comparison.winner === 'A';
  const isParserBWinner = comparison.winner === 'B';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Resume Parser Comparison
          </h1>
          <p className="text-gray-600 text-lg">
            Parser A (NLP) vs Parser B (Regex) - Performance Analysis
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          <ComparisonCard
            metrics={comparison.parserA}
            isWinner={isParserAWinner}
          />
          <ComparisonCard
            metrics={comparison.parserB}
            isWinner={isParserBWinner}
          />
        </div>

        <div className="bg-white rounded-lg shadow-md p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-8">
            Performance Metrics
          </h2>
          <PerformanceChart parserA={comparison.parserA} parserB={comparison.parserB} />
        </div>

        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Detailed Comparison
          </h2>
          <ComparisonTable
            parserA={comparison.parserA}
            parserB={comparison.parserB}
            winner={comparison.winner}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-lg border-l-4 border-blue-600 shadow-sm">
            <h3 className="text-lg font-bold text-blue-900 mb-3">🎯 Production Use</h3>
            <p className="text-gray-700 text-sm">
              Use <strong>Parser A (NLP)</strong> as the primary parser for
              production systems requiring high accuracy and comprehensive
              extraction.
            </p>
          </div>

          <div className="bg-gradient-to-br from-yellow-50 to-orange-50 p-6 rounded-lg border-l-4 border-yellow-600 shadow-sm">
            <h3 className="text-lg font-bold text-yellow-900 mb-3">
              🔄 Fallback Strategy
            </h3>
            <p className="text-gray-700 text-sm">
              Use <strong>Parser B (Regex)</strong> as a fallback option or for
              high-volume, low-accuracy scenarios.
            </p>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-lg border-l-4 border-green-600 shadow-sm">
            <h3 className="text-lg font-bold text-green-900 mb-3">
              ⚡ Future: Hybrid Approach
            </h3>
            <p className="text-gray-700 text-sm">
              Implement a hybrid parser combining both approaches for maximum
              coverage and accuracy.
            </p>
          </div>
        </div>

        <div className="text-center text-gray-500 text-sm">
          <p>
            Generated: {new Date(comparison.generatedAt).toLocaleDateString()}
            {' | '}
            {comparison.resumesTested} resume{comparison.resumesTested !== 1 ? 's' : ''} tested
          </p>
        </div>
      </div>
    </div>
  );
};
