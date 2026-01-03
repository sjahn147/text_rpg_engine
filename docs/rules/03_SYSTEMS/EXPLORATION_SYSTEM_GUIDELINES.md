# 탐험 시스템 가이드라인

> **상태**: Placeholder - 구현 예정  
> **참고 문서**: `docs/design/UI_REDESIGN_BG3_STYLE.md`, `docs/design/UI_REDESIGN_BG3_STYLE_SYSTEM_INTEGRATION.md`

## ⚠️ 중요: 구현 전 필수 읽기

- `00_CORE/01_PHILOSOPHY.md`: 핵심 개발 철학
- `00_CORE/02_ARCHITECTURE_PRINCIPLES.md`: 아키텍처 설계 원칙
- `database/setup/mvp_schema.sql`: 데이터베이스 스키마 참조 필수

## 1. 개요

탐험 시스템은 발견한 셀, 오브젝트, 엔티티를 추적하고 탐험 진행도를 계산하는 시스템입니다.

## 2. 탐험 진행도 계산

### 2.1 계산 방법

```
탐험 진행도 = (발견한 셀 수 / 전체 셀 수) * 100
```

### 2.2 데이터 소스

- **발견한 셀**: `discoveredCells` Set
- **전체 셀 수**: `game_data.world_cells` 테이블

## 3. API 엔드포인트

### 3.1 필수 API

- [ ] `/api/gameplay/exploration/{session_id}`: 탐험 진행도 조회
  - **참고**: 발견한 셀 수 / 전체 셀 수 계산

## 4. Service Layer

### 4.1 ExplorationService (생성 예정)

- [ ] `ExplorationService` 생성 (`app/services/gameplay/exploration_service.py`)
  - **참고**: `00_CORE/02_ARCHITECTURE_PRINCIPLES.md` - Service 계층 원칙
  - **참고**: `BaseGameplayService` 상속

## 5. UI 통합

### 5.1 탐험 시스템

- [ ] 탐험 진행도 표시
- [ ] 발견한 정보 추적 및 시각화

## 6. 프론트엔드 상태 관리

### 6.1 Zustand Store 확장

- [ ] `explorationProgress`: 탐험 진행도 (발견한 셀 수 / 전체 셀 수)

## 7. TODO

이 문서는 placeholder입니다. 구현 시 다음 사항들을 추가해야 합니다:

1. 탐험 진행도 계산 로직 상세 정의
2. 발견한 정보 추적 로직
3. 탐험 UI 컴포넌트 설계
4. 탐험 테스트 방법

## 8. 참고 문서

- `docs/design/UI_REDESIGN_BG3_STYLE.md`: 탐험 시스템 기획
- `docs/design/UI_REDESIGN_BG3_STYLE_SYSTEM_INTEGRATION.md`: 탐험 시스템 통합 가이드
- `04_DEVELOPMENT/UI_REDESIGN_TODO.md`: UI 리디자인 TODO

