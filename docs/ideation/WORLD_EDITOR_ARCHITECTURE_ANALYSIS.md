# World Editor 아키텍처 분석

> **생성일**: 2025-12-28  
> **목적**: World Editor가 리팩토링의 영향을 덜 받는 이유 분석

---

## 🔍 현재 상황

### **World Editor의 독립성**

World Editor는 현재 리팩토링의 영향을 거의 받지 않습니다. 그 이유는:

#### 1. **Manager 클래스를 사용하지 않음**

```python
# app/world_editor/services/entity_service.py
class EntityService:
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
        # ❌ EntityManager를 사용하지 않음
        # ✅ 직접 DB 쿼리 수행
```

```python
# app/world_editor/services/cell_service.py
class CellService:
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
        self.game_data_repo = GameDataRepository(self.db)
        # ❌ CellManager를 사용하지 않음
        # ✅ Repository만 사용
```

#### 2. **직접 DB 접근**

World Editor Services는:
- ✅ `DatabaseConnection` 직접 사용
- ✅ `GameDataRepository` 직접 사용
- ✅ Raw SQL 쿼리 직접 실행
- ❌ Manager 클래스 미사용
- ❌ 비즈니스 로직 계층 미사용

#### 3. **Game Data만 조작**

World Editor는:
- ✅ `game_data` 스키마만 조작 (템플릿 데이터)
- ❌ `runtime_data` 스키마 미사용 (세션 데이터)
- ❌ 세션 관리 불필요
- ❌ 캐싱 불필요
- ❌ Effect Carrier 불필요

#### 4. **단순 CRUD 작업**

World Editor의 주요 작업:
- ✅ 엔티티 생성/조회/수정/삭제
- ✅ 셀 생성/조회/수정/삭제
- ✅ 위치/지역 관리
- ❌ 복잡한 비즈니스 로직 없음
- ❌ 트랜잭션 관리 최소화

---

## 📊 아키텍처 비교

### **게임 런타임 (Manager 사용)**

```
User Action
    ↓
ActionHandler
    ↓
EntityManager / CellManager
    ↓
Repository + Business Logic
    ↓
Database (game_data + runtime_data)
```

**특징:**
- 세션 관리
- 캐싱
- Effect Carrier
- 트랜잭션 관리
- 비즈니스 로직 검증

### **World Editor (Manager 미사용)**

```
API Request
    ↓
Route
    ↓
Service (직접 DB 접근)
    ↓
Repository (또는 Raw SQL)
    ↓
Database (game_data만)
```

**특징:**
- 단순 CRUD
- 직접 DB 접근
- 비즈니스 로직 최소화
- 세션 관리 불필요

---

## ⚠️ 현재 문제점

### **1. 구조적 중복**

```python
# app/managers/entity_manager.py
class EntityManager:
    async def create_entity(...):
        # 복잡한 비즈니스 로직
        # 세션 관리
        # 캐싱
        # Effect Carrier 연동

# app/world_editor/services/entity_service.py
class EntityService:
    async def create_entity(...):
        # 단순 DB INSERT
        # 비즈니스 로직 없음
```

**문제:**
- 같은 엔티티를 다루지만 다른 방식으로 접근
- 코드 중복 가능성
- 일관성 부족

### **2. 책임 분리 부족**

World Editor Services가:
- ❌ Manager를 사용하지 않아 계층 구조가 깨짐
- ❌ 직접 DB 쿼리로 인해 Repository 패턴 위반
- ❌ 비즈니스 로직이 Service에 혼재

---

## 🎯 리팩토링 후 계획

### **옵션 1: World Editor도 Manager 사용 (권장하지 않음)**

```python
# app/world_editor/services/entity_service.py
class EntityService:
    def __init__(self, entity_manager: IEntityManager):
        self.entity_manager = entity_manager
    
    async def create_entity(self, data: EntityCreate):
        # Manager를 통해 접근
        return await self.entity_manager.create_entity(...)
```

**문제점:**
- World Editor는 `game_data`만 조작하는데 Manager는 `runtime_data`도 관리
- Manager의 복잡한 비즈니스 로직이 불필요
- 오버엔지니어링

### **옵션 2: World Editor는 그대로 유지 (현재 상태)**

**장점:**
- ✅ 단순하고 명확한 구조
- ✅ 불필요한 복잡성 제거
- ✅ 성능 최적화 (불필요한 계층 제거)

**단점:**
- ⚠️ 코드 중복 가능성
- ⚠️ 일관성 부족

### **옵션 3: Game Data 전용 Manager 생성 (권장)**

```python
# app/managers/game_data_manager.py
class GameDataManager:
    """Game Data 전용 Manager (World Editor용)"""
    
    async def create_entity_template(self, ...):
        # game_data만 조작
        # 세션 관리 없음
        # 캐싱 최소화
    
    async def create_cell_template(self, ...):
        # game_data만 조작
```

**장점:**
- ✅ Manager 패턴 일관성
- ✅ World Editor와 게임 런타임의 명확한 분리
- ✅ 코드 재사용성

---

## 📝 결론

### **현재 상태**

World Editor가 리팩토링의 영향을 덜 받는 이유:

1. **독립적인 아키텍처**: Manager를 사용하지 않고 직접 DB 접근
2. **단순한 요구사항**: Game Data CRUD만 필요
3. **명확한 책임 분리**: World Editor는 템플릿 편집, Manager는 런타임 관리

### **리팩토링 영향**

- ✅ **현재**: World Editor는 리팩토링의 영향을 받지 않음
- ✅ **이유**: Manager를 사용하지 않으므로 import 경로 변경과 무관
- ⚠️ **향후**: 옵션 3을 통해 통합 고려 가능

### **권장 사항**

1. **현재 상태 유지**: World Editor는 그대로 두고 리팩토링 진행
2. **향후 통합**: Phase 3 (Service 통합)에서 Game Data 전용 Manager 고려
3. **명확한 분리**: World Editor (템플릿 편집) vs Manager (런타임 관리)

---

## 🔄 리팩토링 계획 반영

재구조화 계획에서:

- **Phase 3: Service 통합**에서 World Editor Services를 `app/services/world_editor_service.py`로 통합
- 하지만 World Editor는 Manager를 사용하지 않으므로 **독립적으로 유지** 가능
- 또는 **Game Data 전용 Manager**를 생성하여 World Editor가 사용하도록 할 수 있음

**결론**: World Editor는 현재 구조로도 잘 작동하며, 리팩토링 후에도 큰 변경 없이 유지 가능합니다.

