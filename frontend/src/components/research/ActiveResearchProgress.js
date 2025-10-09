import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible';
import { Clock, TrendingUp, Target, CheckCircle, Sparkles, ChevronDown, ExternalLink, XCircle, AlertCircle, Loader } from 'lucide-react';

export default function ActiveResearchProgress({ activeTask, getResearchConfig, onViewReport }) {
  const cardRef = useRef(null);
  const [isOpen, setIsOpen] = useState(true); // Start expanded (Collapsible state)
  const prevTaskIdRef = useRef(null); // Track task changes
  const [elapsedTime, setElapsedTime] = useState('0:00'); // Elapsed time display

  const progress = activeTask?.workflow_status?.progress || activeTask?.progress || 0;
  const details = activeTask?.workflow_status?.details || activeTask?.details || 'Multi-agent analysis in progress...';
  const currentStep = activeTask?.workflow_status?.current_step || activeTask?.current_step;
  const taskStatus = activeTask?.status;
  const isCompleted = progress >= 100 || taskStatus === 'completed';
  const isFailed = taskStatus === 'failed' || taskStatus === 'error';
  const isAborted = taskStatus === 'aborted';
  // Only show "queued" state if explicitly in queued step (not just progress=0)
  const isQueued = currentStep === 'queued';

  // Expand when a new task starts (regardless of previous state)
  useEffect(() => {
    if (activeTask?.request_id && activeTask.request_id !== prevTaskIdRef.current) {
      setIsOpen(true); // Force expand on new task
      prevTaskIdRef.current = activeTask.request_id;
    }
  }, [activeTask?.request_id]);

  // Progressive scroll into view when component appears
  useEffect(() => {
    if (activeTask && cardRef.current) {
      // Use requestAnimationFrame for smoother, more progressive scroll
      requestAnimationFrame(() => {
        const elementPosition = cardRef.current.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - 20;
        
        // Progressive smooth scroll with longer duration
        const startPosition = window.pageYOffset;
        const distance = offsetPosition - startPosition;
        const duration = 1000; // 1000ms for smoother scroll
        let start = null;
        
        function progressiveScroll(timestamp) {
          if (!start) start = timestamp;
          const progress = timestamp - start;
          const percentage = Math.min(progress / duration, 1);
          
          // Ease-out-cubic for smooth deceleration at the end (no "bang")
          const ease = 1 - Math.pow(1 - percentage, 3);
          
          window.scrollTo(0, startPosition + distance * ease);
          
          if (progress < duration) {
            requestAnimationFrame(progressiveScroll);
          }
        }
        
        requestAnimationFrame(progressiveScroll);
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTask?.request_id]); // Only trigger on task change, not on progress updates

  // Update elapsed time every second
  useEffect(() => {
    if (!activeTask?.started_at) return;
    
    const updateElapsed = () => {
      const startTime = new Date(activeTask.started_at).getTime();
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
  }, [activeTask?.started_at, isCompleted]);

  // Auto-collapse when completed (only for successful completion)
  useEffect(() => {
    if (isCompleted && isOpen) {
      const timer = setTimeout(() => {
        setIsOpen(false); // Collapse after 4 seconds
      }, 4000);
      
      return () => clearTimeout(timer);
    }
  }, [isCompleted, isOpen]);

  // Auto-hide when task fails or is aborted
  useEffect(() => {
    if (isFailed || isAborted) {
      const timer = setTimeout(() => {
        // Clear activeTask in parent so component unmounts
        // This will be handled by App.js polling which already does this
      }, 2000);
      
      return () => clearTimeout(timer);
    }
  }, [isFailed, isAborted]);

  // Simple: show component if there's an activeTask
  if (!activeTask) {
    return null;
  }
  
  // Hide after error (let App.js handle clearing activeTask)
  if ((isFailed || isAborted) && taskStatus !== 'processing') {
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
                      onViewReport && onViewReport();
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
                <div className="w-1 h-1 bg-blue-500 rounded-full animate-pulse"></div>
                <div className="w-1 h-1 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-1 h-1 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
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
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
                  <div className="absolute right-0 top-0 bottom-0 w-6 bg-gradient-to-l from-white/40 to-transparent animate-pulse"></div>
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

