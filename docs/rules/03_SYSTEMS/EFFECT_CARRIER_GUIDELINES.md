# Effect Carrier 시스템 사용 가이드라인

> **최신화 날짜**: 2026-01-03  
> **적용 범위**: Effect Carrier 시스템 사용 전 필수 읽기

## 1. 개요

Effect Carrier는 게임 내 모든 효과(스킬, 버프, 아이템, 축복, 저주, 의식)를 통일된 방식으로 관리하는 시스템입니다.

## 2. 핵심 개념

### 2.1 Effect Carrier의 두 가지 연결 방식

Effect Carrier는 **두 가지 방식**으로 엔티티와 연결됩니다:

#### **1. 아이템의 속성 (소유 관계)**

아이템/장비가 `effect_carrier_id` FK로 Effect Carrier를 참조합니다.

```sql
-- 아이템이 Effect Carrier를 소유
game_data.items (
  item_id VARCHAR(50) PRIMARY KEY,
  effect_carrier_id UUID,  -- FK to effect_carriers
  ...
)

-- 장비가 Effect Carrier를 소유
game_data.equipment_weapons (
  weapon_id VARCHAR(50) PRIMARY KEY,
  effect_carrier_id UUID,  -- FK to effect_carriers
  ...
)

game_data.equipment_armors (
  armor_id VARCHAR(50) PRIMARY KEY,
  effect_carrier_id UUID,  -- FK to effect_carriers
  ...
)
```

**사용 시나리오**:
- 아이템을 장착하거나 사용할 때 Effect Carrier의 효과를 적용
- 인벤토리 조회 시 아이템의 Effect Carrier 정보 포함

#### **2. 엔티티의 적용 중인 상태 (적용 관계)**

`reference_layer.entity_effect_ownership` 테이블을 통해 관리됩니다.

```sql
reference_layer.entity_effect_ownership (
  session_id UUID,
  runtime_entity_id UUID,
  effect_id UUID,  -- FK to effect_carriers
  acquired_at TIMESTAMP,
  source VARCHAR(100),
  is_active BOOLEAN DEFAULT true,
  expires_at TIMESTAMP,
  ...
)
```

**사용 시나리오**:
- 질병, 저주, 가호, 버프 등을 "적용받은" 상태로 관리
- **아이템처럼 소유하는 것이 아니라 "적용 중인 상태"로 조회됨**

### 2.2 Effect Carrier 타입

Effect Carrier는 6가지 타입을 지원합니다:

```python
class EffectCarrierType(str, Enum):
    SKILL = "skill"      # 스킬 효과
    BUFF = "buff"        # 버프 효과
    ITEM = "item"        # 아이템 효과
    BLESSING = "blessing"  # 축복 효과
    CURSE = "curse"      # 저주 효과
    RITUAL = "ritual"    # 의식 효과
```

**중요**: Effect Carrier 타입이 `skill`인 것은 스킬 시스템(`abilities_skills`)과 **별도**입니다.
- Effect Carrier `skill`: 버프/효과를 의미
- `abilities_skills`: 실제 스킬 능력 정의

## 3. Effect Carrier Manager 사용법

### 3.1 Effect Carrier 적용

엔티티에 Effect Carrier를 적용할 때:

```python
from app.managers.effect_carrier_manager import EffectCarrierManager

# Effect Carrier 적용
effect_result = await effect_carrier_manager.grant_effect_to_entity(
    session_id=session_id,
    runtime_entity_id=runtime_entity_id,
    effect_id=effect_id  # UUID
)

if not effect_result.success:
    raise ValueError(f"Effect Carrier 적용 실패: {effect_result.message}")
```

**주의사항**:
- `effect_id`는 반드시 UUID 형식이어야 함
- `session_id`와 `runtime_entity_id`는 유효해야 함
- 이미 적용된 Effect Carrier는 중복 적용되지 않음

### 3.2 적용 중인 Effect Carrier 조회

엔티티에 적용 중인 Effect Carrier를 조회할 때:

```python
# 적용 중인 Effect Carrier 조회
effects_result = await effect_carrier_manager.get_entity_effects(
    session_id=session_id,
    runtime_entity_id=runtime_entity_id
)

if effects_result.success:
    applied_effects = effects_result.data  # List[EffectCarrierData]
    for effect in applied_effects:
        print(f"Effect: {effect.name}, Type: {effect.carrier_type}")
```

