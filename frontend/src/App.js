import React, { useEffect } from 'react';
import './App.css';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Brain, Target, FileText, Clock, CheckCircle, XCircle, Ban } from 'lucide-react';
import { ResearchForm, ActiveResearchProgress } from './components/research';
import ResearchTaskList from './components/research/ResearchTaskList';
import { useAppState } from './hooks/useAppState';
import useResearchTasks from './hooks/useResearchTasks';
import useSearchesRemaining from './hooks/useSearchesRemaining';
import { getResearchConfig } from './constants/researchConfig';
import { exportResults } from './utils/exportUtils';
import { API_BASE } from './config/api';

export default function ProductMarketFitResearch() {
  const appState = useAppState();
  const {
    productIdea,
    setProductIdea,
    researchDepth,
    setResearchDepth,
    isSubmitting,
    error,
    activeTab,
    setActiveTab,
    activeTask,
    setActiveTask
  } = appState;

  const {
    researchTasks,
    totalTasks,
    totalPages,
    currentPage,
    setCurrentPage,
    statusFilter,
    setStatusFilter,
    isLoading,
    showFullReport,
    reportData,
    loadingReports,
    reportTabs,
    setReportTabs,
    loadTasks,
    submitProductResearch,
    deleteTask,
    abortTask,
    rerunTask,
    fetchReport,
    toggleFullReport
  } = useResearchTasks(appState);

  const { searchesRemaining: searchesRemainingData, isLoading: isLoadingSearchesData, fetchSearches } = useSearchesRemaining();

  // Load tasks when component mounts or when dependencies change
  useEffect(() => {
    loadTasks();
  }, [loadTasks, currentPage, statusFilter]);

  // Load searches remaining when component mounts
  useEffect(() => {
    fetchSearches();
  }, [fetchSearches]);

  // Poll activeTask status for real-time updates
  useEffect(() => {
    if (!activeTask?.request_id) return;

    const pollStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/${activeTask.request_id}/status`);
        if (response.ok) {
          const statusData = await response.json();
            setActiveTask(prev => ({
              ...prev,
            ...statusData,
            workflow_status: statusData
          }));
        }
      } catch (error) {
        console.error('Failed to poll activeTask status:', error);
      }
    };

    // Poll every 5 seconds
    const interval = setInterval(pollStatus, 5000);
    
    // Clear activeTask when completed/failed
    if (activeTask?.status === 'completed' || activeTask?.status === 'failed' || activeTask?.status === 'aborted') {
      const timer = setTimeout(() => {
        setActiveTask(null);
      }, 3000);
    return () => {
        clearInterval(interval);
        clearTimeout(timer);
      };
    }

    return () => clearInterval(interval);
  }, [activeTask?.request_id, activeTask?.status, setActiveTask]);

  const handleTabChange = (value) => {
    setActiveTab(value);
    localStorage.setItem('productMarketFitActiveTab', value);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'processing':
        return <Clock className="w-4 h-4 text-yellow-500" title="Processing" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" title="Completed" />;
      case 'failed':
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" title="Failed" />;
      case 'aborted':
        return <Ban className="w-4 h-4 text-orange-500" title="Aborted" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" title="Pending" />;
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-12 text-center">
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full blur-lg opacity-30 animate-pulse"></div>
              <Brain className="relative w-12 h-12 text-white bg-gradient-to-r from-blue-600 to-purple-600 p-2 rounded-full shadow-lg" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent leading-normal py-2">
              Product-Market Fit Research
            </h1>
          </div>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto leading-relaxed">
            AI-powered research to validate your product ideas and find market opportunities
          </p>
        </div>

          <Tabs value={activeTab} onValueChange={handleTabChange} className="space-y-8">
           <div className="flex justify-center">
             <TabsList className="grid w-full max-w-md grid-cols-2 p-1 rounded-2xl bg-gray-100 shadow-lg h-12">
               <TabsTrigger 
                 value="new-research"
                 className="flex items-center justify-center gap-2 px-4 py-0 text-sm font-semibold rounded-xl h-10 transition-all duration-300 ease-in-out data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-sm data-[state=inactive]:text-gray-600 data-[state=inactive]:hover:text-gray-800 data-[state=inactive]:hover:bg-gray-50"
               >
                 <Target className="w-4 h-4 transition-colors duration-300" />
                 <span className="transition-colors duration-300">Validate Idea</span>
               </TabsTrigger>
               <TabsTrigger 
                 value="research-tasks"
                 className="flex items-center justify-center gap-2 px-4 py-0 text-sm font-semibold rounded-xl h-10 transition-all duration-300 ease-in-out data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-sm data-[state=inactive]:text-gray-600 data-[state=inactive]:hover:text-gray-800 data-[state=inactive]:hover:bg-gray-50"
               >
                 <FileText className="w-4 h-4 transition-colors duration-300" />
                 <span className="transition-colors duration-300">My Research</span>
               </TabsTrigger>
             </TabsList>
           </div>

          {/* New Market Research Tab */}
          <TabsContent value="new-research" className="space-y-8 animate-fade-in">
            <ResearchForm
              productIdea={productIdea}
              setProductIdea={setProductIdea}
              researchDepth={researchDepth}
              setResearchDepth={setResearchDepth}
              searchesRemaining={searchesRemainingData}
              isLoadingSearches={isLoadingSearchesData}
              isSubmitting={isSubmitting}
              error={error}
              onSubmit={submitProductResearch}
              getResearchConfig={getResearchConfig}
            />

            <ActiveResearchProgress
              activeTask={activeTask}
              getResearchConfig={getResearchConfig}
              onViewReport={() => {
                setActiveTab('research-tasks');
                setActiveTask(null);
              }}
            />
          </TabsContent>

          {/* Research Tasks Tab */}
          <TabsContent value="research-tasks" className="space-y-8 animate-fade-in">
            <ResearchTaskList
              researchTasks={researchTasks}
              totalTasks={totalTasks}
              totalPages={totalPages}
              currentPage={currentPage}
              statusFilter={statusFilter}
              setStatusFilter={setStatusFilter}
              setCurrentPage={setCurrentPage}
              isLoadingTasks={isLoading}
                        showFullReport={showFullReport}
                        toggleFullReport={toggleFullReport}
                        reportData={reportData}
                        loadingReports={loadingReports}
                        reportTabs={reportTabs}
                        setReportTabs={setReportTabs}
                        getStatusIcon={getStatusIcon}
              exportResults={(task) => exportResults(task, reportData, fetchReport)}
                        fetchReport={fetchReport}
                        abortTask={abortTask}
                        rerunTask={rerunTask}
                        deleteTask={deleteTask}
              setActiveTab={setActiveTab}
            />
          </TabsContent>
        </Tabs>
      </div>
    </main>
  );
}