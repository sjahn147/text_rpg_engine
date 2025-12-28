"""
JSONB 데이터 처리 유틸리티
"""
import json
from typing import Any, Dict, List, Optional, Union


def parse_jsonb_data(data: Any) -> Union[Dict[str, Any], List[Any], None]:
    """
    JSONB 데이터를 파싱하여 Python 객체로 변환
    
    Args:
        data: JSONB 데이터 (문자열 또는 이미 파싱된 객체)
        
    Returns:
        파싱된 Python 객체 (딕셔너리, 리스트, 또는 None)
    """
    if data is None:
        return None
    
    if isinstance(data, (dict, list)):
        return data
    
    if isinstance(data, str):
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return None
    
    return None


def serialize_jsonb_data(data: Any) -> str:
    """
    Python 객체를 JSONB 문자열로 직렬화
    
    Args:
        data: 직렬화할 Python 객체
        
    Returns:
        JSON 문자열
    """
    if data is None:
        return '{}'
    
    if isinstance(data, str):
        return data
    
    try:
        return json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError):
        return '{}'


def safe_jsonb_get(data: Any, key: str, default: Any = None) -> Any:
    """
    JSONB 데이터에서 안전하게 값을 가져오기
    
    Args:
        data: JSONB 데이터
        key: 가져올 키
        default: 기본값
        
    Returns:
        키에 해당하는 값 또는 기본값
    """
    parsed_data = parse_jsonb_data(data)
    if isinstance(parsed_data, dict):
        return parsed_data.get(key, default)
    return default


def safe_jsonb_set(data: Any, key: str, value: Any) -> Dict[str, Any]:
    """
    JSONB 데이터에 안전하게 값을 설정하기
    
    Args:
        data: 기존 JSONB 데이터
        key: 설정할 키
        value: 설정할 값
        
    Returns:
        업데이트된 딕셔너리
    """
    parsed_data = parse_jsonb_data(data)
    if not isinstance(parsed_data, dict):
        parsed_data = {}
    
    parsed_data[key] = value
    return parsed_data


def merge_jsonb_data(base_data: Any, update_data: Any) -> Dict[str, Any]:
    """
    두 JSONB 데이터를 병합
    
    Args:
        base_data: 기본 데이터
        update_data: 업데이트할 데이터
        
    Returns:
        병합된 딕셔너리
    """
    base_parsed = parse_jsonb_data(base_data)
    update_parsed = parse_jsonb_data(update_data)
    
    if not isinstance(base_parsed, dict):
        base_parsed = {}
    
    if not isinstance(update_parsed, dict):
        return base_parsed
    
    # 깊은 병합
    result = base_parsed.copy()
    for key, value in update_parsed.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_jsonb_data(result[key], value)
        else:
            result[key] = value
    
    return result
