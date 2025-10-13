export const exportResults = async (task, reportData, fetchReport) => {
  // Fetch report if not already cached
  let report = reportData[task.request_id];
  
  if (!report) {
    report = await fetchReport(task.request_id);
    if (!report) {
      alert('Failed to fetch report for export');
      return;
    }
  }

  const finalReport = report.result?.final_report || {};
  const content = generateMarkdownReport(task, finalReport, report);

  const blob = new Blob([content], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `market-research-${(task.product_idea || 'untitled').replace(/\s+/g, '-').toLowerCase()}-${task.request_id.slice(0, 8)}.md`;
  a.click();
  URL.revokeObjectURL(url);
};

// Map backend research depth values to UI display names
const mapResearchDepth = (depth) => {
  const mapping = {
    'basic': 'Essential Research',
    'standard': 'Standard Research', 
    'comprehensive': 'Deep Research'
  };
  return mapping[depth] || 'N/A';
};

const generateMarkdownReport = (task, finalReport, report) => {
  return `# Market Research Report: ${task.product_idea || 'Untitled Idea'}

## Executive Summary
${finalReport.executive_summary?.overview || 'No executive summary available'}

### Key Findings
${finalReport.executive_summary?.key_findings ? finalReport.executive_summary.key_findings.map(finding => `- ${finding}`).join('\n') : 'No key findings available'}

### Market Assessment
${finalReport.executive_summary?.market_assessment || 'No market assessment available'}

## Market Insights
${finalReport.market_insights ? `
**Market Size:** ${(() => {
  const marketSize = finalReport.market_insights.market_size;
  if (!marketSize) return 'N/A';
  
  if (typeof marketSize === 'string') {
    return marketSize;
  }
  
  if (typeof marketSize === 'object') {
    // Handle the actual structure with current and projected
    if (marketSize.current && marketSize.projected) {
      return `${marketSize.current}, projected to reach ${marketSize.projected}`;
    } else if (marketSize.current) {
      return marketSize.current;
    } else if (marketSize.projected) {
      return `Projected: ${marketSize.projected}`;
    }
    
    // Fallback for other object structures
    return JSON.stringify(marketSize, null, 2);
  }
  
  return String(marketSize);
})()}

**Growth Rate:** ${finalReport.market_insights.growth_rate || 'N/A'}

**Key Trends:**
${finalReport.market_insights.key_trends ? finalReport.market_insights.key_trends.map(trend => `- ${trend}`).join('\n') : 'No trends available'}

**Market Drivers:**
${finalReport.market_insights.market_drivers ? finalReport.market_insights.market_drivers.map(driver => `- ${driver}`).join('\n') : 'No drivers available'}

**Regulatory Landscape:** ${finalReport.market_insights.regulatory_landscape || 'N/A'}

**Technology Impact:** ${finalReport.market_insights.technology_impact || 'N/A'}

**Future Outlook:** ${finalReport.market_insights.future_outlook || 'N/A'}

**Key Insights:**
${finalReport.market_insights.key_insights ? finalReport.market_insights.key_insights.map(insight => `- ${insight}`).join('\n') : 'No key insights available'}
` : 'No market insights available'}

## Competitive Landscape
${finalReport.competitive_landscape ? `
**Overview:** ${finalReport.competitive_landscape.competitive_landscape || 'N/A'}

**Market Leaders:**
${finalReport.competitive_landscape.market_leaders ? finalReport.competitive_landscape.market_leaders.map(leader => `- ${leader}`).join('\n') : 'No market leaders identified'}

**Key Competitors:**
${finalReport.competitive_landscape.key_competitors ? finalReport.competitive_landscape.key_competitors.map(comp => `- ${comp}`).join('\n') : 'No competitors identified'}

**Competitive Gaps:**
${finalReport.competitive_landscape.competitive_gaps ? finalReport.competitive_landscape.competitive_gaps.map(gap => `- ${gap}`).join('\n') : 'No gaps identified'}

**Pricing Landscape:** ${finalReport.competitive_landscape.pricing_landscape || 'N/A'}
` : 'No competitor analysis available'}

## Customer Insights
${finalReport.customer_insights ? `
**Primary Pain Points:**
${finalReport.customer_insights.primary_pain_points ? finalReport.customer_insights.primary_pain_points.map(pain => 
  typeof pain === 'string' ? `- ${pain}` : `- ${pain.issue} (Frequency: ${pain.frequency}, Impact: ${pain.impact})`
).join('\n') : 'No pain points identified'}

**Unmet Needs:**
${finalReport.customer_insights.unmet_needs ? finalReport.customer_insights.unmet_needs.map(need => `- ${need}`).join('\n') : 'No unmet needs identified'}

**Customer Segments:**
${finalReport.customer_insights.customer_segments && finalReport.customer_insights.customer_segments.length > 0 ? finalReport.customer_insights.customer_segments.map(segment => {
  if (typeof segment === 'string') {
    return `- ${segment}`;
  }
  
  let segmentText = `- ${segment.name}`;
  
  if (segment.demographics) {
    segmentText += ` (${segment.demographics})`;
  }
  
  if (segment.characteristics) {
    segmentText += ` - ${segment.characteristics}`;
  }
  
  if (segment.needs && segment.needs.length > 0) {
    segmentText += ` - Needs: ${segment.needs.join(', ')}`;
  }
  
  return segmentText;
}).join('\n') : 'No customer segments identified'}

**Satisfaction Drivers:**
${finalReport.customer_insights.satisfaction_drivers ? finalReport.customer_insights.satisfaction_drivers.map(driver => `- ${driver}`).join('\n') : 'No satisfaction drivers identified'}

**Feature Priorities:**
${finalReport.customer_insights.feature_priorities ? finalReport.customer_insights.feature_priorities.map(feature => `- ${feature}`).join('\n') : 'No feature priorities identified'}
` : 'No customer insights available'}

## Product-Market Fit Assessment
${finalReport.pmf_assessment ? `
**Product Fit Score:** ${finalReport.pmf_assessment.product_fit_score || 'N/A'}

**Success Probability:** ${finalReport.pmf_assessment.success_probability || 'N/A'}

**Time to Market:** ${finalReport.pmf_assessment.time_to_market || 'N/A'}

**Market Opportunities:**
${finalReport.pmf_assessment.market_opportunities ? finalReport.pmf_assessment.market_opportunities.map(opp => `- ${opp}`).join('\n') : 'No opportunities identified'}

**Key Risks:**
${finalReport.pmf_assessment.key_risks ? finalReport.pmf_assessment.key_risks.map(risk => `- ${risk}`).join('\n') : 'No risks identified'}
` : 'No PMF assessment available'}

## Strategic Recommendations
${finalReport.strategic_recommendations ? `
### Immediate Actions
${finalReport.strategic_recommendations.immediate_actions ? finalReport.strategic_recommendations.immediate_actions.map(action => `- ${action}`).join('\n') : 'No immediate actions specified'}

### Product Development
${finalReport.strategic_recommendations.product_development && finalReport.strategic_recommendations.product_development.length > 0 ? finalReport.strategic_recommendations.product_development.map(item => `- ${item}`).join('\n') : 'No product development recommendations'}

### Market Entry
${finalReport.strategic_recommendations.market_entry && finalReport.strategic_recommendations.market_entry.length > 0 ? finalReport.strategic_recommendations.market_entry.map(item => `- ${item}`).join('\n') : 'No market entry recommendations'}

### Competitive Strategy
${finalReport.strategic_recommendations.competitive_strategy && finalReport.strategic_recommendations.competitive_strategy.length > 0 ? finalReport.strategic_recommendations.competitive_strategy.map(item => `- ${item}`).join('\n') : 'No competitive strategy specified'}

### Success Metrics
${finalReport.strategic_recommendations.success_metrics && finalReport.strategic_recommendations.success_metrics.length > 0 ? finalReport.strategic_recommendations.success_metrics.map(metric => `- ${metric}`).join('\n') : 'No success metrics defined'}
` : 'No recommendations available'}

## Citations & Sources

${finalReport.citations && finalReport.citations.length > 0 ? `
This report is based on ${finalReport.citations.length} verified sources:

${finalReport.citations.map((citation, idx) => `
### [${idx + 1}] ${citation.title || 'Source'}
- **Type:** ${citation.source_type || 'N/A'}
- **URL:** ${citation.url || 'N/A'}
- **Key Insights:**
${citation.key_insights && citation.key_insights.length > 0 ? citation.key_insights.map(insight => `  - ${insight}`).join('\n') : '  - No insights recorded'}
`).join('\n')}

---
` : 'No citations available. This report may be based on limited or unavailable source data.'}

  ## Metadata
  - **Product Idea:** ${task.product_idea || 'N/A'}
  - **Sector:** ${report?.result?.research_plan?.sector || task.sector || ''}
  - **Research Depth:** ${mapResearchDepth(task.research_depth)}
  - **Analysis Date:** ${finalReport.metadata?.analysis_date ? new Date(finalReport.metadata.analysis_date).toLocaleString() : new Date().toLocaleString()}
  - **Report Version:** ${finalReport.metadata?.report_version || '1.0'}
`;
};
