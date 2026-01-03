# 게임 데이터 제작 가이드라인

> **최신화 날짜**: 2026-01-03  
> **적용 범위**: 게임 데이터 제작 및 수정 시 필수 읽기

## ⚠️ 중요: mvp_schema.sql 참조 필수

**모든 게임 데이터 제작은 반드시 `database/setup/mvp_schema.sql`을 참조해야 합니다.**

게임 데이터는 YAML 파일로 정의되며, `UnifiedGameDataLoader`를 통해 데이터베이스에 저장됩니다.

## 1. 개요

게임 데이터 제작 시스템은 YAML 파일을 사용하여 게임 데이터를 정의하고, 통합 로더를 통해 데이터베이스에 저장하는 시스템입니다.

### 1.1 시스템 구조

```
database/game_data/
├── unified_loader.py          # 통합 로더 (메인 진입점)
├── data_definitions/          # YAML 데이터 정의
│   ├── regions/              # 지역 데이터
│   ├── locations/            # 장소 데이터
│   ├── cells/                # 셀 데이터
│   ├── entities/             # 엔티티 데이터
│   ├── objects/              # 오브젝트 데이터
│   ├── items/                # 아이템 데이터
│   └── base_properties/      # 기본 속성 데이터
├── FACTORY_PATTERN_EXPLANATION.md
├── UNIFIED_GAME_DATA_SYSTEM_PROPOSAL.md
└── ID_SEMANTIC_VERIFICATION.md
```

### 1.2 핵심 원칙

1. **YAML 파일로 데이터 정의**: 코드가 아닌 데이터 파일로 정의
2. **Factory 패턴 사용**: 기존 `WorldDataFactory` 재사용
3. **의존성 자동 해결**: 통합 로더가 자동으로 로드 순서 결정
4. **ID 의미적 준수**: 명명 규칙 준수 필수
5. **스키마 참조 필수**: `mvp_schema.sql` 참조 필수

## 2. ID 명명 규칙

### 2.1 필수 준수 규칙

**⚠️ 중요**: 모든 ID는 의미적 명명 규칙을 준수해야 합니다.

| 타입 | 규칙 | 예시 |
|------|------|------|
| **Region** | `REG_[대륙]_[지역]_[일련번호]` | `REG_ANBRETIA_REKRESTA_01` |
| **Location** | `LOC_[지역]_[장소]_[일련번호]` | `LOC_REKRESTA_HOTEL_01` |
| **Cell** | `CELL_[위치타입]_[세부위치]_[일련번호]` | `CELL_HOTEL_LOBBY_001` |
| **Entity** | `[종족]_[직업/역할]_[일련번호]` | `NPC_HOTEL_MANAGER_001` |
| **Object** | `OBJ_[타입]_[이름]_[일련번호]` | `OBJ_HOTEL_RECEPTION_DESK_001` |
| **Item** | `ITEM_[종류]_[효과]_[일련번호]` | `ITEM_POTION_HEAL_001` |
| **Base Property** | `PROP_[속성분류]_[세부속성]_[일련번호]` | `PROP_ITEM_CLOTHING_001` |

### 2.2 잘못된 예시

```yaml
# ❌ 잘못된 예시: 대륙 부분 누락
region:
  id: REG_REKRESTA_001  # ❌ REG_ANBRETIA_REKRESTA_001이어야 함

# ✅ 올바른 예시
region:
  id: REG_ANBRETIA_REKRESTA_01  # ✅ 대륙 포함
```

### 2.3 ID 검증

ID 의미적 준수 검증은 `ID_SEMANTIC_VERIFICATION.md`를 참조하세요.

## 3. YAML 파일 구조

### 3.1 Region 예시

```yaml
region:
  id: REG_ANBRETIA_REKRESTA_01
  name: 레크레스타
  type: town
  description: 해변을 접하고 있는 아름다운 관광지
  properties:
    theme: 아름다운 것은 거기에 비밀이 있기 때문
    population: 5000
    location: 안브레티아
  locations:
    - id: LOC_REKRESTA_HOTEL_01
      name: 레크레스타 호텔
      type: location
      description: 최고의 서비스를 제공하는 호텔
      properties: {}
      cells:
        - id: CELL_HOTEL_LOBBY
          name: 로비
          width: 25
          height: 25
          description: 호텔의 로비
          properties: {}
          entities: []
          objects: []
```

### 3.2 Entity 예시

```yaml
entity:
  id: NPC_HOTEL_MANAGER_001
  name: 호텔 지배인 엘리자베스
  type: npc
  description: 친절하고 전문적인 호텔 지배인
  cell_id: CELL_HOTEL_LOBBY
  position:
    x: 15.0
    y: 5.0
    z: 0.0
  size: medium
  stats:
    strength: 8
    intelligence: 16
    charisma: 18
  properties:
    personality: friendly
    knowledge: ["local_news", "hotel_services"]
    interaction_flags: ["can_talk", "can_trade"]
  dialogue:
    greeting: "어서오세요! 레크레스타 호텔에 오신 것을 환영합니다."
    topics:
      - id: hotel_services
        content: "호텔 서비스에 대해 알려드리겠습니다."
```

