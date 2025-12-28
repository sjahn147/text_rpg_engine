# 아이템/장비와 Effect Carrier 아키텍처 제안

**작성일**: 2025-12-28  
**최종 결정**: 2025-12-28  
**목적**: 시니어 개발자 관점에서 최적의 아키텍처 설계 제안

## ✅ 최종 결정: 하이브리드 접근법 (Option C)

**결정 이유**:
- 아이템/장비는 Effect Carrier이기도 하지만, 아이템/장비 자체의 속성(수량, 스택, 내구도, 무게 등)이 많아서 별도 테이블로 관리하는 것이 낫다
- 너무 추상화하면 관리가 어렵다
- 최소 변경으로 기존 구조를 유지하면서 확장성 확보

---

## 🔍 현재 상황 분석

### 현재 DB 구조

1. **`game_data.items`** (아이템 템플릿)
   - `item_id`, `item_type`, `consumable`, `stack_size`
   - `item_properties` (JSONB) - 효과 데이터 포함

2. **`game_data.equipment_weapons`**, **`game_data.equipment_armors`** (장비 템플릿)
   - `weapon_id`, `armor_id`
   - `weapon_properties`, `armor_properties` (JSONB) - 효과 데이터 포함

3. **`game_data.effect_carriers`** (효과 통일 관리)
   - `effect_id` (UUID), `carrier_type` ('skill', 'buff', **'item'**, 'blessing', 'curse', 'ritual')
   - `effect_json` (JSONB) - 효과 데이터
   - `constraints_json` (JSONB) - 사용 조건

### 문제점

- **중복**: 아이템 효과가 `items.item_properties`와 `effect_carriers.effect_json`에 중복 가능
- **일관성 부족**: 아이템 효과를 두 곳에서 관리
- **확장성 제한**: 새로운 효과 타입 추가 시 여러 테이블 수정 필요

---

## 🎯 두 가지 옵션 비교

### Option A: 아이템/장비가 Effect Carrier 자체

**구조**:
```
game_data.effect_carriers
  ├── carrier_type='item' → 아이템 역할
  ├── carrier_type='skill' → 스킬
  └── carrier_type='buff' → 버프
```

**아이템/장비는 Effect Carrier로 통합**:
- `game_data.items`, `equipment_*` 테이블은 deprecated
- 모든 아이템/장비는 `effect_carriers`에 `carrier_type='item'`으로 저장
- 인벤토리는 `entity_effect_ownership`로 관리

**장점**:
- ✅ **단일 책임 원칙 (SRP)**: 모든 효과를 Effect Carrier로 통일
- ✅ **확장성**: 새로운 효과 타입 추가 용이
- ✅ **일관성**: 모든 효과가 동일한 인터페이스
- ✅ **Effect Carrier 설계 철학과 일치**: "특수성은 소유한 형식에 있음"
- ✅ **쿼리 단순화**: 하나의 테이블로 모든 효과 조회

**단점**:
- ❌ **기존 데이터 마이그레이션 필요**: `items`, `equipment_*` → `effect_carriers`
- ❌ **인벤토리 관리 복잡**: `entity_effect_ownership`만으로는 수량/스택 관리 어려움
- ❌ **타입 안전성**: `carrier_type='item'`인 Effect Carrier와 실제 아이템 구분 필요

---

### Option B: 아이템/장비가 Effect Carrier를 소유 (Composition)

**구조**:
```
game_data.items
  ├── item_id
  ├── item_type
  └── effect_carrier_id (FK) → game_data.effect_carriers

game_data.equipment_weapons
  ├── weapon_id
  └── effect_carrier_id (FK) → game_data.effect_carriers
```

**아이템/장비는 Effect Carrier를 참조**:
- `items`, `equipment_*` 테이블은 유지
- 효과는 `effect_carriers`에 저장하고 참조
- 인벤토리는 `entity_states.inventory`로 관리

**장점**:
- ✅ **역할 분리**: 아이템/장비는 인벤토리 관리, Effect Carrier는 효과 관리
- ✅ **기존 구조 유지**: 마이그레이션 최소화
- ✅ **타입 안전성**: 아이템과 Effect Carrier 명확히 구분
- ✅ **인벤토리 관리 용이**: 수량, 스택, 소비 등 기존 로직 유지

**단점**:
- ❌ **복잡성 증가**: 두 시스템을 모두 이해해야 함
- ❌ **데이터 중복 가능**: 아이템 속성과 Effect Carrier 속성 중복
- ❌ **일관성 부족**: 아이템 효과와 스킬 효과가 다른 방식으로 관리

---

## 💡 시니어 개발자 제안: **하이브리드 접근법 (Option C)**

### 핵심 아이디어: **"아이템/장비는 Effect Carrier를 소유하되, Effect Carrier는 아이템 역할도 수행"**

**구조**:
```
game_data.items
  ├── item_id
  ├── item_type
  ├── effect_carrier_id (FK, Optional) → game_data.effect_carriers
  └── item_properties (JSONB) - 인벤토리 관련 속성만 (stack_size, consumable 등)

game_data.equipment_weapons
  ├── weapon_id
  ├── effect_carrier_id (FK, Optional) → game_data.effect_carriers
  └── weapon_properties (JSONB) - 장비 관련 속성만 (durability 등)

game_data.effect_carriers
  ├── effect_id (UUID)
  ├── carrier_type ('skill', 'buff', 'item', 'blessing', 'curse', 'ritual')
  ├── effect_json (JSONB) - 효과 데이터
  └── constraints_json (JSONB) - 사용 조건
```

