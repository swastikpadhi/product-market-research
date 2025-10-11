import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Search, X } from 'lucide-react';
import { API_BASE } from '../../config/api';

export default function ResearchSearch({ onSearchResults, onClearSearch }) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const debounceRef = useRef(null);
  const searchRef = useRef(null);
  const abortControllerRef = useRef(null);

  const searchTasks = useCallback(async (searchQuery) => {
    if (!searchQuery.trim()) {
      onClearSearch();
      return;
    }

    setIsSearching(true);
    try {
      const response = await fetch(`${API_BASE}/search?query=${encodeURIComponent(searchQuery)}&limit=20`);
      if (response.ok) {
        const data = await response.json();
        onSearchResults(data.results || []);
      } else {
        console.error('Search failed');
        onSearchResults([]);
      }
    } catch (err) {
      console.error('Search error:', err);
      onSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, [onSearchResults, onClearSearch]);

  const getSuggestions = useCallback(async (partialQuery) => {
    if (!partialQuery.trim() || partialQuery.trim().length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    try {
          const response = await fetch(`${API_BASE}/search/suggestions?partial_query=${encodeURIComponent(partialQuery)}&limit=5`, {
        signal: abortControllerRef.current.signal
      });
      
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
        setShowSuggestions(true);
      } else {
        console.error('Suggestions API error:', response.status);
        setSuggestions([]);
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('Suggestions error:', err);
        setSuggestions([]);
      }
    }
  }, []);

  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    
    // Clear previous debounce
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    
    if (value.trim()) {
      // Debounce suggestions with shorter delay for faster response
      debounceRef.current = setTimeout(() => {
        getSuggestions(value);
      }, 300);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
      onClearSearch();
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      searchTasks(query);
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion.query);
    searchTasks(suggestion.query);
    setShowSuggestions(false);
  };

  const handleClear = () => {
    setQuery('');
    setSuggestions([]);
    setShowSuggestions(false);
    onClearSearch();
  };

  // Handle escape key and click outside
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        setShowSuggestions(false);
      }
    };

    const handleClickOutside = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Cleanup debounce timer and abort controller on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return (
    <div ref={searchRef} className="relative w-full">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/70 w-4 h-4" />
          <input
            type="text"
            value={query}
            onChange={handleInputChange}
            placeholder="Search research reports..."
            className="w-full pl-10 pr-10 py-2 bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl text-sm font-medium text-white placeholder-white/70 focus:bg-white/30 focus:ring-4 focus:ring-white/20 focus:border-transparent transition-all duration-200"
          />
          {query && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/70 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
        
        {isSearching && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          </div>
        )}
      </form>

        {showSuggestions && suggestions.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors"
              >
                <div className="flex flex-col">
                  <div className="font-medium">{suggestion.query}</div>
                  {suggestion.started_at && (
                    <div className="text-xs text-gray-500 mt-0.5">
                      Created: {new Date(suggestion.started_at).toLocaleString()}
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
    </div>
  );
}