### 3.3 Object 예시

```yaml
object:
  id: OBJ_HOTEL_RECEPTION_DESK_001
  name: 접수 데스크
  type: interactive
  description: 대리석으로 만들어진 접수 데스크
  cell_id: CELL_HOTEL_LOBBY
  position:
    x: 15.0
    y: 3.0
  interaction_type: openable
  possible_states: ["closed", "open"]
  properties:
    material: marble
    height: 1.2
    interactions:
      - type: talk
        action: check_in
  wall_mounted: false
  passable: false
  movable: false
  height: 1.2
  width: 2.0
  depth: 0.8
  weight: 150.0
```

### 3.4 Item 예시

```yaml
item:
  id: ITEM_CLOTHING_BASIC_001
  base_property_id: PROP_ITEM_CLOTHING_001  # 의존성
  type: clothing
  stack_size: 1
  consumable: false
  properties:
    description: 평범한 여행자용 의복입니다.
    durability: 100
```

### 3.5 Base Property 예시

```yaml
base_property:
  id: PROP_ITEM_CLOTHING_001
  name: 기본 의복
  description: 평범한 여행자용 의복입니다.
  type: item
  base_effects: {}
  requirements: {}
```

## 4. 의존성 규칙

### 4.1 의존성 계층

```
1. Base Properties (최상위)
   ↓
2. Items (Base Property 의존)
   ↓
3. Regions
   ↓
4. Locations (Region 의존)
   ↓
5. Cells (Location 의존)
   ↓
6. Entities, Objects (Cell 의존)
```

### 4.2 로드 순서

통합 로더가 자동으로 의존성을 해결하여 올바른 순서로 로드합니다:

1. **Base Properties**: 모든 기본 속성
2. **Items**: 아이템 (Base Property 참조)
3. **Regions**: 지역
4. **Locations**: 장소 (Region 참조)
5. **Cells**: 셀 (Location 참조)
6. **Entities**: 엔티티 (Cell 참조)
7. **Objects**: 오브젝트 (Cell 참조)

### 4.3 의존성 참조

**✅ 올바른 참조**:

```yaml
# Item이 Base Property 참조
item:
  id: ITEM_CLOTHING_BASIC_001
  base_property_id: PROP_ITEM_CLOTHING_001  # ✅ 존재하는 Base Property

# Location이 Region 참조
location:
  id: LOC_REKRESTA_HOTEL_01
  region_id: REG_ANBRETIA_REKRESTA_01  # ✅ 존재하는 Region

# Cell이 Location 참조
cell:
  id: CELL_HOTEL_LOBBY
  location_id: LOC_REKRESTA_HOTEL_01  # ✅ 존재하는 Location

# Entity가 Cell 참조
entity:
  id: NPC_HOTEL_MANAGER_001
  cell_id: CELL_HOTEL_LOBBY  # ✅ 존재하는 Cell
```

**❌ 잘못된 참조**:

```yaml
# ❌ 존재하지 않는 Base Property 참조
item:
  id: ITEM_CLOTHING_BASIC_001
  base_property_id: PROP_NONEXISTENT  # ❌ 존재하지 않음

# ❌ 존재하지 않는 Region 참조
location:
  id: LOC_REKRESTA_HOTEL_01
  region_id: REG_NONEXISTENT  # ❌ 존재하지 않음
```

## 5. UnifiedGameDataLoader 사용법

### 5.1 통합 로더 초기화

```python
from database.game_data.unified_loader import UnifiedGameDataLoader
from pathlib import Path

# 로더 초기화
loader = UnifiedGameDataLoader()

# 데이터 디렉토리 지정
data_dir = Path("database/game_data/data_definitions")
```

### 5.2 모든 데이터 로드

```python
# 모든 게임 데이터 로드
results = await loader.load_all(data_dir, validate_only=False)

print(f"로드됨: {results['loaded']}개")
print(f"건너뜀: {results['skipped']}개")
print(f"에러: {results['errors']}개")
```

### 5.3 검증만 수행

```python
# 데이터 검증 (DB 저장하지 않음)
results = await loader.load_all(data_dir, validate_only=True)

if results['errors'] > 0:
    print("❌ 검증 실패:")
    for detail in results['details']:
        if 'Error' in detail:
            print(f"  - {detail}")
```

### 5.4 CLI 사용

```bash
# 모든 데이터 로드
python -m database.game_data.unified_loader

# 특정 데이터 디렉토리 지정
python -m database.game_data.unified_loader --data-dir /path/to/data_definitions

# 검증만 수행
python -m database.game_data.unified_loader --validate-only
```

## 6. Factory 패턴 사용

### 6.1 Factory 패턴의 역할

통합 로더는 **기존 Factory 클래스들을 재사용**하여 일관성을 유지합니다:

```
UnifiedGameDataLoader
    ↓ (YAML 파싱 및 변환)
WorldDataFactory
    ↓ (상속)
GameDataFactory
    ↓ (실제 DB 작업)
Database
```

### 6.2 Factory 사용 원칙

