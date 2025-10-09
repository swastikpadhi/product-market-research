import React from 'react';

export default function Pagination({ 
  currentPage, 
  totalPages, 
  totalTasks, 
  pageSize, 
  onPageChange 
}) {
  if (totalPages <= 1) return null;

  const startRecord = (currentPage - 1) * pageSize + 1;
  const endRecord = Math.min(currentPage * pageSize, totalTasks);

  return (
    <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
      {/* Left: Record count */}
      <div className="text-sm text-gray-600">
        <span className="font-semibold text-gray-900">
          {startRecord} - {endRecord}
        </span>
        {' '}/{' '}
        <span className="font-semibold text-gray-900">{totalTasks}</span> records
      </div>
      
      {/* Right: Page navigation */}
      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(Math.max(1, currentPage - 1))}
          disabled={currentPage === 1}
          className="px-3 py-1.5 text-xs rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Previous
        </button>
        
        {/* Show page numbers with stable positioning */}
        {(() => {
          const pages = [];
          const maxVisiblePages = 3;
          
          // Calculate which pages to show
          let startPage, endPage;
          
          if (totalPages <= maxVisiblePages) {
            // Show all pages if total is small
            startPage = 1;
            endPage = totalPages;
          } else {
            // Show a sliding window of pages
            const halfVisible = Math.floor(maxVisiblePages / 2);
            
            if (currentPage <= halfVisible) {
              // Near the beginning
              startPage = 1;
              endPage = maxVisiblePages;
            } else if (currentPage >= totalPages - halfVisible) {
              // Near the end
              startPage = totalPages - maxVisiblePages + 1;
              endPage = totalPages;
            } else {
              // In the middle
              startPage = currentPage - halfVisible;
              endPage = currentPage + halfVisible;
            }
          }
          
          // Add first page and ellipsis if needed
          if (startPage > 1) {
            pages.push(
              <button
                key={1}
                onClick={() => onPageChange(1)}
                className="px-3 py-1.5 text-xs rounded-lg border border-gray-300 hover:bg-gray-50 text-gray-700 transition-colors"
              >
                1
              </button>
            );
            
            if (startPage > 2) {
              pages.push(
                <span key="ellipsis-start" className="px-2 text-gray-500">
                  ...
                </span>
              );
            }
          }
          
          // Add visible page range
          for (let i = startPage; i <= endPage; i++) {
            pages.push(
              <button
                key={i}
                onClick={() => onPageChange(i)}
                className={`px-3 py-1.5 text-xs rounded-lg transition-all duration-200 ${
                  currentPage === i 
                    ? 'bg-blue-600 text-white shadow-md' 
                    : 'border border-gray-300 hover:bg-gray-50 text-gray-700'
                }`}
              >
                {i}
              </button>
            );
          }
          
          // Add ellipsis and last page if needed
          if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
              pages.push(
                <span key="ellipsis-end" className="px-2 text-gray-500">
                  ...
                </span>
              );
            }
            
            pages.push(
              <button
                key={totalPages}
                onClick={() => onPageChange(totalPages)}
                className="px-3 py-1.5 text-xs rounded-lg border border-gray-300 hover:bg-gray-50 text-gray-700 transition-colors"
              >
                {totalPages}
              </button>
            );
          }
          
          return pages;
        })()}
        
        <button
          onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
          disabled={currentPage === totalPages}
          className="px-3 py-1.5 text-xs rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  );
}
