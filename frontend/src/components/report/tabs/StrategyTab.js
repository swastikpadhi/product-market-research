import React from 'react';

export default function StrategyTab({ data }) {
  if (!data) return null;

  return (
    <div className="space-y-3 animate-fadeIn">
      {/* Immediate Actions */}
      {data.immediate_actions && data.immediate_actions.length > 0 && (
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="flex items-center mb-3">
            <span className="text-xl mr-2">🚀</span>
            <h5 className="font-semibold text-gray-900 text-sm">Immediate Actions</h5>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {data.immediate_actions.map((action, idx) => (
              <div key={idx} className="flex items-start text-sm text-gray-700">
                <span className="text-red-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                <span>{action}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Two Column Layout for Other Sections */}
      <div className="grid grid-cols-2 gap-3">
        {/* Product Development */}
        {data.product_development && data.product_development.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <span className="text-xl mr-2">🔧</span>
              <h5 className="font-semibold text-gray-900 text-sm">Product Development</h5>
            </div>
            <div className="space-y-1.5">
              {data.product_development.map((item, idx) => (
                <div key={idx} className="flex items-start text-sm text-gray-700">
                  <span className="text-blue-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Market Entry */}
        {data.market_entry && data.market_entry.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <span className="text-xl mr-2">🎯</span>
              <h5 className="font-semibold text-gray-900 text-sm">Market Entry Strategy</h5>
            </div>
            <div className="space-y-1.5">
              {data.market_entry.map((item, idx) => (
                <div key={idx} className="flex items-start text-sm text-gray-700">
                  <span className="text-green-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Competitive Strategy */}
        {data.competitive_strategy && data.competitive_strategy.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <span className="text-xl mr-2">⚔️</span>
              <h5 className="font-semibold text-gray-900 text-sm">Competitive Strategy</h5>
            </div>
            <div className="space-y-1.5">
              {data.competitive_strategy.map((item, idx) => (
                <div key={idx} className="flex items-start text-sm text-gray-700">
                  <span className="text-purple-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Success Metrics */}
        {data.success_metrics && data.success_metrics.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <span className="text-xl mr-2">📊</span>
              <h5 className="font-semibold text-gray-900 text-sm">Success Metrics</h5>
            </div>
            <div className="space-y-1.5">
              {data.success_metrics.map((metric, idx) => (
                <div key={idx} className="flex items-start text-sm text-gray-700">
                  <span className="text-gray-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                  <span>{metric}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

