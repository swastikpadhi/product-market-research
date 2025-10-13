import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible';
import { Clock, TrendingUp, Target, CheckCircle, Sparkles, ChevronDown, ExternalLink, XCircle, AlertCircle, Loader } from 'lucide-react';

export default function ActiveResearchProgress({ activeTask, getResearchConfig, onViewReport, setActiveTask }) {
  const cardRef = useRef(null);
  const [isOpen, setIsOpen] = useState(true); // Start expanded (Collapsible state)
  const prevTaskIdRef = useRef(null); // Track task changes
  const [elapsedTime, setElapsedTime] = useState('0:00'); // Elapsed time display
  const [startTime, setStartTime] = useState(null); // Client-side start time

  const progress = activeTask?.workflow_status?.progress || activeTask?.progress || 0;
  const currentStep = activeTask?.workflow_status?.current_step || activeTask?.current_step;
  
  // Get progress message based on checkpoint count (simpler approach)
  const getProgressMessage = (checkpointCount) => {
    const messages = {
      0: '🚀 Starting research...',
      1: '🎯 Crafting your research strategy...',
      2: '🔍 Generating targeted search queries...',
      3: '📊 Analyzing market trends and opportunities...',
      4: '📈 Gathering market intelligence...',
      5: '💡 Extracting key market insights...',
      6: '📋 Synthesizing market insights...',
      7: '🏢 Researching competitive landscape...',
      8: '⚔️ Analyzing competitor strategies...',
      9: '🎯 Identifying competitive gaps...',
      10: '⚖️ Evaluating competitive positioning...',
      11: '👥 Understanding customer needs...',
      12: '💬 Analyzing customer feedback...',
      13: '🎭 Building customer personas...',
      14: '🧠 Processing customer intelligence...',
      15: '📝 Generating comprehensive report...',
      16: '✨ Finalizing research findings...',
      17: '🎉 Research complete!'
    };
    
    return messages[checkpointCount] || '🔬 Conducting deep market research...';
  };
  
  // Use checkpoint count to determine progress message (frontend handles this entirely)
  const checkpointCount = activeTask?.workflow_status?.completed_checkpoints || activeTask?.completed_checkpoints || 0;
  const details = getProgressMessage(checkpointCount);
  const taskStatus = activeTask?.status;
  const isCompleted = progress >= 100 || taskStatus === 'completed' || currentStep === 'finalization_complete';
  const isFailed = taskStatus === 'failed' || taskStatus === 'error';
  const isAborted = taskStatus === 'aborted';
  // Only show "queued" state if explicitly in queued step (not just progress=0)
  const isQueued = currentStep === 'queued';

  // Expand when a new task starts (regardless of previous state)
  useEffect(() => {
    if (activeTask?.request_id && activeTask.request_id !== prevTaskIdRef.current) {
      setIsOpen(true); // Force expand on new task
      prevTaskIdRef.current = activeTask.request_id;
      
      // Smooth scroll to the component when it appears
      setTimeout(() => {
        if (cardRef.current) {
          cardRef.current.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
          });
        }
      }, 100); // Small delay to ensure component is rendered
    }
  }, [activeTask?.request_id]);


  // Client-side timer - start when component mounts with new task
  useEffect(() => {
    if (activeTask?.request_id && activeTask.request_id !== prevTaskIdRef.current) {
      // Reset timer for new task
      setStartTime(Date.now());
      setElapsedTime('0:00');
    }
  }, [activeTask?.request_id]);

  // Update elapsed time every second using client-side start time
  useEffect(() => {
    if (!startTime) return;
    
    const updateElapsed = () => {
      const now = Date.now();
      const elapsed = Math.floor((now - startTime) / 1000); // seconds
      
      const minutes = Math.floor(elapsed / 60);
      const seconds = elapsed % 60;
      setElapsedTime(`${minutes}:${seconds.toString().padStart(2, '0')}`);
    };
    
    // Update immediately
    updateElapsed();
    
    // Update every second if not completed
    if (!isCompleted) {
      const interval = setInterval(updateElapsed, 1000);
      return () => clearInterval(interval);
    }
  }, [startTime, isCompleted]);

  // Auto-collapse when completed (only for successful completion)
  useEffect(() => {
    if (isCompleted && isOpen) {
      const timer = setTimeout(() => {
        setIsOpen(false); // Collapse after 4 seconds
      }, 4000);
      
      return () => clearTimeout(timer);
    }
  }, [isCompleted, isOpen]);

  // Handle View Report click - clear activeTask to hide the card
  const handleViewReport = () => {
    if (onViewReport) {
      onViewReport(activeTask?.request_id);
    }
    // Clear activeTask to hide the card completely
    setActiveTask(null);
  };

  // Auto-collapse when task completes, fails, or is aborted
  useEffect(() => {
    if (isCompleted || isFailed || isAborted) {
      const timer = setTimeout(() => {
        setIsOpen(false); // Collapse the component but keep it visible
      }, 3000); // Collapse after 3 seconds
      
      return () => clearTimeout(timer);
    }
  }, [isCompleted, isFailed, isAborted]);

  // Simple: show component if there's an activeTask
  if (!activeTask) {
    return null;
  }

  return (
    <Collapsible 
      ref={cardRef}
      open={isOpen}
      onOpenChange={setIsOpen}
      className="mb-6"
    >
      <Card className="border-2 border-gray-200 bg-white rounded-3xl overflow-hidden transition-all duration-300 ease-in-out" style={{ boxShadow: '0 10px 40px -10px rgba(0, 0, 0, 0.1)' }}>
        {/* Header - Always visible, clickable to toggle */}
        <CollapsibleTrigger asChild>
          <div className={`px-5 py-3 cursor-pointer hover:opacity-90 transition-all duration-700 ease-in-out ${
            isFailed ? 'bg-gradient-to-r from-red-500 to-red-600' :
            isAborted ? 'bg-gradient-to-r from-orange-500 to-orange-600' :
            isCompleted ? 'bg-gradient-to-r from-green-500 to-emerald-500' :
            isQueued ? 'bg-gradient-to-r from-blue-500 to-indigo-500' :
            'bg-gradient-to-r from-yellow-500 via-orange-500 to-pink-500'
          }`}>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-white text-lg font-bold">
                <div className="p-1.5 bg-white/10 rounded-xl backdrop-blur-sm border border-white/20 transition-all duration-300">
                  {isFailed ? <XCircle className="w-5 h-5" /> :
                   isAborted ? <AlertCircle className="w-5 h-5" /> :
                   isCompleted ? <CheckCircle className="w-5 h-5" /> :
                   isQueued ? <Loader className="w-5 h-5 animate-spin" /> :
                   <Sparkles className="w-5 h-5 animate-pulse" />}
                </div>
                <span className="transition-all duration-300">
                  {isFailed ? 'Analysis Failed' :
                   isAborted ? 'Analysis Aborted' :
                   isCompleted ? 'Analysis Complete' :
                   isQueued ? 'Waiting for Worker...' :
                   'Analysis in Progress'}
                </span>
              </CardTitle>
              <div className="flex items-center gap-2">
                {isCompleted && (
                  <Button
                    onClick={(e) => {
                      e.stopPropagation(); // Don't toggle collapse when clicking button
                      handleViewReport();
                    }}
                    size="sm"
                    className="bg-white hover:bg-gray-50 text-green-700 text-xs px-2.5 py-1 h-7 shadow-sm border border-green-200 flex items-center gap-1"
                  >
                    <ExternalLink className="w-3 h-3" />
                    View Report
                  </Button>
                )}
                <div className="bg-white/20 px-3 py-1 rounded-full backdrop-blur-sm transition-all duration-300 flex items-center gap-2">
                  <div className="flex items-center gap-1.5 w-[60px]">
                    {isCompleted ? (
                      <CheckCircle className="w-3.5 h-3.5 text-white flex-shrink-0" />
                    ) : (
                      <Clock className="w-3.5 h-3.5 text-white flex-shrink-0" />
                    )}
                    <span className="text-white text-sm font-semibold tabular-nums">{progress}%</span>
                  </div>
                  <div className="h-3 w-px bg-white/30 flex-shrink-0"></div>
                  <span className="text-white text-sm font-semibold tabular-nums w-[38px] text-right">{elapsedTime}</span>
                </div>
                <ChevronDown 
                  className={`w-5 h-5 text-white transition-transform duration-300 ${isOpen ? '' : 'rotate-180'}`}
                />
              </div>
            </div>
          </div>
        </CollapsibleTrigger>
        
        <CollapsibleContent className="transition-all data-[state=closed]:animate-slideUp data-[state=open]:animate-slideDown">
          <CardContent className="p-4">
          <div className="space-y-3">
            {/* Product Info */}
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="text-xs text-gray-500 mb-0.5">Product Idea</div>
                <div className="font-semibold text-gray-900 text-sm">{activeTask.product_idea}</div>
              </div>
              <div className="flex items-center gap-3">
                {activeTask.research_depth && (
                  <span className={`${getResearchConfig(activeTask.research_depth).color} text-xs px-2.5 py-0.5 rounded-full inline-flex items-center font-semibold whitespace-nowrap`}>
                    {getResearchConfig(activeTask.research_depth).label}
                  </span>
                )}
              </div>
            </div>

            {/* Current Status - Simple Text */}
            <div className="flex items-center gap-2 py-1">
              <div className="flex items-center gap-1">
                {!isCompleted && <div className="w-1 h-1 bg-blue-400 rounded-full animate-wave" style={{ animationDelay: '0ms', animationDuration: '1.2s' }}></div>}
                {!isCompleted && <div className="w-1 h-1 bg-blue-400 rounded-full animate-wave" style={{ animationDelay: '200ms', animationDuration: '1.2s' }}></div>}
                {!isCompleted && <div className="w-1 h-1 bg-blue-400 rounded-full animate-wave" style={{ animationDelay: '400ms', animationDuration: '1.2s' }}></div>}
              </div>
              <span className="text-sm text-gray-600 font-medium">{details}</span>
            </div>

            {/* Progress Bar - Multi-color gradient */}
            <div className="space-y-1">
              <div className="relative h-2.5 rounded-full bg-gray-200 overflow-hidden shadow-inner">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 transition-all duration-700 ease-out relative"
                  style={{ width: `${progress}%` }}
                >
                  {!isCompleted && <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>}
                  {!isCompleted && <div className="absolute right-0 top-0 bottom-0 w-6 bg-gradient-to-l from-white/40 to-transparent animate-pulse"></div>}
                </div>
              </div>
            </div>

            {/* Simple Pipeline Steps */}
            <div className="flex items-center justify-between gap-2 pt-1">
              {/* Stage 1: Research */}
              <div className={`flex-1 flex flex-col items-center gap-1 transition-all duration-500 ${
                progress <= 70 ? 'scale-105' : 'scale-100'
              }`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 ${
                  progress === 0 ? 'bg-gray-200 text-gray-400' :
                  progress <= 70 ? 'bg-blue-500 text-white shadow-lg ring-2 ring-blue-200 animate-pulse' :
                  'bg-blue-400 text-white shadow-md'
                }`}>
                  {progress > 70 ? <CheckCircle className="w-5 h-5" /> : <TrendingUp className="w-5 h-5" />}
                </div>
                <div className="text-center">
                  <div className={`text-[11px] font-semibold ${progress <= 70 ? 'text-blue-600' : 'text-gray-600'}`}>
                    Research
                  </div>
                  {progress > 0 && progress <= 70 && (
                    <div className="text-[9px] text-blue-500 font-medium">Active</div>
                  )}
                </div>
              </div>
              
              <div className={`flex-1 h-0.5 rounded-full transition-all duration-500 ${
                progress > 70 ? 'bg-gradient-to-r from-blue-400 to-green-400' : 'bg-gray-200'
              }`}></div>
              
              {/* Stage 2: Report */}
              <div className={`flex-1 flex flex-col items-center gap-1 transition-all duration-500 ${
                progress > 70 ? 'scale-105' : 'scale-100'
              }`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 ${
                  progress <= 70 ? 'bg-gray-200 text-gray-400' :
                  progress < 100 ? 'bg-green-500 text-white shadow-lg ring-2 ring-green-200 animate-pulse' :
                  'bg-green-500 text-white shadow-xl ring-2 ring-green-300'
                }`}>
                  {progress >= 100 ? <CheckCircle className="w-5 h-5" /> : <Target className="w-5 h-5" />}
                </div>
                <div className="text-center">
                  <div className={`text-[11px] font-semibold ${progress > 70 ? 'text-green-600' : 'text-gray-600'}`}>
                    {progress >= 100 ? 'Complete' : 'Report'}
                  </div>
                  {progress > 70 && progress < 100 && (
                    <div className="text-[9px] text-green-500 font-medium">Active</div>
                  )}
                  {progress >= 100 && (
                    <div className="text-[9px] text-green-600 font-bold">Done!</div>
                  )}
                </div>
              </div>
            </div>

          </div>
          </CardContent>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  );
}

