# 개발 워크플로우 가이드

> **최신화 날짜**: 2026-01-03  
> **목적**: 신규 개발자가 새로운 기능을 추가하거나 기존 기능을 수정할 때 따라야 할 단계별 가이드  
> **핵심 원칙**: 문서 먼저, 테스트 먼저, 철학 준수

---

## 📋 목차

1. [개발 시작 전 체크리스트](#개발-시작-전-체크리스트)
2. [새로운 기능 추가하기](#새로운-기능-추가하기)
3. [기존 기능 수정하기](#기존-기능-수정하기)
4. [데이터베이스 스키마 변경하기](#데이터베이스-스키마-변경하기)
5. [API 엔드포인트 추가하기](#api-엔드포인트-추가하기)
6. [테스트 작성하기](#테스트-작성하기)
7. [코드 리뷰 체크리스트](#코드-리뷰-체크리스트)

---

## 개발 시작 전 체크리스트

### 필수 문서 읽기

- [ ] `00_CORE/01_PHILOSOPHY.md` - 핵심 개발 철학 이해
- [ ] `00_CORE/02_ARCHITECTURE_PRINCIPLES.md` - 아키텍처 설계 원칙 이해
- [ ] `01_TYPE_SAFETY/UUID_GUIDELINES.md` - UUID 사용법 (가장 중요한 에러 방지)
- [ ] 작업할 시스템의 가이드라인 확인 (`03_SYSTEMS/` 폴더)

### 환경 설정 확인

- [ ] 데이터베이스 설정 완료 (`database/setup/mvp_schema.sql` 실행)
- [ ] 의존성 설치 완료 (`pip install -r requirements.txt`)
- [ ] 테스트 실행 가능 (`python -m pytest tests/qa/ -v`)

### 필수 참조 파일 확인

- [ ] `database/setup/mvp_schema.sql` - 데이터베이스 스키마 (DB 작업 시 필수)
- [ ] `app/common/utils/uuid_helper.py` - UUID 헬퍼 함수 (UUID 작업 시 필수)

---

## 새로운 기능 추가하기

### 1단계: 문제 정의 및 계획 (30분)

1. **문제 정의**
   - 무엇을 해결하려는가?
   - 왜 필요한가?
   - 기존 시스템과 어떻게 통합되는가?

2. **관련 문서 확인**
   - 관련 시스템 가이드라인 확인 (`03_SYSTEMS/` 폴더)
   - 아키텍처 원칙 확인 (`00_CORE/02_ARCHITECTURE_PRINCIPLES.md`)
   - 데이터베이스 스키마 확인 (`database/setup/mvp_schema.sql`)

3. **계획 수립**
   - 필요한 API 엔드포인트 정의
   - 필요한 데이터베이스 변경 사항 정의
   - 필요한 Service/Manager/Repository 계층 정의

### 2단계: 데이터베이스 설계 (1시간)

**⚠️ 데이터베이스 작업 전 필수 확인**:
- `02_DATABASE/DATABASE_SCHEMA_DESIGN.md` 읽기
- `database/setup/mvp_schema.sql` 참조 필수

1. **스키마 설계**
   - `game_data`, `reference_layer`, `runtime_data` 중 어느 스키마에 속하는가?
   - Reference Layer 우회 금지 원칙 준수 확인
   - UUID 타입 사용 확인
   - JSONB 필드 설계 확인

2. **마이그레이션 작성**
   - `02_DATABASE/MIGRATION_GUIDELINES.md` 참조
   - Idempotent 마이그레이션 작성
   - 롤백 계획 수립

### 3단계: Repository 계층 구현 (1시간)

1. **Repository 클래스 생성**
   - `database/repositories/` 폴더에 생성
   - 데이터베이스 쿼리만 담당
   - 비즈니스 로직 포함 금지

2. **타입 안전성 확인**
   - UUID 타입 구분 (`uuid_helper.py` 사용)
   - JSONB 직렬화 확인
   - 트랜잭션 범위 확인

### 4단계: Manager 계층 구현 (2시간)

1. **Manager 클래스 생성**
   - `app/managers/` 폴더에 생성
   - Repository를 사용하여 비즈니스 로직 구현
   - 에러 처리: `common/utils/error_handler.py` 사용

2. **에러 처리**
   - `04_DEVELOPMENT/ERROR_HANDLING_GUIDELINES.md` 참조
   - Manager 계층 에러 처리 시스템 사용

### 5단계: Service 계층 구현 (2시간)

1. **Service 클래스 생성**
   - `app/services/` 폴더에 생성
   - `BaseGameplayService` 상속 고려
   - 여러 Manager를 조합하여 사용

2. **에러 처리**
   - `app/common/decorators/error_handler.py` 사용
   - FastAPI `HTTPException`으로 변환

### 6단계: API 엔드포인트 추가 (1시간)

1. **Route 파일 수정**
   - `app/ui/backend/routes/` 폴더에 추가
   - Service 계층 호출
   - 타입 힌트 명시

2. **API 문서화**
   - FastAPI 자동 문서화 활용
   - 요청/응답 모델 정의

### 7단계: 테스트 작성 (2시간)

**⚠️ 테스트 작성 전 필수 확인**:
- `04_DEVELOPMENT/TESTING_GUIDELINES.md` 읽기
- 커버리지 80% 이상 목표

1. **단위 테스트**
   - Repository 테스트
   - Manager 테스트
   - Service 테스트

2. **통합 테스트**
   - API 엔드포인트 테스트
   - 전체 워크플로우 테스트

3. **테스트 실행**
   ```bash
   python -m pytest tests/ -v --cov=app --cov-report=html
   ```

### 8단계: 코드 리뷰 및 문서화 (1시간)

1. **코드 리뷰 체크리스트 확인**
   - 아래 "코드 리뷰 체크리스트" 참조

2. **문서 업데이트**
   - 관련 가이드라인 문서 업데이트
   - CHANGELOG 업데이트

---

## 기존 기능 수정하기

### 1단계: 변경 사항 파악 (30분)

1. **현재 구현 확인**
   - 관련 코드 읽기
   - 관련 테스트 읽기
   - 관련 문서 읽기

2. **변경 범위 정의**
   - 어떤 부분을 수정하는가?
   - 어떤 부분에 영향을 주는가?
   - Breaking change가 있는가?

### 2단계: 테스트 작성/수정 (1시간)

1. **기존 테스트 확인**
   - 기존 테스트가 통과하는지 확인
   - 수정이 필요한 테스트 식별

2. **새 테스트 작성**
   - 변경 사항을 검증하는 테스트 작성
   - TDD 방식으로 진행

### 3단계: 코드 수정 (2-4시간)

1. **코드 수정**
   - 철학 원칙 준수 확인
   - 타입 안전성 확인
   - 에러 처리 확인

2. **테스트 통과 확인**
   - 모든 테스트 통과 확인
   - 커버리지 확인

### 4단계: 코드 리뷰 및 문서화 (1시간)

1. **코드 리뷰 체크리스트 확인**
2. **문서 업데이트**

---

## 데이터베이스 스키마 변경하기

### 1단계: 스키마 설계 (1시간)

**⚠️ 필수 확인**:
- `02_DATABASE/DATABASE_SCHEMA_DESIGN.md` 읽기
- `database/setup/mvp_schema.sql` 참조 필수
- Reference Layer 우회 금지 원칙 준수

1. **스키마 설계**
   - 어느 스키마에 속하는가? (`game_data`, `reference_layer`, `runtime_data`)
   - Reference Layer를 통한 연결인가?
   - UUID 타입 사용인가?
   - JSONB 필드 설계인가?

2. **마이그레이션 계획**
   - Idempotent 마이그레이션 작성
   - 롤백 계획 수립
   - 데이터 마이그레이션 계획

### 2단계: 마이그레이션 작성 (2시간)

1. **마이그레이션 스크립트 작성**
   - `02_DATABASE/MIGRATION_GUIDELINES.md` 참조
   - Idempotent 마이그레이션 작성
   - 롤백 스크립트 작성

2. **테스트 환경에서 실행**
   - 테스트 데이터베이스에서 실행
   - 롤백 테스트

### 3단계: 스키마 업데이트 (1시간)

1. **`mvp_schema.sql` 업데이트**
   - 마이그레이션 내용 반영
   - 주석 업데이트

2. **문서 업데이트**
   - `02_DATABASE/DATABASE_SCHEMA_DESIGN.md` 업데이트 (필요 시)

---

## API 엔드포인트 추가하기

### 1단계: API 설계 (30분)

1. **엔드포인트 정의**
   - HTTP 메서드 (GET, POST, PUT, DELETE)
   - 경로 정의
   - 요청/응답 모델 정의

2. **Service 계층 확인**
   - 필요한 Service 메서드 확인
   - 없으면 Service 계층 구현 필요

### 2단계: Route 구현 (1시간)

1. **Route 파일 수정**
   - `app/ui/backend/routes/` 폴더에 추가
   - Service 계층 호출
   - 타입 힌트 명시

2. **에러 처리**
   - `app/common/decorators/error_handler.py` 사용
   - FastAPI `HTTPException`으로 변환

### 3단계: 테스트 작성 (1시간)

1. **API 테스트 작성**
   - 요청/응답 테스트
   - 에러 케이스 테스트

2. **테스트 실행**
   ```bash
   python -m pytest tests/ -v
   ```

---

## 테스트 작성하기

### 테스트 작성 전 필수 확인

- [ ] `04_DEVELOPMENT/TESTING_GUIDELINES.md` 읽기
- [ ] 커버리지 80% 이상 목표

### 테스트 카테고리

1. **단위 테스트 (Unit Tests)**
   - 개별 함수/메서드 테스트
   - Mock 사용 가능

2. **통합 테스트 (Integration Tests)**
   - 여러 계층 통합 테스트
   - 실제 데이터베이스 사용

3. **시나리오 테스트 (Scenario Tests)**
   - 전체 워크플로우 테스트
   - 실제 사용 시나리오 기반

4. **QA 테스트 (QA Tests)**
   - 품질 보증 테스트
   - 엣지 케이스 테스트

### 테스트 작성 예시

```python
import pytest
from app.managers.entity_manager import EntityManager
from database.connection import DatabaseConnection

@pytest.mark.asyncio
async def test_create_entity(db_connection: DatabaseConnection):
    """엔티티 생성 테스트"""
    manager = EntityManager(db_connection)
    
    result = await manager.create_entity(
        entity_id="TEST_ENTITY_001",
        entity_type="npc",
        session_id=test_session_id
    )
    
    assert result.success is True
    assert result.data is not None
```

---

## 코드 리뷰 체크리스트

### 철학 원칙 준수

- [ ] Data-Centric Development 원칙 준수
- [ ] Immutability-First 원칙 준수
- [ ] Type-Safety-First 원칙 준수
- [ ] Async-First 원칙 준수
- [ ] 불확정성 불허 원칙 준수

### 아키텍처 원칙 준수

- [ ] Reference Layer 우회 금지 원칙 준수
- [ ] Factory vs Handler 패턴 올바른 사용
- [ ] Service 계층 원칙 준수
- [ ] Manager/Repository 계층 원칙 준수

### 타입 안전성

- [ ] UUID 타입 구분 (`uuid_helper.py` 사용)
- [ ] JSONB 직렬화 확인
- [ ] 트랜잭션 범위 확인
- [ ] 타입 힌트 100% 적용

### 에러 처리

- [ ] 계층별 적절한 에러 처리 시스템 사용
- [ ] 명시적 에러 처리 (기본값으로 은폐 금지)
- [ ] 에러 로깅 확인

### 테스트

- [ ] 테스트 커버리지 80% 이상
- [ ] 모든 테스트 통과
- [ ] 통합 테스트 포함

### 문서화

- [ ] 관련 가이드라인 문서 업데이트
- [ ] CHANGELOG 업데이트
- [ ] 주석 및 docstring 작성

---

## 참고 문서

- `00_CORE/01_PHILOSOPHY.md`: 핵심 개발 철학
- `00_CORE/02_ARCHITECTURE_PRINCIPLES.md`: 아키텍처 설계 원칙
- `01_TYPE_SAFETY/UUID_GUIDELINES.md`: UUID 사용법
- `01_TYPE_SAFETY/TRANSACTION_GUIDELINES.md`: 트랜잭션 사용법
- `02_DATABASE/DATABASE_SCHEMA_DESIGN.md`: 데이터베이스 스키마 설계
- `04_DEVELOPMENT/TESTING_GUIDELINES.md`: 테스트 작성 가이드
- `04_DEVELOPMENT/ERROR_HANDLING_GUIDELINES.md`: 에러 처리 가이드

---

## 결론

이 가이드를 따라 개발하면:
- ✅ 철학 원칙을 준수한 코드 작성
- ✅ 아키텍처 원칙을 준수한 설계
- ✅ 타입 안전성 확보
- ✅ 테스트 커버리지 확보
- ✅ 일관된 개발 프로세스 유지

**핵심**: 문서 먼저, 테스트 먼저, 철학 준수

