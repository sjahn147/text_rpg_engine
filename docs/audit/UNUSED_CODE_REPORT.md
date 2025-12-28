# app 폴더 사용되지 않는 코드 리포트

> **생성일**: 2025-12-28  
> **목적**: `app` 폴더에서 현재 어디에서도 사용되지 않는 코드 식별

---

## 📋 사용되지 않는 파일/모듈

### 1. **`app/entity/base.py`** ❌
- **상태**: 사용되지 않음
- **내용**: `BaseEntity` 클래스 정의
- **사용처**: 없음 (자기 자신만 import)
- **비고**: 레거시 코드로 보임, 현재 `EntityManager`가 Pydantic 모델 사용

### 2. **`app/simulation/`** ❌
- **상태**: 빈 폴더 (파일 없음)
- **내용**: 없음
- **비고**: `__pycache__`만 존재

### 3. **`app/world_editor/integrate_to_main.py`** ⚠️
- **상태**: 사용되지 않음 (직접 호출 없음)
- **내용**: World Editor 라우터를 기존 FastAPI 앱에 통합하는 헬퍼 함수
- **사용처**: 없음 (문서에서만 언급)
- **비고**: 유틸리티 함수이지만 실제로 사용되지 않음

---

## ⚠️ 잘못된 사용 패턴 (의존성 주입 위반)

다음 파일들은 **의존성 주입 없이 직접 인스턴스화**하고 있어 문제가 있습니다:

### 1. **`app/game_session.py`** ⚠️
```python
# 문제: 의존성 주입 없이 직접 생성
self.cell_manager = CellManager()  # ❌ 인자 없이 호출
self.game_manager = GameManager()  # ❌ 인자 없이 호출
```
- **문제점**: `CellManager`와 `GameManager`는 의존성 주입이 필요한데 인자 없이 호출
- **현재 상태**: 이 파일은 사용되지만 **작동하지 않을 가능성 높음**

### 2. **`app/core/scenario_executor.py`** ⚠️
```python
# 문제: 의존성 주입 없이 직접 생성
self.game_manager = GameManager()  # ❌
self.entity_manager = EntityManager()  # ❌
self.instance_manager = InstanceManager()  # ❌
self.cell_manager = CellManager()  # ❌
```
- **문제점**: 모든 Manager를 인자 없이 생성
- **현재 상태**: 사용되지만 **작동하지 않을 가능성 높음**

### 3. **`app/ui/main_window.py`** ⚠️
```python
# 문제: 의존성 주입 없이 직접 생성
self.game_manager = GameManager()  # ❌
```
- **문제점**: `GameManager`는 의존성 주입이 필요한데 인자 없이 호출
- **현재 상태**: 사용되지만 **작동하지 않을 가능성 높음**

### 4. **`app/ui/screens/map_screen.py`** ⚠️
```python
# 문제: 의존성 주입 없이 직접 생성
cell_manager = CellManager()  # ❌
```
- **문제점**: `CellManager`는 의존성 주입이 필요한데 인자 없이 호출
- **현재 상태**: 사용되지만 **작동하지 않을 가능성 높음**

---

## ✅ 사용 중인 파일들

### Core 모듈
- ✅ `app/core/game_manager.py` - 테스트에서 사용
- ✅ `app/core/scenario_executor.py` - `main_window.py`에서 사용 (하지만 잘못된 사용)
- ✅ `app/core/scenario_loader.py` - `main_window.py`에서 사용
- ⚠️ `app/core/framework_manager.py` - 테스트에서만 사용, 실제 운영 코드에서는 미사용

### Entity 모듈
- ✅ `app/entity/entity_manager.py` - 테스트 및 다른 모듈에서 사용
- ⚠️ `app/entity/instance_manager.py` - `scenario_executor.py`에서만 사용 (잘못된 사용)

### World 모듈
- ✅ `app/world/cell_manager.py` - 테스트 및 다른 모듈에서 사용

### Interaction 모듈
- ✅ `app/interaction/dialogue_manager.py` - 테스트에서 사용
- ✅ `app/interaction/action_handler.py` - 테스트에서 사용

### Systems 모듈
- ✅ `app/systems/time_system.py` - 테스트에서 사용
- ⚠️ `app/systems/npc_behavior.py` - 레거시 테스트에서만 사용, 실제 운영 코드에서는 미사용

### UI 모듈
- ✅ `app/ui/main_window.py` - 메인 엔트리 포인트 (`if __name__ == '__main__'`)
- ✅ `app/ui/dashboard.py` - 메인 엔트리 포인트 (`if __name__ == '__main__'`)
- ✅ `app/ui/screens/map_screen.py` - `main_window.py`에서 사용
- ✅ `app/ui/screens/dialogue_screen.py` - `main_window.py`에서 사용
- ✅ `app/ui/screens/inventory_screen.py` - `main_window.py`에서 사용
- ✅ `app/ui/screens/status_screen.py` - `main_window.py`에서 사용

### Game Session
- ✅ `app/game_session.py` - `main_window.py`, `dashboard.py`에서 사용 (하지만 잘못된 사용)

### World Editor
- ✅ `app/world_editor/run_server.py` - 직접 실행 가능 (`python run_server.py`)
- ✅ `app/world_editor/main.py` - `run_server.py`에서 사용
- ✅ `app/world_editor/` 모든 routes, services - World Editor에서 사용

---

## 🔧 권장 사항

### 즉시 삭제 가능
1. **`app/entity/base.py`** - 완전히 사용되지 않음
2. **`app/simulation/`** 폴더 - 빈 폴더

### 수정 필요 (의존성 주입)
1. **`app/game_session.py`** - Manager 클래스들을 의존성 주입으로 수정
2. **`app/core/scenario_executor.py`** - Manager 클래스들을 의존성 주입으로 수정
3. **`app/ui/main_window.py`** - `GameManager`를 의존성 주입으로 수정
4. **`app/ui/screens/map_screen.py`** - `CellManager`를 의존성 주입으로 수정

### 검토 필요
1. **`app/core/framework_manager.py`** - 실제 운영 코드에서 사용되는지 확인
2. **`app/systems/npc_behavior.py`** - 실제 운영 코드에서 사용되는지 확인
3. **`app/world_editor/integrate_to_main.py`** - 실제로 필요한지 확인

---

## 📊 요약

- **완전히 사용되지 않는 파일**: 2개 (`base.py`, `simulation/` 폴더)
- **잘못된 사용 패턴**: 4개 파일 (의존성 주입 위반)
- **검토 필요**: 3개 파일 (실제 사용 여부 불명확)

