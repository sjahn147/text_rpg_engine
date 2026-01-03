# 저널 시스템 가이드라인

> **상태**: Placeholder - 구현 예정  
> **참고 문서**: `docs/design/UI_REDESIGN_BG3_STYLE.md`, `docs/design/UI_REDESIGN_BG3_STYLE_SYSTEM_INTEGRATION.md`

## ⚠️ 중요: 구현 전 필수 읽기

- `00_CORE/01_PHILOSOPHY.md`: 핵심 개발 철학
- `00_CORE/02_ARCHITECTURE_PRINCIPLES.md`: 아키텍처 설계 원칙
- `database/setup/mvp_schema.sql`: 데이터베이스 스키마 참조 필수

## 1. 개요

저널 시스템은 게임 플레이 전체 저널, 발견한 정보, 만난 NPC 기록, 방문한 장소 등을 관리하는 시스템입니다.

## 2. 저널 탭 구조

### 2.1 탭 목록

1. **퀘스트**: 활성 퀘스트 및 완료된 퀘스트
2. **이야기**: 게임 플레이 전체 저널, 주요 이벤트, 선택한 분기
3. **발견**: 발견한 오브젝트, 셀, 엔티티
4. **인물**: 만난 NPC 목록 및 대화 히스토리
5. **장소**: 방문한 셀/위치 목록

## 3. 데이터 소스

### 3.1 이야기 히스토리

- **소스**: `triggered_events`, `action_logs` 테이블
- **내용**: 주요 이벤트, 선택한 분기

### 3.2 발견한 정보

- **소스**: `discoveredObjects`, `discoveredCells` Set
- **내용**: 발견한 오브젝트, 셀, 엔티티

### 3.3 만난 NPC

- **소스**: `dialogue_history` 테이블
- **내용**: 만난 NPC 목록 및 대화 히스토리

### 3.4 방문한 장소

- **소스**: `discoveredCells` Set
- **내용**: 방문한 셀/위치 목록

## 4. API 엔드포인트

### 4.1 필수 API

- [ ] `/api/gameplay/journal/{session_id}`: 저널 데이터 조회 (통합)
- [ ] `/api/gameplay/journal/story/{session_id}`: 이야기 히스토리 조회
- [ ] `/api/gameplay/journal/discoveries/{session_id}`: 발견한 정보 조회
- [ ] `/api/gameplay/journal/characters/{session_id}`: 만난 NPC 목록 및 대화 히스토리
- [ ] `/api/gameplay/journal/locations/{session_id}`: 방문한 셀/위치 목록

## 5. Service Layer

### 5.1 JournalService (생성 예정)

- [ ] `JournalService` 생성 (`app/services/gameplay/journal_service.py`)
  - **참고**: `00_CORE/02_ARCHITECTURE_PRINCIPLES.md` - Service 계층 원칙
  - **참고**: `BaseGameplayService` 상속

## 6. UI 통합

### 6.1 저널 패널

- [ ] 저널 패널 컴포넌트 생성
- [ ] 탭 구조 구현 (퀘스트/이야기/발견/인물/장소)
- [ ] 검색/필터 기능 구현

## 7. 프론트엔드 상태 관리

### 7.1 Zustand Store 확장

- [ ] `journal`: 저널 데이터 (퀘스트, 이야기, 발견, 인물, 장소)
- [ ] `discoveredCells`: 발견한 셀 Set
- [ ] `discoveredEntities`: 발견한 엔티티 Set
- [ ] `storyHistory`: 이야기 히스토리 (주요 이벤트, 선택한 분기)

## 8. TODO

이 문서는 placeholder입니다. 구현 시 다음 사항들을 추가해야 합니다:

1. 저널 데이터 구조 상세 정의
2. 저널 데이터 수집 로직
3. 저널 UI 컴포넌트 설계
4. 검색/필터 기능 구현
5. 저널 테스트 방법

## 9. 참고 문서

- `docs/design/UI_REDESIGN_BG3_STYLE.md`: 저널 시스템 기획
- `docs/design/UI_REDESIGN_BG3_STYLE_SYSTEM_INTEGRATION.md`: 저널 시스템 통합 가이드
- `04_DEVELOPMENT/UI_REDESIGN_TODO.md`: UI 리디자인 TODO

