# Cell Properties 명세서

**작성일**: 2025-01-XX  
**프로젝트**: RPG Engine - World Editor  
**버전**: v1.0.0

## 📋 개요

Cell Properties는 게임 내 셀(방)의 다양한 환경적, 게임플레이적 특성을 정의하는 JSONB 구조입니다. 이 명세서는 게임 디자이너가 셀의 모든 특성을 체계적으로 관리할 수 있도록 설계되었습니다.

## 🎯 설계 원칙

1. **확장성**: 새로운 속성을 쉽게 추가할 수 있어야 함
2. **타입 안전성**: 각 속성의 타입이 명확히 정의되어야 함
3. **게임플레이 연동**: 실제 게임 로직에서 활용 가능해야 함
4. **디자이너 친화적**: 직관적이고 이해하기 쉬운 구조

## 📊 Cell Properties 구조

### 전체 구조

```json
{
  "environment": {
    "temperature": 20.0,
    "humidity": 50.0,
    "air_quality": "fresh",
    "visibility": 100.0,
    "gravity": 1.0
  },
  "terrain": {
    "type": "stone",
    "elevation": 0.0,
    "water_level": 0.0,
    "obstacles": []
  },
  "lighting": {
    "level": "bright",
    "source": "torch",
    "color_temperature": 3000,
    "flicker": false
  },
  "weather": {
    "type": "clear",
    "intensity": 0.0,
    "wind_speed": 0.0,
    "precipitation": "none"
  },
  "gameplay": {
    "spawn_points": [],
    "safe_zones": [],
    "danger_zones": [],
    "interaction_zones": [],
    "restricted_areas": []
  },
  "atmosphere": {
    "ambiance": "peaceful",
    "music": "village_01",
    "sound_effects": [],
    "background_noise": "quiet"
  },
  "special": {
    "portals": [],
    "teleport_points": [],
    "hidden_areas": [],
    "locked_doors": [],
    "traps": []
  }
}
```

## 🔍 상세 속성 정의

### 1. Environment (환경)

셀의 물리적 환경 조건을 정의합니다.

| 속성 | 타입 | 기본값 | 설명 | 예시 |
|------|------|-------|------|------|
| `temperature` | number | 20.0 | 온도 (섭씨) | 20.0 (실내), -5.0 (외부 겨울) |
| `humidity` | number | 50.0 | 습도 (0-100%) | 50.0 (보통), 90.0 (습한 동굴) |
| `air_quality` | string | "normal" | 공기 질 | "fresh", "stale", "toxic", "normal" |
| `visibility` | number | 100.0 | 가시거리 (0-100%) | 100.0 (명확), 30.0 (안개) |
| `gravity` | number | 1.0 | 중력 배율 | 1.0 (정상), 0.5 (낮은 중력) |

**air_quality 값:**
- `"fresh"`: 신선한 공기 (야외, 환기된 실내)
- `"normal"`: 일반적인 공기 (대부분의 실내)
- `"stale"`: 탁한 공기 (밀폐된 공간)
- `"toxic"`: 독성 공기 (독가스 지역)

### 2. Terrain (지형)

셀의 지형적 특성을 정의합니다.

| 속성 | 타입 | 기본값 | 설명 | 예시 |
|------|------|-------|------|------|
| `type` | string | "stone" | 지형 타입 | "stone", "wooden_floor", "dirt", "grass" |
| `elevation` | number | 0.0 | 고도 (미터) | 0.0 (평지), 5.0 (언덕) |
| `water_level` | number | 0.0 | 수위 (0-100%) | 0.0 (건조), 50.0 (물웅덩이), 100.0 (물속) |
| `obstacles` | array | [] | 장애물 목록 | `[{"type": "rock", "position": {"x": 5, "y": 5}}]` |

**terrain.type 값:**
- `"stone"`: 돌바닥 (광장, 성 내부)
- `"wooden_floor"`: 나무 바닥 (집, 상점)
- `"dirt"`: 흙바닥 (야외, 농장)
- `"grass"`: 잔디 (야외, 정원)
- `"sand"`: 모래 (사막, 해변)
- `"snow"`: 눈 (겨울 지역)
- `"water"`: 물 (호수, 강)
- `"lava"`: 용암 (화산 지역)

**water_level 설명:**
- `0.0`: 완전히 건조
- `1-49`: 물웅덩이, 얕은 물
- `50-99`: 깊은 물 (수영 가능)
- `100.0`: 완전히 물에 잠김

### 3. Lighting (조명)

셀의 조명 상태를 정의합니다.

