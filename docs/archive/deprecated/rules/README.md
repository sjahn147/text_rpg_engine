# Rules EntryPoint – Start Here

모든 에이전트/개발자는 이 페이지부터 읽고 작업하세요. 10분 내에 필수 규칙을 익히고, 필요할 때 심화 문서를 탐색할 수 있도록 구성했습니다.

## 1. TL;DR (필수)
1) `docs/CONVENTION.md` – MUST 규칙(병합 차단 기준)
2) `docs/rules/03_DECISION_TREE.md` – 차단/충돌 해결 트리
3) `docs/rules/04_QUALITY_RULES.yml` – CI 품질 게이트(자동 차단 규칙)

## 2. Why (철학)
- 시스템은 “무결성/예측가능성/검증가능성”을 우선합니다. 세부 근거는 아래 문서를 참고하세요.
  - `docs/rules/01_PHILOSOPHY.md`

## 3. How (실전 규약)
- 코딩 규약(우선순위/스코프 포함): `docs/rules/01_RULES_03_RULES_CODING_CONVENTIONS.md`
- 아키텍처와 RPG 특화 규약: `docs/ARCHITECTURE.md`
- 안티패턴과 수정 가이드: `docs/ANTI_PATTERNS.md`

## 4. TDD & 실행 루프
- 워크플로우: `docs/rules/02_WORKFLOW_TDD.md`
- 시뮬레이션/RNG/AI 테스트 가이드: `docs/ARCHITECTURE.md` 4장

## 5. 빠른 셋업 (개발 1시간 가이드)
- 에디터/도구 코드는 DB 안전 규칙(MUST)을 준수합니다(백업+Human Confirm).
- 런타임(프레임/틱)은 메모리 우선, Tick 내부 지역 가변 허용, 경계에서 스냅샷.
- 모든 PR은 최소 1개 실패 테스트 → Green → 리팩터링 순서 필수.

## 6. 리뷰 실행 도구 (시니어 감사 메커니즘)
- 리뷰어 플레이북: `docs/rules/REVIEWER_PLAYBOOK.md`
- PR 체크리스트: `docs/rules/PR_CHECKLIST.md`
- 한국어 Few‑Shot 예시: `docs/rules/REVIEW_FEWSHOTS.ko.yaml`
- 품질 파이프라인 샘플: `docs/rules/QUALITY_PIPELINE_SAMPLES.md`

## 7. FAQ
- 이 규칙이 너무 엄격한가요? → MUST만 병합 차단이며, SHOULD/MAY는 권고/경고입니다.
- 게임 로직의 비결정성은? → 시뮬레이션/프로퍼티/골든 스냅샷 테스트를 사용하세요.


