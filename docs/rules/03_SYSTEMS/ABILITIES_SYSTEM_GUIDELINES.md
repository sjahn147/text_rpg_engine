# 스킬 및 주문 시스템 사용 가이드라인

> **최신화 날짜**: 2026-01-03  
> **적용 범위**: 스킬/주문 시스템 사용 전 필수 읽기

## 1. 개요

스킬 및 주문 시스템은 Effect Carrier와 **별도**로 관리되는 독립적인 시스템입니다.

**중요**: 
- Effect Carrier 타입이 `skill`인 것은 스킬 시스템과 **다릅니다**
- Effect Carrier `skill`: 버프/효과를 의미
- `abilities_skills`: 실제 스킬 능력 정의

## 2. 데이터베이스 구조

### 2.1 스킬 정의

```sql
game_data.abilities_skills (
  skill_id VARCHAR(50) PRIMARY KEY,
  base_property_id VARCHAR(50) NOT NULL,
  cooldown INTEGER,
  skill_type VARCHAR(50),
  skill_properties JSONB,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (base_property_id) REFERENCES game_data.base_properties(property_id)
)
```

**스킬 ID 명명 규칙**: `SKILL_[직업/계열]_[효과]_[일련번호]`

예시:
- `SKILL_WARRIOR_SLASH_001`
- `SKILL_ROGUE_STEALTH_001`
- `SKILL_MAGE_FIREBALL_001`

### 2.2 주문 정의

```sql
game_data.abilities_magic (
  magic_id VARCHAR(50) PRIMARY KEY,
  base_property_id VARCHAR(50) NOT NULL,
  mana_cost INTEGER,
  cast_time INTEGER,
  magic_school VARCHAR(50),
  magic_properties JSONB,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (base_property_id) REFERENCES game_data.base_properties(property_id)
)
```

**주문 ID 명명 규칙**: `MAGIC_[속성]_[효과]_[일련번호]`

예시:
- `MAGIC_FIRE_BALL_001`
- `MAGIC_ICE_SHIELD_001`
- `MAGIC_HEAL_RESTORE_001`

### 2.3 엔티티 소유

엔티티의 스킬/주문은 `entities.default_abilities` JSONB 필드에 저장됩니다:

```sql
game_data.entities (
  entity_id VARCHAR(50) PRIMARY KEY,
  default_abilities JSONB,  -- {"skills": ["SKILL_WARRIOR_SLASH_001"], "magic": ["MAGIC_FIRE_BALL_001"]}
  ...
)
```

**JSONB 구조**:
```json
{
  "skills": ["SKILL_WARRIOR_SLASH_001", "SKILL_WARRIOR_CHARGE_001"],
  "magic": ["MAGIC_FIRE_BALL_001", "MAGIC_HEAL_RESTORE_001"]
}
```

## 3. 스킬/주문 조회 방법

### 3.1 엔티티의 스킬/주문 조회

```python
from database.repositories.game_data import GameDataRepository
from common.utils.jsonb_handler import parse_jsonb_data

async def get_character_abilities(
    self,
    session_id: UUID,
    runtime_entity_id: UUID
) -> Dict[str, List[Dict[str, Any]]]:
    """
    캐릭터의 스킬 및 주문 목록 조회
    
    Returns:
        {
            "skills": [...],  # 스킬 상세 정보
            "magic": [...]    # 주문 상세 정보
        }
    """
    # 1. entity_references를 통해 game_entity_id 조회
    entity_ref = await self.reference_layer.get_entity_reference(
        runtime_entity_id, session_id
    )
    if not entity_ref:
        raise ValueError(f"Entity not found: {runtime_entity_id}")
    
    game_entity_id = entity_ref.game_entity_id
    
    # 2. entities 테이블에서 default_abilities JSONB 조회
    entity_data = await self.game_data.get_entity(game_entity_id)
    if not entity_data:
        raise ValueError(f"Game entity not found: {game_entity_id}")
    
    default_abilities = parse_jsonb_data(entity_data.get('default_abilities', {}))
    skill_ids = default_abilities.get('skills', [])
    magic_ids = default_abilities.get('magic', [])
    
    # 3. abilities_skills 테이블에서 스킬 상세 정보 조회
    skills = []
    for skill_id in skill_ids:
        skill_data = await self.game_data.get_skill(skill_id)
        if skill_data:
            skills.append(skill_data)
    
    # 4. abilities_magic 테이블에서 주문 상세 정보 조회
    magic = []
    for magic_id in magic_ids:
        magic_data = await self.game_data.get_magic(magic_id)
        if magic_data:
            magic.append(magic_data)
    
    return {
        "skills": skills,
        "magic": magic
    }
```

### 3.2 스킬/주문 상세 정보 조회