**주의사항**:
- `is_active=True`인 Effect Carrier만 조회됨
- 만료된 Effect Carrier(`expires_at`이 지난 것)는 자동으로 제외됨

### 3.3 Effect Carrier 제거

엔티티에서 Effect Carrier를 제거할 때:

```python
# Effect Carrier 제거
revoke_result = await effect_carrier_manager.revoke_effect_from_entity(
    session_id=session_id,
    runtime_entity_id=runtime_entity_id,
    effect_id=effect_id
)

if not revoke_result.success:
    raise ValueError(f"Effect Carrier 제거 실패: {revoke_result.message}")
```

### 3.4 EntityManager를 통한 사용

EntityManager는 EffectCarrierManager를 통합하고 있습니다:

```python
from app.managers.entity_manager import EntityManager

# EntityManager를 통한 Effect Carrier 적용
result = await entity_manager.apply_effect_carrier(
    entity_id=runtime_entity_id,
    effect_id=effect_id,
    session_id=session_id
)

if not result.success:
    raise ValueError(result.message)
```

## 4. 아이템/장비와 Effect Carrier 연결

### 4.1 스키마 설계 (권장)

아이템/장비와 Effect Carrier를 연결하려면 FK를 추가해야 합니다:

```sql
-- equipment_weapons 테이블에 추가
ALTER TABLE game_data.equipment_weapons
ADD COLUMN effect_carrier_id UUID,
ADD CONSTRAINT fk_weapons_effect_carrier
    FOREIGN KEY (effect_carrier_id)
    REFERENCES game_data.effect_carriers(effect_id)
    ON DELETE SET NULL;

-- equipment_armors 테이블에 추가
ALTER TABLE game_data.equipment_armors
ADD COLUMN effect_carrier_id UUID,
ADD CONSTRAINT fk_armors_effect_carrier
    FOREIGN KEY (effect_carrier_id)
    REFERENCES game_data.effect_carriers(effect_id)
    ON DELETE SET NULL;

-- items 테이블에 추가
ALTER TABLE game_data.items
ADD COLUMN effect_carrier_id UUID,
ADD CONSTRAINT fk_items_effect_carrier
    FOREIGN KEY (effect_carrier_id)
    REFERENCES game_data.effect_carriers(effect_id)
    ON DELETE SET NULL;

-- 인덱스 추가 (쿼리 성능 향상)
CREATE INDEX idx_weapons_effect_carrier ON game_data.equipment_weapons(effect_carrier_id);
CREATE INDEX idx_armors_effect_carrier ON game_data.equipment_armors(effect_carrier_id);
CREATE INDEX idx_items_effect_carrier ON game_data.items(effect_carrier_id);
```

**이유**:
- **Data-Centric Development**: 데이터베이스 스키마가 SSOT이므로 FK로 명시
- **Type-Safety-First**: FK 제약조건으로 타입 안전성 보장
- **데이터 무결성**: FK 제약조건으로 참조 무결성 보장
- **쿼리 효율성**: JOIN 쿼리가 쉬움, 인덱스 활용 가능

### 4.2 아이템 조회 시 Effect Carrier 포함

인벤토리나 장착 아이템을 조회할 때 Effect Carrier 정보를 포함해야 합니다:

