# PR 리뷰 체크리스트 (MUST 중심)

PR 병합 전, 아래 항목을 모두 확인하세요. 링크는 근거 문서입니다.

## MUST
- [ ] 타입 안전: 공개 API 100% 타입 힌트, mypy 오류 0
  - 참고: docs/CONVENTION.md, docs/rules/04_QUALITY_RULES.yml
- [ ] 비동기 I/O: 동기 I/O 사용 없음(runtime)
  - 참고: docs/rules/03_DECISION_TREE.md (6), QUALITY_RULES async_rules
- [ ] 테스트 선행: 최소 1개 실패 테스트 → Green, 커버리지 보고서 첨부
  - 참고: docs/rules/02_WORKFLOW_TDD.md, QUALITY_RULES coverage
- [ ] DB 안전: 백업/컨펌/마이그레이션(해당 시)
  - 참고: docs/rules/04_QUALITY_RULES.yml database_rules
- [ ] 금지 패턴 없음: global/except:/print/문자열 SQL 등
  - 참고: QUALITY_RULES forbidden_patterns, docs/ANTI_PATTERNS.md

## SHOULD
- [ ] Enum/Literal로 허용값 제한
- [ ] 구조화 로깅/의도 드러나는 네이밍
- [ ] 리팩터 트리거(함수>50줄, 중첩>3) 충족 여부
  - 참고: docs/rules/03_DECISION_TREE.md (3)

## 링크
- docs/rules/03_DECISION_TREE.md
- docs/rules/04_QUALITY_RULES.yml
- docs/ANTI_PATTERNS.md
- docs/ARCHITECTURE.md
- docs/CONVENTION.md
