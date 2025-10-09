import React from 'react';

export default function ReportSummaryCards({ report, task }) {
  if (!report.market_insights && !report.pmf_assessment) {
    return null;
  }

  // Calculate actual analysis time from timestamps
  const calculateAnalysisTime = () => {
    if (!task.started_at || !task.completed_at) {
      return 'N/A';
    }
    
    const startTime = new Date(task.started_at);
    const endTime = new Date(task.completed_at);
    const durationMs = endTime - startTime;
    
    if (isNaN(durationMs) || durationMs < 0) {
      return 'N/A';
    }
    
    const minutes = Math.floor(durationMs / 60000);
    const seconds = Math.floor((durationMs % 60000) / 1000);
    
    if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    } else {
      return `${seconds}s`;
    }
  };

  // Extract just the percentage from PMF score (e.g., "85%" from "85% - Strong fit")
  const extractPercentage = (score) => {
    if (!score) return 'N/A';
    const match = score.match(/(\d+%)/);
    return match ? match[1] : score;
  };

  // Handle market_size as either string or object with current and projected
  const marketSizeObj = report.market_insights?.market_size;
  const marketSize = marketSizeObj ? 
    (typeof marketSizeObj === 'string' ? 
      marketSizeObj : 
      [marketSizeObj.current, marketSizeObj.projected]
        .filter(val => val && val !== 'Data unavailable' && val !== 'N/A')
        .join(', ') || 'N/A'
    ) : 'N/A';
  const growthRate = report.market_insights?.growth_rate || 'N/A';

  return (
    <div className="grid grid-cols-4 gap-4 mb-6">
      {/* Market Size Card */}
      <div className="bg-white border border-blue-200 rounded-lg p-4 shadow-sm h-[72px] flex flex-col">
        <div className="text-xs font-medium text-blue-600 mb-1">Market Size</div>
        <div className="text-sm font-bold text-gray-900 truncate flex-1" title={marketSize}>
          {marketSize}
        </div>
      </div>

      {/* Growth Rate Card */}
      <div className="bg-white border border-green-200 rounded-lg p-4 shadow-sm h-[72px] flex flex-col">
        <div className="text-xs font-medium text-green-600 mb-1">Growth Rate</div>
        <div className="text-sm font-bold text-gray-900 truncate flex-1" title={growthRate}>
          {growthRate}
        </div>
      </div>

      {/* PMF Score Card - Only show percentage */}
      <div className="bg-white border border-purple-200 rounded-lg p-4 shadow-sm h-[72px] flex flex-col">
        <div className="text-xs font-medium text-purple-600 mb-1">PMF Score</div>
        <div className="text-sm font-bold text-gray-900 flex-1">
          {extractPercentage(report.pmf_assessment?.product_fit_score)}
        </div>
      </div>

      {/* Analysis Time Card */}
      <div className="bg-white border border-orange-200 rounded-lg p-4 shadow-sm h-[72px] flex flex-col">
        <div className="text-xs font-medium text-orange-600 mb-1">Analysis Time</div>
        <div className="text-sm font-bold text-gray-900 flex-1">
          {calculateAnalysisTime()}
        </div>
      </div>
    </div>
  );
}