```python
async def get_character_inventory_with_effects(
    self, 
    session_id: UUID,
    runtime_entity_id: UUID
) -> Dict[str, Any]:
    """
    인벤토리 및 Effect Carrier 조회
    
    Returns:
        {
            "inventory": [...],
            "equipped": {...},
            "effect_carriers": {
                "from_items": [...],  # 아이템 기반 Effect Carrier
                "from_equipment": [...],  # 장비 기반 Effect Carrier
                "applied": [...]  # 적용 중인 Effect Carrier
            }
        }
    """
    # 1. entity_states에서 인벤토리/장착 아이템 조회
    entity_state = await self._get_entity_state(runtime_entity_id, session_id)
    inventory = parse_jsonb_data(entity_state.inventory)
    equipped = parse_jsonb_data(entity_state.equipped_items)
    
    # 2. 각 아이템의 effect_carrier_id 확인
    item_effect_ids = []
    for item_id in inventory.get('items', []):
        item_data = await self.game_data.get_item(item_id)
        if item_data and item_data.get('effect_carrier_id'):
            item_effect_ids.append(item_data['effect_carrier_id'])
    
    # 3. 장비의 effect_carrier_id 확인
    equipment_effect_ids = []
    for slot, item_id in equipped.get('slots', {}).items():
        # item_id가 weapon_id인지 armor_id인지 확인
        weapon_data = await self.game_data.get_weapon(item_id)
        armor_data = await self.game_data.get_armor(item_id)
        
        if weapon_data and weapon_data.get('effect_carrier_id'):
            equipment_effect_ids.append(weapon_data['effect_carrier_id'])
        elif armor_data and armor_data.get('effect_carrier_id'):
            equipment_effect_ids.append(armor_data['effect_carrier_id'])
    
    # 4. Effect Carrier 정보 조회
    from app.managers.effect_carrier_manager import EffectCarrierManager
    effect_carrier_manager = EffectCarrierManager(...)
    
    item_effects = []
    for effect_id in item_effect_ids:
        effect = await effect_carrier_manager.get_effect_carrier(effect_id)
        if effect.success:
            item_effects.append(effect.data)
    
    equipment_effects = []
    for effect_id in equipment_effect_ids:
        effect = await effect_carrier_manager.get_effect_carrier(effect_id)
        if effect.success:
            equipment_effects.append(effect.data)
    
    # 5. 적용 중인 Effect Carrier 조회
    applied_result = await effect_carrier_manager.get_entity_effects(
        session_id, runtime_entity_id
    )
    applied_effects = applied_result.data if applied_result.success else []
    
    return {
        "inventory": inventory,
        "equipped": equipped,
        "effect_carriers": {
            "from_items": item_effects,
            "from_equipment": equipment_effects,
            "applied": applied_effects
        }
    }
```

## 5. API 엔드포인트 설계

### 5.1 인벤토리/장착 아이템 조회 (Effect Carrier 포함)

```python
@router.get("/character/inventory/{session_id}")
async def get_character_inventory(session_id: str):
    """인벤토리 및 장착 아이템 조회 (Effect Carrier 포함)"""
    # 1. entity_states에서 인벤토리/장착 아이템 조회
    # 2. 각 아이템의 effect_carrier_id 확인
    # 3. Effect Carrier 정보 조회
    # 4. 함께 반환
    ...
```

### 5.2 적용 중인 Effect Carrier 조회

```python
@router.get("/character/applied-effects/{session_id}")
async def get_character_applied_effects(session_id: str):
    """캐릭터에 적용 중인 Effect Carrier 목록 조회 (질병, 저주, 가호, 버프 등)"""
    # entity_effect_ownership 테이블 조회
    # is_active=True인 것만 필터링
    # expires_at이 지난 것은 제외
    ...
```

## 6. 금지 사항

### 6.1 추측 로직 금지

```python
# ❌ 잘못된 코드: 추측에 의존
if effect_id.startswith("SKILL_"):
    # 스킬이라고 추측
    pass
elif effect_id.startswith("BUFF_"):
    # 버프라고 추측
    pass

# ✅ 올바른 코드: 명시적 조회
effect = await effect_carrier_manager.get_effect_carrier(effect_id)
if not effect.success:
    raise ValueError(f"Invalid effect_id: {effect_id}")

carrier_type = effect.data.carrier_type  # 명시적으로 타입 확인
```

### 6.2 기본값으로 에러 은폐 금지

```python
# ❌ 잘못된 코드: 기본값으로 에러 은폐
effect_id = item_data.get('effect_carrier_id') or "DEFAULT_EFFECT"

# ✅ 올바른 코드: 명시적 에러 처리
effect_id = item_data.get('effect_carrier_id')
if not effect_id:
    # Effect Carrier가 없는 아이템은 None 반환
    return None
```

### 6.3 타입 추측 금지

```python
# ❌ 잘못된 코드: 타입 추측
if isinstance(effect_id, str) and len(effect_id) == 36:
    # UUID라고 추측
    uuid_obj = UUID(effect_id)
else:
    # 문자열이라고 추측
    pass

# ✅ 올바른 코드: 명시적 타입 변환
from app.common.utils.uuid_helper import to_uuid

uuid_obj = to_uuid(effect_id)
if not uuid_obj:
    raise ValueError(f"Invalid effect_id format: {effect_id}")
```

## 7. 트랜잭션 사용

Effect Carrier 적용/제거는 트랜잭션 내에서 수행해야 합니다:

