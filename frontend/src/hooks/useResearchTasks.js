import { useState, useCallback, useRef } from 'react';
import { API_BASE } from '../config/api';

export default function useResearchTasks(appState) {
  const { setActiveTask } = appState;
  const [researchTasks, setResearchTasks] = useState([]);
  const [totalTasks, setTotalTasks] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showFullReport, setShowFullReport] = useState(false);
  const [reportData, setReportData] = useState({});
  const [loadingReports, setLoadingReports] = useState({});
  const [reportTabs, setReportTabs] = useState('overview');
  const isPollingRef = useRef(false);

  const loadTasks = useCallback(async () => {
    if (isPollingRef.current) return; // Prevent concurrent requests
    isPollingRef.current = true;
    setIsLoading(true);
    
    try {
      // Build URL with pagination and status filter
      const params = new URLSearchParams();
      if (statusFilter) params.append('status', statusFilter);
      params.append('page', currentPage.toString());
      
      const url = `${API_BASE}?${params.toString()}`;
      const response = await fetch(url);
      
      if (response.ok) {
        const data = await response.json();
        const sortedTasks = (data.research_tasks || []).sort((a, b) => 
          new Date(b.started_at) - new Date(a.started_at)
        );
        
        setResearchTasks(sortedTasks);
        setTotalTasks(data.total || 0);
        setTotalPages(data.total_pages || 1);
        
        // If we're on a page that doesn't exist, reset to page 1
        if (sortedTasks.length === 0 && currentPage > 1 && data.total > 0) {
          setCurrentPage(1);
        }
        
        setError('');
      } else {
        setError('Failed to load research tasks. Please check your connection.');
      }
    } catch (err) {
      console.error('Failed to load research tasks:', err);
      setError('Failed to load research tasks. Please check your connection.');
    } finally {
      setIsLoading(false);
      isPollingRef.current = false;
    }
  }, [currentPage, statusFilter]);

  const addTask = (task) => {
    setResearchTasks(prev => [task, ...prev]);
  };

  const submitProductResearch = useCallback(async (productIdea, researchDepth) => {
    try {
      const response = await fetch(`${API_BASE}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_idea: productIdea,
          research_depth: researchDepth
        })
      });

      if (response.ok) {
        const data = await response.json();
        const newTask = {
          request_id: data.request_id,
          product_idea: productIdea,
          research_depth: researchDepth,
          status: 'pending',
          started_at: new Date().toISOString(),
          progress: 0,
          current_step: 'initializing'
        };
        addTask(newTask);
        setActiveTask(newTask);
        return data;
      } else {
        throw new Error('Failed to submit research');
      }
    } catch (err) {
      console.error('Failed to submit research:', err);
      throw err;
    }
  }, [setActiveTask]);

  const fetchReport = useCallback(async (requestId) => {
    setLoadingReports(prev => ({ ...prev, [requestId]: true }));
    try {
      const response = await fetch(`${API_BASE}/result/${requestId}`);
      
      if (response.ok) {
        const data = await response.json();
        setReportData(prev => ({
          ...prev,
          [requestId]: data
        }));
        return data;
      } else {
        throw new Error('Failed to fetch report');
      }
    } catch (err) {
      console.error('Failed to fetch report:', err);
      throw err;
    } finally {
      setLoadingReports(prev => ({ ...prev, [requestId]: false }));
    }
  }, []); // Remove reportData dependency - let the component handle caching

  const deleteTask = useCallback(async (requestId) => {
    try {
      const response = await fetch(`${API_BASE}/${requestId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        setResearchTasks(prev => prev.filter(task => task.request_id !== requestId));
        setReportData(prev => {
          const newData = { ...prev };
          delete newData[requestId];
          return newData;
        });
      } else {
        throw new Error('Failed to delete task');
      }
    } catch (err) {
      console.error('Failed to delete task:', err);
      throw err;
    }
  }, []);

  const abortTask = useCallback(async (requestId) => {
    try {
      const response = await fetch(`${API_BASE}/${requestId}/abort`, {
        method: 'POST'
      });
      if (response.ok) {
        setResearchTasks(prev => prev.map(task => 
          task.request_id === requestId 
            ? { ...task, status: 'aborted' }
            : task
        ));
      } else {
        throw new Error('Failed to abort task');
      }
    } catch (err) {
      console.error('Failed to abort task:', err);
      throw err;
    }
  }, []);

  const rerunTask = useCallback(async (requestId) => {
    try {
      const response = await fetch(`${API_BASE}/${requestId}/rerun`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        const newTask = {
          request_id: data.request_id,
          product_idea: data.product_idea,
          research_depth: data.research_depth,
          status: 'pending',
          started_at: new Date().toISOString(),
          progress: 0,
          current_step: 'initializing'
        };
        addTask(newTask);
        return data;
      } else {
        throw new Error('Failed to rerun task');
      }
    } catch (err) {
      console.error('Failed to rerun task:', err);
      throw err;
    }
  }, []);

  const toggleFullReport = useCallback((requestId) => {
    setShowFullReport(prev => {
      const isCurrentlyOpen = prev[requestId];
      if (isCurrentlyOpen) {
        // If currently open, close it
        const newState = { ...prev };
        delete newState[requestId];
        return newState;
      } else {
        // If closed, open it and close all others
        return { [requestId]: true };
      }
    });
  }, []);

  // No automatic fetching - reports will be fetched on demand when user opens them

  return {
    researchTasks,
    totalTasks,
    totalPages,
    currentPage,
    statusFilter,
    isLoading,
    error,
    showFullReport,
    reportData,
    loadingReports,
    reportTabs,
    setCurrentPage,
    setStatusFilter,
    setReportTabs,
    loadTasks,
    addTask,
    submitProductResearch,
    deleteTask,
    abortTask,
    rerunTask,
    fetchReport,
    toggleFullReport
  };
}

