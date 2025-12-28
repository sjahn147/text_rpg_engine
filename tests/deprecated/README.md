# Deprecated Tests (삭제 예정)

> **아카이브 날짜**: 2025-10-20  
> **삭제 예정일**: 2025-11-01 (2주 후)

---

## ⚠️ 이 테스트들은 삭제 예정입니다

이 디렉토리의 테스트들은 다음 이유로 **삭제 예정**입니다:

### 삭제 사유

1. **중복 테스트**: 다른 테스트와 기능이 중복됨
2. **일회성 스크립트**: 특정 문제 해결용 임시 코드
3. **의미 없는 테스트**: 실제 검증 가치가 없음
4. **구 인프라 의존**: 더 이상 존재하지 않는 코드 테스트

---

## 📂 파일 목록 및 삭제 이유

### 중복 테스트
```
database_test.py
├─ 이유: test_database_connection.py와 중복
└─ 대체: tests/unit/test_database_connection.py

test_simple_db_connection.py
├─ 이유: 기본 DB 연결 테스트 중복
└─ 대체: tests/active/integration/test_entity_manager_db_integration.py
```

### 디버깅/수정 스크립트 (일회성)
```
test_db_connection_debug.py
└─ 이유: 연결 문제 디버깅용 임시 스크립트

fix_triggers.py
└─ 이유: DB 트리거 수정용 일회성 스크립트
```

### 구버전 테스트 (Legacy보다 오래됨)
```
database_integrity_test.py
├─ 이유: 구 스키마 기반 무결성 테스트
└─ 대체: 새로 작성 예정 (tests/active/integration/test_data_integrity.py)

scenarios/test_simple_db_scenarios.py
├─ 이유: 초기 프로토타입용 단순 시나리오
└─ 대체: tests/active/scenarios/test_real_db_scenarios.py

scenarios/test_direct_db_scenarios.py
├─ 이유: Manager 없이 직접 DB 접근 (안티패턴)
└─ 대체: Repository 패턴 사용

scenarios/test_final_integration.py
├─ 이유: "최종" 통합 테스트 (실제로는 최종이 아님)
└─ 대체: tests/active/integration/test_manager_integration.py
```

### 무효화된 통합 테스트
```
integration/test_db_integrity.py
├─ 이유: database_integrity_test.py와 중복
└─ 대체: 새로 작성 예정

integration/test_game_flow.py
├─ 이유: 구 아키텍처 기반, 실행 불가
└─ 대체: tests/legacy/integration/test_mvp_goals.py (수정 후)

integration/test_improved_db_integration.py
├─ 이유: "improved"가 붙었지만 실제로는 legacy
└─ 대체: tests/active/integration/test_manager_integration.py
```

---

## 🔍 주요 문제점

### 1. 테스트 이름의 혼란
- `test_simple_*`, `test_improved_*`, `test_final_*` 같은 임시 이름
- 실제 기능을 설명하지 않음

### 2. 일관성 없는 구조
- 일부는 pytest, 일부는 스크립트
- 픽스처 사용 불일치

### 3. 코드 품질 낮음
- 하드코딩된 값
- 에러 처리 부족
- 문서화 부족

---

## ✅ 대체 가이드

### 기본 DB 연결 테스트
```python
# 삭제 예정: tests/deprecated/database_test.py
# 대체: tests/unit/test_database_connection.py

@pytest.mark.asyncio
async def test_connection_initialization():
    """데이터베이스 연결 초기화 테스트"""
    db = DatabaseConnection()
    await db.initialize()
    assert db.pool is not None
    await db.close()
```

### DB 무결성 테스트
```python
# 삭제 예정: tests/deprecated/database_integrity_test.py
# 대체: tests/active/integration/test_data_integrity.py (작성 예정)

@pytest.mark.asyncio
async def test_foreign_key_constraints(db_connection):
    """외래 키 제약조건 검증"""
    # 새로운 스키마 기반으로 작성
```

### 시나리오 테스트
```python
# 삭제 예정: tests/deprecated/scenarios/test_simple_db_scenarios.py
# 대체: tests/active/scenarios/test_real_db_scenarios.py

class TestRealDBScenarios:
    async def test_entity_creation_scenario(self, managers):
        """엔티티 생성 시나리오"""
        # Repository 패턴 사용
        # 정적 템플릿 기반
```

---

## 📅 삭제 일정

### Phase 1: 2주 유예 (2025-10-20 ~ 2025-11-01)
- 현재: `tests/deprecated/` 디렉토리에 보관
- 목적: 혹시 필요한 코드가 있는지 최종 확인

### Phase 2: 삭제 (2025-11-01 이후)
- 전체 `tests/deprecated/` 디렉토리 삭제
- Git 히스토리에는 남아있음

---

## 🚨 주의사항

만약 이 테스트들 중 **꼭 필요한 것**이 있다면:
1. 즉시 `tests/legacy/`로 이동 (아카이브로 보관)
2. 또는 새로운 테스트로 재작성하여 `tests/active/`에 추가
3. `TEST_REFACTORING_DECISION.md`에 이유 문서화

---

## 📊 통계

```
총 파일: 11개
├─ 중복: 3개
├─ 일회성 스크립트: 2개
├─ 구버전 테스트: 3개
└─ 무효화된 통합 테스트: 3개
```

---

**아카이브 날짜**: 2025-10-20  
**검토자**: AI Assistant  
**최종 삭제 예정**: 2025-11-01

