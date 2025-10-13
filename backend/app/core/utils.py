"""
Core Utilities - JSON extraction from LLM responses and content management
"""
import re
import json
from typing import List, Dict, Any
from .constants import MAX_CHARACTERS_PER_REQUEST

def extract_json_from_response(text: str) -> str:
    """Extract JSON from LLM response"""
    # Try to find JSON in code blocks first
    json_pattern = r'```json\s*(.*?)\s*```'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    
    # Try to find JSON in any code block
    json_pattern = r'```\s*(.*?)\s*```'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            json.loads(match.group(1))
            return match.group(1)
        except json.JSONDecodeError:
            pass
    
    # Find first { to last }
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return text[start_idx:end_idx + 1]
    
    return text

def truncate_content_for_llm(content: str, max_chars: int = MAX_CHARACTERS_PER_REQUEST) -> str:
    """Truncate content to fit within OpenAI token limits"""
    if len(content) <= max_chars:
        return content
    
    # Truncate and add truncation notice
    truncation_notice = f"\n\n[Content truncated - original: {len(content)} chars]"
    available_chars = max_chars - len(truncation_notice)
    truncated = content[:available_chars]
    return f"{truncated}{truncation_notice}"

def truncate_search_results(search_results: List[Dict[str, Any]], max_chars: int = MAX_CHARACTERS_PER_REQUEST) -> List[Dict[str, Any]]:
    """Truncate search results to fit within token limits"""
    if not search_results:
        return search_results
    
    # Calculate total content length efficiently
    total_length = sum(len(result.get('content', '')) + 2 for result in search_results)  # +2 for newlines
    
    if total_length <= max_chars:
        return search_results
    
    # Truncate results to fit within limit
    truncated_results = []
    current_length = 0
    truncation_notice = "\n[Content truncated due to length limits]"
    notice_length = len(truncation_notice)
    
    for result in search_results:
        content = result.get('content', '')
        if not content:
            truncated_results.append(result)
            continue
        
        # Calculate available space
        remaining_chars = max_chars - current_length - notice_length
        
        if remaining_chars <= 0:
            # Add placeholder for truncated content
            truncated_result = result.copy()
            truncated_result['content'] = "[Content truncated due to length limits]"
            truncated_results.append(truncated_result)
            break
        
        if len(content) <= remaining_chars:
            # This result fits completely
            truncated_results.append(result)
            current_length += len(content) + 2  # +2 for newlines
        else:
            # Truncate this result
            truncated_result = result.copy()
            truncated_result['content'] = content[:remaining_chars] + truncation_notice
            truncated_results.append(truncated_result)
            break
    
    return truncated_results
