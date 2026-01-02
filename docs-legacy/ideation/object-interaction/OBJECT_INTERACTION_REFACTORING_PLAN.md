# 오브젝트 상호작용 핸들러 모듈화 계획

**작성일**: 2025-12-28  
**목적**: ActionHandler 파일이 너무 길어서 (2595줄) 모듈화 필요

---

## 현재 문제점

1. **파일 크기**: `action_handler.py`가 2595줄로 너무 길어서 수정이 어려움
2. **확장성 부족**: 새로운 상호작용 추가 시 파일이 더 길어짐
3. **유지보수 어려움**: 특정 카테고리만 수정하려 해도 전체 파일을 봐야 함

---

## 모듈화 구조

### 디렉토리 구조

```
app/handlers/
├── action_handler.py              # 메인 핸들러 (라우터 역할)
├── object_interaction_base.py     # 베이스 클래스
└── object_interactions/
    ├── __init__.py
    ├── information.py            # 정보 확인 (examine, inspect, search)
    ├── state_change.py            # 상태 변경 (open, close, light, etc.)
    ├── position.py                # 위치 변경 (sit, stand, lie, etc.)
    ├── recovery.py                # 회복 (rest, sleep, meditate)
    ├── consumption.py             # 소비 (eat, drink, consume)
    ├── learning.py                # 학습/정보 (read, study, write)
    ├── item_manipulation.py      # 아이템 조작 (pickup, place, take, put)
    ├── crafting.py                # 조합/제작 (combine, craft, cook, repair)
    └── destruction.py             # 파괴/변형 (destroy, break, dismantle)
```

### 클래스 구조

#### 1. ObjectInteractionHandlerBase (베이스 클래스)

```python
class ObjectInteractionHandlerBase(ABC):
    """오브젝트 상호작용 핸들러 베이스 클래스"""
    
    def __init__(self, db_connection, object_state_manager, ...):
        # 공통 의존성 초기화
    
    async def _parse_object_id(self, target_id, session_id):
        """오브젝트 ID 파싱 헬퍼"""
    
    async def _get_object_state(self, ...):
        """오브젝트 상태 조회 헬퍼"""
    
    async def _update_object_state(self, ...):
        """오브젝트 상태 업데이트 헬퍼"""
    
    @abstractmethod
    async def handle(self, ...):
        """상호작용 처리 (추상 메서드)"""
```

#### 2. 카테고리별 핸들러

각 카테고리별로 별도 클래스:

- `InformationInteractionHandler`: `handle_examine()`, `handle_inspect()`, `handle_search()`
- `StateChangeInteractionHandler`: `handle_open()`, `handle_close()`, `handle_light()`, etc.
- `PositionInteractionHandler`: `handle_sit()`, `handle_stand()`, `handle_lie()`, etc.
- `RecoveryInteractionHandler`: `handle_rest()`, `handle_sleep()`, `handle_meditate()`
- `ConsumptionInteractionHandler`: `handle_eat()`, `handle_drink()`, `handle_consume()`
- `LearningInteractionHandler`: `handle_read()`, `handle_study()`, `handle_write()`
- `ItemManipulationInteractionHandler`: `handle_pickup()`, `handle_place()`, `handle_take()`, `handle_put()`
- `CraftingInteractionHandler`: `handle_combine()`, `handle_craft()`, `handle_cook()`, `handle_repair()`
- `DestructionInteractionHandler`: `handle_destroy()`, `handle_break()`, `handle_dismantle()`

#### 3. ActionHandler (라우터)

```python
class ActionHandler:
    def __init__(self, ...):
        # 기존 의존성들...
        self._init_object_interaction_handlers()
    
    def _init_object_interaction_handlers(self):
        """오브젝트 상호작용 핸들러 초기화"""
        handler_kwargs = {...}
        self.info_handler = InformationInteractionHandler(**handler_kwargs)
        self.state_handler = StateChangeInteractionHandler(**handler_kwargs)
        # ... 나머지 핸들러들
    
    async def handle_examine_object(self, ...):
        """오브젝트 조사 (라우터)"""
        return await self.info_handler.handle_examine(...)
    
    async def handle_open_object(self, ...):
        """오브젝트 열기 (라우터)"""
        return await self.state_handler.handle_open(...)
    
    # ... 나머지 핸들러들도 위임
```

---

## 리팩토링 단계

### Phase 1: 베이스 클래스 및 카테고리 핸들러 생성 ✅
- [x] `ObjectInteractionHandlerBase` 생성
- [x] 9개 카테고리별 핸들러 클래스 생성
- [x] 각 핸들러에 기본 메서드 구현

### Phase 2: ActionHandler 리팩토링 (진행 중)
- [x] `_init_object_interaction_handlers()` 메서드 추가
- [x] `handle_examine_object`, `handle_open_object`, `handle_close_object`, `handle_light_object` 위임
- [ ] 나머지 핸들러 메서드들 위임
  - [ ] 정보 확인: `handle_inspect_object`, `handle_search_object`
  - [ ] 상태 변경: `handle_extinguish_object`, `handle_activate_object`, `handle_deactivate_object`, `handle_lock_object`, `handle_unlock_object`
  - [ ] 위치 변경: `handle_sit_at_object`, `handle_stand_from_object`, `handle_lie_on_object`, `handle_get_up_from_object`, `handle_climb_object`, `handle_descend_from_object`
  - [ ] 회복: `handle_rest_at_object`, `handle_sleep_at_object`, `handle_meditate_at_object`
  - [ ] 소비: `handle_eat_from_object`, `handle_drink_from_object`, `handle_consume_object`
  - [ ] 학습: `handle_read_object`, `handle_study_object`, `handle_write_object`
  - [ ] 아이템 조작: `handle_pickup_from_object`, `handle_place_in_object`, `handle_take_from_object`, `handle_put_in_object`
  - [ ] 조합/제작: `handle_combine_with_object`, `handle_craft_at_object`, `handle_cook_at_object`, `handle_repair_object`
  - [ ] 파괴/변형: `handle_destroy_object`, `handle_break_object`, `handle_dismantle_object`
  - [ ] 기타: `handle_use_object`

### Phase 3: 기존 코드 제거
- [ ] ActionHandler에서 기존 핸들러 메서드 구현 코드 제거
- [ ] 중복 코드 정리

### Phase 4: 테스트 및 검증
- [ ] 모든 상호작용 동작 확인
- [ ] 통합 테스트 작성

---

## 장점

1. **모듈화**: 각 카테고리별로 독립적인 파일
2. **확장성**: 새로운 상호작용 추가 시 해당 카테고리 파일만 수정
3. **유지보수성**: 특정 카테고리만 수정하면 됨
4. **테스트 용이성**: 각 핸들러를 독립적으로 테스트 가능
5. **코드 재사용**: 공통 로직을 베이스 클래스에 모음

---

## 주의사항

1. **하위 호환성**: ActionHandler의 인터페이스는 유지 (라우터 역할)
2. **의존성 주입**: 각 핸들러가 필요한 Manager를 주입받도록 설계
3. **에러 처리**: 각 핸들러에서 일관된 에러 처리

