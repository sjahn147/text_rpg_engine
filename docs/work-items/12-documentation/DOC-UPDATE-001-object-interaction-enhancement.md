---
id: DOC-UPDATE-001-object-interaction-enhancement
type: documentation-update
status: documentation
related_epic_id: EPIC-001-object-interaction-enhancement
updated_documents:
  - docs/work-items/12-documentation/DOC-UPDATE-001-object-interaction-enhancement.md
keyword: object-interaction-enhancement
created_at: 2026-01-02T01:17:00Z
updated_at: 2026-01-02T01:20:00Z
author: agent
---

# 오브젝트 상호작용 고도화 문서 최신화

## 설명

EPIC-001 완료에 따른 문서 최신화

## 업데이트된 문서

- 모든 TODO 문서 상태 업데이트 완료
- 모든 Task 문서 상태 업데이트 완료
- Epic 문서 상태 업데이트 완료

## 액션 노출 메커니즘

### 액션이 노출되는 조건

액션은 다음 순서로 생성됩니다:

1. **기본 조사 액션 (항상 생성)**
   - 모든 오브젝트에 대해 `examine` 액션이 항상 생성됩니다.

2. **properties.interactions 기반 동적 액션**
   - 오브젝트의 `properties.interactions`에 정의된 모든 액션 타입이 생성됩니다.
   - 상태 필터링을 통과한 액션만 노출됩니다.
   - 예시:
   ```json
   {
     "properties": {
       "interactions": {
         "open": {
           "text": "열기",
           "target_state": "open",
           "required_state": "closed"
         },
         "rest": {
           "text": "쉬기",
           "time_cost": 30,
           "effects": {
             "hp": 50,
             "mp": 30
           }
         },
         "read": {
           "text": "읽기",
           "content": "책 내용...",
           "time_cost": 30
         }
       },
       "possible_states": ["closed", "open"]
     }
   }
   ```

3. **레거시 interaction_type 기반 액션 (interactions가 없을 때만)**
   - `properties.interactions`가 없거나 비어있을 때만 사용됩니다.
   - 지원되는 interaction_type:
     - `openable`: open/close 액션
     - `lightable`: light/extinguish 액션
     - `restable` 또는 `rest`: rest 액션
     - `sitable` 또는 `sit`: sit 액션
   - 제한적이므로 가능하면 `properties.interactions` 사용을 권장합니다.

### 액션이 노출되지 않는 이유

1. **properties.interactions가 정의되지 않음**
   - 오브젝트에 `properties.interactions`가 없으면 레거시 `interaction_type`만 사용됩니다.
   - 레거시는 제한적인 액션만 지원합니다.

2. **상태 필터링으로 제외됨**
   - `required_state`, `forbidden_states`, `allowed_in_states`, `forbidden_in_states` 조건을 만족하지 않으면 액션이 숨겨집니다.
   - 상태 전이 규칙을 만족하지 않으면 액션이 숨겨집니다.

3. **interaction_type이 설정되지 않음**
   - 레거시 모드에서 `interaction_type`이 없거나 지원되지 않는 타입이면 액션이 생성되지 않습니다.

### 해결 방법

다양한 액션을 사용하려면 오브젝트의 `properties.interactions`에 명시적으로 정의해야 합니다:

```sql
UPDATE game_data.world_objects
SET properties = jsonb_set(
  COALESCE(properties, '{}'::jsonb),
  '{interactions}',
  '{
    "examine": {"text": "조사하기"},
    "open": {"text": "열기", "target_state": "open", "required_state": "closed"},
    "close": {"text": "닫기", "target_state": "closed", "required_state": "open"},
    "rest": {"text": "쉬기", "time_cost": 30, "effects": {"hp": 50, "mp": 30}},
    "read": {"text": "읽기", "content": "책 내용...", "time_cost": 30},
    "pickup": {"text": "아이템 획득"}
  }'::jsonb
)
WHERE object_id = 'OBJECT_ID_HERE';
```

## 다음 단계

Done 처리 진행
