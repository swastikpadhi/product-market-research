import React from 'react';
import { Download, XCircle, RefreshCw, Trash2, FileText } from 'lucide-react';
import {
  ExecutiveSummaryTab,
  MarketInsightsTab,
  CompetitorsTab,
  CustomerInsightsTab,
  ProductMarketFitTab,
  StrategyTab
} from '../report/tabs';
import ReportSummaryCards from '../report/ReportSummaryCards';
import ReportTabNavigation from '../report/ReportTabNavigation';

export default function ResearchTaskCard({
  task,
  idx,
  showFullReport,
  toggleFullReport,
  reportData,
  loadingReports,
  reportTabs,
  setReportTabs,
  getStatusIcon,
  getResearchConfig,
  exportResults,
  fetchReport,
  abortTask,
  rerunTask,
  deleteTask
}) {
  const isExpanded = showFullReport[task.request_id];
  const report = reportData[task.request_id]?.result?.final_report || {};
  const currentReportTab = reportTabs[task.request_id] || 'summary';
  
  const setCurrentReportTab = (tabId) => {
    setReportTabs(prev => ({
      ...prev,
      [task.request_id]: tabId
    }));
  };
  
  const getFitScorePercent = () => {
    const score = report.pmf_assessment?.product_fit_score || '';
    const match = score.match(/(\d+)/);
    return match ? parseInt(match[0]) : 70;
  };

  const handleCardClick = async (e) => {
    // Prevent collapse when user is selecting text
    const selection = window.getSelection();
    if (selection && selection.toString().length > 0) {
      return;
    }
    if (task.status === 'completed') {
      // Fetch report if not already loaded
      if (!reportData[task.request_id] && fetchReport) {
        try {
          await fetchReport(task.request_id);
        } catch (err) {
          console.error('Failed to fetch report:', err);
        }
      }
      
      toggleFullReport(task.request_id);
    }
  };

  return (
    <div 
      key={task.request_id} 
      className="bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition-all duration-200 cursor-pointer fade-in"
      style={{ animationDelay: `${idx * 30}ms`, animationFillMode: 'both' }}
      onClick={handleCardClick}
    >
      <div className="p-4">
        <div className="flex items-center justify-between gap-4">
          {/* Left: Status Icon + Content */}
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className="shrink-0">
              {getStatusIcon(task.status)}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="font-semibold text-gray-900 text-base truncate max-w-xl" title={task.product_idea || `${task.sector || 'Unknown Sector'} Product Validation`}>
                  {task.product_idea || `${task.sector || 'Unknown Sector'} Product Validation`}
                </h3>
                {task.research_depth && (
                  <span className={`${getResearchConfig(task.research_depth).color} text-xs px-2 py-0.5 shrink-0 rounded-full inline-flex items-center font-semibold`}>
                    {getResearchConfig(task.research_depth).label}
                  </span>
                )}
              </div>
            </div>
          </div>
          
          {/* Right: Action Icons or Loading Indicator */}
          <div className="flex items-center gap-1 shrink-0 min-h-[40px]">
            {loadingReports[task.request_id] ? (
              <div className="flex items-center gap-2 text-blue-600 p-2">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
                <span className="text-sm font-medium">Loading...</span>
              </div>
            ) : (
              <>
                {task.status === 'completed' && (
                  <button
                    className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    onClick={(e) => {
                      e.stopPropagation();
                      exportResults(task);
                    }}
                    title="Export results as JSON"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                )}
                {task.status === 'processing' ? (
                  <button
                    className="p-2 text-gray-600 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                    onClick={(e) => {
                      e.stopPropagation();
                      abortTask(task.request_id);
                    }}
                    title="Abort this task"
                  >
                    <XCircle className="w-4 h-4" />
                  </button>
                ) : (
                  <>
                    <button
                      className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      onClick={(e) => {
                        e.stopPropagation();
                        rerunTask(task);
                      }}
                      title="Re-run this validation"
                    >
                      <RefreshCw className="w-4 h-4" />
                    </button>
                    <button
                      className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteTask(task.request_id);
                      }}
                      title="Delete this task"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </>
                )}
              </>
            )}
          </div>
        </div>
      </div>
      
      {/* Expandable Report Section with Animation */}
      <div 
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isExpanded ? 'max-h-[5000px] opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="border-t border-gray-200 bg-gradient-to-br from-gray-50 to-white p-6">
          {loadingReports[task.request_id] ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Loading report...</span>
            </div>
          ) : reportData[task.request_id] ? (
            <div className="space-y-6">
              {/* Key Metrics Summary Row */}
              <ReportSummaryCards report={report} task={task} />

              {/* Tabs Navigation */}
              <ReportTabNavigation 
                report={report} 
                currentTab={currentReportTab} 
                onTabChange={setCurrentReportTab} 
              />

              {/* Tab Content */}
              <div className="min-h-[400px]">
                {/* Show message if no data available */}
                {!report.executive_summary && !report.market_insights && !report.competitive_landscape && !report.customer_insights && !report.pmf_assessment && !report.strategic_recommendations && (
                  <div className="flex flex-col items-center justify-center py-16 text-gray-500">
                    <FileText className="w-12 h-12 mb-4 text-gray-400" />
                    <p className="text-lg font-medium">No report data available</p>
                    <p className="text-sm mt-2">The analysis may still be processing or incomplete.</p>
                  </div>
                )}
                
                {/* Executive Summary Tab */}
                {currentReportTab === 'summary' && report.executive_summary && (
                  <ExecutiveSummaryTab data={report.executive_summary} />
                )}

                {/* Market Insights Tab */}
                {currentReportTab === 'market' && report.market_insights && (
                  <MarketInsightsTab data={report.market_insights} />
                )}

                {/* Competitors Tab */}
                {currentReportTab === 'competitors' && report.competitive_landscape && (
                  <CompetitorsTab data={report.competitive_landscape} />
                )}

                {/* Customer Insights Tab */}
                {currentReportTab === 'customers' && report.customer_insights && (
                  <CustomerInsightsTab data={report.customer_insights} />
                )}

                {/* PMF Assessment Tab */}
                {currentReportTab === 'pmf' && report.pmf_assessment && (
                  <ProductMarketFitTab data={report.pmf_assessment} getFitScorePercent={getFitScorePercent} />
                )}

                {/* Strategic Recommendations Tab */}
                {currentReportTab === 'recommendations' && report.strategic_recommendations && (
                  <StrategyTab data={report.strategic_recommendations} />
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>Report data not available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

