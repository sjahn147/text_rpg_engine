# RPG Engine Development Workflow – TDD & Execution Loop

> **최신화 날짜**: 2025-12-28

본 문서는 RPG Engine 개발 에이전트가 따라야 하는 작업 절차를 정의한다.
기능은 "테스트에 의해 증명되지 않으면 존재하지 않는 것"으로 간주한다.

---

## 1. Workflow Overview

[Requirement] → [Test (Red)] → [Implement (Green)] → [Refactor] → [Quality Gate]

모든 기능, 버그 수정, 리팩토링은 반드시 이 순서를 따른다.

---

## 2. Step-by-Step Protocol

### 2.1 Requirement Definition
- 입력, 출력, 실패 조건을 명시한다.
- 스펙이 불명확하면 구현을 중단하고 정의를 먼저 생성한다.
- 스토리/시나리오가 존재하는 기능은 테스트 시나리오로 변환한다.

**Output:** `spec_feature_id.md`, 또는 테스트 내부의 docstring

---

### 2.2 Test First (Red Stage)
- 실패하는 테스트를 생성한다.
- 단순 유닛 테스트가 아니라, 시나리오 기반 행동을 포함해야 한다.
- 외부 의존성(DB, API 등)은 Mock으로 대체한다.

**Test Types:**
- Unit Test (단일 함수/메서드)
- Integration Test (Entity ↔ Service ↔ DB)
- Scenario Test (게임 행위 흐름: 예 "플레이어 공격 시 경험치 증가")

---

### 2.3 Minimal Implementation (Green Stage)
- 테스트 통과에 필요한 최소한의 코드를 작성한다.
- 성능 최적화, 구조 개선은 이 단계에서 하지 않는다.
- 실패하는 테스트를 통과시키는 것만을 목표로 한다.

---

### 2.4 Refactor
- 중복, 비표준, 사이드 이펙트가 있으면 제거한다.
- 함수는 단일 책임을 가지도록 재구성한다.
- 불변성, 타입 안정성, 의존성 주입을 이 시점에 반영한다.

Refactor Triggers:
- 함수 길이 > 50줄
- if/for 중첩 > 3단계
- 유사한 코드 반복 발견

---

### 2.5 Quality Gate (Merge 조건)
- 테스트 통과
- 코드 커버리지 ≥ 80%
- mypy (타입 오류 0)
- flake8 (Lint 오류 0)
- DB 접근 코드: Safety Check 수행됨

**통과하지 못하면 PR 차단**

---

## 3. CI/CD Integration

| 단계 | 작업 |
|------|------|
| pre-commit | black, isort, flake8 |
| test | pytest, coverage |
| type-check | mypy |
| review | PR에서 철학 위반 여부 검사 |

---

## 4. Feature Completion Definition (완료 정의)

기능은 아래 모든 조건을 만족해야 “완료”로 간주한다:

- ✅ 모든 테스트 통과
- ✅ 문서(docstring, usage) 존재
- ✅ 예외 처리 명시
- ✅ 사이드 이펙트 없음
- ✅ 결정 트리에 따라 위험 통과

### RNG/AI/시뮬레이션 테스트 지침
- 단위 테스트에서 결정성 필요 시 고정 Seed 사용(Seed를 로그/리포트에 기록)
- 시뮬레이션 기반 검증: 대량 러닝 후 통계적 특성(평균/분산/분포)을 어서션
- 프로퍼티 테스트: 불변식(예: 체력은 음수가 되지 않음)을 코드로 명시
- 골든 스냅샷: 관측 가능한 결과 스냅샷을 저장/비교하여 회귀 탐지

---

## 5. Bug Fix Protocol

- 실패 테스트 추가 (재현)
- 최소 수정
- Refactor & Gate

Bug는 코드 수정이 아니라 **원인 문서화 + 재발 방지 테스트**를 포함한다.

---

## 6. Non-Functional Features (비기능 작업)
아래 작업 역시 TDD를 따른다:

| 작업 | 예 |
|------|----|
| 성능 | 엔티티 1만 개 처리 성능 |
| 보안 | SQL 인젝션 방지 테스트 |
| 회귀 | 기존 기능이 깨지지 않는 테스트 |

---

## 7. Forbidden Bypasses (우회 금지)

| 행위 | 상태 |
|------|------|
| 테스트 없는 직접 구현 | 금지 |
| 기능 개발 후 테스트 작성 | 금지 |
| 수동 테스트 주장 (“직접 돌려봄”) | 무효 |
| 통합 테스트 실패 무시 | 금지 |

---

## 8. Escalation Rule (중단 기준)

개발은 아래 상황에서 즉시 중단하고 문제를 기록해야 한다:

- 요구사항이 불명확
- 철학 위반 의도 감지
- DB 파괴 가능성 감지
- 외부 리스크 감지 (Deadlock, OOM 등)