| 속성 | 타입 | 기본값 | 설명 | 예시 |
|------|------|-------|------|------|
| `level` | string | "moderate" | 조명 수준 | "bright", "moderate", "dim", "dark" |
| `source` | string | null | 조명원 | "torch", "lantern", "window", "magic" |
| `color_temperature` | number | 3000 | 색온도 (켈빈) | 3000 (따뜻한 빛), 6500 (차가운 빛) |
| `flicker` | boolean | false | 깜빡임 여부 | true (횃불), false (안정적) |

**lighting.level 값:**
- `"bright"`: 밝음 (낮, 강한 조명)
- `"moderate"`: 보통 (일반 실내)
- `"dim"`: 어둡음 (약한 조명)
- `"dark"`: 어둠 (조명 없음)

**lighting.source 값:**
- `"torch"`: 횃불
- `"lantern"`: 등불
- `"window"`: 창문 (자연광)
- `"magic"`: 마법 조명
- `"fireplace"`: 벽난로
- `null`: 조명원 없음

### 4. Weather (날씨)

셀의 날씨 상태를 정의합니다. (주로 외부 셀에 적용)

| 속성 | 타입 | 기본값 | 설명 | 예시 |
|------|------|-------|------|------|
| `type` | string | "clear" | 날씨 타입 | "clear", "rain", "snow", "fog" |
| `intensity` | number | 0.0 | 강도 (0-100%) | 0.0 (없음), 50.0 (보통), 100.0 (강함) |
| `wind_speed` | number | 0.0 | 풍속 (m/s) | 0.0 (무풍), 10.0 (강한 바람) |
| `precipitation` | string | "none" | 강수 형태 | "none", "rain", "snow", "hail" |

**weather.type 값:**
- `"clear"`: 맑음
- `"cloudy"`: 흐림
- `"rain"`: 비
- `"snow"`: 눈
- `"fog"`: 안개
- `"storm"`: 폭풍

### 5. Gameplay (게임플레이)

게임플레이 관련 특수 영역을 정의합니다.

| 속성 | 타입 | 기본값 | 설명 | 예시 |
|------|------|-------|------|------|
| `spawn_points` | array | [] | 스폰 포인트 목록 | `[{"id": "spawn_1", "position": {"x": 10, "y": 10}, "type": "player"}]` |
| `safe_zones` | array | [] | 안전 지역 목록 | `[{"area": {"x": 0, "y": 0, "width": 10, "height": 10}}]` |
| `danger_zones` | array | [] | 위험 지역 목록 | `[{"area": {"x": 5, "y": 5, "width": 5, "height": 5}, "damage_per_second": 10}]` |
| `interaction_zones` | array | [] | 상호작용 영역 목록 | `[{"area": {"x": 15, "y": 15, "width": 2, "height": 2}, "type": "chest"}]` |
| `restricted_areas` | array | [] | 제한된 영역 목록 | `[{"area": {"x": 0, "y": 0, "width": 5, "height": 5}, "reason": "locked"}]` |

**spawn_points 구조:**
```json
{
  "id": "spawn_1",
  "position": {"x": 10, "y": 10, "z": 0},
  "type": "player" | "npc" | "enemy" | "item",
  "facing": {"x": 1, "y": 0, "z": 0}
}
```

**danger_zones 구조:**
```json
{
  "area": {"x": 5, "y": 5, "width": 5, "height": 5},
  "damage_per_second": 10,
  "damage_type": "fire" | "poison" | "cold" | "electric",
  "effect": "burning" | "poisoned" | "frozen" | "shocked"
}
```

### 6. Atmosphere (분위기)

셀의 오디오 및 분위기 설정을 정의합니다.

| 속성 | 타입 | 기본값 | 설명 | 예시 |
|------|------|-------|------|------|
| `ambiance` | string | "neutral" | 분위기 | "peaceful", "tense", "mysterious" |
| `music` | string | null | 배경음악 ID | "village_01", "dungeon_01" |
| `sound_effects` | array | [] | 사운드 이펙트 목록 | `["water_dripping", "wind_howling"]` |
| `background_noise` | string | "quiet" | 배경 소음 레벨 | "quiet", "moderate", "loud" |

**ambiance 값:**
- `"peaceful"`: 평화로운
- `"tense"`: 긴장된
- `"mysterious"`: 신비로운
- `"dangerous"`: 위험한
- `"neutral"`: 중립적

**background_noise 값:**
- `"quiet"`: 조용함
- `"moderate"`: 보통
- `"loud"`: 시끄러움

### 7. Special (특수 기능)

셀의 특수 기능 및 포털 등을 정의합니다.

