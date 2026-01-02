# Location 및 Cell Properties 확장 명세서

**작성일**: 2025-01-XX  
**프로젝트**: RPG Engine - World Editor  
**버전**: v1.0.0

## 📋 개요

이 문서는 Location(방문 가능한 구체적 장소)과 Cell(실질적 공간)의 Properties JSONB 구조 확장 명세입니다.  
기존 구현과 중복되지 않도록, **추가로 필요한 속성들만** 정의합니다.

### 참고 문서
- **Cell Properties 기본 명세**: `docs/world-editor/51_cell_properties_specification.md` (이미 구현됨)
- **Region Properties**: `region_properties`의 `dnd_structured_info`, `detail_sections`, `lore` 구조 (이미 구현됨)

### 현재 구현 상태
- ✅ Cell Properties: `environment`, `terrain`, `lighting`, `weather`, `gameplay`, `atmosphere`, `special` 구조 정의됨
- ✅ Cell Properties API: `GET/PUT /api/cells/{cell_id}/properties` 구현됨
- ✅ Location Properties: `background_music`, `ambient_effects` 사용 중
- ✅ Region Properties: `dnd_structured_info`, `detail_sections`, `lore` 구조 구현됨
- ✅ Cell 컬럼: `cell_status`, `cell_type` 컬럼 존재

---

## 🏛️ Location Properties 확장 구조

Location은 **방문 가능한 구체적 장소**입니다 (시장, 건널목, 마을, 광장, 던전 입구 등).

### 현재 구현된 속성
```json
{
  "background_music": "peaceful_01",
  "ambient_effects": ["birds", "wind"]
}
```

### 추가해야 할 속성

#### 1. 접근성 및 운영 정보 (`accessibility`, `operating_hours`)
```json
{
  "accessibility": {
    "is_public": true,
    "requires_key": false,
    "key_item_id": null,
    "requires_permission": null,
    "access_conditions": [],
    "entry_points": [
      {"direction": "north", "cell_id": "CELL_MARKET_ENTRANCE_001"},
      {"direction": "south", "cell_id": "CELL_MARKET_EXIT_001"}
    ]
  },
  "operating_hours": {
    "is_always_open": false,
    "open_time": "06:00",
    "close_time": "22:00",
    "closed_days": [],
    "seasonal_hours": {}
  }
}
```

**속성 설명:**
- `accessibility.is_public`: 공개 장소 여부
- `accessibility.requires_key`: 열쇠 필요 여부
- `accessibility.key_item_id`: 필요한 열쇠 아이템 ID
- `accessibility.requires_permission`: 필요한 권한 (예: "guild_member")
- `accessibility.access_conditions`: 접근 조건 목록
- `accessibility.entry_points`: 진입 지점 (방향, cell_id)
- `operating_hours.is_always_open`: 항상 개방 여부
- `operating_hours.open_time` / `close_time`: 운영 시간 (HH:MM 형식)
- `operating_hours.closed_days`: 휴무일 목록
- `operating_hours.seasonal_hours`: 계절별 운영 시간

#### 2. 서비스 및 기능 (`services`)
```json
{
  "services": {
    "available_services": ["shop", "inn", "blacksmith", "temple", "guild_hall"],
    "trading_post": {
      "enabled": true,
      "buy_modifier": 1.0,
      "sell_modifier": 0.8
    }
  }
}
```

**속성 설명:**
- `services.available_services`: 제공되는 서비스 목록
- `services.trading_post`: 거래소 설정 (활성화 여부, 구매/판매 가격 수정자)

**⚠️ 이미 구현됨**: 서비스 제공자 NPC는 `entities` 테이블로 관리됩니다.
- API: `GET /api/entities/location/{location_id}` (`entitiesApi.getByLocation(locationId)`)
- 프론트엔드: `PinEditorNew`에서 이미 사용 중
- NPC 정보: `entity_id`, `entity_name`, `entity_properties.occupation` 등은 `entities` 테이블에 저장됨

#### 3. NPC 및 인물 정보 (`npcs`)

**⚠️ 이미 구현됨**: NPC는 `entities` 테이블로 관리됩니다.
- API: `GET /api/entities/location/{location_id}` (`entitiesApi.getByLocation(locationId)`)
- 프론트엔드: `PinEditorNew`에서 이미 사용 중
- NPC 정보: `entity_id`, `entity_name`, `entity_properties.occupation`, `entity_properties.role` 등은 `entities` 테이블에 저장됨

