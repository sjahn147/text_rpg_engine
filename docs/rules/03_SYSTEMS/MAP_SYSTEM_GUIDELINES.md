# 맵 시스템 가이드라인

> **상태**: Placeholder - 구현 예정  
> **참고 문서**: `docs/design/UI_REDESIGN_BG3_STYLE.md`, `docs/design/UI_REDESIGN_BG3_STYLE_SYSTEM_INTEGRATION.md`

## ⚠️ 중요: 구현 전 필수 읽기

- `00_CORE/01_PHILOSOPHY.md`: 핵심 개발 철학
- `00_CORE/02_ARCHITECTURE_PRINCIPLES.md`: 아키텍처 설계 원칙
- `database/setup/mvp_schema.sql`: 데이터베이스 스키마 참조 필수

## 1. 개요

맵 시스템은 전체 맵 뷰, 발견한 셀 표시, 퀘스트 마커 등을 관리하는 시스템입니다.

## 2. 맵 데이터 구조

### 2.1 계층적 구조

```
지역 (Region)
  └── 위치 (Location)
      └── 셀 (Cell)
```

### 2.2 데이터 소스

- **전체 맵**: `game_data.world_regions`, `game_data.world_locations`, `game_data.world_cells` 테이블
- **발견한 셀**: `discoveredCells` Set

## 3. API 엔드포인트

### 3.1 필수 API

- [ ] `/api/gameplay/map/{session_id}`: 맵 데이터 조회 (계층적 구조: 지역 → 위치 → 셀)
- [ ] `/api/gameplay/map/discovered/{session_id}`: 발견한 셀 목록 조회
  - **참고**: `discoveredCells` Set 활용

## 4. Service Layer

### 4.1 MapService (생성 예정)

- [ ] `MapService` 생성 (`app/services/gameplay/map_service.py`)
  - **참고**: `00_CORE/02_ARCHITECTURE_PRINCIPLES.md` - Service 계층 원칙
  - **참고**: `BaseGameplayService` 상속

## 5. UI 통합

### 5.1 맵 시스템

- [ ] 전체 맵 뷰 구현
- [ ] 발견한 셀 표시
- [ ] 퀘스트 마커 표시
- [ ] 미니맵 개선

## 6. 프론트엔드 상태 관리

### 6.1 Zustand Store 확장

- [ ] `mapData`: 전체 맵 데이터 (계층적 구조)
- [ ] `currentLocation`: 현재 위치 정보

## 7. TODO

이 문서는 placeholder입니다. 구현 시 다음 사항들을 추가해야 합니다:

1. 맵 데이터 구조 상세 정의
2. 맵 렌더링 방법
3. 발견한 셀 추적 로직
4. 퀘스트 마커 표시 로직
5. 맵 테스트 방법

## 8. 참고 문서

- `docs/design/UI_REDESIGN_BG3_STYLE.md`: 맵 시스템 기획
- `docs/design/UI_REDESIGN_BG3_STYLE_SYSTEM_INTEGRATION.md`: 맵 시스템 통합 가이드
- `04_DEVELOPMENT/UI_REDESIGN_TODO.md`: UI 리디자인 TODO

