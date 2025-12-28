# app/core 모듈 분석 및 필요성 진단

**분석 일자**: 2025-12-28

## 📋 모듈 개요

### 1. `game_session.py` (469 lines)
**기능**: 게임 세션 관리
- 세션 초기화/종료
- 셀 진입/이탈
- 플레이어 이동
- NPC 대화 처리
- 세션 상태 조회/저장

**사용처**:
- `scenario_executor.py`
- `main_window.py`

**문제점**:
- ❌ `CellManager()` 직접 인스턴스화 (의존성 주입 없음)
- ❌ `GameManager()` 직접 인스턴스화 (의존성 주입 없음)
- ❌ Manager 클래스들이 이미 재구조화되었는데 import 경로가 오래됨

**필요성**: ⚠️ **부분적 필요** - 기능은 필요하나 리팩토링 필요

---

### 2. `scenario_executor.py` (404 lines)
**기능**: 시나리오 실행 엔진
- JSON/YAML 시나리오 파일 실행
- 단계별 시나리오 실행 (setup_data, create_session, create_entity 등)
- 콜백 함수 지원 (on_step_start, on_step_complete 등)
- 일시정지/재개/중지 기능

**사용처**:
- `main_window.py` (UI에서 시나리오 실행)

**문제점**:
- ❌ 모든 Manager를 직접 인스턴스화 (`GameManager()`, `EntityManager()` 등)
- ❌ 의존성 주입 없음
- ❌ `from app.game_session import GameSession` - 경로 오류 (실제로는 `app/core/game_session.py`)

**필요성**: ⚠️ **부분적 필요** - UI에서 사용 중이지만 리팩토링 필요

---

### 3. `framework_manager.py` (480 lines)
**기능**: 프레임워크 중앙 관리 시스템
- 모듈 의존성 관리
- 초기화 순서 관리 (의존성 그래프 기반)
- 성능 최적화 (캐시, 메모리)
- 헬스 체크
- 프레임워크 보고서 생성

**사용처**:
- `tests/database/test_framework_stabilization.py` (legacy 테스트)
- 실제 프로덕션 코드에서는 사용되지 않음

**문제점**:
- ❌ 실제로 사용되지 않음 (legacy 테스트만)
- ❌ Manager들을 직접 생성 (의존성 주입은 있지만 복잡함)
- ❌ 전역 싱글톤 패턴 (`framework_manager = FrameworkManager()`)

**필요성**: ❌ **불필요** - 사용되지 않음, 제거 고려

---

### 4. `game_manager.py` (547 lines)
**기능**: 게임 전체 관리 핵심 클래스
- 새 게임 시작 (`start_new_game`)
- 플레이어 이동 (`move_player`)
- 대화 처리 (`start_dialogue`, `process_dialogue_choice`)
- 게임 상태 저장/로드 (`save_game_state`, `load_game_state`)
- 셀 컨텐츠 로드 (`load_cell_contents`)
- 상호작용 처리 (`handle_interaction`)

**사용처**:
- `game_session.py`
- `scenario_executor.py`
- `main_window.py`
- `dashboard.py`

**문제점**:
- ⚠️ 의존성 주입 구조는 있지만, 실제 사용 시 인자 없이 호출됨 (`GameManager()`)
- ❌ `start_new_game`에서 `InstanceFactory` 사용 - 하지만 실제로는 `InstanceManager` 사용해야 함
- ❌ 일부 메서드가 Manager 클래스와 중복 기능

**필요성**: ⚠️ **부분적 필요** - 사용 중이지만 Manager 클래스와 역할 중복

---

### 5. `scenario_loader.py` (160 lines)
**기능**: 시나리오 파일 로드 및 검증
- JSON/YAML 파일 파싱
- 시나리오 데이터 검증
- 시나리오 파일 목록 조회
- 시나리오 정보 조회

**사용처**:
- `main_window.py` (UI에서 시나리오 로드)

**문제점**:
- ✅ 비교적 깔끔함
- ⚠️ 단순 유틸리티 클래스

**필요성**: ✅ **필요** - UI에서 사용 중

---

## 🔍 종합 분석

### 현재 상태
1. **의존성 주입 문제**: 대부분의 모듈이 Manager를 직접 인스턴스화
2. **경로 문제**: 재구조화 후 import 경로가 업데이트되지 않음
3. **역할 중복**: `GameManager`와 `EntityManager`/`CellManager` 등이 중복 기능
4. **사용되지 않는 코드**: `FrameworkManager`는 legacy 테스트에서만 사용

### 필요성 평가

| 모듈 | 필요성 | 우선순위 | 조치 |
|------|--------|----------|------|
| `game_session.py` | ⚠️ 부분적 | 높음 | 리팩토링 (의존성 주입) |
| `scenario_executor.py` | ⚠️ 부분적 | 높음 | 리팩토링 (의존성 주입, 경로 수정) |
| `framework_manager.py` | ❌ 불필요 | 낮음 | 제거 고려 |
| `game_manager.py` | ⚠️ 부분적 | 중간 | Manager와 역할 분리 또는 통합 |
| `scenario_loader.py` | ✅ 필요 | 낮음 | 유지 |

---

## 💡 권장 사항

### 1. 즉시 조치
- [ ] `scenario_executor.py`: import 경로 수정 (`app.game_session` → `app.core.game_session`)
- [ ] `scenario_executor.py`: Manager 인스턴스화를 의존성 주입으로 변경
- [ ] `game_session.py`: Manager 인스턴스화를 의존성 주입으로 변경

### 2. 중기 조치
- [ ] `GameManager`와 `EntityManager`/`CellManager` 역할 분리
  - `GameManager`: 게임 세션 생명주기 관리
  - `EntityManager`/`CellManager`: 엔티티/셀 CRUD 작업
- [ ] `FrameworkManager` 제거 또는 실제 사용처 추가

### 3. 장기 조치
- [ ] `app/core` 폴더 구조 재검토
  - `core`는 핵심 비즈니스 로직이 아닌 인프라/유틸리티에 적합
  - 게임 로직은 `app/managers` 또는 `app/services`로 이동 고려

---

## 📊 사용 현황

### 실제 사용 중인 모듈
- ✅ `game_session.py` - UI에서 사용
- ✅ `scenario_executor.py` - UI에서 사용
- ✅ `scenario_loader.py` - UI에서 사용
- ⚠️ `game_manager.py` - UI에서 사용하지만 역할 중복

### 사용되지 않는 모듈
- ❌ `framework_manager.py` - legacy 테스트에서만 사용

---

## 🎯 결론

**핵심 문제**: 재구조화 후 import 경로와 의존성 주입이 업데이트되지 않음

**권장 조치**:
1. **즉시**: import 경로 수정 및 의존성 주입 적용
2. **중기**: 역할 중복 해소 및 불필요한 코드 제거
3. **장기**: `app/core` 폴더 구조 재검토

