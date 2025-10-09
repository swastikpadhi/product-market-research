import React from 'react';

const getPriority = (f, i) => {
  if ((f === 'High' && i === 'High')) return { label: 'Critical', color: 'bg-red-100 text-red-700' };
  if ((f === 'High' || i === 'High')) return { label: 'High', color: 'bg-orange-100 text-orange-700' };
  if ((f === 'Medium' && i === 'Medium')) return { label: 'Medium', color: 'bg-yellow-100 text-yellow-700' };
  return { label: 'Low', color: 'bg-green-100 text-green-700' };
};

export default function CustomerInsightsTab({ data }) {
  if (!data) return null;

  return (
    <div className="space-y-3 animate-fadeIn">
      {data.primary_pain_points && data.primary_pain_points.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="px-4 py-2.5 bg-gray-50 border-b border-gray-200">
            <h5 className="font-semibold text-gray-900 text-sm">Pain Points Matrix</h5>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left px-4 py-2 font-semibold text-gray-700 border-b text-xs">Issue</th>
                  <th className="text-center px-4 py-2 font-semibold text-gray-700 border-b text-xs">Frequency</th>
                  <th className="text-center px-4 py-2 font-semibold text-gray-700 border-b text-xs">Impact</th>
                  <th className="text-center px-4 py-2 font-semibold text-gray-700 border-b text-xs">Priority</th>
                </tr>
              </thead>
              <tbody>
                {data.primary_pain_points.map((pain, idx) => {
                  const freq = typeof pain === 'string' ? 'Medium' : pain.frequency;
                  const impact = typeof pain === 'string' ? 'Medium' : pain.impact;
                  const issue = typeof pain === 'string' ? pain : pain.issue;
                  const priority = getPriority(freq, impact);
                  
                  return (
                    <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-2.5 text-gray-700 text-sm">{issue}</td>
                      <td className="px-4 py-2.5 text-center">
                        <span className="inline-block min-w-[70px] px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                          {freq}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        <span className="inline-block min-w-[70px] px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                          {impact}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        <span className="inline-block min-w-[70px] px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                          {priority.label}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        {data.unmet_needs && data.unmet_needs.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <span className="text-xl mr-2">💡</span>
              <h5 className="font-semibold text-gray-900 text-sm">Unmet Customer Needs</h5>
            </div>
            <div className="space-y-1.5">
              {data.unmet_needs.map((need, idx) => (
                <div key={idx} className="flex items-start">
                  <span className="text-blue-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                  <span className="text-sm text-gray-700">{need}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {data.feature_priorities && data.feature_priorities.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <span className="text-xl mr-2">🎯</span>
              <h5 className="font-semibold text-gray-900 text-sm">Feature Priorities</h5>
            </div>
            <div className="space-y-1.5">
              {data.feature_priorities.map((feature, idx) => (
                <div key={idx} className="flex items-start">
                  <span className="text-purple-600 mr-2 flex-shrink-0 -translate-y-[1px]">•</span>
                  <span className="text-sm text-gray-700">{feature}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

