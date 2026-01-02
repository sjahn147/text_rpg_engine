# 연결 풀 크기 조정 적용 요약

## 적용 일자
2026-01-01

## 적용 내용

### 1. 연결 풀 크기 동적 조정

**파일**: `database/connection.py`

```python
# 테스트 환경 자동 감지
is_test = (
    "pytest" in sys.modules or 
    any("pytest" in arg for arg in sys.argv) or
    "PYTEST_CURRENT_TEST" in os.environ
)

# 환경별 연결 풀 크기 설정
min_size = 2
max_size = 20 if is_test else 10  # 테스트: 20, 프로덕션: 10
```

### 2. 변경 사항

#### Before
```python
self._pool = await asyncpg.create_pool(
    ...
    min_size=2,
    max_size=10  # 고정값
)
```

#### After
```python
self._pool = await asyncpg.create_pool(
    ...
    min_size=2,
    max_size=20 if is_test else 10,  # 테스트 환경: 20
    command_timeout=60  # 타임아웃 증가
)
```

### 3. 로깅 개선

```python
self.logger.info(f"Database connection pool initialized successfully (min={min_size}, max={max_size}, test={is_test})")
```

연결 풀 초기화 시 크기와 환경 정보를 로그에 기록합니다.

## 효과

### 예상 효과
- **연결 풀 고갈 감소**: 테스트 환경에서 최대 연결 수 2배 증가 (10 → 20)
- **동시 실행 안정성 향상**: 여러 테스트 동시 실행 시 연결 풀 충돌 감소
- **타임아웃 방지**: `command_timeout=60`으로 긴 실행 시간 테스트 지원

### 제한사항
- **근본 해결 아님**: Fixture 스코프 변경이나 트랜잭션 격리가 더 근본적인 해결책
- **서버 레벨 제한**: PostgreSQL 서버의 `max_connections` 설정에 따라 여전히 제한될 수 있음

## 테스트 결과

### 개별 실행
- ✅ 모든 테스트 통과

### 전체 실행
- ⚠️ 일부 테스트 여전히 실패 (6개)
- **원인**: Fixture 스코프 문제로 인한 연결 풀 공유 이슈

## 다음 단계

### 권장 추가 개선
1. **Fixture 스코프 변경**: `scope="function"` → `scope="session"`
2. **트랜잭션 격리**: 각 테스트마다 트랜잭션 롤백으로 데이터 격리
3. **테스트 실행 제한**: `pytest -n 2` (최대 2개 동시 실행)

자세한 내용은 `docs/qa/DB_CONNECTION_POOL_ISSUE_ANALYSIS.md` 참조

