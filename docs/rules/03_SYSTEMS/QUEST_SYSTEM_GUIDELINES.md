# 퀘스트 시스템 가이드라인

> **상태**: Placeholder - 구현 예정  
> **참고 문서**: `docs/design/UI_REDESIGN_BG3_STYLE.md`, `docs/design/UI_REDESIGN_BG3_STYLE_CORRECTIONS.md`

## ⚠️ 중요: 구현 전 필수 읽기

- `00_CORE/01_PHILOSOPHY.md`: 핵심 개발 철학
- `00_CORE/02_ARCHITECTURE_PRINCIPLES.md`: 아키텍처 설계 원칙
- `database/setup/mvp_schema.sql`: 데이터베이스 스키마 참조 필수

## 1. 개요

퀘스트 시스템은 게임 내 퀘스트의 생성, 진행, 완료, 실패를 관리하는 시스템입니다.

## 2. 데이터베이스 구조

### 2.1 현재 구조 (검토 필요)

**옵션 A: `triggered_events` 테이블 활용**
```sql
runtime_data.triggered_events (
  event_id UUID PRIMARY KEY,
  session_id UUID,
  event_type VARCHAR(50),  -- 'quest'
  event_data JSONB,  -- 퀘스트 정보, 목표, 진행도 등
  source_entity_ref UUID,  -- 퀘스트 제공자
  target_entity_ref UUID,  -- 퀘스트 대상
  triggered_at TIMESTAMP,
  ...
)
```

**옵션 B: `runtime_data.quests` 테이블 생성 (권장)**
```sql
runtime_data.quests (
  quest_id UUID PRIMARY KEY,
  session_id UUID,
  quest_template_id VARCHAR(50),  -- FK to game_data.quest_templates (향후)
  quest_status VARCHAR(50),  -- 'active', 'completed', 'failed'
  quest_data JSONB,  -- 퀘스트 정보, 목표, 진행도 등
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  ...
)
```

### 2.2 향후 스키마

- [ ] `game_data.quest_templates`: 퀘스트 템플릿 (정적 데이터)
- [ ] `runtime_data.quests`: 퀘스트 상태 관리 (런타임 데이터)

## 3. API 엔드포인트

### 3.1 필수 API

- [ ] `/api/gameplay/quests/{session_id}`: 퀘스트 목록 조회
- [ ] `/api/gameplay/quests/{session_id}/events`: 퀘스트 이벤트 조회
  - **참고**: `triggered_events` 테이블, `event_type LIKE 'QUEST_%'` 필터링

## 4. Service Layer

### 4.1 QuestService (생성 예정)

- [ ] `QuestService` 생성 (`app/services/gameplay/quest_service.py`)
  - **참고**: `00_CORE/02_ARCHITECTURE_PRINCIPLES.md` - Service 계층 원칙
  - **참고**: `BaseGameplayService` 상속

## 5. UI 통합

### 5.1 퀘스트 저널

- [ ] 퀘스트 목록 표시
- [ ] 퀘스트 목표 및 진행도 표시
- [ ] 완료된 퀘스트 기록

## 6. TODO

이 문서는 placeholder입니다. 구현 시 다음 사항들을 추가해야 합니다:

1. 퀘스트 데이터 구조 상세 정의
2. 퀘스트 상태 전이 로직
3. 퀘스트 이벤트 처리 방법
4. 퀘스트 UI 컴포넌트 설계
5. 퀘스트 테스트 방법

## 7. 참고 문서

- `docs/design/UI_REDESIGN_BG3_STYLE.md`: 퀘스트 시스템 기획
- `docs/design/UI_REDESIGN_BG3_STYLE_CORRECTIONS.md`: 퀘스트 저장 구조
- `04_DEVELOPMENT/UI_REDESIGN_TODO.md`: UI 리디자인 TODO

