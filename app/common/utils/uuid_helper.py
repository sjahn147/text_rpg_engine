"""
UUID 처리 헬퍼 함수

UUID 객체와 문자열 간의 변환 및 비교를 일관되게 처리하기 위한 유틸리티 함수
"""
from typing import Union, Optional
from uuid import UUID
import uuid
import re


def normalize_uuid(value: Union[str, UUID, None]) -> Optional[str]:
    """
    UUID를 문자열로 정규화
    
    Args:
        value: UUID 객체, UUID 문자열, 또는 None
        
    Returns:
        UUID 문자열 또는 None (유효하지 않은 경우)
        
    Examples:
        >>> normalize_uuid(uuid.uuid4())
        '550e8400-e29b-41d4-a716-446655440000'
        >>> normalize_uuid('550e8400-e29b-41d4-a716-446655440000')
        '550e8400-e29b-41d4-a716-446655440000'
        >>> normalize_uuid(None)
        None
        >>> normalize_uuid('invalid')
        None
    """
    if value is None:
        return None
    
    # UUID 객체인 경우 문자열로 변환
    if isinstance(value, UUID):
        return str(value)
    
    # 문자열인 경우 UUID 형식 검증
    if isinstance(value, str):
        # UUID 형식 검증 (대소문자 무시)
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if re.match(uuid_pattern, value, re.IGNORECASE):
            return value.lower()  # 소문자로 정규화
        
        # 유효하지 않은 형식
        return None
    
    # 지원하지 않는 타입
    return None


def to_uuid(value: Union[str, UUID, None]) -> Optional[UUID]:
    """
    값을 UUID 객체로 변환
    
    Args:
        value: UUID 문자열, UUID 객체, 또는 None
        
    Returns:
        UUID 객체 또는 None (유효하지 않은 경우)
        
    Examples:
        >>> to_uuid('550e8400-e29b-41d4-a716-446655440000')
        UUID('550e8400-e29b-41d4-a716-446655440000')
        >>> to_uuid(uuid.uuid4())
        UUID('...')
        >>> to_uuid(None)
        None
        >>> to_uuid('invalid')
        None
    """
    if value is None:
        return None
    
    # 이미 UUID 객체인 경우
    if isinstance(value, UUID):
        return value
    
    # 문자열인 경우 UUID로 변환 시도
    if isinstance(value, str):
        try:
            return UUID(value)
        except (ValueError, AttributeError, TypeError):
            return None
    
    # 지원하지 않는 타입
    return None


def compare_uuids(uuid1: Union[str, UUID, None], uuid2: Union[str, UUID, None]) -> bool:
    """
    두 UUID를 비교 (타입 무관)
    
    Args:
        uuid1: 첫 번째 UUID (문자열 또는 UUID 객체)
        uuid2: 두 번째 UUID (문자열 또는 UUID 객체)
        
    Returns:
        두 UUID가 같으면 True, 다르거나 None이면 False
        
    Examples:
        >>> compare_uuids('550e8400-e29b-41d4-a716-446655440000', 
        ...               uuid.UUID('550e8400-e29b-41d4-a716-446655440000'))
        True
        >>> compare_uuids('550e8400-e29b-41d4-a716-446655440000', 
        ...               '550e8400-e29b-41d4-a716-446655440001')
        False
        >>> compare_uuids(None, None)
        False
    """
    uuid1_str = normalize_uuid(uuid1)
    uuid2_str = normalize_uuid(uuid2)
    
    if uuid1_str is None or uuid2_str is None:
        return False
    
    return uuid1_str == uuid2_str


def is_valid_uuid(value: Union[str, UUID, None]) -> bool:
    """
    값이 유효한 UUID인지 확인
    
    Args:
        value: 확인할 값
        
    Returns:
        유효한 UUID이면 True
        
    Examples:
        >>> is_valid_uuid('550e8400-e29b-41d4-a716-446655440000')
        True
        >>> is_valid_uuid('invalid')
        False
        >>> is_valid_uuid(None)
        False
    """
    return normalize_uuid(value) is not None


def ensure_uuid_string(value: Union[str, UUID, None], default: Optional[str] = None) -> str:
    """
    UUID를 문자열로 보장 (None이면 기본값 반환)
    
    Args:
        value: UUID 객체, UUID 문자열, 또는 None
        default: value가 None이거나 유효하지 않을 때 반환할 기본값
        
    Returns:
        UUID 문자열 또는 default
        
    Raises:
        ValueError: value가 유효하지 않고 default도 None인 경우
        
    Examples:
        >>> ensure_uuid_string(uuid.uuid4())
        '550e8400-e29b-41d4-a716-446655440000'
        >>> ensure_uuid_string(None, 'default-uuid')
        'default-uuid'
        >>> ensure_uuid_string('invalid', 'default-uuid')
        'default-uuid'
    """
    normalized = normalize_uuid(value)
    if normalized is not None:
        return normalized
    
    if default is not None:
        return default
    
    raise ValueError(f"Invalid UUID value: {value} and no default provided")


def ensure_uuid_object(value: Union[str, UUID, None], default: Optional[UUID] = None) -> UUID:
    """
    UUID를 객체로 보장 (None이면 기본값 반환)
    
    Args:
        value: UUID 문자열, UUID 객체, 또는 None
        default: value가 None이거나 유효하지 않을 때 반환할 기본값
        
    Returns:
        UUID 객체 또는 default
        
    Raises:
        ValueError: value가 유효하지 않고 default도 None인 경우
        
    Examples:
        >>> ensure_uuid_object('550e8400-e29b-41d4-a716-446655440000')
        UUID('550e8400-e29b-41d4-a716-446655440000')
        >>> ensure_uuid_object(None, uuid.uuid4())
        UUID('...')
    """
    converted = to_uuid(value)
    if converted is not None:
        return converted
    
    if default is not None:
        return default
    
    raise ValueError(f"Invalid UUID value: {value} and no default provided")