```python
# 스킬 상세 정보 조회
skill_data = await game_data_repo.get_skill("SKILL_WARRIOR_SLASH_001")

# 주문 상세 정보 조회
magic_data = await game_data_repo.get_magic("MAGIC_FIRE_BALL_001")
```

## 4. API 엔드포인트 설계

### 4.1 스킬/주문 목록 조회

```python
@router.get("/character/abilities/{session_id}")
async def get_character_abilities(session_id: str):
    """캐릭터의 스킬 및 주문 목록 조회"""
    # 1. entity_references를 통해 game_entity_id 조회
    # 2. entities 테이블에서 default_abilities JSONB 조회
    # 3. abilities_skills 테이블에서 스킬 상세 정보 조회
    # 4. abilities_magic 테이블에서 주문 상세 정보 조회
    # 5. 함께 반환
    ...
```

**응답 구조**:
```json
{
  "success": true,
  "skills": [
    {
      "skill_id": "SKILL_WARRIOR_SLASH_001",
      "name": "강타",
      "cooldown": 5,
      "skill_type": "combat",
      "skill_properties": {
        "damage_multiplier": 1.5,
        "range": 2
      }
    }
  ],
  "magic": [
    {
      "magic_id": "MAGIC_FIRE_BALL_001",
      "name": "파이어볼",
      "mana_cost": 10,
      "cast_time": 2,
      "magic_school": "evocation",
      "magic_properties": {
        "damage": 50,
        "area_of_effect": {"radius": 3, "type": "circle"}
      }
    }
  ]
}
```

## 5. Effect Carrier와의 차이점

### 5.1 스킬/주문 vs Effect Carrier

| 구분 | 스킬/주문 시스템 | Effect Carrier 시스템 |
|------|-----------------|---------------------|
| **저장 위치** | `abilities_skills`, `abilities_magic` | `effect_carriers` |
| **엔티티 소유** | `entities.default_abilities` JSONB | `entity_effect_ownership` 테이블 |
| **용도** | 능력 정의 (스킬/주문 자체) | 효과 정의 (버프/디버프/아이템 효과) |
| **타입** | `skill_id`, `magic_id` (VARCHAR) | `effect_id` (UUID) |
| **관리자** | GameDataRepository | EffectCarrierManager |

### 5.2 사용 시나리오

**스킬/주문 시스템 사용**:
- 캐릭터가 보유한 스킬/주문 목록 조회
- 액션 바에 스킬/주문 슬롯 표시
- 스킬/주문 사용 (마나 소모, 쿨다운 등)

**Effect Carrier 시스템 사용**:
- 아이템/장비의 효과 조회
- 적용 중인 버프/디버프 조회
- 질병, 저주, 가호 등 상태 효과 관리

## 6. 금지 사항

### 6.1 Effect Carrier와 혼동 금지

```python
# ❌ 잘못된 코드: Effect Carrier로 스킬 조회 시도
effect = await effect_carrier_manager.get_effect_carrier("SKILL_WARRIOR_SLASH_001")
# SKILL_WARRIOR_SLASH_001은 VARCHAR이므로 UUID가 아님

# ✅ 올바른 코드: 스킬 시스템으로 조회
skill = await game_data_repo.get_skill("SKILL_WARRIOR_SLASH_001")
```

### 6.2 추측 로직 금지

```python
# ❌ 잘못된 코드: ID 형식으로 타입 추측
if skill_id.startswith("SKILL_"):
    # 스킬이라고 추측
    skill = await game_data_repo.get_skill(skill_id)
elif skill_id.startswith("MAGIC_"):
    # 주문이라고 추측
    magic = await game_data_repo.get_magic(skill_id)

# ✅ 올바른 코드: 명시적 파라미터로 구분
async def get_ability(self, ability_type: str, ability_id: str):
    """ability_type: 'skill' 또는 'magic'"""
    if ability_type == 'skill':
        return await self.game_data.get_skill(ability_id)
    elif ability_type == 'magic':
        return await self.game_data.get_magic(ability_id)
    else:
        raise ValueError(f"Invalid ability_type: {ability_type}")
```

### 6.3 JSONB 파싱 에러 처리

```python
# ❌ 잘못된 코드: JSONB 파싱 실패 시 기본값 사용
default_abilities = parse_jsonb_data(entity_data.get('default_abilities', {}))
skill_ids = default_abilities.get('skills', [])  # 기본값 사용

# ✅ 올바른 코드: 명시적 검증
from common.utils.jsonb_handler import parse_jsonb_data

default_abilities_raw = entity_data.get('default_abilities')
if not default_abilities_raw:
    raise ValueError(f"Entity {entity_id} has no default_abilities")

default_abilities = parse_jsonb_data(default_abilities_raw)
if not isinstance(default_abilities, dict):
    raise ValueError(f"Invalid default_abilities format: {default_abilities}")

skill_ids = default_abilities.get('skills', [])
if not isinstance(skill_ids, list):
    raise ValueError(f"Invalid skills format: {skill_ids}")
```

