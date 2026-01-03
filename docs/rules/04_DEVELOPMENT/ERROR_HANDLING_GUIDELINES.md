# 에러 처리 가이드라인

> **최신화 날짜**: 2026-01-03  
> **적용 범위**: 모든 에러 처리 및 예외 처리 시 필수 읽기

## ⚠️ 중요: 계층별 에러 처리 시스템 사용

**각 계층별로 적절한 에러 처리 시스템을 사용해야 합니다. 혼용하지 마세요.**

## 1. 에러 처리 시스템 구조 (리팩토링 완료)

### 1.1 에러 처리 파일 위치

```
common/
├── error_handling/
│   ├── error_types.py          # System 계층: RPGEngineError 계층 구조
│   └── error_handler.py        # 선택적: 통합 에러 추적용 (향후 사용 예정)
├── utils/
│   └── error_handler.py        # Manager 계층: ManagerError 및 유틸리티
└── exceptions/
    └── __init__.py             # 비어있음 (향후 확장 가능)

app/common/
└── decorators/
    └── error_handler.py        # Service 계층: handle_service_errors 데코레이터
```

### 1.2 각 시스템의 역할 및 사용처 (리팩토링 후)

| 파일 | 역할 | 사용처 | 상태 |
|------|------|--------|------|
| `common/error_handling/error_types.py` | **System 계층**: RPGEngineError 계층 구조 정의 | `app/systems/time_system.py`, `app/core/framework_manager.py` | **System 계층에서 사용 중** |
| `common/error_handling/error_handler.py` | **선택적**: 통합 에러 추적 및 모니터링 (향후 사용 예정) | 현재 사용 안 됨 (향후 통합 에러 추적용) | **선택적 모듈** |
| `common/utils/error_handler.py` | **Manager 계층**: ManagerError 및 유틸리티 함수 | `app/managers/entity_manager.py`, `app/managers/object_state_manager.py` | **Manager 계층에서 사용 중** |
| `app/common/decorators/error_handler.py` | **Service 계층**: handle_service_errors 데코레이터 | `app/services/world_editor/` (cell_service, entity_service, location_service) | **Service 계층에서 사용 중** |

### 1.3 리팩토링 변경 사항

**변경 전**:
- `framework_manager`에서 ErrorHandler를 필수 의존성으로 관리
- ErrorHandler가 실제로는 사용되지 않음

**변경 후**:
- `framework_manager`에서 ErrorHandler 의존성 제거
- 각 계층별로 명확히 분리된 에러 처리 시스템 사용
- `common/error_handling/error_handler.py`는 선택적 모듈로 유지 (향후 통합 에러 추적용)

## 2. 계층별 에러 처리 가이드라인

### 2.1 Manager 계층

**사용 시스템**: `common/utils/error_handler.py`

**사용 방법**:
```python
from common.utils.error_handler import (
    handle_database_error,
    handle_validation_error,
    validate_session_id,
    validate_entity_id,
    ManagerError
)

# 데이터베이스 에러 처리
try:
    await conn.execute("INSERT INTO ...")
except Exception as e:
    db_error = handle_database_error(e, "create_entity", "game_data.entities")
    self.logger.error(f"Database error: {db_error.message}")
    return EntityCreationResult.error(
        message=db_error.message,
        error_code="DATABASE_ERROR"
    )

# 검증 에러 처리
try:
    if not validate_entity_id(entity_id):
        raise ValueError("Invalid entity ID")
except Exception as e:
    validation_error = handle_validation_error(e, "entity_id")
    return EntityCreationResult.error(
        message=validation_error.message,
        error_code="VALIDATION_ERROR"
    )
```

**ManagerError 특징**:
- `error_type`: ErrorType Enum (SCHEMA_MISMATCH, DATABASE_ERROR, VALIDATION_ERROR 등)
- `details`: Dict[str, Any] (추가 정보)
- Manager 계층 전용 에러 타입

### 2.2 Service 계층

**사용 시스템**: `app/common/decorators/error_handler.py`

**사용 방법**:
```python
from app.common.decorators.error_handler import handle_service_errors

class MyService:
    @handle_service_errors
    async def delete_entity(self, entity_id: str) -> bool:
        """엔티티 삭제 (자동으로 HTTPException 변환)"""
        # ValueError → HTTPException(status_code=400)
        # ForeignKeyViolationError → HTTPException(status_code=409)
        # UniqueViolationError → HTTPException(status_code=409)
        # 기타 Exception → HTTPException(status_code=500)
        ...
```

**handle_service_errors 데코레이터 특징**:
- 자동으로 Exception을 HTTPException으로 변환
- FastAPI와 통합
- Service 계층 전용

### 2.3 System 계층 (TimeSystem 등)

**사용 시스템**: `common/error_handling/error_types.py`

**사용 방법**:
```python
from common.error_handling.error_types import (
    SystemError,
    ErrorContext,
    ErrorSeverity
)

# SystemError 사용
raise SystemError(
    message=f"TimeSystem 시작 실패: {str(e)}",
    error_code="TIMESYSTEM_START_FAILED",
    context=ErrorContext(session_id=session_id)
)
```

**RPGEngineError 특징**:
- `error_code`: 에러 코드
- `severity`: ErrorSeverity (LOW, MEDIUM, HIGH, CRITICAL)
- `category`: ErrorCategory (DATABASE, VALIDATION, BUSINESS_LOGIC, SYSTEM 등)
- `context`: ErrorContext (user_id, session_id, entity_id 등)
- `details`: Dict[str, Any] (추가 정보)

## 3. 에러 처리 원칙

### 3.1 필수 원칙

