# Reviewer Playbook – 규칙→행동 매핑

본 문서는 시니어 리뷰어처럼 일관된 판단을 내리기 위한 '규칙→행동' 매핑을 제공합니다.

## 1. 판단 카테고리
- [BLOCK] 병합 불가: MUST 위반, 보안/무결성 위험
- [REQUEST CHANGES] 리팩토링 필요: SHOULD 위반 또는 구조적 위험
- [TEST REQUIRED] 증명 부족: 테스트/재현/지표 누락
- [HUMAN CONFIRM] 사용자 확인 필요: DB/스키마/데이터 파괴 위험
- [APPROVE] 승인: 기준 충족

## 2. 규칙→행동 매핑 (핵심 케이스)
- 전역 상태 사용(global) → [BLOCK]
  - 근거: docs/rules/03_DECISION_TREE.md (5), docs/rules/04_QUALITY_RULES.yml (forbidden_patterns)
  - 조치: DI/Context로 상태 이관
- 런타임 동기 I/O → [BLOCK]
  - 근거: DECISION_TREE (6), QUALITY_RULES async_rules
  - 조치: async 전환, 컨텍스트 매니저
- 문자열 기반 SQL/스키마 변경 → [HUMAN CONFIRM] 또는 [BLOCK]
  - 근거: QUALITY_RULES database_rules
  - 조치: 백업/마이그레이션/환경확인/컨펌
- 테스트 선행 위반 → [TEST REQUIRED]
  - 근거: 02_WORKFLOW_TDD.md (2.2/2.5)
  - 조치: 실패 테스트 작성 후 구현
- 불변성 경계 위반(외부 노출) → [REQUEST CHANGES]
  - 근거: ARCHITECTURE.md (2.1/3)
  - 조치: 스냅샷/DTO 경계 확립

## 3. 리뷰 코멘트 템플릿
- [차단] <사유>
  - 근거(문서/조항), 영향, 즉시 조치 목록(번호)
- [수정 요청] <영역>
  - 문제점, 권장 구조, 참고 링크(ANTI_PATTERNS/ARCHITECTURE)
- [테스트 필요] <시나리오>
  - 최소 실패 테스트 목록, 경계/에지케이스
- [사용자 확인 필요] <작업>
  - 위험 요약, 필요 단계(백업/환경/승인), 대기 선언
- [승인]
  - 충족 기준 요약, 후속 제안(선택)

## 4. 운영 절차
- 차단 사유 발견 시 즉시 [BLOCK]
- 테스트 부재/증명 부족 시 [TEST REQUIRED]
- DB 관련 작업은 기본 [HUMAN CONFIRM]
- 기타는 [REQUEST CHANGES] 또는 [APPROVE]

## 5. 링크
- docs/rules/03_DECISION_TREE.md
- docs/rules/04_QUALITY_RULES.yml
- docs/ANTI_PATTERNS.md
- docs/ARCHITECTURE.md
- docs/CONVENTION.md
