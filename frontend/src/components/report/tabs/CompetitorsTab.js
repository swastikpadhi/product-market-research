import React from 'react';

export default function CompetitorsTab({ data }) {
  if (!data) return null;

  return (
    <div className="space-y-3 animate-fadeIn">
      {data?.competitive_landscape && (
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="flex items-center mb-3">
            <span className="text-xl mr-2">🏢</span>
            <h5 className="font-semibold text-gray-900 text-sm">Competitive Landscape Overview</h5>
          </div>
          <p className="text-sm text-gray-700 leading-relaxed">{data.competitive_landscape}</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        {data.market_leaders && data.market_leaders.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <h5 className="font-semibold text-gray-900 mb-3 flex items-center text-sm">
              <span className="text-yellow-500 mr-2">👑</span>
              Market Leaders
            </h5>
            <div className="space-y-1.5">
              {data.market_leaders.map((leader, idx) => (
                <div key={idx} className="flex items-start">
                  <span className="text-yellow-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                  <span className="text-sm text-gray-700">{leader}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {data.key_competitors && data.key_competitors.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <h5 className="font-semibold text-gray-900 mb-3 flex items-center text-sm">
              <span className="text-blue-500 mr-2">🏢</span>
              Key Competitors
            </h5>
            <div className="space-y-1.5">
              {data.key_competitors.map((comp, idx) => (
                <div key={idx} className="flex items-start">
                  <span className="text-blue-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                  <span className="text-sm text-gray-700">{comp}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {data.competitive_gaps && data.competitive_gaps.length > 0 && (
        <div className="border border-gray-200 rounded-lg p-4">
          <h5 className="font-semibold text-gray-900 mb-3 flex items-center text-sm">
            <span className="text-green-600 mr-2">🎯</span>
            Market Gaps & Opportunities
          </h5>
          <div className="space-y-1.5">
            {data.competitive_gaps.map((gap, idx) => (
              <div key={idx} className="flex items-start">
                <span className="text-green-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                <span className="text-sm text-gray-700">{gap}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {data?.pricing_landscape && (
        <div className="border border-gray-200 rounded-lg p-4">
          <h5 className="font-semibold text-gray-900 mb-3 text-sm">Pricing Landscape</h5>
          <p className="text-sm text-gray-700 leading-relaxed">{data.pricing_landscape}</p>
        </div>
      )}
    </div>
  );
}

