# CONVENTION.md – Mandatory Coding Rules (MUST)

> **최신화 날짜**: 2025-12-28

이 문서는 리뷰와 PR 병합을 위한 "필수(MUST)" 규칙을 간결히 요약합니다. 세부 근거와 예시는 참조 문서에 링크합니다.

## 1. Types & Errors (scope: both)
- 모든 공개 함수/클래스/API에 타입 힌트 100%
- 광범위 예외 금지: `except:` / `except Exception` 사용 금지
- 명시적 예외 정의 및 처리(계층별 예외 사용)
- Any 우회 금지(`mypy: error_on_any=true`)

참조: `docs/rules/01_RULES_03_RULES_CODING_CONVENTIONS.md`, `docs/rules/04_QUALITY_RULES.yml`

## 2. Async I/O (scope: both)
- 동기 I/O 사용 금지(네트워크/파일/DB). 비동기 컨텍스트 매니저 사용
- 전역 락 금지, 필요 시 파인 그레인 락/세마포어

참조: `docs/rules/03_DECISION_TREE.md`

## 3. Test-First (scope: both)
- 구현 전 최소 1개 실패 테스트 생성(RED)
- 모든 PR은 테스트 포함 및 통과 필수(커버리지 80%는 SHOULD)
- 외부 의존성은 Mock/Stub

참조: `docs/rules/02_WORKFLOW_TDD.md`

## 4. Database Safety (scope: tooling)
- DB 쓰기 작업은 백업 생성 + Human Confirm 필요
- 스키마 변경(DROP/ALTER/TRUNCATE) 차단
- 문자열 기반 SQL, 포맷팅 SQL 금지(파라미터 쿼리/리포지토리 사용)

참조: `docs/rules/04_QUALITY_RULES.yml`

## 5. Immutability Boundary (scope: both)
- 외부로 노출되는 모델/DTO/이벤트는 불변 스냅샷
- 런타임 Tick 내부 hot path는 지역 가변 허용, Tick 경계에서 스냅샷 복원

참조: `docs/ARCHITECTURE.md`, `docs/rules/03_DECISION_TREE.md`

## 6. Security & Forbidden
- 전역 상태/하드코딩 비밀/`eval`/`exec`/`print` 금지
- 리뷰 차단 규칙은 `04_QUALITY_RULES.yml`의 MUST/forbidden_patterns 기준을 따른다

## 7. Review Checklist
- MUST 위반 여부(즉시 차단)
- SHOULD/MAY는 권고/경고로 코멘트
- 문서/의도 명확성, 로그/에러 맥락 포함 여부 확인