## 7. 트랜잭션 사용

스킬/주문 사용 시 상태 변경이 발생하면 트랜잭션을 사용해야 합니다:

```python
from app.common.decorators.transaction import with_transaction

@with_transaction
async def use_skill(
    self,
    session_id: UUID,
    runtime_entity_id: UUID,
    skill_id: str,
    conn=None
):
    """스킬 사용 (트랜잭션 보장)"""
    # 1. 스킬 정보 조회
    skill = await self.game_data.get_skill(skill_id)
    if not skill:
        raise ValueError(f"Skill not found: {skill_id}")
    
    # 2. 쿨다운 확인
    # 3. 마나 소모 확인
    # 4. 스킬 사용 처리
    # 5. 쿨다운 설정
    # 6. 마나 차감
    ...
```

## 8. 미구현 및 추가 필요 사항

### 8.1 API 엔드포인트 구현 필요

- [ ] **스킬/주문 목록 조회 API 구현**
  - [ ] `/api/gameplay/character/abilities/{session_id}`: 스킬/주문 목록 조회
  - [ ] `entities.default_abilities` JSONB 파싱 및 상세 정보 조회
  - [ ] `abilities_skills`, `abilities_magic` 테이블 조회
  - **참고**: `04_DEVELOPMENT/UI_REDESIGN_TODO.md` - API 엔드포인트 TODO

### 8.2 스킬/주문 UI 통합 (기획 필요)

- [ ] **스킬/주문 UI 표시 방법 정의**
  - [ ] 액션 바에 스킬/주문 슬롯 표시 방법 정의
  - [ ] 스킬/주문 아이콘 매핑 규칙 정의
  - [ ] 스킬/주문 툴팁 표시 내용 정의
  - [ ] 스킬/주문 사용 UI 정의
  - **참고**: `docs/design/UI_REDESIGN_BG3_STYLE.md` - 스킬/주문 시스템 UI 통합

- [ ] **스킬/주문 사용 로직 구현**
  - [ ] 스킬 사용 시 쿨다운 처리
  - [ ] 주문 사용 시 마나 소모 처리
  - [ ] 스킬/주문 사용 시 상태 변경 (트랜잭션 필요)
  - **참고**: `01_TYPE_SAFETY/TRANSACTION_GUIDELINES.md` - 트랜잭션 사용법

### 8.3 Service Layer 추가 필요

- [ ] **CharacterService에 스킬/주문 조회 메서드 추가**
  - [ ] `get_character_abilities()` 메서드 구현
  - [ ] `use_skill()` 메서드 구현 (향후)
  - [ ] `use_magic()` 메서드 구현 (향후)
  - **참고**: `00_CORE/02_ARCHITECTURE_PRINCIPLES.md` - Service 계층 원칙

### 8.4 데이터베이스 스키마 검증 필요

- [ ] **스키마 확인**
  - [ ] `abilities_skills` 테이블 구조 확인 (`mvp_schema.sql` 참조)
  - [ ] `abilities_magic` 테이블 구조 확인 (`mvp_schema.sql` 참조)
  - [ ] `entities.default_abilities` JSONB 필드 구조 확인
  - **참고**: `02_DATABASE/DATABASE_SCHEMA_DESIGN.md` - mvp_schema.sql 참조 필수

### 8.5 정책 결정 필요

- [ ] **스킬/주문 습득 정책**
  - [ ] 스킬/주문 습득 방법 정의 (레벨업, 아이템 사용, 퀘스트 완료 등)
  - [ ] 스킬/주문 습득 시 `default_abilities` 업데이트 방법 정의
  - [ ] 런타임 스킬/주문 습득 저장 위치 결정 (`entity_states` vs `default_abilities`)

- [ ] **스킬/주문 사용 제한 정책**
  - [ ] 스킬/주문 사용 조건 정의 (마나, 쿨다운, 상태 등)
  - [ ] 스킬/주문 사용 실패 시 처리 방법 정의
  - [ ] 스킬/주문 사용 로그 저장 정책 결정

## 9. 참고 문서

- `docs/rules/01_PHILOSOPHY.md`: 핵심 개발 철학
- `docs/rules/EFFECT_CARRIER_GUIDELINES.md`: Effect Carrier 시스템 가이드라인
- `docs/rules/TRANSACTION_GUIDELINES.md`: 트랜잭션 사용 가이드라인
- `docs/design/UI_REDESIGN_BG3_STYLE_CORRECTIONS.md`: 스킬/주문 시스템 정정
- `docs/design/UI_REDESIGN_BG3_STYLE.md`: 스킬/주문 시스템 UI 통합
- `database/setup/mvp_schema.sql`: 데이터베이스 스키마
- `04_DEVELOPMENT/UI_REDESIGN_TODO.md`: UI 리디자인 TODO