1. **기존 Factory 재사용**: `WorldDataFactory`, `GameDataFactory` 사용
2. **일관성 유지**: 모든 데이터가 동일한 Factory를 통해 생성
3. **로직 분리**: YAML 파싱은 로더, DB 작업은 Factory

### 6.3 Factory 호출 흐름

```python
# unified_loader.py 내부
async def _load_region(self, region_data: Dict[str, Any]):
    # YAML 데이터를 Factory 형식으로 변환
    region_config = {
        "region_id": region_data["id"],
        "region_name": region_data["name"],
        "locations": [...]
    }
    
    # ⭐ 기존 WorldDataFactory 사용
    await self.factory.create_region_with_children(region_config)
```

자세한 내용은 `database/game_data/FACTORY_PATTERN_EXPLANATION.md`를 참조하세요.

## 7. 데이터 필드 매핑

### 7.1 YAML → DB 필드 매핑

통합 로더는 YAML 필드를 DB 스키마 필드로 자동 매핑합니다:

| YAML 필드 | DB 필드 | 타입 |
|-----------|---------|------|
| `id` | `region_id`, `location_id`, `cell_id`, etc. | VARCHAR(50) |
| `name` | `region_name`, `location_name`, `cell_name`, etc. | VARCHAR(100) |
| `type` | `region_type`, `location_type`, `object_type`, etc. | VARCHAR(50) |
| `description` | `region_description`, `location_description`, etc. | TEXT |
| `properties` | `region_properties`, `location_properties`, etc. | JSONB |
| `width`, `height` | `matrix_width`, `matrix_height` | INTEGER |
| `position` | `default_position_3d`, `default_position` | JSONB |
| `stats` | `base_stats` | JSONB |

### 7.2 JSONB 필드 처리

**⚠️ 중요**: JSONB 필드에 UUID를 저장할 때는 반드시 문자열로 변환해야 합니다.

```python
# ✅ 올바른 방법: normalize_uuid() 사용
from app.common.utils.uuid_helper import normalize_uuid

position = {
    'x': 15.0,
    'y': 5.0,
    'runtime_cell_id': normalize_uuid(cell_id)  # ✅ 문자열로 변환
}

# ❌ 잘못된 방법: UUID 객체 직접 저장
position = {
    'x': 15.0,
    'y': 5.0,
    'runtime_cell_id': cell_id  # ❌ UUID 객체 (JSON 직렬화 실패)
}
```

## 8. 자주 발생하는 에러 및 해결

### 8.1 ID 의미적 위반

**에러**: ID가 명명 규칙을 위반함

**해결**:
- `ID_SEMANTIC_VERIFICATION.md` 참조
- 명명 규칙 준수 확인
- 예: `REG_REKRESTA_001` → `REG_ANBRETIA_REKRESTA_01`

### 8.2 의존성 참조 오류

**에러**: 존재하지 않는 ID 참조

**해결**:
- 참조하는 ID가 먼저 로드되었는지 확인
- 로드 순서 확인 (Base Properties → Items → Regions → ...)
- 참조 ID가 올바른지 확인

### 8.3 JSONB 직렬화 실패

**에러**: `TypeError: Object of type UUID is not JSON serializable`

**해결**:
- JSONB 필드에 UUID 저장 시 `normalize_uuid()` 사용
- `01_TYPE_SAFETY/UUID_GUIDELINES.md` 참조

### 8.4 스키마 불일치

**에러**: 필드 타입 불일치 또는 필수 필드 누락

**해결**:
- `database/setup/mvp_schema.sql` 참조
- 필드 타입 및 제약조건 확인
- 필수 필드 확인

## 9. 체크리스트

게임 데이터 제작 전 확인사항:

- [ ] `mvp_schema.sql`의 테이블 구조 확인
- [ ] ID 명명 규칙 준수 확인
- [ ] 의존성 참조 확인 (Base Property → Item → Region → ...)
- [ ] YAML 파일 구조 확인
- [ ] JSONB 필드에 UUID 저장 시 `normalize_uuid()` 사용
- [ ] 검증 모드로 먼저 테스트 (`--validate-only`)
- [ ] Factory 패턴 사용 확인

## 10. 참고 문서

- `00_CORE/02_ARCHITECTURE_PRINCIPLES.md`: Factory 패턴 사용 원칙
- `01_TYPE_SAFETY/UUID_GUIDELINES.md`: UUID 처리 가이드라인
- `02_DATABASE/DATABASE_SCHEMA_DESIGN.md`: 데이터베이스 스키마 설계 가이드라인
- `database/setup/mvp_schema.sql`: **데이터베이스 스키마 (필수 참조)**
- `database/game_data/unified_loader.py`: 통합 로더 구현
- `database/game_data/FACTORY_PATTERN_EXPLANATION.md`: Factory 패턴 설명
- `database/game_data/UNIFIED_GAME_DATA_SYSTEM_PROPOSAL.md`: 통합 시스템 제안서
- `database/game_data/ID_SEMANTIC_VERIFICATION.md`: ID 의미적 검증
- `database/game_data/data_definitions/README.md`: 데이터 정의 파일 가이드

