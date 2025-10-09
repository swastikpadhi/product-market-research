import React from 'react';

export default function ProductMarketFitTab({ data, getFitScorePercent }) {
  if (!data) return null;

  return (
    <div className="space-y-3 animate-fadeIn">
      {/* Scorecard with Gauge */}
      <div className="border border-gray-200 rounded-lg p-6">
        <h5 className="font-semibold text-gray-900 mb-6 text-center text-sm">Product-Market Fit Score</h5>
        <div className="flex items-center justify-center mb-4">
          {/* Simple Progress Circle */}
          <div className="relative w-32 h-32">
            <svg className="transform -rotate-90 w-32 h-32">
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="#e5e7eb"
                strokeWidth="12"
                fill="none"
              />
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="url(#gradient)"
                strokeWidth="12"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 56}`}
                strokeDashoffset={`${2 * Math.PI * 56 * (1 - getFitScorePercent() / 100)}`}
                strokeLinecap="round"
                className="transition-all duration-1000"
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#8b5cf6" />
                  <stop offset="100%" stopColor="#3b82f6" />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
              <div className="text-3xl font-bold text-gray-900">{getFitScorePercent()}%</div>
              <div className="text-xs text-gray-600">Fit Score</div>
            </div>
          </div>
        </div>
        {data?.product_fit_score && (
          <p className="text-center text-sm text-gray-700">{data.product_fit_score}</p>
        )}
        
        <div className="grid grid-cols-2 gap-3 mt-6">
          {data?.success_probability && (
            <div className="text-center p-3 border border-gray-200 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Success Probability</div>
              <div className="text-sm font-semibold text-gray-900">{data.success_probability}</div>
            </div>
          )}
          {data?.time_to_market && (
            <div className="text-center p-3 border border-gray-200 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Time to Market</div>
              <div className="text-sm font-semibold text-gray-900">{data.time_to_market}</div>
            </div>
          )}
        </div>
      </div>

      {/* Opportunities vs Risks - Two Column Layout */}
      <div className="grid grid-cols-2 gap-3">
        {/* Opportunities */}
        {data.market_opportunities && data.market_opportunities.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <h5 className="font-semibold text-gray-900 mb-3 flex items-center text-sm">
              <span className="text-green-600 mr-2">✓</span>
              Opportunities
            </h5>
            <div className="space-y-1.5">
              {data.market_opportunities.map((opp, idx) => (
                <div key={idx} className="flex items-start">
                  <span className="text-green-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                  <span className="text-sm text-gray-700">{opp}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Risks */}
        {data.key_risks && data.key_risks.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <h5 className="font-semibold text-gray-900 mb-3 flex items-center text-sm">
              <span className="text-red-600 mr-2">!</span>
              Key Risks
            </h5>
            <div className="space-y-1.5">
              {data.key_risks.map((risk, idx) => (
                <div key={idx} className="flex items-start">
                  <span className="text-red-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                  <span className="text-sm text-gray-700">{risk}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