**추가 메타데이터만 필요:**
```json
{
  "npcs": {
    "population_density": "high",
    "npc_spawn_rules": {
      "max_npcs": 20,
      "spawn_types": ["merchant", "guard", "citizen"],
      "spawn_schedule": "daytime"
    }
  }
}
```

**속성 설명:**
- `npcs.population_density`: 인구 밀도 ("low", "medium", "high")
- `npcs.npc_spawn_rules`: NPC 스폰 규칙 (최대 수, 스폰 타입, 스폰 일정)

**참고**: 실제 NPC 목록은 `entitiesApi.getByLocation(locationId)`로 조회하세요.

#### 4. 이벤트 및 퀘스트 (`events`, `quests`)
```json
{
  "events": {
    "scheduled_events": [
      {"event_id": "EVENT_MARKET_DAY", "schedule": "weekly", "day": "sunday"}
    ],
    "random_events": [
      {"event_id": "EVENT_THIEF", "probability": 0.1}
    ]
  },
  "quests": {
    "available_quests": ["QUEST_DELIVERY_001"],
    "quest_givers": ["NPC_MERCHANT_001"]
  }
}
```

**속성 설명:**
- `events.scheduled_events`: 예정된 이벤트 목록
- `events.random_events`: 랜덤 이벤트 목록 (확률 포함)
- `quests.available_quests`: 사용 가능한 퀘스트 ID 목록
- `quests.quest_givers`: 퀘스트 제공자 NPC ID 목록

#### 5. 로어 및 역사 (`lore`)
```json
{
  "lore": {
    "history": "이 시장은 200년 전에 세워졌다...",
    "legends": ["유명한 상인들의 전설", "보물의 전설"],
    "secrets": ["지하 비밀 통로", "숨겨진 상점"],
    "notable_events": ["대화재", "전쟁"]
  }
}
```

**참고**: Region의 `lore` 구조와 동일합니다.

#### 6. 연결성 및 이동 (`connections`)

**⚠️ 이미 구현됨**: Location 간 연결은 `world_roads` 테이블로 관리됩니다.
- 테이블: `game_data.world_roads`
- 컬럼: `from_location_id`, `to_location_id`, `distance`, `travel_time`
- API: `GET /api/roads` (`roadsApi.getAll()`)

**추가 메타데이터만 필요:**
```json
{
  "connections": {
    "transportation": {
      "has_stable": true,
      "has_portal": false
    }
  }
}
```

**속성 설명:**
- `connections.transportation.has_stable`: 마구간 존재 여부
- `connections.transportation.has_portal`: 포털 존재 여부

**참고**: 
- 실제 Location 간 연결은 `world_roads` 테이블에서 `from_location_id` 또는 `to_location_id`로 조회하세요.
- 텔레포트 포인트는 Cell Properties의 `special.teleport_points`로 관리됩니다.

#### 7. 주인 및 소유권 (`ownership`)
```json
{
  "ownership": {
    "owner_entity_id": null,
    "ownership_type": "public",
    "faction_control": null,
    "tax_rate": 0.05
  }
}
```

**속성 설명:**
- `ownership.owner_entity_id`: 주인 NPC 엔티티 ID (참조만 저장)
- `ownership.ownership_type`: 소유 형태 ("public", "private", "guild", "government")
- `ownership.faction_control`: 통제하는 파벌 ID
- `ownership.tax_rate`: 세율 (0.0 ~ 1.0)

**⚠️ SSOT 준수**: `owner_name`은 저장하지 않습니다. API에서 `owner_entity_id`로 JOIN하여 `entities` 테이블에서 조회합니다.
- 이유: 엔티티 이름 변경 시 동기화 문제 방지
- API 응답: `GET /api/locations/{location_id}`에서 `owner_name` 필드 포함 (JOIN으로 해결)
- 상세: [SSOT 분석 문서](./54_location_cell_properties_ssot_analysis.md) 참조

#### 8. 텍스트 섹션 (`detail_sections`)
```json
{
  "detail_sections": [
    {
      "title": "시장의 특징",
      "content": "이 시장은 다양한 상품을 판매한다...",
      "category": "description"
    },
    {
      "title": "주요 상점",
      "content": "무기 상점, 방어구 상점, 물약 상점이 있다...",
      "category": "services"
    }
  ]
}
```

**참고**: Region의 `detail_sections` 구조와 동일합니다.

#### 9. 게임플레이 설정 (`gameplay`)
```json
{
  "gameplay": {
    "danger_level": 1,
    "recommended_level": {"min": 1, "max": 5},
    "pvp_enabled": false,
    "safe_zone": true,
    "respawn_point": true,
    "rest_area": true
  }
}
```

