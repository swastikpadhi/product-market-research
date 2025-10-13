import React, { useRef, useEffect } from 'react';
import { Card, CardContent, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { AlertCircle, Clock, Target } from 'lucide-react';

export default function ResearchForm({
  productIdea,
  setProductIdea,
  researchDepth,
  setResearchDepth,
  searchesRemaining,
  isLoadingSearches,
  isSubmitting,
  error,
  onSubmit,
  getResearchConfig,
  activeTab,
}) {
  const textareaRef = useRef(null);

  // Auto-focus the textarea when component mounts
  useEffect(() => {
    const timer = setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }, 100);
    
    return () => clearTimeout(timer);
  }, []);

  // Auto-focus the textarea when switching to this tab
  useEffect(() => {
    if (activeTab === 'new-research') {
      // Add a small delay to ensure the DOM is ready
      const timer = setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.focus();
        }
      }, 100);
      
      return () => clearTimeout(timer);
    }
  }, [activeTab]);
  const getSearchesRemaining = (depth) => {
    if (!searchesRemaining || isLoadingSearches) return 'N/A';
    return searchesRemaining[depth] || 0;
  };

  // Check if user has any credits for the selected research depth
  const hasCreditsForSelectedDepth = () => {
    if (!searchesRemaining || isLoadingSearches) return false;
    const remaining = searchesRemaining[researchDepth] || 0;
    return remaining > 0;
  };

  return (
    <Card className="border-0 shadow-2xl bg-white/90 backdrop-blur-sm rounded-3xl overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 px-6 py-5">
        <CardTitle className="flex items-center gap-3 text-white text-xl font-bold">
          <div className="p-2 bg-white/10 rounded-xl backdrop-blur-sm border border-white/20">
            <Target className="w-6 h-6" />
          </div>
          Validate Your Product Idea
        </CardTitle>
      </div>
      <CardContent className="p-8 space-y-6">
        {error && (
          <Alert variant="destructive" className="border-red-200 bg-red-50/50 backdrop-blur-sm">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{typeof error === 'string' ? error : JSON.stringify(error)}</AlertDescription>
          </Alert>
        )}
        
        {/* Product Idea Input */}
        <div className="space-y-3">
          <Label htmlFor="productIdea" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"></div>
            Product Idea *
          </Label>
          <Textarea
            ref={textareaRef}
            id="productIdea"
            placeholder="e.g., A mobile app that helps small businesses manage inventory using AI, or a SaaS platform for remote team collaboration"
            value={productIdea}
            onChange={(e) => setProductIdea(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!isSubmitting && productIdea.trim() && hasCreditsForSelectedDepth()) {
                  onSubmit(productIdea, researchDepth);
                }
              }
            }}
            className="min-h-[100px] border-2 border-gray-200 focus:border-blue-500 rounded-xl resize-none transition-all duration-200 focus:ring-4 focus:ring-blue-100"
          />
          <p className="text-xs text-gray-500 mt-2">Target market/sector will be automatically extracted from your product idea</p>
        </div>

        {/* Research Depth Selection */}
        <div className="space-y-4">
          <Label className="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <div className="w-2 h-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"></div>
            Research Depth
          </Label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {['basic', 'standard', 'comprehensive'].map((depth) => {
              const config = getResearchConfig(depth);
              const searchesLeft = getSearchesRemaining(depth);
              return (
                <div
                  key={depth}
                  onMouseDown={(e) => {
                    e.preventDefault();
                    setResearchDepth(depth);
                  }}
                  className={`p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 flex flex-col ${
                    researchDepth === depth
                      ? 'border-blue-500 bg-blue-50 shadow-md'
                      : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-center mb-3">
                    <span className={`${config.color} text-xs font-semibold px-3 py-1 rounded-full inline-flex items-center`}>
                      {config.label}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 text-center mb-4 leading-relaxed h-10 flex items-center justify-center">
                    {config.description}
                  </p>
                  <div className="flex items-center justify-center text-xs pt-2 border-t border-gray-200 mt-auto h-6">
                    {isLoadingSearches ? (
                      <div className="flex items-center gap-1">
                        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce"></div>
                        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    ) : (
                      <span className="font-semibold text-blue-600">
                        {searchesLeft} searches remaining
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>


        <Button 
          onClick={() => onSubmit(productIdea, researchDepth)} 
          disabled={isSubmitting || !productIdea.trim() || !hasCreditsForSelectedDepth()}
          className="w-full bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-2xl shadow-2xl hover:shadow-3xl transition-all duration-300 transform hover:scale-[1.02] hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          {isSubmitting ? (
            <>
              <Clock className="w-6 h-6 mr-3 animate-spin" />
              Researching Product-Market Fit...
            </>
          ) : !hasCreditsForSelectedDepth() ? (
            <>
              <Target className="w-6 h-6 mr-3" />
              Insufficient Credits
            </>
          ) : (
            <>
              <Target className="w-6 h-6 mr-3" />
              Validate Product Idea
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}

