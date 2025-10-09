import React from 'react';

export default function ExecutiveSummaryTab({ data }) {
  if (!data) return null;

  return (
    <div className="space-y-3 animate-fadeIn">
      {data.overview && (
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <span className="text-xl mr-2">📝</span>
              <h5 className="font-semibold text-gray-900 text-sm">Overview</h5>
            </div>
            {data.confidence_level && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-600">Confidence:</span>
                <span className="px-2.5 py-1 bg-green-600 text-white rounded-full text-xs font-medium">
                  {data.confidence_level}
                </span>
              </div>
            )}
          </div>
          <p className="text-sm text-gray-700 leading-relaxed">{data.overview}</p>
        </div>
      )}

      {/* Key Findings and Critical Success Factors */}
      <div className="grid grid-cols-2 gap-3">
        {data.key_findings && data.key_findings.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <h5 className="font-semibold text-gray-900 mb-3 text-sm">Key Findings</h5>
            <div className="space-y-1.5">
              {data.key_findings.map((finding, idx) => (
                <div key={idx} className="flex items-start">
                  <span className="text-green-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                  <span className="text-sm text-gray-700 leading-relaxed">{finding}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {data.critical_success_factors && data.critical_success_factors.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <h5 className="font-semibold text-gray-900 mb-3 text-sm">Critical Success Factors</h5>
            <div className="space-y-1.5">
              {data.critical_success_factors.map((factor, idx) => (
                <div key={idx} className="flex items-start">
                  <span className="text-purple-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                  <span className="text-sm text-gray-700 leading-relaxed">{factor}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {data.market_assessment && (
        <div className="border border-gray-200 rounded-lg p-4">
          <h5 className="font-semibold text-gray-900 mb-3 text-sm">Market Assessment</h5>
          <p className="text-sm text-gray-700 leading-relaxed">{data.market_assessment}</p>
        </div>
      )}
    </div>
  );
}

