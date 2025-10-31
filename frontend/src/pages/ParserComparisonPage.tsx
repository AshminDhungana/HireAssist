import React from 'react';

export const ParserComparisonPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          📊 Resume Parser Comparison
        </h1>
        
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 mb-6">
          <p className="text-blue-900 font-semibold mb-2">✅ Dashboard Working!</p>
          <p className="text-blue-800 text-sm">
            Parser A vs Parser B Performance Analysis
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Parser A Card */}
          <div className="bg-white border-2 border-blue-400 rounded-lg p-6 shadow-md">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Parser A (NLP) ⭐ WINNER
            </h2>
            <div className="space-y-4 bg-blue-50 p-4 rounded">
              <div>
                <p className="text-gray-600 text-sm">Skills Detected</p>
                <p className="text-3xl font-bold text-blue-600">41</p>
              </div>
              <div>
                <p className="text-gray-600 text-sm">Experience Extracted</p>
                <p className="text-3xl font-bold text-green-600">4 years ✓</p>
              </div>
              <div>
                <p className="text-gray-600 text-sm">Parsing Time</p>
                <p className="text-3xl font-bold text-orange-600">105.79ms</p>
              </div>
              <div>
                <p className="text-gray-600 text-sm">Success Rate</p>
                <p className="text-3xl font-bold text-green-600">100%</p>
              </div>
              <div>
                <p className="text-gray-600 text-sm">Accuracy Estimate</p>
                <p className="text-3xl font-bold text-purple-600">90%+</p>
              </div>
            </div>
          </div>

          {/* Parser B Card */}
          <div className="bg-white border-2 border-orange-400 rounded-lg p-6 shadow-md">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Parser B (Regex)
            </h2>
            <div className="space-y-4 bg-orange-50 p-4 rounded">
              <div>
                <p className="text-gray-600 text-sm">Skills Detected</p>
                <p className="text-3xl font-bold text-orange-600">15</p>
              </div>
              <div>
                <p className="text-gray-600 text-sm">Experience Extracted</p>
                <p className="text-3xl font-bold text-red-600">0 years ✗</p>
              </div>
              <div>
                <p className="text-gray-600 text-sm">Parsing Time</p>
                <p className="text-3xl font-bold text-orange-600">113.86ms</p>
              </div>
              <div>
                <p className="text-gray-600 text-sm">Success Rate</p>
                <p className="text-3xl font-bold text-green-600">100%</p>
              </div>
              <div>
                <p className="text-gray-600 text-sm">Accuracy Estimate</p>
                <p className="text-3xl font-bold text-orange-600">60%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Comparison Table */}
        <div className="mt-8 bg-white border-2 border-gray-300 rounded-lg overflow-hidden shadow-md">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4">
            <h3 className="text-xl font-bold text-white">📋 Detailed Comparison</h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-100 border-b-2 border-gray-300">
                <tr>
                  <th className="text-left p-4 font-bold text-gray-900">Metric</th>
                  <th className="text-center p-4 font-bold text-blue-600">Parser A (NLP)</th>
                  <th className="text-center p-4 font-bold text-orange-600">Parser B (Regex)</th>
                  <th className="text-center p-4 font-bold text-green-600">Winner</th>
                </tr>
              </thead>
              <tbody className="bg-white">
                <tr className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="p-4 font-semibold text-gray-900">Skills Detected</td>
                  <td className="text-center p-4 text-blue-600 font-bold">41</td>
                  <td className="text-center p-4">15</td>
                  <td className="text-center p-4 font-bold text-blue-600">Parser A ✓</td>
                </tr>
                <tr className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="p-4 font-semibold text-gray-900">Experience Extraction</td>
                  <td className="text-center p-4 text-blue-600 font-bold">4 years ✓</td>
                  <td className="text-center p-4">0 years ✗</td>
                  <td className="text-center p-4 font-bold text-blue-600">Parser A ✓</td>
                </tr>
                <tr className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="p-4 font-semibold text-gray-900">Parsing Time (ms)</td>
                  <td className="text-center p-4 text-blue-600 font-bold">105.79</td>
                  <td className="text-center p-4">113.86</td>
                  <td className="text-center p-4 font-bold text-blue-600">Parser A ✓</td>
                </tr>
                <tr className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="p-4 font-semibold text-gray-900">Success Rate</td>
                  <td className="text-center p-4">100%</td>
                  <td className="text-center p-4">100%</td>
                  <td className="text-center p-4 font-bold text-gray-600">Tie ═</td>
                </tr>
                <tr className="hover:bg-gray-50">
                  <td className="p-4 font-semibold text-gray-900">Accuracy Estimate</td>
                  <td className="text-center p-4 text-blue-600 font-bold">90%+</td>
                  <td className="text-center p-4">60%</td>
                  <td className="text-center p-4 font-bold text-blue-600">Parser A ✓</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Recommendations */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-blue-50 border-l-4 border-blue-600 p-6 rounded-lg shadow-md">
            <h4 className="font-bold text-blue-900 mb-2 text-lg">🎯 Production Use</h4>
            <p className="text-sm text-blue-800">
              Use Parser A (NLP) as the primary parser for production systems requiring high accuracy and comprehensive extraction.
            </p>
          </div>
          <div className="bg-yellow-50 border-l-4 border-yellow-600 p-6 rounded-lg shadow-md">
            <h4 className="font-bold text-yellow-900 mb-2 text-lg">🔄 Fallback Strategy</h4>
            <p className="text-sm text-yellow-800">
              Use Parser B (Regex) as a fallback option or for high-volume, low-accuracy scenarios.
            </p>
          </div>
          <div className="bg-green-50 border-l-4 border-green-600 p-6 rounded-lg shadow-md">
            <h4 className="font-bold text-green-900 mb-2 text-lg">⚡ Future: Hybrid Approach</h4>
            <p className="text-sm text-green-800">
              Implement a hybrid parser combining both approaches for maximum coverage and accuracy.
            </p>
          </div>
        </div>

        <div className="mt-8 p-6 bg-gradient-to-r from-gray-100 to-gray-200 rounded-lg text-center border border-gray-300">
          <p className="text-gray-700 font-semibold">
            ✅ Dashboard is working!
          </p>
        </div>
      </div>
    </div>
  );
};

export default ParserComparisonPage;
