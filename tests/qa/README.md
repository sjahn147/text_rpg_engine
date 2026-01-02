# QA 테스트 스위트

## 개요

게임 엔진의 핵심 기능과 데이터 무결성을 체계적으로 검증하는 QA 테스트 스위트입니다.

## 테스트 구조

```
tests/qa/
├── __init__.py
├── conftest.py              # 공통 Fixtures
├── test_game_start_flow.py  # 게임 시작 플로우 테스트 (P0)
├── test_data_integrity.py   # 데이터 무결성 테스트 (P0)
├── test_transaction_integrity.py  # 트랜잭션 무결성 테스트 (P0)
└── test_api_endpoints.py    # API 엔드포인트 테스트 (P1)
```

## 테스트 실행

### 전체 테스트 실행
```bash
pytest tests/qa/ -v
```

### 특정 카테고리만 실행
```bash
# 게임 시작 플로우만
pytest tests/qa/test_game_start_flow.py -v

# 데이터 무결성만
pytest tests/qa/test_data_integrity.py -v

# 트랜잭션 무결성만
pytest tests/qa/test_transaction_integrity.py -v
```

### 커버리지 포함 실행
```bash
pytest tests/qa/ --cov=app --cov-report=html
```

## 테스트 우선순위

### P0 (Critical - 즉시 수정 필요)
- 게임 시작 플로우 전체 검증
- 외래키 제약조건 검증
- 데이터 생성 순서 검증
- SSOT 검증
- 트랜잭션 원자성 검증

### P1 (High - 빠른 시일 내 수정)
- API 엔드포인트 검증
- 에러 처리 검증

## 테스트 결과 해석

### 통과 (PASSED)
- 모든 검증 항목이 통과
- 기능이 정상적으로 동작

### 실패 (FAILED)
- 검증 항목 중 하나 이상 실패
- 기능에 문제가 있음
- 즉시 수정 필요

### 에러 (ERROR)
- 테스트 실행 중 예외 발생
- 테스트 코드 문제 또는 환경 문제
- 테스트 코드 수정 필요

## 주의사항

1. **테스트 데이터 격리**: 각 테스트는 독립적으로 실행 가능
2. **데이터베이스 상태**: 테스트 전후 데이터베이스 상태 확인
3. **외래키 제약조건**: 실제 데이터베이스를 사용하여 검증
4. **트랜잭션**: 트랜잭션 원자성 검증 포함

## 지속적 개선

- 테스트 커버리지 모니터링
- 누락된 시나리오 추가
- 테스트 성능 최적화
- 테스트 유지보수

