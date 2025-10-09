import re
import json
from typing import Any, Dict, Optional

def extract_json_from_response(text: str) -> str:
    json_pattern = r'```json\s*(.*?)\s*```'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    
    json_pattern = r'```\s*(.*?)\s*```'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            json.loads(match.group(1))
            return match.group(1)
        except json.JSONDecodeError:
            pass
    
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return text[start_idx:end_idx + 1]
    
    return text

def validate_json_structure(data: Dict[str, Any], required_fields: list) -> bool:
    for field in required_fields:
        if field not in data:
            return False
    return True

def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())

# Truncation function removed to allow free data flow

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    return data.get(key, default) if isinstance(data, dict) else default
