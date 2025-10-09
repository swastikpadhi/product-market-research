import React from 'react';

export default function ReportTabNavigation({ report, currentTab, onTabChange }) {
  const tabs = [
    { id: 'summary', label: 'Executive Summary', icon: '📊', hasData: report.executive_summary },
    { id: 'market', label: 'Market Insights', icon: '📈', hasData: report.market_insights },
    { id: 'competitors', label: 'Competitors', icon: '🏢', hasData: report.competitive_landscape },
    { id: 'customers', label: 'Customer Insights', icon: '👥', hasData: report.customer_insights },
    { id: 'pmf', label: 'Product-Market Fit', icon: '🎯', hasData: report.pmf_assessment },
    { id: 'recommendations', label: 'Strategy', icon: '💡', hasData: report.strategic_recommendations }
  ];

  return (
    <div className="flex justify-between border-b border-gray-200 mb-6">
      {tabs.filter(tab => tab.hasData).map(tab => (
        <button
          key={tab.id}
          onClick={(e) => {
            e.stopPropagation();
            onTabChange(tab.id);
          }}
          className={`px-4 py-2.5 text-sm font-medium transition-all duration-200 border-b-2 cursor-pointer ${
            currentTab === tab.id
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
          }`}
        >
          <span className="mr-1.5">{tab.icon}</span>
          {tab.label}
        </button>
      ))}
    </div>
  );
}