1. **계층별 적절한 시스템 사용**:
   - Manager 계층: `common/utils/error_handler.py`
   - Service 계층: `app/common/decorators/error_handler.py`
   - System 계층: `common/error_handling/error_types.py`

2. **명시적 에러 처리**: 모든 예외를 명시적으로 처리
3. **에러 로깅**: 모든 에러를 로깅
4. **에러 정보 보존**: 원본 에러 정보 보존 (`original_error`)
5. **컨텍스트 제공**: 에러 발생 컨텍스트 정보 제공

### 3.2 금지 사항

1. **❌ 계층 간 에러 처리 시스템 혼용**: Manager에서 Service 데코레이터 사용 금지
2. **❌ 에러 무시**: `except: pass` 같은 에러 무시 금지
3. **❌ 기본값으로 에러 은폐**: 에러를 기본값으로 대체하지 않음 (불확정성 불허 원칙)
4. **❌ 추측 로직**: 에러 타입을 추측하지 않고 명시적으로 처리

## 4. 에러 처리 패턴

### 4.1 Manager 계층 패턴

```python
from common.utils.error_handler import handle_database_error, ManagerError

async def create_entity(self, entity_id: str, ...):
    """엔티티 생성"""
    try:
        # 비즈니스 로직
        result = await self._create_entity_internal(...)
        return EntityCreationResult.success(...)
        
    except Exception as e:
        # 데이터베이스 에러 처리
        if "database" in str(e).lower() or "connection" in str(e).lower():
            db_error = handle_database_error(e, "create_entity", "game_data.entities")
            self.logger.error(f"Database error: {db_error.message}")
            return EntityCreationResult.error(
                message=db_error.message,
                error_code="DATABASE_ERROR"
            )
        
        # 기타 에러
        self.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return EntityCreationResult.error(
            message=f"엔티티 생성 실패: {str(e)}",
            error_code="UNEXPECTED_ERROR"
        )
```

### 4.2 Service 계층 패턴

```python
from app.common.decorators.error_handler import handle_service_errors

class EntityService:
    @handle_service_errors
    async def delete_entity(self, entity_id: str) -> bool:
        """엔티티 삭제 (자동으로 HTTPException 변환)"""
        # ValueError → HTTPException(status_code=400)
        # ForeignKeyViolationError → HTTPException(status_code=409)
        # 기타 Exception → HTTPException(status_code=500)
        
        # 비즈니스 로직
        if not entity_id:
            raise ValueError("Entity ID is required")
        
        # Manager 호출
        result = await self.entity_manager.delete_entity(entity_id)
        if not result.success:
            raise ValueError(result.message)
        
        return True
```

### 4.3 System 계층 패턴

```python
from common.error_handling.error_types import SystemError, ErrorContext

async def start(self, session_id: str):
    """시스템 시작"""
    try:
        # 초기화 로직
        await self._initialize()
        
    except Exception as e:
        # SystemError 사용
        raise SystemError(
            message=f"시스템 시작 실패: {str(e)}",
            error_code="SYSTEM_START_FAILED",
            context=ErrorContext(session_id=session_id),
            original_error=e
        )
```

## 5. 리팩토링 완료 사항

### 5.1 리팩토링 내용

1. **framework_manager 의존성 정리**: ErrorHandler를 필수 의존성에서 제거
2. **계층별 명확한 분리**: 각 계층별로 적절한 에러 처리 시스템 사용
3. **문서화 개선**: 각 파일에 계층별 사용 목적 명시
4. **선택적 모듈 명확화**: `common/error_handling/error_handler.py`는 선택적 모듈로 유지

### 5.2 현재 구조 (리팩토링 후)

**계층별 에러 처리 시스템**:

- **Manager 계층**: `common/utils/error_handler.py` 사용 (ManagerError)
- **Service 계층**: `app/common/decorators/error_handler.py` 사용 (handle_service_errors)
- **System 계층**: `common/error_handling/error_types.py` 사용 (RPGEngineError)
- **선택적**: `common/error_handling/error_handler.py` (향후 통합 에러 추적용)

### 5.3 향후 개선 방안

**통합 에러 추적 시스템** (선택적):
- `common/error_handling/error_handler.py`를 활용하여 모든 계층의 에러를 중앙에서 추적
- 에러 통계 및 모니터링 기능 추가
- 에러 복구 메커니즘 강화

## 6. 에러 처리 체크리스트

에러 처리 구현 전 확인사항:

- [ ] **계층 확인**: 적절한 계층의 에러 처리 시스템 사용
  - Manager 계층: `common/utils/error_handler.py`
  - Service 계층: `app/common/decorators/error_handler.py`
  - System 계층: `common/error_handling/error_types.py`
- [ ] **명시적 처리**: 모든 예외를 명시적으로 처리
- [ ] **로깅**: 에러 로깅 포함
- [ ] **정보 보존**: 원본 에러 정보 보존 (`original_error`)
- [ ] **컨텍스트**: 컨텍스트 정보 제공 (session_id, entity_id 등)
- [ ] **타입 명시**: 에러 타입 명시 (ManagerError, HTTPException, SystemError)
- [ ] **추측 금지**: 추측 로직 없음 (불확정성 불허 원칙)
- [ ] **혼용 금지**: 계층 간 에러 처리 시스템 혼용 금지

## 7. 참고 문서

- `00_CORE/01_PHILOSOPHY.md`: 불확정성 불허 원칙
- `00_CORE/02_ARCHITECTURE_PRINCIPLES.md`: 아키텍처 원칙
- `common/utils/error_handler.py`: Manager 계층 에러 처리
- `app/common/decorators/error_handler.py`: Service 계층 에러 처리
- `common/error_handling/error_types.py`: System 계층 에러 타입