| 속성 | 타입 | 기본값 | 설명 | 예시 |
|------|------|-------|------|------|
| `portals` | array | [] | 포털 목록 | `[{"id": "portal_1", "target_cell_id": "CELL_OTHER_001", "position": {"x": 10, "y": 10}}]` |
| `teleport_points` | array | [] | 텔레포트 포인트 목록 | `[{"id": "tp_1", "position": {"x": 5, "y": 5}}]` |
| `hidden_areas` | array | [] | 숨겨진 영역 목록 | `[{"area": {"x": 0, "y": 0, "width": 3, "height": 3}, "discovery_method": "search"}]` |
| `locked_doors` | array | [] | 잠긴 문 목록 | `[{"door_id": "door_1", "key_id": "key_001", "position": {"x": 10, "y": 10}}]` |
| `traps` | array | [] | 함정 목록 | `[{"id": "trap_1", "position": {"x": 15, "y": 15}, "type": "pressure_plate", "damage": 20}]` |

## 📝 사용 예시

### 예시 1: 평범한 마을 집 내부
```json
{
  "environment": {
    "temperature": 22.0,
    "humidity": 40.0,
    "air_quality": "normal",
    "visibility": 100.0,
    "gravity": 1.0
  },
  "terrain": {
    "type": "wooden_floor",
    "elevation": 0.0,
    "water_level": 0.0,
    "obstacles": []
  },
  "lighting": {
    "level": "moderate",
    "source": "window",
    "color_temperature": 3000,
    "flicker": false
  },
  "weather": {
    "type": "clear",
    "intensity": 0.0,
    "wind_speed": 0.0,
    "precipitation": "none"
  },
  "gameplay": {
    "spawn_points": [],
    "safe_zones": [{"area": {"x": 0, "y": 0, "width": 20, "height": 20}}],
    "danger_zones": [],
    "interaction_zones": [],
    "restricted_areas": []
  },
  "atmosphere": {
    "ambiance": "peaceful",
    "music": "village_01",
    "sound_effects": [],
    "background_noise": "quiet"
  },
  "special": {
    "portals": [],
    "teleport_points": [],
    "hidden_areas": [],
    "locked_doors": [],
    "traps": []
  }
}
```

### 예시 2: 위험한 던전 셀
```json
{
  "environment": {
    "temperature": 15.0,
    "humidity": 80.0,
    "air_quality": "stale",
    "visibility": 50.0,
    "gravity": 1.0
  },
  "terrain": {
    "type": "stone",
    "elevation": -2.0,
    "water_level": 10.0,
    "obstacles": [{"type": "rock", "position": {"x": 5, "y": 5}}]
  },
  "lighting": {
    "level": "dim",
    "source": "torch",
    "color_temperature": 2000,
    "flicker": true
  },
  "weather": {
    "type": "clear",
    "intensity": 0.0,
    "wind_speed": 0.0,
    "precipitation": "none"
  },
  "gameplay": {
    "spawn_points": [{"id": "enemy_spawn_1", "position": {"x": 10, "y": 10}, "type": "enemy"}],
    "safe_zones": [],
    "danger_zones": [{"area": {"x": 0, "y": 0, "width": 5, "height": 5}, "damage_per_second": 5, "damage_type": "poison"}],
    "interaction_zones": [{"area": {"x": 15, "y": 15, "width": 2, "height": 2}, "type": "chest"}],
    "restricted_areas": []
  },
  "atmosphere": {
    "ambiance": "dangerous",
    "music": "dungeon_01",
    "sound_effects": ["water_dripping", "distant_groan"],
    "background_noise": "moderate"
  },
  "special": {
    "portals": [],
    "teleport_points": [],
    "hidden_areas": [{"area": {"x": 0, "y": 0, "width": 3, "height": 3}, "discovery_method": "search"}],
    "locked_doors": [{"door_id": "door_1", "key_id": "key_001", "position": {"x": 10, "y": 10}}],
    "traps": [{"id": "trap_1", "position": {"x": 15, "y": 15}, "type": "pressure_plate", "damage": 20}]
  }
}
```

## 🔧 API 명세

### GET /api/cells/{cell_id}/properties
셀의 properties를 조회합니다.

**응답:**
```json
{
  "cell_id": "CELL_VILLAGE_CENTER_001",
  "properties": { ... }
}
```

### PUT /api/cells/{cell_id}/properties
셀의 properties를 업데이트합니다.

**요청 본문:**
```json
{
  "properties": { ... }
}
```

**응답:**
```json
{
  "cell_id": "CELL_VILLAGE_CENTER_001",
  "properties": { ... },
  "updated_at": "2025-01-XX..."
}
```

## 📌 참고사항

1. 모든 속성은 선택적(optional)입니다. 필요한 속성만 정의하면 됩니다.
2. 배열 속성은 빈 배열 `[]`로 초기화할 수 있습니다.
3. 숫자 속성은 범위 검증이 필요할 수 있습니다 (예: humidity는 0-100).
4. 문자열 속성은 enum 값으로 제한하는 것이 좋습니다.
5. 게임 로직에서 properties를 읽을 때는 항상 기본값을 고려해야 합니다.