**속성 설명:**
- `gameplay.danger_level`: 위험도 (1-10)
- `gameplay.recommended_level`: 권장 레벨 범위
- `gameplay.pvp_enabled`: PvP 활성화 여부
- `gameplay.safe_zone`: 안전 지역 여부
- `gameplay.respawn_point`: 리스폰 포인트 여부
- `gameplay.rest_area`: 휴식 지역 여부

---

## 🏠 Cell Properties 확장 구조

Cell은 Location **안에 있는 실질적 공간**입니다 (방, 구역 등).

### 현재 구현된 속성
기존 명세서(`docs/world-editor/51_cell_properties_specification.md`)에 다음 구조가 정의되어 있습니다:
- `environment`: 온도, 습도, 공기 질, 가시거리, 중력
- `terrain`: 지형 타입, 고도, 수위, 장애물
- `lighting`: 조명 수준, 조명원, 색온도, 깜빡임
- `weather`: 날씨 타입, 강도, 풍속, 강수
- `gameplay`: 스폰 포인트, 안전/위험 지역, 상호작용 영역, 제한 영역
- `atmosphere`: 분위기, 배경음악, 사운드 이펙트, 배경 소음
- `special`: 포털, 텔레포트 포인트, 숨겨진 영역, 잠긴 문, 함정

**현재 사용 중인 속성:**
- `terrain` (단순 문자열): 프론트엔드에서 `cell_properties.terrain` 사용
- `weather` (단순 문자열): 프론트엔드에서 `cell_properties.weather` 사용

### 추가해야 할 속성

**⚠️ 이미 구현된 것:**
- Cell에 배치된 오브젝트: `world_objects` 테이블의 `default_cell_id`로 관리
  - API: `GET /api/world-objects/cell/{cell_id}`
  - 프론트엔드: `worldObjectsApi.getByCell(cellId)` 사용 중
- Cell에 배치된 엔티티: `entities` 테이블의 `default_position_3d.cell_id`로 관리
  - API: `GET /api/entities/cell/{cell_id}`
  - 프론트엔드: `entitiesApi.getByCell(cellId)` 사용 중

#### 1. 공간 구조 및 통로 (`structure`)
```json
{
  "structure": {
    "exits": [
      {"direction": "north", "cell_id": "CELL_CORRIDOR_001", "requires_key": false},
      {"direction": "east", "cell_id": "CELL_STORAGE_001", "requires_key": true, "key_item_id": "ITEM_KEY_STORAGE_001"}
    ],
    "entrances": [
      {"direction": "south", "cell_id": "CELL_LOBBY_001"}
    ],
    "connections": [
      {"cell_id": "CELL_ADJACENT_001", "connection_type": "door", "is_locked": false}
    ],
    "barriers": [
      {"type": "wall", "position": {"x": 10, "y": 0}, "direction": "north"}
    ]
  }
}
```

**속성 설명:**
- `structure.exits`: 출구 목록 (방향, 연결된 셀 ID, 열쇠 필요 여부)
- `structure.entrances`: 입구 목록 (방향, 연결된 셀 ID)
- `structure.connections`: 연결된 셀 목록 (연결 타입, 잠금 여부)
- `structure.barriers`: 장벽 목록 (타입, 위치, 방향)

**참고**: 기존 `special.locked_doors`와 통합 고려 필요.

#### 2. 오브젝트 배치 및 상호작용 (`objects`)

**⚠️ 이미 구현됨**: Cell에 배치된 오브젝트는 `world_objects` 테이블의 `default_cell_id`로 관리됩니다.
- API: `GET /api/world-objects/cell/{cell_id}` (`worldObjectsApi.getByCell(cellId)`)
- 프론트엔드: `CellEditorModal`에서 이미 사용 중
- 오브젝트 정보: `object_id`, `object_name`, `default_position`, `interaction_type` 등은 `world_objects` 테이블에 저장됨

**추가 고려사항:**
- `interaction_zones`: 게임플레이용 상호작용 영역 (기존 `gameplay.interaction_zones`와 통합 고려)
```json
{
  "objects": {
    "interaction_zones": [
      {"type": "crafting", "position": {"x": 2, "y": 2}, "radius": 2},
      {"type": "rest", "position": {"x": 5, "y": 5}, "radius": 1}
    ]
  }
}
```