### 설계 원칙

1. **아이템/장비는 인벤토리 관리의 주체**
   - `entity_states.inventory`에 `item_id` 저장
   - 수량, 스택, 소비 등은 `items` 테이블에서 관리

2. **Effect Carrier는 효과의 주체**
   - 아이템/장비의 효과는 `effect_carriers`에 저장
   - `items.effect_carrier_id`로 참조

3. **선택적 결합 (Optional Composition)**
   - `effect_carrier_id`는 Optional
   - 효과가 없는 아이템도 가능 (예: 재료 아이템)
   - 효과만 있는 Effect Carrier도 가능 (예: 스킬, 버프)

### 장점

- ✅ **역할 분리**: 인벤토리 관리 vs 효과 관리
- ✅ **유연성**: 효과가 있는 아이템과 없는 아이템 모두 지원
- ✅ **확장성**: 새로운 효과 타입 추가 용이
- ✅ **기존 구조 유지**: 마이그레이션 최소화
- ✅ **타입 안전성**: 아이템과 Effect Carrier 명확히 구분

---

## 🏗️ 권장 구현 방안

### 1. DB 스키마 수정

```sql
-- items 테이블에 effect_carrier_id 추가
ALTER TABLE game_data.items
ADD COLUMN effect_carrier_id UUID,
ADD CONSTRAINT fk_items_effect_carrier
    FOREIGN KEY (effect_carrier_id) 
    REFERENCES game_data.effect_carriers(effect_id) 
    ON DELETE SET NULL;

-- equipment_weapons 테이블에 effect_carrier_id 추가
ALTER TABLE game_data.equipment_weapons
ADD COLUMN effect_carrier_id UUID,
ADD CONSTRAINT fk_weapons_effect_carrier
    FOREIGN KEY (effect_carrier_id) 
    REFERENCES game_data.effect_carriers(effect_id) 
    ON DELETE SET NULL;

-- equipment_armors 테이블에 effect_carrier_id 추가
ALTER TABLE game_data.equipment_armors
ADD COLUMN effect_carrier_id UUID,
ADD CONSTRAINT fk_armors_effect_carrier
    FOREIGN KEY (effect_carrier_id) 
    REFERENCES game_data.effect_carriers(effect_id) 
    ON DELETE SET NULL;
```

### 2. 데이터 구조

#### 아이템 예시
```json
{
  "item_id": "ITEM_POTION_HEAL_001",
  "item_type": "consumable",
  "consumable": true,
  "stack_size": 10,
  "effect_carrier_id": "550e8400-e29b-41d4-a716-446655440000",
  "item_properties": {
    "weight": 0.1,
    "value": 50
  }
}
```

#### Effect Carrier 예시
```json
{
  "effect_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Healing Potion Effect",
  "carrier_type": "item",
  "effect_json": {
    "heal_amount": 50,
    "instant": true
  },
  "constraints_json": {
    "use_in_combat": true,
    "use_out_of_combat": true
  }
}
```

### 3. 획득 플로우

```
1. 오브젝트의 properties.contents에서 item_id 추출
   ↓
2. game_data.items 테이블 조회
   ↓
3. effect_carrier_id가 있으면:
   - Effect Carrier 조회
   - 효과 정보 포함하여 인벤토리 추가
   ↓
4. entity_states.inventory에 item_id 추가
   ↓
5. (선택적) entity_effect_ownership에 effect_carrier_id 추가
   (아이템 사용 시 효과 적용을 위해)
```

---

## 📊 최종 권장사항

### **Option C (하이브리드 접근법) 권장**

**이유**:
1. **실용성**: 기존 구조를 최대한 활용하면서 확장성 확보
2. **명확한 책임 분리**: 인벤토리 관리와 효과 관리 분리
3. **유연성**: 효과가 있는 아이템과 없는 아이템 모두 지원
4. **마이그레이션 부담 최소화**: 기존 데이터 구조 유지

### 구현 우선순위

1. **Phase 1**: DB 스키마 수정 (effect_carrier_id 추가)
2. **Phase 2**: 기존 아이템/장비에 Effect Carrier 연결
3. **Phase 3**: 획득/사용 로직 수정
4. **Phase 4**: (선택적) 기존 items.item_properties의 효과 데이터를 Effect Carrier로 마이그레이션

---

## 🔄 대안: 완전 통합 (Option A)을 선택하는 경우

만약 **장기적으로 완전한 통합**을 원한다면:

1. **모든 아이템/장비를 Effect Carrier로 마이그레이션**
2. **인벤토리 관리 확장**:
   - `entity_effect_ownership`에 수량 정보 추가
   - 또는 별도의 인벤토리 테이블 생성

**장점**: 완전한 일관성, 단일 인터페이스  
**단점**: 대규모 마이그레이션 필요, 인벤토리 관리 복잡도 증가

---

## ✅ 결론

**권장**: **Option C (하이브리드 접근법)**

- 아이템/장비는 인벤토리 관리의 주체
- Effect Carrier는 효과의 주체
- 선택적 결합으로 유연성 확보
- 기존 구조 유지하면서 확장성 확보

