# 오브젝트 상호작용 실패 원인 분석

**작성일**: 2025-01-XX  
**문제**: 리팩토링 후 오브젝트 상호작용이 작동하지 않음

---

## 문제 현상

오브젝트 상호작용이 원래 잘 작동했었는데, 리팩토링 과정에서 작동이 실패하고 있음.

---

## 원인 분석

### 1. 핸들러 초기화 조건 문제 ⚠️ **가장 가능성 높음**

**위치**: `app/handlers/action_handler.py:416-419`

```python
def _init_object_interaction_handlers(self):
    """오브젝트 상호작용 핸들러 초기화"""
    if not self.object_state_manager:
        return  # ⚠️ object_state_manager가 None이면 핸들러 초기화 안 함
```

**문제점**:
- `object_state_manager`가 `None`이면 오브젝트 상호작용 핸들러들이 전혀 초기화되지 않음
- 이 경우 `handle_examine_object` 같은 메서드들이 "정보 확인 핸들러가 초기화되지 않았습니다" 에러를 반환

**확인 결과**:
- `BaseGameplayService`에서는 `object_state_manager`를 제대로 전달하고 있음 (라인 111)
- 하지만 `ActionHandler.__init__`에서 `_init_object_interaction_handlers()`가 호출되는 시점에 `object_state_manager`가 `None`일 가능성

**해결 방안**:
- `_init_object_interaction_handlers`에서 `object_state_manager`가 `None`이어도 핸들러를 초기화하도록 수정
- 또는 `object_state_manager`가 필수 파라미터가 되도록 변경

### 2. execute_action 파라미터 전달 문제

**위치**: `app/handlers/action_handler.py:188-202`

```python
async def execute_action(self, action_type: ActionType, 
                       entity_id: str, 
                       target_id: Optional[str] = None,
                       parameters: Optional[Dict[str, Any]] = None,
                       session_id: str = None) -> ActionResult:
    # ...
    result = await handler(entity_id, target_id, parameters)
```

**확인 결과**:
- `InteractionService`에서는 `parameters={"session_id": session_id}`로 전달하고 있음 (라인 278)
- 하지만 `execute_action`의 `session_id` 파라미터가 `parameters`에 병합되지 않음
- 만약 `parameters`가 `None`이거나 `session_id`가 포함되지 않으면 핸들러에서 세션 ID를 찾을 수 없음

**해결 방안**:
- `execute_action`에서 `session_id` 파라미터가 있으면 `parameters`에 병합
- `parameters`가 `None`이면 `{"session_id": session_id}`로 초기화

### 3. 오브젝트 ID 전달 형식 문제

**위치**: `app/services/gameplay/interaction_service.py:277`

```python
target_id=target_object.get('runtime_object_id') or target_object.get('game_object_id'),
```

**확인 필요**:
- `target_object`에서 `runtime_object_id`와 `game_object_id` 중 어떤 것이 실제로 존재하는지 확인
- `_parse_object_id`가 올바르게 파싱하는지 확인

### 4. 오브젝트 상태 조회 실패 가능성

**위치**: `app/handlers/object_interaction_base.py:85-104`

```python
async def _get_object_state(
    self,
    runtime_object_id: Optional[str],
    game_object_id: str,
    session_id: str
):
    """오브젝트 상태 조회 헬퍼"""
    if not game_object_id:
        return None  # ⚠️ game_object_id가 없으면 None 반환
```

**문제점**:
- `game_object_id`가 없으면 `None`을 반환
- 이 경우 핸들러에서 "오브젝트 상태를 조회할 수 없습니다" 에러 발생

---

## 해결 방안

### 즉시 조치 (우선순위 높음)

1. **핸들러 초기화 조건 수정**
   ```python
   def _init_object_interaction_handlers(self):
       """오브젝트 상호작용 핸들러 초기화"""
       # object_state_manager가 None이어도 핸들러 초기화
       # (핸들러 내부에서 필요시 체크)
       handler_kwargs = {
           'db_connection': self.db,
           'object_state_manager': self.object_state_manager,  # None일 수 있음
           'entity_manager': self.entity_manager,
           'inventory_manager': self.inventory_manager,
           'effect_carrier_manager': self.effect_carrier_manager,
       }
       
       self.info_handler = InformationInteractionHandler(**handler_kwargs)
       # ... 나머지 핸들러들
   ```

2. **execute_action 파라미터 병합**
   ```python
   async def execute_action(self, action_type: ActionType, 
                          entity_id: str, 
                          target_id: Optional[str] = None,
                          parameters: Optional[Dict[str, Any]] = None,
                          session_id: str = None) -> ActionResult:
       # session_id를 parameters에 병합
       if parameters is None:
           parameters = {}
       if session_id and "session_id" not in parameters:
           parameters["session_id"] = session_id
       
       result = await handler(entity_id, target_id, parameters)
   ```

3. **에러 로깅 강화**
   - 각 단계에서 상세한 에러 로그 추가
   - 핸들러 초기화 여부 로그 추가
   - 오브젝트 ID 파싱 결과 로그 추가

---

## 확인해야 할 코드 위치

1. **ActionHandler 초기화**: `app/handlers/action_handler.py:57-106`
2. **핸들러 초기화**: `app/handlers/action_handler.py:416-438`
3. **execute_action**: `app/handlers/action_handler.py:188-212`
4. **InteractionService**: `app/services/gameplay/interaction_service.py:166-292`
5. **오브젝트 ID 파싱**: `app/handlers/object_interaction_base.py:43-83`

---

## 다음 단계

1. **즉시 수정**: `_init_object_interaction_handlers`에서 `object_state_manager` None 체크 제거 또는 핸들러 내부에서 처리
2. **즉시 수정**: `execute_action`에서 `session_id` 파라미터 병합
3. **테스트**: 오브젝트 상호작용 동작 확인
4. **로깅 추가**: 각 단계에서 상세한 로그 추가