**참고**: 실제 오브젝트 목록은 `worldObjectsApi.getByCell(cellId)`로 조회하세요.

#### 2. 로어 및 비밀 (`lore`)
```json
{
  "lore": {
    "history": "이 방은 과거에 창고로 사용되었다...",
    "legends": ["유령이 나타난다는 전설"],
    "secrets": [
      {"type": "hidden_door", "position": {"x": 15, "y": 10}, "reveal_condition": "search"},
      {"type": "hidden_chest", "position": {"x": 8, "y": 12}, "reveal_condition": "perception_check"}
    ]
  }
}
```

**속성 설명:**
- `lore.history`: 방의 역사/과거 사용
- `lore.legends`: 관련 전설/이야기
- `lore.secrets`: 숨겨진 정보/비밀 (타입, 위치, 발견 조건)

**참고**: Region의 `lore` 구조와 유사하지만, Cell은 위치 정보가 포함된 `secrets`를 가집니다.

#### 3. 주인 및 소유권 (`ownership`)
```json
{
  "ownership": {
    "owner_entity_id": "NPC_MERCHANT_001",
    "is_private": false,
    "access_restrictions": {
      "requires_key": false,
      "requires_permission": null,
      "allowed_entities": []
    }
  }
}
```

**속성 설명:**
- `ownership.owner_entity_id`: 주인 NPC 엔티티 ID (참조만 저장)
- `ownership.is_private`: 사적 공간 여부
- `ownership.access_restrictions`: 접근 제한 (열쇠 필요, 권한 필요, 허용된 엔티티 목록)

**⚠️ SSOT 준수**: `owner_name`은 저장하지 않습니다. API에서 `owner_entity_id`로 JOIN하여 `entities` 테이블에서 조회합니다.
- 이유: 엔티티 이름 변경 시 동기화 문제 방지
- API 응답: `GET /api/cells/{cell_id}`에서 `owner_name` 필드 포함 (JOIN으로 해결)
- 상세: [SSOT 분석 문서](./54_location_cell_properties_ssot_analysis.md) 참조

#### 4. 텍스트 섹션 (`detail_sections`)
```json
{
  "detail_sections": [
    {
      "title": "방의 특징",
      "content": "큰 창문이 있어 밝다...",
      "category": "description"
    },
    {
      "title": "주요 가구",
      "content": "책상, 의자, 책장이 배치되어 있다...",
      "category": "furniture"
    }
  ]
}
```

**참고**: Region의 `detail_sections` 구조와 동일합니다.

#### 5. 방 특성 (`room_features`)

**⚠️ 이미 구현됨**: 
- 가구/오브젝트: `world_objects` 테이블의 `default_cell_id`로 관리
  - API: `GET /api/world-objects/cell/{cell_id}` (`worldObjectsApi.getByCell(cellId)`)
- 함정, 숨겨진 문: Cell Properties의 `special.traps`, `special.hidden_areas`로 관리
- 포털: Cell Properties의 `special.portals`로 관리

**추가 메타데이터만 필요:**
```json
{
  "room_features": {
    "features": ["fireplace", "window"],
    "decorations": ["painting", "vase", "candle"],
    "special_properties": {
      "is_magical": false,
      "is_haunted": false
    }
  }
}
```

**속성 설명:**
- `room_features.features`: 방 특징 목록 (벽난로, 창문 등 - 오브젝트가 아닌 환경적 특징)
- `room_features.decorations`: 장식품 목록 (오브젝트가 아닌 메타데이터)
- `room_features.special_properties`: 특수 속성 (마법적, 유령 출몰 등)

**참고**: 
- 실제 가구/오브젝트는 `worldObjectsApi.getByCell(cellId)`로 조회하세요.
- 함정, 숨겨진 문은 Cell Properties의 `special.traps`, `special.hidden_areas`로 관리됩니다.
- 포털은 Cell Properties의 `special.portals`로 관리됩니다.

---

## 🔄 기존 구현과의 통합

### 1. Cell Properties의 `terrain` 및 `weather` 통합
**현재 상태:**
- 프론트엔드에서 `cell_properties.terrain` (문자열) 사용
- 프론트엔드에서 `cell_properties.weather` (문자열) 사용

**권장 사항:**
- 기존 명세서의 `terrain.type` 및 `weather.type`과 통합
- 마이그레이션: `terrain` → `terrain.type`, `weather` → `weather.type`

### 2. Cell Properties의 `special` 통합
**기존 명세서에 정의된 속성:**
- `special.locked_doors`: 잠긴 문 목록

