export const getResearchConfig = (depth) => {
  const configs = {
    basic: { 
      label: 'Essential Research', 
      description: 'Fast market validation with key insights and competitor overview',
      color: 'bg-blue-100 text-blue-700'
    },
    standard: { 
      label: 'Standard Research', 
      description: 'Detailed market analysis with customer insights and strategic recommendations',
      color: 'bg-green-100 text-green-700'
    },
    comprehensive: { 
      label: 'Deep Research', 
      description: 'Comprehensive intelligence with in-depth competitor analysis and actionable strategies',
      color: 'bg-purple-100 text-purple-700'
    }
  };
  return configs[depth] || configs.standard;
};

export const RESEARCH_DEPTHS = ['basic', 'standard', 'comprehensive'];