```python
from app.common.decorators.transaction import with_transaction

@with_transaction
async def apply_effect_to_entity(
    self,
    session_id: UUID,
    runtime_entity_id: UUID,
    effect_id: UUID,
    conn=None
):
    """Effect Carrier 적용 (트랜잭션 보장)"""
    # 1. entity_effect_ownership에 추가
    # 2. entity_states.active_effects 업데이트
    # 3. 관련 이벤트 트리거
    ...
```

## 8. 미구현 및 추가 필요 사항

### 8.1 데이터베이스 스키마 추가 필요

- [ ] **아이템/장비와 Effect Carrier 연결을 위한 FK 추가**
  - [ ] `items.effect_carrier_id` FK 추가 (스키마에 없을 경우)
  - [ ] `equipment_weapons.effect_carrier_id` FK 추가 (스키마에 없을 경우)
  - [ ] `equipment_armors.effect_carrier_id` FK 추가 (스키마에 없을 경우)
  - [ ] 인덱스 추가 (쿼리 성능 향상)
  - **참고**: `02_DATABASE/DATABASE_SCHEMA_DESIGN.md` - FK 설계 원칙
  - **참고**: `02_DATABASE/MIGRATION_GUIDELINES.md` - 마이그레이션 작성 규칙
  - **주의**: `mvp_schema.sql` 참조 필수, 사용자 컨펌 요청 필수

### 8.2 Effect Carrier UI 통합 (기획 필요)

- [ ] **Effect Carrier의 `effect_json` 구조 스키마 정의**
  - [ ] `effect_json` 필드의 JSON 스키마 정의
  - [ ] UI 표시를 위한 데이터 구조 정의
  - [ ] Effect Carrier 타입별 `effect_json` 구조 문서화
  - **참고**: `docs/design/UI_REDESIGN_BG3_STYLE_FEASIBILITY_REVIEW.md` - 7.1 권장 사항

- [ ] **UI 표시를 위한 API 엔드포인트 구현**
  - [ ] `/api/gameplay/character/inventory/{session_id}`: 인벤토리 및 Effect Carrier 조회
  - [ ] `/api/gameplay/character/equipped/{session_id}`: 장착 아이템 및 Effect Carrier 조회
  - [ ] `/api/gameplay/character/applied-effects/{session_id}`: 적용 중인 Effect Carrier 조회
  - **참고**: `04_DEVELOPMENT/UI_REDESIGN_TODO.md` - API 엔드포인트 TODO

- [ ] **Effect Carrier 표시 데이터 구조 정의**
  - [ ] UI에서 표시할 Effect Carrier 데이터 구조 정의
  - [ ] Effect Carrier 아이콘 매핑 규칙 정의
  - [ ] Effect Carrier 툴팁 표시 내용 정의

### 8.3 Service Layer 추가 필요

- [ ] **CharacterService 생성**
  - [ ] `app/services/gameplay/character_service.py` 생성
  - [ ] `BaseGameplayService` 상속
  - [ ] 인벤토리/장착 아이템 조회 시 Effect Carrier 포함
  - **참고**: `00_CORE/02_ARCHITECTURE_PRINCIPLES.md` - Service 계층 원칙

### 8.4 정책 결정 필요

- [ ] **Effect Carrier 만료 처리 정책**
  - [ ] `expires_at`이 지난 Effect Carrier 자동 제거 여부 결정
  - [ ] 만료된 Effect Carrier 조회 정책 결정 (히스토리 보관 여부)
  - [ ] 만료 알림 정책 결정 (UI에 표시 여부)

- [ ] **Effect Carrier 중복 적용 정책**
  - [ ] 동일한 Effect Carrier 중복 적용 허용 여부 결정
  - [ ] 중복 적용 시 효과 중첩 정책 결정
  - [ ] 중복 적용 시 지속 시간 갱신 정책 결정

## 9. 참고 문서

- `docs/rules/01_PHILOSOPHY.md`: 핵심 개발 철학
- `docs/rules/TRANSACTION_GUIDELINES.md`: 트랜잭션 사용 가이드라인
- `docs/rules/UUID_USAGE_GUIDELINES.md`: UUID 사용 가이드라인
- `docs/design/UI_REDESIGN_BG3_STYLE_CORRECTIONS.md`: Effect Carrier 개념 정정
- `docs/design/UI_REDESIGN_BG3_STYLE_FEASIBILITY_REVIEW.md`: Effect Carrier UI 통합 방법
- `app/managers/effect_carrier_manager.py`: Effect Carrier Manager 구현
- `04_DEVELOPMENT/UI_REDESIGN_TODO.md`: UI 리디자인 TODO

