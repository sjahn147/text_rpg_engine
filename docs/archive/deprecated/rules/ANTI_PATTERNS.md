# ANTI_PATTERNS.md – Review Verdicts and CI Mappings

문제 패턴을 리뷰에서 일관되게 판단하기 위한 기준을 정의합니다. 각 항목은 판정, 근거, CI 매핑, 수정 가이드를 포함합니다.

템플릿
- 제목
  - 판정: Reject | Request-Refactor | Informational
  - 근거: 위험/영향
  - CI 매핑: flake8/mypy/quality_rules 링크
  - Fix: 허용 형태로의 변경 지침 및 예시 링크

---

## 문자열 기반 SQL (SQL_STRING_CONCAT)
- 판정: Reject (MUST 위반)
- 근거: SQL 인젝션/쿼리 계획 캐시 실패/가독성 저하
- CI 매핑:
  - `docs/rules/04_QUALITY_RULES.yml`: forbidden_patterns.code, database_rules.priority: MUST
  - 커스텀 훅: 문자열 내 `SELECT *`, f-string으로 쿼리 구성 탐지
- Fix:
  - 파라미터 바인딩 사용, 리포지토리 API로 캡슐화

## 광범위 예외 (BROAD_EXCEPTION)
- 판정: Reject (MUST 위반)
- 근거: 에러 원인 은폐, 회복 불가 상태 양산
- CI 매핑:
  - forbidden_patterns.code: `except:`, `except Exception`
  - mypy: Any 우회 금지와 함께 타입 기반 예외 분기 권장
- Fix:
  - 구체 예외 사용, 계층별 예외 정의 후 처리

## 전역 상태 (GLOBAL_STATE)
- 판정: Reject (MUST 위반)
- 근거: 테스트 불가능/경합 조건/숨은 의존성 증가
- CI 매핑:
  - forbidden_patterns.code: `global `
- Fix:
  - 의존성 주입, 상태 객체 스코프 제한, 불변 스냅샷 사용

## 동기 I/O (SYNC_IO_IN_RUNTIME)
- 판정: Reject (MUST 위반)
- 근거: 프레임 블로킹, 지연 누적
- CI 매핑:
  - async_rules: block_sync_io: true
- Fix:
  - 비동기 클라이언트 사용, 컨텍스트 매니저화

참조: `docs/ARCHITECTURE.md` 2.1/2.3, `docs/rules/03_DECISION_TREE.md` 8장

## 불변성 무시 – 외부 경계
- 판정: Request-Refactor (SHOULD)
- 근거: 사이드 이펙트/디버깅 비용 증가
- Fix:
  - 외부로는 스냅샷/DTO로만 노출, 내부는 지역 가변 허용

## 테스트 우회 – 구현 후 테스트
- 판정: Reject (MUST)
- 근거: 회귀/커버리지 공백
- CI 매핑:
  - test_rules: require_red_phase_before_implementation: true
- Fix:
  - 최소 실패 테스트 → 그린 구현 → 리팩터링 절차 준수


