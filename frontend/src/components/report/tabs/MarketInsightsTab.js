import React from 'react';

export default function MarketInsightsTab({ data }) {
  if (!data) return null;

  return (
    <div className="space-y-3 animate-fadeIn">
      {/* Market Size and Growth Rate */}
      <div className="grid grid-cols-2 gap-3">
        {data.market_size && (
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <span className="text-xl mr-2">📊</span>
              <h5 className="font-semibold text-gray-900 text-sm">Market Size</h5>
            </div>
            <div className="space-y-2">
              {typeof data.market_size === 'string' ? (
                <p className="text-sm text-gray-700 leading-relaxed">{data.market_size}</p>
              ) : (
                <>
                  {data.market_size.current && (
                    <div>
                      <p className="text-xs text-gray-600 mb-1">Current Market</p>
                      <p className="text-sm font-semibold text-gray-900">{data.market_size.current}</p>
                    </div>
                  )}
                  {data.market_size.projected && (
                    <div>
                      <p className="text-xs text-gray-600 mb-1">Projected Market</p>
                      <p className="text-sm font-semibold text-gray-900">{data.market_size.projected}</p>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}

        {data.growth_rate && (
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <span className="text-xl mr-2">📈</span>
              <h5 className="font-semibold text-gray-900 text-sm">Growth Rate</h5>
            </div>
            <p className="text-sm text-gray-700 leading-relaxed">{data.growth_rate}</p>
          </div>
        )}
      </div>

      {/* Key Trends and Market Drivers */}
      <div className="grid grid-cols-2 gap-3">
        {data.key_trends && data.key_trends.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <h5 className="font-semibold text-gray-900 mb-3 flex items-center text-sm">
              <span className="text-blue-500 mr-2">🔍</span>
              Key Market Trends
            </h5>
            <div className="space-y-1.5">
              {data.key_trends.map((trend, idx) => (
                <div key={idx} className="flex items-start">
                  <span className="text-blue-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                  <span className="text-sm text-gray-700 leading-relaxed">{trend}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {data.market_drivers && data.market_drivers.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <h5 className="font-semibold text-gray-900 mb-3 flex items-center text-sm">
              <span className="text-green-500 mr-2">🚀</span>
              Market Drivers
            </h5>
            <div className="space-y-1.5">
              {data.market_drivers.map((driver, idx) => (
                <div key={idx} className="flex items-start">
                  <span className="text-green-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                  <span className="text-sm text-gray-700 leading-relaxed">{driver}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Future Outlook */}
      {data.future_outlook && (
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="flex items-center mb-3">
            <span className="text-xl mr-2">🔮</span>
            <h5 className="font-semibold text-gray-900 text-sm">Future Outlook</h5>
          </div>
          <p className="text-sm text-gray-700 leading-relaxed">{data.future_outlook}</p>
        </div>
      )}

      {/* No Data Message */}
      {(!data.market_size && !data.growth_rate && (!data.key_trends || data.key_trends.length === 0) && (!data.market_drivers || data.market_drivers.length === 0) && !data.future_outlook) && (
        <div className="text-center py-8 text-gray-500">
          <p>No market insights data available</p>
        </div>
      )}
    </div>
  );
}