**추가 속성:**
- `structure.exits`: 출구 목록 (잠금 정보 포함)

**권장 사항:**
- `special.locked_doors`와 `structure.exits`의 잠금 정보 통합 고려

### 3. Cell Properties의 `gameplay` 통합
**기존 명세서에 정의된 속성:**
- `gameplay.interaction_zones`: 상호작용 영역 목록

**추가 속성:**
- `objects.interaction_zones`: 상호작용 영역 목록 (게임플레이용 특수 영역)

**권장 사항:**
- `gameplay.interaction_zones`와 `objects.interaction_zones`는 역할이 다름
  - `gameplay.interaction_zones`: 게임플레이 메커니즘용 (제작대, 휴식 지점 등)
  - 실제 오브젝트 목록은 `worldObjectsApi.getByCell(cellId)`로 조회

---

## 📝 데이터베이스 스키마 주석 업데이트

### Location Properties 주석 업데이트
```sql
COMMENT ON COLUMN game_data.world_locations.location_properties IS 
'JSONB 구조: {
  "background_music": "peaceful_01",
  "ambient_effects": ["birds", "wind"],
  "accessibility": {...},
  "operating_hours": {...},
  "services": {...},
  "npcs": {...},
  "events": {...},
  "quests": {...},
  "lore": {...},
  "connections": {...},
  "ownership": {...},
  "detail_sections": [...],
  "gameplay": {...}
}';
```

### Cell Properties 주석 업데이트
```sql
COMMENT ON COLUMN game_data.world_cells.cell_properties IS 
'JSONB 구조: {
  "environment": {...},
  "terrain": {...},
  "lighting": {...},
  "weather": {...},
  "gameplay": {...},
  "atmosphere": {...},
  "special": {...},
  "structure": {...},
  "objects": {...},
  "lore": {...},
  "ownership": {...},
  "detail_sections": [...],
  "room_features": {...}
}
상세 명세는 docs/world-editor/51_cell_properties_specification.md 참조';
```

---

## 🎯 구현 우선순위

### High Priority
1. ✅ **접근성 및 운영 정보** (Location) - 게임플레이 필수
2. ✅ **서비스 및 기능** (Location) - 게임플레이 필수
3. ✅ **공간 구조 및 통로** (Cell) - 게임플레이 필수
4. ✅ **로어 및 역사** (Location, Cell) - 스토리텔링 필수
5. ✅ **텍스트 섹션** (Location, Cell) - 정보 표시 필수

### Medium Priority
6. **NPC 및 인물 정보** (Location) - 게임플레이 중요
7. **이벤트 및 퀘스트** (Location) - 게임플레이 중요
8. **주인 및 소유권** (Location, Cell) - 게임플레이 중요

**참고**: Cell의 오브젝트 배치는 이미 `world_objects` 테이블로 관리되므로 추가 구현 불필요

### Low Priority
10. **연결성 및 이동** (Location) - 편의 기능
11. **방 특성** (Cell) - 편의 기능
12. **게임플레이 설정** (Location, Cell) - 고급 기능

---

## 📌 참고사항

1. **모든 속성은 선택적(optional)**입니다. 필요한 속성만 정의하면 됩니다.
2. **기존 데이터와의 호환성**: 기존 `terrain`, `weather` (문자열)는 유지하되, 새로운 구조로 확장 가능합니다.
3. **Region과의 일관성**: `lore`, `detail_sections` 구조는 Region과 동일하게 유지합니다.
4. **API 호환성**: 기존 `GET/PUT /api/cells/{cell_id}/properties` API는 그대로 사용 가능합니다.
5. **Location Properties API**: Location에도 `GET/PUT /api/locations/{location_id}/properties` API 추가 권장.

## ⚠️ SSOT (Single Source of Truth) 준수

이 명세는 SSOT 원칙을 준수합니다. 상세한 위험성 분석과 구현 계획은 다음 문서를 참조하세요:
- **[SSOT 분석 및 구현 계획](./54_location_cell_properties_ssot_analysis.md)**

### 주요 SSOT 원칙
1. **참조는 ID만 저장**: Properties에 저장되는 참조는 ID만 저장하고, 이름/설명은 원본 테이블에서 조회
2. **캐시된 데이터 제거**: `owner_name` 같은 캐시된 데이터는 저장하지 않음
3. **삭제 시 검증**: 참조된 엔티티/Cell 삭제 시 검증 로직 실행
4. **API에서 JOIN**: 읽기 시 참조를 해결하여 반환

