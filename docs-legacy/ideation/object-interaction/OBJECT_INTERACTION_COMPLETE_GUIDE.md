# 오브젝트 상호작용 완전 가이드

**작성일**: 2025-12-28  
**최신화 날짜**: 2025-12-28  
**목적**: 오브젝트 상호작용 시스템의 완전한 설계, 아키텍처, 구현 가이드

**참고 문서**:
- `ACTION_HANDLER_MODULARIZATION_PROPOSAL.md`: ActionHandler 전체 모듈화 제안
- `ARCHITECTURE_DISCUSSION.md`: 아키텍처 설계 토론

---

## 목차

1. [엔티티 정의](#1-엔티티-정의)
2. [현재 구현 상태](#2-현재-구현-상태)
3. [문제점 분석](#3-문제점-분석)
4. [아키텍처 제안](#4-아키텍처-제안)
5. [ID 설계 분석](#5-id-설계-분석)
6. [상호작용 타입 정의](#6-상호작용-타입-정의)
7. [데이터베이스 속성 표현](#7-데이터베이스-속성-표현)
8. [구현 계획](#8-구현-계획)
9. [TimeSystem 연동](#9-timesystem-연동)
10. [Effect 시스템 연동](#10-effect-시스템-연동)

---

## 1. 엔티티 정의

### 1.1 World Objects (`game_data.world_objects`)

**정의**: 셀에 고정된 물체 (환경 오브젝트)

**특징**:
- `object_type`: `'static'`, `'interactive'`, `'trigger'`
- `movable`: 물리적으로 이동 가능한지 여부 (예: 의자, 상자)
  - **중요**: `movable=true`여도 오브젝트 자체는 인벤토리에 들어가지 않음
  - 오브젝트는 셀에 고정된 환경 요소
- `properties.contents`: 오브젝트 안에 들어있는 아이템/장비/Effect Carrier ID 목록
  - 예: `{"contents": ["ITEM_POTION_001", "WEAPON_SWORD_001", "EFFECT_ID_UUID"]}`

**예시**:
- 침대, 책상, 창문, 문 (고정물)
- 상자, 의자 (movable이지만 환경 오브젝트)
- 상자 안의 아이템은 `properties.contents`에 저장

**획득 불가**: 오브젝트 자체는 획득할 수 없음

### 1.2 Items (`game_data.items`)

**정의**: 인벤토리에 들어갈 수 있는 아이템 템플릿

**특징**:
- `item_id`: 아이템 템플릿 ID (예: `"ITEM_POTION_HEAL_001"`)
- `item_type`: 아이템 종류
- `consumable`: 소비 가능 여부
- `stack_size`: 스택 가능 개수

**저장 위치**:
- `runtime_data.entity_states.inventory` (JSONB)
  - 구조: `{"items": ["ITEM_POTION_001", "ITEM_BREAD_001"], "quantities": {"ITEM_POTION_001": 5}}`

**획득 방법**:
1. 오브젝트의 `properties.contents`에서 `item_id` 추출
2. `InstanceFactory.create_item_instance()`로 런타임 아이템 인스턴스 생성
3. 플레이어의 `entity_states.inventory`에 추가

### 1.3 Equipment (`game_data.equipment_weapons`, `game_data.equipment_armors`)

**정의**: 무기/방어구 장비 템플릿

**특징**:
- `weapon_id`: 무기 템플릿 ID (예: `"WEAPON_SWORD_001"`)
- `armor_id`: 방어구 템플릿 ID (예: `"ARMOR_LEATHER_001"`)
- `base_property_id`: `base_properties` 참조

**저장 위치**:
- `runtime_data.entity_states.equipped_items` (JSONB)
  - 구조: `{"weapon": "WEAPON_SWORD_001", "armor": {"body": "ARMOR_LEATHER_001"}}`

**획득 방법**:
1. 오브젝트의 `properties.contents`에서 `weapon_id` 또는 `armor_id` 추출
2. 장비 인스턴스 생성 (아이템과 유사)
3. 플레이어의 `entity_states.equipped_items`에 추가 (또는 인벤토리에 추가 후 장착)

### 1.4 Effect Carriers (`game_data.effect_carriers`)

**정의**: 모든 효과를 통일된 인터페이스로 관리 (스킬, 버프, 아이템, 축복, 저주, 의식)

**특징**:
- `effect_id`: UUID (예: `"550e8400-e29b-41d4-a716-446655440000"`)
- `carrier_type`: `'skill'`, `'buff'`, `'item'`, `'blessing'`, `'curse'`, `'ritual'`
- `effect_json`: 효과의 세부 데이터
- `constraints_json`: 사용 조건 및 제약사항

**저장 위치**:
- `reference_layer.entity_effect_ownership`
  - 구조: `(session_id, runtime_entity_id, effect_id, acquired_at, source)`

**획득 방법**:
1. 오브젝트의 `properties.contents`에서 `effect_id` (UUID) 추출
2. `EffectCarrierManager.grant_effect_to_entity()`로 엔티티에 부여
3. `entity_effect_ownership` 테이블에 추가

**중요**: `carrier_type='item'`인 Effect Carrier도 있음 (일반 `items`와는 별개)

### 1.5 엔티티 비교표

| 구분 | World Objects | Items | Equipment | Effect Carriers |
|------|--------------|-------|-----------|-----------------|
| **테이블** | `game_data.world_objects` | `game_data.items` | `game_data.equipment_*` | `game_data.effect_carriers` |
| **ID 형식** | `OBJ_*` | `ITEM_*` | `WEAPON_*`, `ARMOR_*` | UUID |
| **저장 위치** | 셀에 고정 | `entity_states.inventory` | `entity_states.equipped_items` | `entity_effect_ownership` |
| **획득 가능** | ❌ (오브젝트 자체는 획득 불가) | ✅ | ✅ | ✅ |
| **내용물** | `properties.contents`에 아이템/장비 ID 저장 | - | - | - |
| **용도** | 환경 요소, 상호작용 대상 | 플레이어가 소유/사용 | 플레이어가 소유/사용 | 효과 관리 |

### 1.6 획득 플로우

#### 시나리오 1: 상자에서 아이템 획득

```
1. 플레이어가 상자 오브젝트와 상호작용 (open)
   ↓
2. 오브젝트의 properties.contents 확인
   {"contents": ["ITEM_POTION_001", "WEAPON_SWORD_001"]}
   ↓
3. 각 ID 타입 확인:
   - "ITEM_POTION_001" → game_data.items 테이블 조회
   - "WEAPON_SWORD_001" → game_data.equipment_weapons 테이블 조회
   ↓
4. 아이템 획득:
   - InstanceFactory.create_item_instance("ITEM_POTION_001", ...)
   - entity_states.inventory에 추가
   ↓
5. 장비 획득:
   - 장비 인스턴스 생성
   - entity_states.inventory 또는 equipped_items에 추가
   ↓
6. 오브젝트의 contents 업데이트 (또는 제거)
```

#### 시나리오 2: Effect Carrier 획득

```
1. 오브젝트의 properties.contents에서 effect_id (UUID) 추출
   ↓
2. EffectCarrierManager.grant_effect_to_entity() 호출
   ↓
3. entity_effect_ownership 테이블에 추가
   ↓
4. 엔티티의 active_effects에 반영 (런타임)
```

---

## 2. 현재 구현 상태

### 2.1 이미 구현된 상호작용

| 액션 | 위치 | 상태 관리 | Manager 사용 | 완성도 |
|------|------|-----------|--------------|--------|
| `examine` | `gameplay.py:851` | 없음 | 없음 | ✅ 완료 |
| `open` | `gameplay.py:723` | ✅ 런타임 상태 | ❌ 직접 SQL | ⚠️ 개선 필요 |
| `light` | `gameplay.py:779` | ✅ 런타임 상태 | ❌ 직접 SQL | ⚠️ 개선 필요 |
| `pickup` | `gameplay.py:1086` | ✅ 런타임 상태 | ✅ InventoryManager | ✅ 완료 |
| `sit` | `gameplay.py:824` | ❌ 없음 | ❌ 없음 | ⚠️ 미완성 |
| `rest` | `gameplay.py:831` | ❌ 없음 | ❌ 없음 | ❌ 미완성 (HP/MP 회복 안 됨) |

### 2.2 현재 코드베이스 구조

| 계층 | 위치 | 역할 | 예시 |
|------|------|------|------|
| **Factories** | `database/factories/` | 데이터 생성 (정적/런타임) | `GameDataFactory`, `InstanceFactory` |
| **Managers** | `app/managers/` | 도메인별 상태 관리 | `EntityManager`, `CellManager`, `InventoryManager` |
| **Handlers** | `app/handlers/` | 게임 행동 처리 | `ActionHandler` |
| **Services** | `app/services/` | 특정 기능 제공 | `CollisionService`, WorldEditor 서비스들 |

### 2.3 현재 사용 가능한 Manager

- ✅ `CellManager`: 셀 및 오브젝트 조회
- ✅ `InventoryManager`: 인벤토리 관리
- ✅ `EffectCarrierManager`: Effect Carrier 관리
- ✅ `EntityManager`: 엔티티 기본 관리 (HP/MP 회복 메서드 추가 필요)
- ✅ `RuntimeDataRepository.update_entity_stats()`: 스탯 업데이트 (사용 가능)
- ❌ `ObjectStateManager`: 없음 (생성 필요)

---

## 3. 문제점 분석

### 3.1 상태 관리 일관성 부족

- `open`, `light`는 런타임 상태를 업데이트하지만
- `sit`, `rest`는 상태를 업데이트하지 않음
- `rest`는 HP/MP 회복 효과를 계산하지만 실제로 플레이어 상태를 업데이트하지 않음

### 3.2 Manager 부재

- 대부분의 상호작용이 직접 SQL을 실행
- 재사용 가능한 로직이 없음
- 테스트하기 어려움

### 3.3 데이터베이스 속성 표현 불일치

- `properties`에 다양한 형식으로 저장됨
- `rest_effect`, `restore_hp`, `restore_mp` 등 일관성 없음

---

## 4. 아키텍처 제안

### 4.1 Factory 패턴은 부적합

**이유**:
1. Factory는 객체 생성에 사용됨 (데이터 생성)
2. 상호작용은 "행동 실행"이지 "객체 생성"이 아님
3. 상호작용 패턴은 Strategy 패턴이나 Registry 패턴이 더 적합

### 4.2 권장 아키텍처: ActionHandler 확장

**이유**:
1. **일관성**: 기존 `ActionHandler`와 동일한 패턴
2. **단순성**: 새로운 계층 추가 불필요
3. **통합성**: 모든 게임 행동을 한 곳에서 관리

**구조**:
```
ActionHandler
├── handle_investigate()      # 기존
├── handle_dialogue()         # 기존
├── handle_move()             # 기존
├── handle_examine_object()   # 신규
├── handle_open_object()      # 신규
├── handle_rest_at_object()   # 신규
└── handle_pickup_from_object() # 신규
```

**의존성**:
```python
class ActionHandler:
    def __init__(self, ...):
        # 기존 의존성들
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
        
        # 신규 의존성들
        self.object_state_manager = ObjectStateManager(...)
        self.inventory_manager = InventoryManager(...)
        self.effect_carrier_manager = effect_carrier_manager
        self.time_system = TimeSystem()  # 선택사항
```

### 4.3 최종 구조

```
app/
├── managers/
│   ├── object_state_manager.py    # 오브젝트 상태 관리 (신규)
│   ├── entity_manager.py          # 기존
│   ├── cell_manager.py            # 기존
│   └── inventory_manager.py       # 기존
├── handlers/
│   └── action_handler.py          # 오브젝트 상호작용 핸들러 추가 (확장)
└── services/
    └── collision_service.py       # 기존 (충돌 검사)
```

**의존성 흐름**:
```
ActionHandler
├── ObjectStateManager (오브젝트 상태)
├── EntityManager (엔티티 상태)
├── InventoryManager (인벤토리)
├── EffectCarrierManager (효과)
├── CellManager (셀 정보)
└── TimeSystem (시간, 선택사항)
```

---

## 5. ID 설계 분석

### 5.1 현재 상황

#### 스키마 불일치 문제

1. **`reference_layer.object_references`**
   - `runtime_object_id`: `VARCHAR(50)` - 문자열 ID 허용
   - 용도: 게임 데이터 오브젝트와 런타임 오브젝트 간 참조

2. **`runtime_data.runtime_objects`**
   - `runtime_object_id`: `UUID` - UUID만 허용
   - 용도: 런타임 오브젝트 인스턴스 저장

3. **`runtime_data.object_states`**
   - `runtime_object_id`: `UUID` - UUID만 허용
   - Foreign Key: `runtime_objects.runtime_object_id` 참조
   - 용도: 오브젝트의 런타임 상태 (열림/닫힘, 내용물 등)

### 5.2 권장사항: UUID 통일 (옵션 A)

**원칙**: 모든 런타임 오브젝트는 `runtime_objects`에 UUID로 생성

**장점**:
- ✅ 타입 일관성: 모든 런타임 오브젝트가 UUID
- ✅ `object_states` 조회 시 타입 변환 불필요
- ✅ 확장성: 나중에 오브젝트별 상태 관리 용이
- ✅ 명확한 구분: 게임 데이터(`game_object_id`) vs 런타임 인스턴스(`runtime_object_id`)

**구현**:
```python
# 셀 로드 시 오브젝트 인스턴스 자동 생성
async def ensure_object_instance(game_object_id, session_id):
    # runtime_objects에 없으면 생성
    runtime_obj = await conn.fetchrow(
        "SELECT runtime_object_id FROM runtime_data.runtime_objects WHERE game_object_id = $1 AND session_id = $2",
        game_object_id, session_id
    )
    if not runtime_obj:
        runtime_object_id = str(uuid.uuid4())
        await conn.execute(
            "INSERT INTO runtime_data.runtime_objects (runtime_object_id, game_object_id, session_id) VALUES ($1, $2, $3)",
            runtime_object_id, game_object_id, session_id
        )
        # object_references에도 등록
        await conn.execute(
            "INSERT INTO reference_layer.object_references (runtime_object_id, game_object_id, session_id, object_type) VALUES ($1, $2, $3, $4)",
            runtime_object_id, game_object_id, session_id, object_type
        )
    return runtime_obj['runtime_object_id'] if runtime_obj else runtime_object_id
```

---

## 6. 상호작용 타입 정의

### 6.1 기본 상호작용 타입

| 상호작용 | 액션 ID | 설명 | 상태 변경 | 엔티티 영향 | TimeSystem |
|----------|---------|------|-----------|-------------|------------|
| **관찰** | `examine` | 오브젝트 상세 정보 확인 | 없음 | 없음 | 없음 |
| **열기** | `open` | 오브젝트 열기 (내용물 확인) | `closed` → `open` | 없음 | 없음 |
| **닫기** | `close` | 오브젝트 닫기 | `open` → `closed` | 없음 | 없음 |
| **불 켜기** | `light` | 오브젝트에 불 켜기 | `unlit` → `lit` | 없음 | 없음 |
| **불 끄기** | `extinguish` | 오브젝트 불 끄기 | `lit` → `unlit` | 없음 | 없음 |
| **앉기** | `sit` | 오브젝트에 앉기 | `unused` → `occupied` | 없음 | 없음 |
| **일어서기** | `stand` | 앉은 자리에서 일어서기 | `occupied` → `unused` | 없음 | 없음 |
| **쉬기** | `rest` | 오브젝트에서 휴식 | `unused` → `rested` | HP/MP 회복 | ✅ 시간 소모 |
| **잠자기** | `sleep` | 오브젝트에서 잠자기 | `unused` → `slept_in` | HP/MP 회복, 피로도 감소 | ✅ 시간 소모 (대량) |
| **먹기** | `eat` | 음식/음료 섭취 | `full` → `consumed` | HP/MP 회복, 효과 적용 | ✅ 시간 소모 |
| **마시기** | `drink` | 음료 섭취 | `full` → `consumed` | MP 회복, 효과 적용 | ✅ 시간 소모 |
| **읽기** | `read` | 책/문서 읽기 | 없음 | 지식/정보 획득, 효과 적용 | ✅ 시간 소모 |
| **쓰기** | `write` | 책/문서 작성 | `empty` → `written` | 없음 | ✅ 시간 소모 |
| **사용하기** | `use` | 도구/장비 사용 | 상태에 따라 변경 | 효과 적용 | ✅ 시간 소모 (선택) |
| **줍기** | `pickup` | 오브젝트에서 아이템 획득 | contents에서 제거 | 인벤토리 추가 | 없음 |
| **놓기** | `place` | 오브젝트에 아이템 배치 | contents에 추가 | 인벤토리에서 제거 | 없음 |
| **조합하기** | `combine` | 오브젝트와 아이템 조합 | 상태 변경, contents 변경 | 인벤토리 변경 | ✅ 시간 소모 |
| **수리하기** | `repair` | 오브젝트 수리 | `broken` → `repaired` | 도구/재료 소모 | ✅ 시간 소모 |
| **파괴하기** | `destroy` | 오브젝트 파괴 | `intact` → `destroyed` | 없음 | ✅ 시간 소모 |

### 6.2 상호작용 카테고리

#### 1. **정보 확인 (Information)**
- `examine`: 기본 관찰
- `inspect`: 상세 조사 (특정 부분)
- `search`: 숨겨진 내용 찾기

#### 2. **상태 변경 (State Change)**
- `open`/`close`: 열기/닫기
- `light`/`extinguish`: 불 켜기/끄기
- `activate`/`deactivate`: 활성화/비활성화
- `lock`/`unlock`: 잠그기/풀기

#### 3. **위치 변경 (Position)**
- `sit`/`stand`: 앉기/일어서기
- `lie`/`get_up`: 눕기/일어나기
- `climb`/`descend`: 오르기/내려가기

#### 4. **회복 (Recovery)**
- `rest`: 휴식 (HP/MP 소량 회복, 시간 소모)
- `sleep`: 잠자기 (HP/MP 대량 회복, 피로도 감소, 시간 대량 소모)
- `meditate`: 명상 (MP 회복, 효과 적용)

#### 5. **소비 (Consumption)**
- `eat`: 먹기 (HP 회복, 효과 적용, 시간 소모)
- `drink`: 마시기 (MP 회복, 효과 적용, 시간 소모)
- `consume`: 일반 소비 (효과 적용)

#### 6. **학습/정보 (Learning)**
- `read`: 읽기 (정보 획득, 효과 적용, 시간 소모)
- `study`: 공부하기 (효과 적용, 시간 대량 소모)
- `write`: 쓰기 (아이템 생성, 시간 소모)

#### 7. **아이템 조작 (Item Manipulation)**
- `pickup`: 줍기 (오브젝트 → 인벤토리)
- `place`: 놓기 (인벤토리 → 오브젝트)
- `take`: 가져가기 (오브젝트 → 인벤토리, `pickup`과 동일)
- `put`: 넣기 (인벤토리 → 오브젝트, `place`와 동일)

#### 8. **조합/제작 (Crafting)**
- `combine`: 조합하기 (아이템 + 오브젝트 → 결과)
- `craft`: 제작하기 (재료 + 오브젝트 → 결과, 시간 소모)
- `cook`: 요리하기 (재료 → 음식, 시간 소모)
- `repair`: 수리하기 (도구 + 오브젝트 → 수리된 오브젝트, 시간 소모)

#### 9. **파괴/변형 (Destruction)**
- `destroy`: 파괴하기 (오브젝트 → 파편/재료)
- `break`: 부수기 (오브젝트 → 파편)
- `dismantle`: 분해하기 (오브젝트 → 부품, 시간 소모)

---

## 7. 데이터베이스 속성 표현

### 7.1 표준화된 `properties` 구조

```json
{
  "interaction_type": "restable",
  "possible_states": ["unused", "rested", "slept_in"],
  "default_state": "unused",
  "current_state": "unused",
  
  "interactions": {
    "rest": {
      "effects": {
        "hp": 50,
        "mp": 30
      },
      "time_cost": 30,
      "state_change": "rested",
      "message": "침대에서 휴식을 취했습니다.",
      "requirements": {
        "fatigue": ">0"
      }
    },
    "sleep": {
      "effects": {
        "hp": 100,
        "mp": 50,
        "fatigue": -100
      },
      "time_cost": 480,
      "state_change": "slept_in",
      "message": "침대에서 잠을 잤습니다.",
      "requirements": {
        "time_period": "night|late_night"
      }
    }
  },
  
  "contents": ["ITEM_PAPER_BLANK_001", "ITEM_PEN_BASIC_001"],
  "max_contents": 10,
  
  "material": "wood",
  "durability": 100,
  "max_durability": 100,
  
  "interaction_requirements": {
    "open": {
      "requires_item": ["ITEM_KEY_001"],
      "requires_skill": ["lockpicking"],
      "skill_level": 5
    }
  }
}
```

### 7.2 상호작용별 속성 예시

#### 열 수 있는 오브젝트 (상자, 문, 서랍)
```json
{
  "interaction_type": "openable",
  "possible_states": ["closed", "open", "locked"],
  "default_state": "closed",
  "interactions": {
    "open": {
      "state_change": "open",
      "reveals_contents": true,
      "message": "{object_name}을(를) 열었습니다."
    },
    "close": {
      "state_change": "closed",
      "message": "{object_name}을(를) 닫았습니다."
    }
  },
  "contents": ["ITEM_GOLD_001", "ITEM_POTION_001"],
  "max_contents": 5
}
```

#### 쉴 수 있는 오브젝트 (침대, 의자)
```json
{
  "interaction_type": "restable",
  "possible_states": ["unused", "rested", "slept_in"],
  "default_state": "unused",
  "interactions": {
    "rest": {
      "effects": {
        "hp": 50,
        "mp": 30
      },
      "time_cost": 30,
      "state_change": "rested",
      "message": "{object_name}에서 휴식을 취했습니다."
    },
    "sleep": {
      "effects": {
        "hp": 100,
        "mp": 50,
        "fatigue": -100
      },
      "time_cost": 480,
      "state_change": "slept_in",
      "message": "{object_name}에서 잠을 잤습니다.",
      "requirements": {
        "time_period": "night|late_night"
      }
    }
  },
  "comfort_level": 8,
  "material": "wood"
}
```

#### 먹을 수 있는 오브젝트 (음식, 음료)
```json
{
  "interaction_type": "consumable",
  "possible_states": ["full", "consumed"],
  "default_state": "full",
  "interactions": {
    "eat": {
      "effects": {
        "hp": 20,
        "hunger": -30
      },
      "time_cost": 5,
      "state_change": "consumed",
      "message": "{object_name}을(를) 먹었습니다.",
      "effect_carrier_id": "EFFECT_FOOD_SATISFACTION_001"
    }
  },
  "nutrition_value": 50,
  "expires_after": 86400
}
```

---

## 8. 구현 계획

### 8.1 ObjectStateManager 설계

```python
# app/managers/object_state_manager.py
from typing import Dict, List, Optional, Any
import uuid
import json
import asyncio
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger
from common.utils.jsonb_handler import parse_jsonb_data, serialize_jsonb_data
from pydantic import BaseModel

class ObjectStateResult(BaseModel):
    """오브젝트 상태 조작 결과"""
    success: bool
    message: str
    object_state: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    @classmethod
    def success_result(cls, object_state: Dict[str, Any], message: str = "성공") -> "ObjectStateResult":
        return cls(success=True, message=message, object_state=object_state)
    
    @classmethod
    def error_result(cls, message: str, error: str = None) -> "ObjectStateResult":
        return cls(success=False, message=message, error=error)


class ObjectStateManager:
    """오브젝트 상태 관리 클래스"""
    
    def __init__(self,
                 db_connection: DatabaseConnection,
                 game_data_repo: GameDataRepository,
                 runtime_data_repo: RuntimeDataRepository,
                 reference_layer_repo: ReferenceLayerRepository):
        self.db = db_connection
        self.game_data = game_data_repo
        self.runtime_data = runtime_data_repo
        self.reference_layer = reference_layer_repo
        self.logger = logger
        
        # 오브젝트 상태 캐시
        self._state_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = asyncio.Lock()
    
    async def get_object_state(
        self,
        runtime_object_id: Optional[str],
        game_object_id: str,
        session_id: str
    ) -> ObjectStateResult:
        """오브젝트의 현재 상태 조회 (런타임 + 기본값 병합)"""
        # 1. 캐시 확인
        # 2. runtime_object_id가 없으면 레퍼런스 레이어에서 조회/생성
        # 3. runtime_data.object_states에서 런타임 상태 조회
        # 4. game_data.world_objects에서 기본값 조회
        # 5. 병합하여 반환
    
    async def update_object_state(
        self,
        runtime_object_id: str,
        game_object_id: str,
        session_id: str,
        state: Optional[str] = None,
        contents: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> ObjectStateResult:
        """오브젝트 상태 업데이트"""
        # 1. runtime_object_id가 없으면 생성
        # 2. 기존 상태 조회
        # 3. 상태 병합
        # 4. runtime_data.object_states에 저장
        # 5. 캐시 업데이트
    
    async def get_object_contents(
        self,
        runtime_object_id: Optional[str],
        game_object_id: str,
        session_id: str
    ) -> ObjectStateResult:
        """오브젝트의 contents 조회 (런타임 상태 반영)"""
        # get_object_state 호출 후 contents 추출
    
    async def remove_from_contents(
        self,
        runtime_object_id: str,
        game_object_id: str,
        session_id: str,
        item_id: str
    ) -> ObjectStateResult:
        """contents에서 아이템 제거"""
        # 1. 현재 contents 조회
        # 2. item_id 제거
        # 3. 상태 업데이트
```

### 8.2 EntityManager 확장

```python
# app/managers/entity_manager.py에 추가
async def restore_hp_mp(
    self,
    runtime_entity_id: str,
    hp: int = 0,
    mp: int = 0
) -> EntityResult:
    """HP/MP 회복"""
    try:
        # 현재 스탯 조회
        pool = await self.db.pool
        async with pool.acquire() as conn:
            entity_state = await conn.fetchrow(
                """
                SELECT current_stats FROM runtime_data.entity_states
                WHERE runtime_entity_id = $1
                """,
                runtime_entity_id
            )
            
            if not entity_state:
                return EntityResult.error_result("엔티티 상태를 찾을 수 없습니다")
            
            current_stats = parse_jsonb_data(entity_state['current_stats'])
            current_hp = current_stats.get('hp', 0)
            current_mp = current_stats.get('mp', 0)
            max_hp = current_stats.get('max_hp', current_hp)
            max_mp = current_stats.get('max_mp', current_mp)
            
            new_hp = min(current_hp + hp, max_hp)
            new_mp = min(current_mp + mp, max_mp)
            
            # 스탯 업데이트
            await self.runtime_data.update_entity_stats(
                runtime_entity_id,
                {'hp': new_hp, 'mp': new_mp}
            )
            
            return EntityResult.success_result(
                entity=None,
                message=f"HP +{new_hp - current_hp}, MP +{new_mp - current_mp}"
            )
    except Exception as e:
        return EntityResult.error_result(f"HP/MP 회복 실패: {str(e)}")
```

### 8.3 ActionHandler 확장

```python
# app/handlers/action_handler.py 확장
class ActionType(str, Enum):
    # 기존 액션들...
    INVESTIGATE = "investigate"
    DIALOGUE = "dialogue"
    TRADE = "trade"
    VISIT = "visit"
    WAIT = "wait"
    MOVE = "move"
    ATTACK = "attack"
    USE_ITEM = "use_item"
    
    # 신규 오브젝트 상호작용 액션들
    EXAMINE_OBJECT = "examine_object"
    OPEN_OBJECT = "open_object"
    CLOSE_OBJECT = "close_object"
    LIGHT_OBJECT = "light_object"
    REST_AT_OBJECT = "rest_at_object"
    EAT_FROM_OBJECT = "eat_from_object"
    PICKUP_FROM_OBJECT = "pickup_from_object"

class ActionHandler:
    def __init__(self, ...):
        # 기존 의존성들...
        self.object_state_manager = ObjectStateManager(...)
        self.inventory_manager = InventoryManager(...)
        
        # 상호작용 핸들러 추가
        self.action_handlers.update({
            ActionType.EXAMINE_OBJECT: self.handle_examine_object,
            ActionType.OPEN_OBJECT: self.handle_open_object,
            ActionType.REST_AT_OBJECT: self.handle_rest_at_object,
            ActionType.PICKUP_FROM_OBJECT: self.handle_pickup_from_object,
            # ...
        })
    
    async def handle_examine_object(self, entity_id: str, target_id: str, ...) -> ActionResult:
        """오브젝트 조사"""
        # ObjectStateManager 사용
        # 결과 반환
    
    async def handle_open_object(self, entity_id: str, target_id: str, ...) -> ActionResult:
        """오브젝트 열기"""
        # ObjectStateManager로 상태 변경
        # 결과 반환
```

### 8.4 구현 단계

#### Phase 1: ObjectStateManager 구현
1. `app/managers/object_state_manager.py` 생성
2. EntityManager와 동일한 패턴 적용
3. 기본 메서드 구현

#### Phase 2: ActionHandler 확장
1. `ActionType`에 오브젝트 상호작용 액션 추가
2. `ActionHandler`에 `ObjectStateManager` 의존성 추가
3. 기본 상호작용 핸들러 구현 (`examine`, `open`, `pickup`)

#### Phase 3: 고급 상호작용 구현
1. 회복 상호작용 (`rest`, `sleep`)
2. 소비 상호작용 (`eat`, `drink`)
3. TimeSystem 연동

#### Phase 4: Effect 시스템 연동
1. EffectCarrierManager 연동
2. 상호작용별 효과 적용

---

## 9. TimeSystem 연동

### 9.1 TimeSystem 인터페이스

```python
# app/systems/time_system.py
class TimeSystem:
    async def advance_time(self, minutes: int) -> None:
        """시간을 지정된 분만큼 진행"""
    
    async def get_current_time(self) -> GameTime:
        """현재 게임 시간 반환"""
    
    async def get_time_period(self) -> TimePeriod:
        """현재 시간대 반환 (dawn, morning, lunch, etc.)"""
```

### 9.2 상호작용에서 시간 소모

```python
# app/handlers/action_handler.py
from app.systems.time_system import TimeSystem

async def handle_rest_at_object(self, entity_id: str, target_id: str, ...) -> ActionResult:
    """오브젝트에서 휴식"""
    # ObjectStateManager로 상태 변경
    state_result = await self.object_state_manager.update_object_state(
        runtime_object_id=runtime_object_id,
        game_object_id=game_object_id,
        session_id=session_id,
        state="rested"
    )
    
    # EntityManager로 HP/MP 회복
    rest_effect = properties.get('interactions', {}).get('rest', {}).get('effects', {})
    hp_regen = rest_effect.get('hp', 0)
    mp_regen = rest_effect.get('mp', 0)
    
    if hp_regen > 0 or mp_regen > 0:
        await self.entity_manager.restore_hp_mp(
            runtime_entity_id=entity_id,
            hp=hp_regen,
            mp=mp_regen
        )
    
    # TimeSystem으로 시간 소모
    time_cost = properties.get('interactions', {}).get('rest', {}).get('time_cost', 0)
    if time_cost > 0:
        time_system = TimeSystem()
        await time_system.advance_time(minutes=time_cost)
    
    return ActionResult.success_result(...)
```

---

## 10. Effect 시스템 연동

### 10.1 EffectCarrierManager 사용

```python
# app/handlers/action_handler.py
from app.managers.effect_carrier_manager import EffectCarrierManager

async def handle_eat_from_object(self, entity_id: str, target_id: str, ...) -> ActionResult:
    """오브젝트에서 먹기"""
    # ObjectStateManager로 상태 변경
    await self.object_state_manager.update_object_state(
        runtime_object_id=runtime_object_id,
        game_object_id=game_object_id,
        session_id=session_id,
        state="consumed"
    )
    
    # EntityManager로 HP 회복
    effects = properties.get('interactions', {}).get('eat', {}).get('effects', {})
    hp_regen = effects.get('hp', 0)
    if hp_regen > 0:
        await self.entity_manager.restore_hp_mp(
            runtime_entity_id=entity_id,
            hp=hp_regen
        )
    
    # EffectCarrierManager로 효과 적용
    effect_carrier_id = properties.get('interactions', {}).get('eat', {}).get('effect_carrier_id')
    if effect_carrier_id:
        await self.effect_carrier_manager.grant_effect_to_entity(
            effect_carrier_id=effect_carrier_id,
            runtime_entity_id=entity_id
        )
    
    # TimeSystem으로 시간 소모
    time_cost = properties.get('interactions', {}).get('eat', {}).get('time_cost', 5)
    if time_cost > 0:
        time_system = TimeSystem()
        await time_system.advance_time(minutes=time_cost)
    
    return ActionResult.success_result(...)
```

---

## 11. Ownership 설계 (소유권 관리)

### 11.1 문제 정의

아이템과의 상호작용에서 두 가지 접근법이 존재:

1. **획득 후 소비 (Acquire then Consume)**: 탁자 위의 빵을 인벤토리로 획득한 후 먹기
2. **직접 상호작용 (Direct Interaction)**: 탁자 위의 빵을 인벤토리 거치지 않고 바로 먹기

### 11.2 비교 분석

| 구분 | 획득 후 소비 | 직접 상호작용 |
|------|------------|--------------|
| **소유권** | 명확 (인벤토리에 존재) | 없음 (즉시 소비) |
| **장점** | 전략적 선택, 나중에 사용 가능, 일관된 시스템 | 직관적, 빠른 UX, 인벤토리 부담 없음, 현실적 |
| **단점** | 복잡한 UX, 인벤토리 부담, 비현실적 | 나중에 사용 불가, 소유권 추적 어려움 |

### 11.3 권장 설계: 하이브리드 접근법

**원칙**: 아이템 타입에 따라 자동 결정 + 플레이어 선택권 제공

#### 아이템 타입별 분류

| 아이템 타입 | 획득 필요 | 직접 상호작용 가능 | 이유 |
|------------|----------|------------------|------|
| **Food/Potion** | ✅ 선택 가능 | ✅ 가능 | 즉시 소비 vs 나중에 사용 |
| **Weapon/Armor** | ✅ 필수 | ❌ 불가 | 소유해야 사용 가능 |
| **Tool** | ✅ 필수 | ❌ 불가 | 소유해야 사용 가능 |
| **Key** | ✅ 필수 | ❌ 불가 | 소유해야 사용 가능 |

#### UX 예시

```
탁자 위에 빵이 있습니다.

[인벤토리에 넣기]  [지금 바로 먹기]  [자세히 보기]
```

- **인벤토리에 넣기**: `pickup_from_object` → 인벤토리로 이동
- **지금 바로 먹기**: `eat_from_object` → 즉시 소비 (인벤토리 거치지 않음)

### 11.4 ActionType 구조

```
# Object Interactions (오브젝트와의 상호작용)
- PICKUP_FROM_OBJECT: 오브젝트에서 아이템 획득 (인벤토리로)
- EAT_FROM_OBJECT: 오브젝트에서 직접 먹기 (인벤토리 거치지 않음)
- DRINK_FROM_OBJECT: 오브젝트에서 직접 마시기

# Item Interactions (아이템과의 상호작용) - 추가 필요
- EAT_ITEM: 인벤토리에서 아이템 먹기
- DRINK_ITEM: 인벤토리에서 아이템 마시기
- USE_ITEM: 인벤토리에서 아이템 사용
- CONSUME_ITEM: 인벤토리에서 아이템 소비
```

### 11.5 구현 예시

```python
async def get_available_actions_for_item(
    self,
    item_id: str,
    item_type: str,
    is_in_inventory: bool,
    is_in_object_contents: bool
) -> List[str]:
    """아이템에 대한 가능한 액션 목록 반환"""
    actions = []
    
    if is_in_object_contents:
        # 오브젝트의 contents에 있는 경우
        if item_type in ["food", "potion", "drink"]:
            actions.extend([
                "pickup_from_object",      # 획득
                "eat_from_object",         # 직접 먹기
                "examine_object"           # 조사
            ])
        else:
            actions.extend([
                "pickup_from_object",      # 획득
                "examine_object"           # 조사
            ])
    
    if is_in_inventory:
        # 인벤토리에 있는 경우
        if item_type in ["food", "potion", "drink"]:
            actions.extend([
                "eat_item",                # 먹기
                "drink_item",              # 마시기
                "use_item",                # 사용
                "drop_item"                # 버리기
            ])
    
    return actions
```

---

## 결론

### 핵심 정리

1. **오브젝트는 고정물**: 셀에 고정된 환경 요소, 자체는 획득 불가
2. **오브젝트의 contents**: 아이템/장비/Effect Carrier ID를 저장
3. **획득 방법**: 오브젝트의 `properties.contents`에서 ID 추출 → 해당 타입에 맞는 인스턴스 생성 → 엔티티에 추가
4. **ID 형식**:
   - 아이템: `ITEM_*`
   - 장비: `WEAPON_*`, `ARMOR_*`
   - Effect Carrier: UUID

### Ownership 설계 결론

1. **소비 가능 아이템 (food, potion)**: 플레이어 선택권 제공
   - ✅ **직접 상호작용 가능**: 즉시 소비하고 싶을 때 (`eat_from_object`)
   - ✅ **획득 후 소비 가능**: 나중에 사용하고 싶을 때 (`pickup_from_object` → `eat_item`)
   - **권장**: 플레이어가 선택

2. **장비 아이템 (weapon, armor)**: 반드시 획득 필요
   - ✅ **반드시 획득 필요**: 인벤토리로만 이동 (`pickup_from_object`)
   - ❌ **직접 상호작용 불가**: 장비는 소유해야 사용 가능

3. **도구 아이템 (tool)**: 획득 후 사용
   - ✅ **획득 후 사용**: 인벤토리에서 사용 (`pickup_from_object` → `use_item`)
   - ❌ **직접 상호작용 불가**: 도구는 소유해야 사용 가능

### 권장 아키텍처

- ✅ **ActionHandler 확장**: 기존 구조와 일관성 유지
- ✅ **ObjectStateManager 생성**: 오브젝트 상태 관리 중앙화
- ✅ **EntityManager 확장**: HP/MP 회복 메서드 추가
- ✅ **카테고리별 핸들러 분리**: 모듈화 및 확장성 향상
- ✅ **하이브리드 Ownership**: 획득 후 소비 + 직접 상호작용 모두 지원
- ❌ **Factory 패턴 사용 안 함**: 객체 생성용이므로 부적합

### 다음 단계

1. **Item Interactions 핸들러 추가** (우선순위: 높음)
   - `EAT_ITEM`, `DRINK_ITEM`, `CONSUME_ITEM` 구현
   - 인벤토리 아이템과의 직접 상호작용 지원

2. **아이템 타입 기반 액션 필터링**
   - 아이템 타입에 따라 가능한 액션 자동 결정
   - 플레이어 선택 UI 구현

3. **기본 상호작용 리팩토링** (open, light, pickup)
4. **회복 상호작용 구현** (rest, sleep)
5. **소비 상호작용 구현** (eat, drink, read)
6. **제작 상호작용 구현** (combine, craft)

