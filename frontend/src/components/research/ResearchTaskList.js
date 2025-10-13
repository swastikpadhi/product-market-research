import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { FileText, Clock, CheckCircle, AlertCircle, TrendingUp, Search } from 'lucide-react';
import ResearchTaskCard from './ResearchTaskCard';
import ResearchSearch from './ResearchSearch';
import Pagination from '../ui/Pagination';
import { getResearchConfig } from '../../constants/researchConfig';
import { API_BASE } from '../../config/api';

export default function ResearchTaskList({
  researchTasks,
  isLoadingTasks,
  totalTasks,
  totalPages,
  currentPage,
  statusFilter,
  setStatusFilter,
  setCurrentPage,
  showFullReport,
  toggleFullReport,
  reportData,
  loadingReports,
  reportTabs,
  setReportTabs,
  getStatusIcon,
  exportResults,
  fetchReport,
  abortTask,
  rerunTask,
  deleteTask,
  setActiveTab,
  fetchSearches,
  onSearchModeChange
}) {
  const [searchResults, setSearchResults] = useState(null);
  const [isSearchMode, setIsSearchMode] = useState(false);
  const [searchPagination, setSearchPagination] = useState({
    page: 1,
    totalPages: 1,
    total: 0
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [highlightedTaskId, setHighlightedTaskId] = useState(null);
  const highlightedTaskRef = useRef(null);

  // Check for highlighted task ID from sessionStorage
  useEffect(() => {
    const taskId = sessionStorage.getItem('highlightTaskId');
    if (taskId) {
      setHighlightedTaskId(taskId);
      sessionStorage.removeItem('highlightTaskId'); // Clear after reading
      
      // Scroll to the highlighted task after a short delay
      setTimeout(() => {
        if (highlightedTaskRef.current) {
          highlightedTaskRef.current.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
          });
        }
      }, 100);
    }
  }, []);

  const handleSearchResults = (searchData, query) => {
    setSearchResults(searchData.results || []);
    setSearchPagination({
      page: searchData.page || 1,
      totalPages: searchData.total_pages || 1,
      total: searchData.total || 0
    });
    setSearchQuery(query);
    setIsSearchMode(true);
    onSearchModeChange?.(true);
  };

  const handleClearSearch = () => {
    setSearchResults(null);
    setSearchPagination({ page: 1, totalPages: 1, total: 0 });
    setSearchQuery('');
    setIsSearchMode(false);
    onSearchModeChange?.(false);
  };

  const displayTasks = isSearchMode ? searchResults : researchTasks;
  const displayPagination = isSearchMode ? searchPagination : { page: currentPage, totalPages, total: totalTasks };

  const handleSearchPageChange = async (page) => {
    if (!searchQuery.trim()) return;
    
    try {
      let url = `${API_BASE}/search?query=${encodeURIComponent(searchQuery)}&limit=5&page=${page}`;
      if (statusFilter && statusFilter !== 'all' && statusFilter !== '') {
        url += `&status=${encodeURIComponent(statusFilter)}`;
      }
      
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        handleSearchResults(data, searchQuery);
      }
    } catch (err) {
      console.error('Search pagination error:', err);
    }
  };

  const handleSearchWithFilter = async (newStatusFilter) => {
    if (!searchQuery.trim()) return;
    
    try {
      let url = `${API_BASE}/search?query=${encodeURIComponent(searchQuery)}&limit=5&page=1`;
      if (newStatusFilter && newStatusFilter !== 'all' && newStatusFilter !== '') {
        url += `&status=${encodeURIComponent(newStatusFilter)}`;
      }
      
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        handleSearchResults(data, searchQuery);
      }
    } catch (err) {
      console.error('Search filter error:', err);
    }
  };

  return (
    <Card className="border-0 shadow-2xl bg-white/90 backdrop-blur-sm rounded-3xl overflow-hidden">
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 px-6 py-5">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-3 text-white text-xl font-bold">
            <div className="p-2 bg-white/10 rounded-xl backdrop-blur-sm border border-white/20">
              <FileText className="w-6 h-6" />
            </div>
            Product Validations
          </CardTitle>
          <div className="flex items-center gap-3">
            <div className="w-64">
            <ResearchSearch 
              onSearchResults={handleSearchResults}
              onClearSearch={handleClearSearch}
              statusFilter={statusFilter}
            />
            </div>
            <div className="flex items-center gap-2">
              <Label htmlFor="status-filter" className="text-white font-semibold text-sm">Filter:</Label>
              <select
                id="status-filter"
                value={statusFilter}
                onChange={(e) => {
                  const newFilter = e.target.value;
                  setStatusFilter(newFilter);
                  setCurrentPage(1);
                  
                  // If in search mode, trigger a new search with the new filter
                  if (isSearchMode && searchQuery.trim()) {
                    handleSearchWithFilter(newFilter);
                  }
                }}
                className="px-3 py-2 bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl text-sm font-medium text-white placeholder-white/70 focus:bg-white/30 focus:ring-4 focus:ring-white/20 transition-all duration-200 w-32"
              >
                <option value="" className="text-gray-800">All Tasks</option>
                <option value="processing" className="text-gray-800">Processing</option>
                <option value="completed" className="text-gray-800">Completed</option>
                <option value="failed" className="text-gray-800">Failed</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      <CardContent className="p-8 relative">

        {/* Subtle loading bar at the top when refreshing */}
        {isLoadingTasks && researchTasks.length > 0 && (
          <div className="absolute top-0 left-0 right-0 h-0.5 bg-blue-600 animate-pulse"></div>
        )}
        
        {isLoadingTasks ? (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
            </div>
            <p className="mt-4 text-gray-600 font-medium">Loading validations...</p>
          </div>
        ) : displayTasks.length === 0 ? (
            <div className="text-center py-16">
              <div className="relative mb-8">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full blur-2xl opacity-20"></div>
                {isSearchMode ? (
                  <Search className="relative w-20 h-20 text-gray-400 mx-auto" />
                ) : statusFilter === 'processing' ? (
                  <Clock className="relative w-20 h-20 text-gray-400 mx-auto" />
                ) : statusFilter === 'completed' ? (
                  <CheckCircle className="relative w-20 h-20 text-gray-400 mx-auto" />
                ) : statusFilter === 'failed' ? (
                  <AlertCircle className="relative w-20 h-20 text-gray-400 mx-auto" />
                ) : (
                  <TrendingUp className="relative w-20 h-20 text-gray-400 mx-auto" />
                )}
              </div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                {isSearchMode 
                  ? 'No search results found'
                  : statusFilter === 'processing' 
                  ? 'No tasks in progress' 
                  : statusFilter === 'completed'
                  ? 'No completed validations'
                  : statusFilter === 'failed'
                  ? 'No failed validations'
                  : 'No product validations yet'}
              </h3>
              <p className="text-gray-500 mb-6">
                {isSearchMode 
                  ? (
                    <>
                      No tasks found for "<span className="font-medium text-gray-700">{searchQuery}</span>". 
                      Try a different search term or check your spelling.
                    </>
                  )
                  : statusFilter === 'processing' 
                  ? 'All validations have been completed or are idle' 
                  : statusFilter === 'completed'
                  ? 'Complete your first validation to see results here'
                  : statusFilter === 'failed'
                  ? 'No validations have failed - great job!'
                  : 'Validate your first product idea to see results here'}
              </p>
              {!statusFilter && !isSearchMode && (
                <Button 
                  onClick={() => {
                    setActiveTab('new-research');
                    fetchSearches();
                  }}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                >
                  Validate Product Idea
                </Button>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              {displayTasks.map((task, idx) => {
                const isHighlighted = highlightedTaskId === task.request_id;
                return (
                  <div
                    key={task.request_id}
                    ref={isHighlighted ? highlightedTaskRef : null}
                    className={isHighlighted ? 'ring-2 ring-blue-500 ring-opacity-50 rounded-lg' : ''}
                  >
                    <ResearchTaskCard
                      task={task}
                      idx={idx}
                      showFullReport={showFullReport}
                      toggleFullReport={(requestId) => {
                        // Clear highlight when report is expanded
                        if (highlightedTaskId === requestId) {
                          setHighlightedTaskId(null);
                        }
                        toggleFullReport(requestId);
                      }}
                      reportData={reportData}
                      loadingReports={loadingReports}
                      reportTabs={reportTabs}
                      setReportTabs={setReportTabs}
                      getStatusIcon={getStatusIcon}
                      getResearchConfig={getResearchConfig}
                      exportResults={exportResults}
                      fetchReport={fetchReport}
                      abortTask={abortTask}
                      rerunTask={rerunTask}
                      deleteTask={deleteTask}
                    />
                  </div>
                );
              })}
              
              {/* Pagination Controls */}
              {displayPagination.totalPages > 1 && (
                <Pagination
                  currentPage={displayPagination.page}
                  totalPages={displayPagination.totalPages}
                  totalTasks={displayPagination.total}
                  pageSize={5}
                  onPageChange={isSearchMode ? handleSearchPageChange : setCurrentPage}
                />
              )}
            </div>
          )}
      </CardContent>
    </Card>
  );
}
