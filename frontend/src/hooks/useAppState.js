import { useState, useRef } from 'react';
import { API_BASE } from '../config/api';

export function useAppState() {
  // Product-Market Fit Research Form State
  const [productIdea, setProductIdea] = useState('');
  const [researchDepth, setResearchDepth] = useState('basic');
  
  // UI State
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingTasks, setIsLoadingTasks] = useState(false);
  const [researchTasks, setResearchTasks] = useState([]);
  const [totalTasks, setTotalTasks] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [activeTask, setActiveTask] = useState(null);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showFullReport, setShowFullReport] = useState({});
  const [reportData, setReportData] = useState({});
  const [loadingReports, setLoadingReports] = useState({});
  const [activeTab, setActiveTab] = useState(() => {
    return localStorage.getItem('productMarketFitActiveTab') || 'new-research';
  });
  const [currentPage, setCurrentPage] = useState(1);
  const isPollingRef = useRef(false);
  const [reportTabs, setReportTabs] = useState({});

  return {
    // Form state
    productIdea,
    setProductIdea,
    researchDepth,
    setResearchDepth,
    
    // UI state
    isSubmitting,
    setIsSubmitting,
    isLoadingTasks,
    setIsLoadingTasks,
    researchTasks,
    setResearchTasks,
    totalTasks,
    setTotalTasks,
    totalPages,
    setTotalPages,
    activeTask,
    setActiveTask,
    error,
    setError,
    statusFilter,
    setStatusFilter,
    showFullReport,
    setShowFullReport,
    reportData,
    setReportData,
    loadingReports,
    setLoadingReports,
    activeTab,
    setActiveTab,
    currentPage,
    setCurrentPage,
    isPollingRef,
    reportTabs,
    setReportTabs,
    
    // Constants
    API_BASE
  };
}
