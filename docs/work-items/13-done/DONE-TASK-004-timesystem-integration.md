---
id: TASK-004-timesystem-integration
type: task
status: task
epic_id: EPIC-001-object-interaction-enhancement
dependencies: []
todos:
  - TODO-003-rest-timesystem-integration
estimated_hours: 2.5
keyword: timesystem-integration
created_at: 2026-01-01T16:50:00Z
updated_at: 2026-01-01T16:50:00Z
author: agent
---

# TimeSystem 연동 확장

## 설명

시간 소모가 필요한 나머지 상호작용에 TimeSystem 연동

## 작업 내용

1. TimeSystem 인터페이스 확인
2. 나머지 핸들러에서 `time_cost` 확인 및 TimeSystem 호출
3. 시간 소모가 필요한 상호작용 목록:
   - ✅ `sleep`: 480분 (완료)
   - ✅ `eat`: 5분 (완료)
   - ✅ `drink`: 2분 (완료)
   - ⚠️ `rest`: 30분 (확인 필요)
   - ⚠️ `read`: 10-30분 (확인 필요)
   - ⚠️ `study`: 60분 (확인 필요)
   - ⚠️ `write`: 15분 (확인 필요)
   - ⚠️ `craft`: 30-120분 (확인 필요)
   - ⚠️ `cook`: 20-60분 (확인 필요)
   - ⚠️ `repair`: 30-60분 (확인 필요)
   - ⚠️ `dismantle`: 15-30분 (확인 필요)

## 예상 작업 시간

2-3시간 (중간값: 2.5시간)

## 관련 Epic

- [EPIC-001-object-interaction-enhancement](../05-epic/EPIC-001-object-interaction-enhancement.md)

## 관련 TODO

- [TODO-003-rest-timesystem-integration](../07-todo/TODO-003-rest-timesystem-integration.md)

## 구현 상태

- [x] TODO 생성 ✅
- [x] 개발 완료 ✅
- [x] 테스트 작성 ✅
- [ ] 품질 게이트 통과

