# Effect Carrier 설계서

> **최신화 날짜**: 2025-12-28  
> **문서 버전**: v1.1  
> **작성일**: 2025-10-18  
> **최종 수정**: 2025-12-28  
> **현재 상태**: Effect Carrier 시스템 구현 완료, 6가지 타입 모두 지원, EffectCarrierManager 구현 완료

## 🎯 **Effect Carrier 시스템 개요**

Effect Carrier는 RPG Engine의 핵심 시스템으로, 모든 효과(skill, buff, item, blessing, curse, ritual)를 통일된 인터페이스로 관리합니다.

### **핵심 철학**
> **"특수성은 엔티티가 아니라 소유한 형식(오브젝트)에 있음"**

- **통일 인터페이스**: 모든 효과를 일관된 방식으로 처리
- **유연한 효과 관리**: 다양한 효과를 동일한 구조로 관리
- **확장 가능성**: 새로운 효과 타입을 쉽게 추가 가능

---

## 🏗️ **시스템 아키텍처**

### **Effect Carrier 테이블 구조**

```sql
-- 이펙트 캐리어 (형식의 통일)
CREATE TABLE game_data.effect_carriers (
  effect_id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  carrier_type TEXT CHECK (carrier_type IN
    ('skill','buff','item','blessing','curse','ritual')),
  effect_json JSONB NOT NULL,       -- 수치/조건/지속시간 등
  constraints_json JSONB DEFAULT '{}'::jsonb,
  source_entity_id UUID NULL,       -- 신격/유래
  tags TEXT[]
);

-- 엔티티가 소유한 형식
CREATE TABLE reference_layer.entity_effect_ownership (
  session_id UUID NOT NULL,
  runtime_entity_id UUID NOT NULL,
  effect_id UUID NOT NULL,
  acquired_at TIMESTAMP NOT NULL DEFAULT now(),
  source TEXT,
  PRIMARY KEY (session_id, runtime_entity_id, effect_id)
);
```

### **Effect Carrier 타입**

#### **1. Skill (스킬)**
```json
{
  "effect_id": "SKILL_FIREBALL_001",
  "name": "Fireball",
  "carrier_type": "skill",
  "effect_json": {
    "damage": 50,
    "range": 3,
    "cooldown": 5,
    "mana_cost": 10,
    "target_type": "enemy",
    "area_of_effect": false
  },
  "constraints_json": {
    "level_required": 5,
    "class_required": ["mage", "wizard"],
    "mana_required": 10
  },
  "source_entity_id": null,
  "tags": ["combat", "magic", "fire"]
}
```

#### **2. Buff (버프)**
```json
{
  "effect_id": "BUFF_STRENGTH_001",
  "name": "Strength Boost",
  "carrier_type": "buff",
  "effect_json": {
    "stat_modifier": {
      "strength": 5
    },
    "duration": 300,
    "stackable": false,
    "removable": true
  },
  "constraints_json": {
    "max_stacks": 1,
    "conflicts_with": ["weakness"]
  },
  "source_entity_id": null,
  "tags": ["temporary", "stat_boost"]
}
```

#### **3. Item (아이템)**
```json
{
  "effect_id": "ITEM_HEALING_POTION_001",
  "name": "Healing Potion",
  "carrier_type": "item",
  "effect_json": {
    "heal_amount": 50,
    "instant": true,
    "consumable": true,
    "stack_size": 10
  },
  "constraints_json": {
    "use_in_combat": true,
    "use_out_of_combat": true
  },
  "source_entity_id": null,
  "tags": ["consumable", "healing"]
}
```

#### **4. Blessing (축복)**
```json
{
  "effect_id": "BLESSING_DIVINE_PROTECTION_001",
  "name": "Divine Protection",
  "carrier_type": "blessing",
  "effect_json": {
    "damage_reduction": 0.2,
    "duration": 3600,
    "divine_source": "temple_priest",
    "removable": false
  },
  "constraints_json": {
    "requires_faith": 50,
    "conflicts_with": ["curse"]
  },
  "source_entity_id": "ENTITY_TEMPLE_PRIEST_001",
  "tags": ["divine", "protection", "long_term"]
}
```

#### **5. Curse (저주)**
```json
{
  "effect_id": "CURSE_WEAKNESS_001",
  "name": "Weakness",
  "carrier_type": "curse",
  "effect_json": {
    "stat_modifier": {
      "strength": -3
    },
    "duration": 1800,
    "removable": true,
    "curable": true
  },
  "constraints_json": {
    "requires_curse_removal": true,
    "conflicts_with": ["blessing"]
  },
  "source_entity_id": "ENTITY_DARK_MAGE_001",
  "tags": ["negative", "temporary", "curable"]
}
```

#### **6. Ritual (의식)**
```json
{
  "effect_id": "RITUAL_SUMMONING_001",
  "name": "Summoning Ritual",
  "carrier_type": "ritual",
  "effect_json": {
    "summon_entity": "ENTITY_SUMMONED_DEMON_001",
    "duration": 600,
    "requires_components": ["candle", "incense", "chalk"],
    "ritual_time": 300
  },
  "constraints_json": {
    "requires_ritual_space": true,
    "requires_darkness": true,
    "level_required": 10
  },
  "source_entity_id": "ENTITY_RITUAL_MASTER_001",
  "tags": ["ritual", "summoning", "complex"]
}
```

---

## 📋 **JSON 구조 관리 시스템**

### **JSON 스키마 정의**

#### **타입별 JSON 스키마**
```python
# effect_carrier_schemas.py
EFFECT_CARRIER_SCHEMAS = {
    "skill": {
        "type": "object",
        "properties": {
            "damage": {"type": "integer", "minimum": 0},
            "range": {"type": "integer", "minimum": 1},
            "cooldown": {"type": "integer", "minimum": 0},
            "mana_cost": {"type": "integer", "minimum": 0},
            "target_type": {"type": "string", "enum": ["enemy", "ally", "self", "area"]},
            "area_of_effect": {"type": "boolean"}
        },
        "required": ["damage", "range", "cooldown"]
    },
    "buff": {
        "type": "object", 
        "properties": {
            "stat_modifier": {"type": "object"},
            "duration": {"type": "integer", "minimum": 0},
            "stackable": {"type": "boolean"},
            "removable": {"type": "boolean"}
        },
        "required": ["stat_modifier", "duration"]
    },
    "item": {
        "type": "object",
        "properties": {
            "heal_amount": {"type": "integer", "minimum": 0},
            "instant": {"type": "boolean"},
            "consumable": {"type": "boolean"},
            "stack_size": {"type": "integer", "minimum": 1}
        }
    },
    "blessing": {
        "type": "object",
        "properties": {
            "damage_reduction": {"type": "number", "minimum": 0, "maximum": 1},
            "duration": {"type": "integer", "minimum": 0},
            "divine_source": {"type": "string"},
            "removable": {"type": "boolean"}
        },
        "required": ["damage_reduction", "duration"]
    },
    "curse": {
        "type": "object",
        "properties": {
            "stat_modifier": {"type": "object"},
            "duration": {"type": "integer", "minimum": 0},
            "removable": {"type": "boolean"},
            "curable": {"type": "boolean"}
        },
        "required": ["stat_modifier", "duration"]
    },
    "ritual": {
        "type": "object",
        "properties": {
            "summon_entity": {"type": "string"},
            "duration": {"type": "integer", "minimum": 0},
            "requires_components": {"type": "array"},
            "ritual_time": {"type": "integer", "minimum": 0}
        },
        "required": ["summon_entity", "duration"]
    }
}
```

### **자동 검증 모듈**

#### **Effect Carrier 검증기**
```python
# effect_carrier_validator.py
import jsonschema
from typing import Dict, Any

class EffectCarrierValidator:
    def __init__(self):
        self.schemas = EFFECT_CARRIER_SCHEMAS
    
    def validate_effect_json(self, carrier_type: str, effect_json: Dict[Any, Any]) -> bool:
        """Effect JSON 검증"""
        if carrier_type not in self.schemas:
            raise ValueError(f"Unknown carrier type: {carrier_type}")
        
        schema = self.schemas[carrier_type]
        
        try:
            jsonschema.validate(effect_json, schema)
            return True
        except jsonschema.ValidationError as e:
            raise ValueError(f"Invalid effect_json: {e.message}")
    
    def validate_constraints_json(self, carrier_type: str, constraints_json: Dict[Any, Any]) -> bool:
        """Constraints JSON 검증"""
        # 제약 조건별 검증 로직
        if carrier_type == "skill":
            return self._validate_skill_constraints(constraints_json)
        elif carrier_type == "buff":
            return self._validate_buff_constraints(constraints_json)
        # ... 다른 타입들
        
        return True
    
    def _validate_skill_constraints(self, constraints: Dict[Any, Any]) -> bool:
        """스킬 제약 조건 검증"""
        if "level_required" in constraints:
            if not isinstance(constraints["level_required"], int) or constraints["level_required"] < 1:
                return False
        
        if "class_required" in constraints:
            if not isinstance(constraints["class_required"], list):
                return False
        
        return True
```

### **Factory 패턴 기반 생성**

#### **Effect Carrier Factory**
```python
# effect_carrier_factory.py
class EffectCarrierFactory:
    def __init__(self):
        self.validators = {
            'skill': SkillEffectValidator(),
            'buff': BuffEffectValidator(),
            'item': ItemEffectValidator(),
            'blessing': BlessingEffectValidator(),
            'curse': CurseEffectValidator(),
            'ritual': RitualEffectValidator()
        }
    
    async def create_effect_carrier(self, name: str, carrier_type: str, 
                                  effect_data: dict, constraints_data: dict = None):
        """Effect Carrier 생성 (자동 검증 포함)"""
        
        # 타입별 검증
        validator = self.validators.get(carrier_type)
        if not validator:
            raise ValueError(f"Unknown carrier type: {carrier_type}")
        
        # Effect JSON 검증
        if not validator.validate_effect_json(effect_data):
            raise ValueError("Invalid effect_json")
        
        # Constraints JSON 검증
        if constraints_data and not validator.validate_constraints_json(constraints_data):
            raise ValueError("Invalid constraints_json")
        
        # Effect Carrier 생성
        effect_carrier = {
            "name": name,
            "carrier_type": carrier_type,
            "effect_json": effect_data,
            "constraints_json": constraints_data or {},
            "tags": validator.get_default_tags(carrier_type)
        }
        
        return effect_carrier
```

### **타입별 검증기**

#### **스킬 검증기**
```python
# skill_effect_validator.py
class SkillEffectValidator:
    def validate_effect_json(self, effect_data: dict) -> bool:
        """스킬 Effect JSON 검증"""
        required_fields = ["damage", "range", "cooldown"]
        
        for field in required_fields:
            if field not in effect_data:
                raise ValueError(f"Missing required field: {field}")
            
            if not isinstance(effect_data[field], int) or effect_data[field] < 0:
                raise ValueError(f"Invalid {field}: must be non-negative integer")
        
        # 선택적 필드 검증
        if "mana_cost" in effect_data:
            if not isinstance(effect_data["mana_cost"], int) or effect_data["mana_cost"] < 0:
                raise ValueError("mana_cost must be non-negative integer")
        
        if "target_type" in effect_data:
            valid_targets = ["enemy", "ally", "self", "area"]
            if effect_data["target_type"] not in valid_targets:
                raise ValueError(f"Invalid target_type: {effect_data['target_type']}")
        
        return True
    
    def validate_constraints_json(self, constraints_data: dict) -> bool:
        """스킬 제약 조건 검증"""
        if "level_required" in constraints_data:
            level = constraints_data["level_required"]
            if not isinstance(level, int) or level < 1 or level > 100:
                raise ValueError("level_required must be integer between 1 and 100")
        
        if "class_required" in constraints_data:
            classes = constraints_data["class_required"]
            if not isinstance(classes, list):
                raise ValueError("class_required must be a list")
            
            valid_classes = ["warrior", "mage", "archer", "rogue"]
            for cls in classes:
                if cls not in valid_classes:
                    raise ValueError(f"Invalid class: {cls}")
        
        return True
    
    def get_default_tags(self, carrier_type: str) -> list:
        """기본 태그 반환"""
        return ["combat", "skill"]
```

### **데이터베이스 레벨 검증**

#### **PostgreSQL JSON 스키마 검증**
```sql
-- Effect Carrier 테이블에 JSON 스키마 제약 조건 추가
ALTER TABLE game_data.effect_carriers 
ADD CONSTRAINT check_skill_effect_json 
CHECK (
    carrier_type != 'skill' OR 
    (effect_json ? 'damage' AND effect_json ? 'range' AND effect_json ? 'cooldown')
);

ALTER TABLE game_data.effect_carriers 
ADD CONSTRAINT check_buff_effect_json 
CHECK (
    carrier_type != 'buff' OR 
    (effect_json ? 'stat_modifier' AND effect_json ? 'duration')
);

-- JSON 필드에 GIN 인덱스 추가
CREATE INDEX idx_effect_carriers_effect_json ON game_data.effect_carriers 
USING GIN (effect_json);

CREATE INDEX idx_effect_carriers_constraints_json ON game_data.effect_carriers 
USING GIN (constraints_json);
```

### **개발 도구 및 UI**

#### **Effect Carrier 편집기**
```python
# effect_carrier_editor.py
class EffectCarrierEditor:
    def __init__(self):
        self.validator = EffectCarrierValidator()
        self.factory = EffectCarrierFactory()
    
    def create_skill_effect(self, name: str, damage: int, range: int, 
                          cooldown: int, mana_cost: int = 0):
        """스킬 Effect 생성 (타입 안전)"""
        effect_data = {
            "damage": damage,
            "range": range, 
            "cooldown": cooldown,
            "mana_cost": mana_cost,
            "target_type": "enemy",
            "area_of_effect": False
        }
        
        constraints_data = {
            "level_required": 1,
            "class_required": []
        }
        
        return self.factory.create_effect_carrier(
            name=name,
            carrier_type="skill",
            effect_data=effect_data,
            constraints_data=constraints_data
        )
    
    def create_buff_effect(self, name: str, stat_modifier: dict, 
                          duration: int, stackable: bool = False):
        """버프 Effect 생성 (타입 안전)"""
        effect_data = {
            "stat_modifier": stat_modifier,
            "duration": duration,
            "stackable": stackable,
            "removable": True
        }
        
        return self.factory.create_effect_carrier(
            name=name,
            carrier_type="buff", 
            effect_data=effect_data
        )
```

### **관리 전략**

#### **Effect Carrier 매니저**
```python
# effect_carrier_manager.py
class EffectCarrierManager:
    def __init__(self):
        self.validator = EffectCarrierValidator()
        self.factory = EffectCarrierFactory()
        self.schema_version = "1.0"
    
    async def create_effect_carrier(self, **kwargs):
        """Effect Carrier 생성 (자동 검증)"""
        # 1. 입력 데이터 검증
        # 2. JSON 스키마 검증  
        # 3. 비즈니스 로직 검증
        # 4. 데이터베이스 저장
        pass
    
    async def update_effect_carrier(self, effect_id: str, **kwargs):
        """Effect Carrier 수정 (자동 검증)"""
        # 1. 기존 데이터 조회
        # 2. 변경사항 검증
        # 3. 스키마 호환성 확인
        # 4. 데이터베이스 업데이트
        pass
    
    async def validate_effect_carrier(self, effect_id: str) -> bool:
        """Effect Carrier 무결성 검증"""
        # 1. JSON 스키마 검증
        # 2. 비즈니스 로직 검증
        # 3. 참조 무결성 검증
        pass
```

### **구현 단계별 접근**

#### **MVP 단계 (즉시 구현)**
- **JSON 스키마 정의**: 타입별 필수/선택 필드 명시
- **Python 검증기**: 런타임 검증
- **Factory 패턴**: 타입 안전한 생성

#### **확장 단계 (나중에 추가)**
- **데이터베이스 제약 조건**: PostgreSQL JSON 스키마 검증
- **UI 편집기**: 시각적 Effect Carrier 생성 도구
- **템플릿 시스템**: 자주 사용하는 Effect Carrier 템플릿

---

## 🔧 **Effect Carrier 관리 시스템**

### **Effect Carrier 생성**

```python
class EffectCarrierManager:
    def __init__(self):
        self.effect_types = {
            'skill': SkillEffect,
            'buff': BuffEffect,
            'item': ItemEffect,
            'blessing': BlessingEffect,
            'curse': CurseEffect,
            'ritual': RitualEffect
        }
    
    async def create_effect(self, name: str, carrier_type: str, 
                           effect_json: dict, constraints_json: dict = None,
                           source_entity_id: str = None, tags: list = None):
        """Effect Carrier 생성"""
        
        # 타입 검증
        if carrier_type not in self.effect_types:
            raise ValueError(f"Invalid carrier_type: {carrier_type}")
        
        # 효과 검증
        effect_class = self.effect_types[carrier_type]
        effect_instance = effect_class(effect_json)
        if not effect_instance.validate():
            raise ValueError(f"Invalid effect_json for {carrier_type}")
        
        # 제약 조건 검증
        if constraints_json:
            if not self.validate_constraints(constraints_json):
                raise ValueError("Invalid constraints_json")
        
        # Effect Carrier 생성
        effect_id = str(uuid.uuid4())
        effect_carrier = {
            "effect_id": effect_id,
            "name": name,
            "carrier_type": carrier_type,
            "effect_json": effect_json,
            "constraints_json": constraints_json or {},
            "source_entity_id": source_entity_id,
            "tags": tags or []
        }
        
        # 데이터베이스에 저장
        await self.save_effect_carrier(effect_carrier)
        
        return effect_carrier
```

### **엔티티 소유 관계 관리**

```python
class EntityEffectOwnership:
    def __init__(self):
        self.ownership_cache = {}
    
    async def grant_effect(self, session_id: str, entity_id: str, 
                          effect_id: str, source: str = None):
        """엔티티에 Effect Carrier 부여"""
        
        # Effect Carrier 존재 확인
        effect_carrier = await self.get_effect_carrier(effect_id)
        if not effect_carrier:
            raise ValueError(f"Effect Carrier not found: {effect_id}")
        
        # 제약 조건 확인
        if not await self.check_constraints(session_id, entity_id, effect_carrier):
            raise ValueError("Constraints not met")
        
        # 소유 관계 생성
        ownership = {
            "session_id": session_id,
            "runtime_entity_id": entity_id,
            "effect_id": effect_id,
            "acquired_at": datetime.now(),
            "source": source
        }
        
        # 데이터베이스에 저장
        await self.save_ownership(ownership)
        
        # 캐시 업데이트
        self.ownership_cache[f"{session_id}:{entity_id}"] = ownership
        
        return ownership
    
    async def revoke_effect(self, session_id: str, entity_id: str, effect_id: str):
        """엔티티에서 Effect Carrier 제거"""
        
        # 소유 관계 확인
        ownership = await self.get_ownership(session_id, entity_id, effect_id)
        if not ownership:
            raise ValueError("Ownership not found")
        
        # 제거 가능 여부 확인
        if not await self.can_revoke(session_id, entity_id, effect_id):
            raise ValueError("Cannot revoke this effect")
        
        # 소유 관계 제거
        await self.remove_ownership(session_id, entity_id, effect_id)
        
        # 캐시 업데이트
        cache_key = f"{session_id}:{entity_id}"
        if cache_key in self.ownership_cache:
            del self.ownership_cache[cache_key]
        
        return True
```

### **Effect Carrier 적용**

```python
class EffectApplicator:
    def __init__(self):
        self.applicators = {
            'skill': self.apply_skill,
            'buff': self.apply_buff,
            'item': self.apply_item,
            'blessing': self.apply_blessing,
            'curse': self.apply_curse,
            'ritual': self.apply_ritual
        }
    
    async def apply_effect(self, session_id: str, entity_id: str, 
                          effect_id: str, target_id: str = None):
        """Effect Carrier 적용"""
        
        # Effect Carrier 조회
        effect_carrier = await self.get_effect_carrier(effect_id)
        if not effect_carrier:
            raise ValueError(f"Effect Carrier not found: {effect_id}")
        
        # 소유 관계 확인
        ownership = await self.get_ownership(session_id, entity_id, effect_id)
        if not ownership:
            raise ValueError("Entity does not own this effect")
        
        # 적용 가능 여부 확인
        if not await self.can_apply(session_id, entity_id, effect_carrier, target_id):
            raise ValueError("Cannot apply this effect")
        
        # Effect Carrier 타입별 적용
        carrier_type = effect_carrier["carrier_type"]
        applicator = self.applicators[carrier_type]
        
        result = await applicator(session_id, entity_id, effect_carrier, target_id)
        
        # 적용 결과 로깅
        await self.log_effect_application(session_id, entity_id, effect_id, result)
        
        return result
    
    async def apply_skill(self, session_id: str, entity_id: str, 
                         effect_carrier: dict, target_id: str):
        """스킬 적용"""
        effect_json = effect_carrier["effect_json"]
        
        # 마나 소모
        mana_cost = effect_json.get("mana_cost", 0)
        await self.consume_mana(entity_id, mana_cost)
        
        # 데미지 계산
        damage = effect_json.get("damage", 0)
        if target_id:
            await self.deal_damage(target_id, damage)
        
        # 쿨다운 적용
        cooldown = effect_json.get("cooldown", 0)
        await self.apply_cooldown(entity_id, effect_carrier["effect_id"], cooldown)
        
        return {
            "success": True,
            "damage_dealt": damage,
            "mana_consumed": mana_cost,
            "cooldown_applied": cooldown
        }
    
    async def apply_buff(self, session_id: str, entity_id: str, 
                        effect_carrier: dict, target_id: str):
        """버프 적용"""
        effect_json = effect_carrier["effect_json"]
        
        # 스탯 수정자 적용
        stat_modifier = effect_json.get("stat_modifier", {})
        await self.apply_stat_modifier(target_id, stat_modifier)
        
        # 지속시간 적용
        duration = effect_json.get("duration", 0)
        await self.apply_duration_effect(target_id, effect_carrier["effect_id"], duration)
        
        return {
            "success": True,
            "stat_modifier": stat_modifier,
            "duration": duration
        }
    
    async def apply_item(self, session_id: str, entity_id: str, 
                        effect_carrier: dict, target_id: str):
        """아이템 적용"""
        effect_json = effect_carrier["effect_json"]
        
        # 즉시 효과 적용
        if effect_json.get("instant", False):
            heal_amount = effect_json.get("heal_amount", 0)
            if heal_amount > 0:
                await self.heal_entity(target_id, heal_amount)
        
        # 소모품 처리
        if effect_json.get("consumable", False):
            await self.consume_item(entity_id, effect_carrier["effect_id"])
        
        return {
            "success": True,
            "heal_amount": effect_json.get("heal_amount", 0),
            "consumed": effect_json.get("consumable", False)
        }
```

---

## 🎮 **게임플레이 통합**

### **Effect Carrier 조회**

```python
class EffectCarrierQuery:
    def __init__(self):
        self.query_cache = {}
    
    async def get_entity_effects(self, session_id: str, entity_id: str):
        """엔티티의 모든 Effect Carrier 조회"""
        
        # 캐시 확인
        cache_key = f"{session_id}:{entity_id}"
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        # 데이터베이스에서 조회
        ownerships = await self.get_entity_ownerships(session_id, entity_id)
        
        effects = []
        for ownership in ownerships:
            effect_carrier = await self.get_effect_carrier(ownership["effect_id"])
            if effect_carrier:
                effects.append({
                    "effect_carrier": effect_carrier,
                    "ownership": ownership
                })
        
        # 캐시 저장
        self.query_cache[cache_key] = effects
        
        return effects
    
    async def get_effects_by_type(self, session_id: str, entity_id: str, 
                                 carrier_type: str):
        """특정 타입의 Effect Carrier 조회"""
        
        all_effects = await self.get_entity_effects(session_id, entity_id)
        
        filtered_effects = [
            effect for effect in all_effects
            if effect["effect_carrier"]["carrier_type"] == carrier_type
        ]
        
        return filtered_effects
    
    async def get_effects_by_tag(self, session_id: str, entity_id: str, tag: str):
        """특정 태그의 Effect Carrier 조회"""
        
        all_effects = await self.get_entity_effects(session_id, entity_id)
        
        filtered_effects = [
            effect for effect in all_effects
            if tag in effect["effect_carrier"]["tags"]
        ]
        
        return filtered_effects
```

### **Effect Carrier 상호작용**

```python
class EffectCarrierInteraction:
    def __init__(self):
        self.interaction_handlers = {
            'combine': self.handle_combine,
            'conflict': self.handle_conflict,
            'stack': self.handle_stack,
            'upgrade': self.handle_upgrade
        }
    
    async def handle_combine(self, session_id: str, entity_id: str, 
                           effect_ids: list):
        """Effect Carrier 조합"""
        
        # 조합 가능 여부 확인
        if not await self.can_combine(effect_ids):
            raise ValueError("Cannot combine these effects")
        
        # 조합 결과 생성
        combined_effect = await self.create_combined_effect(effect_ids)
        
        # 기존 Effect Carrier 제거
        for effect_id in effect_ids:
            await self.revoke_effect(session_id, entity_id, effect_id)
        
        # 조합된 Effect Carrier 부여
        await self.grant_effect(session_id, entity_id, combined_effect["effect_id"])
        
        return combined_effect
    
    async def handle_conflict(self, session_id: str, entity_id: str, 
                            effect_id: str, conflicting_effect_id: str):
        """Effect Carrier 충돌 처리"""
        
        # 충돌 확인
        if not await self.has_conflict(effect_id, conflicting_effect_id):
            return {"conflict": False}
        
        # 충돌 해결 방법 결정
        resolution = await self.resolve_conflict(effect_id, conflicting_effect_id)
        
        if resolution["action"] == "replace":
            # 기존 Effect Carrier 제거
            await self.revoke_effect(session_id, entity_id, conflicting_effect_id)
            # 새로운 Effect Carrier 부여
            await self.grant_effect(session_id, entity_id, effect_id)
        
        elif resolution["action"] == "merge":
            # Effect Carrier 병합
            merged_effect = await self.merge_effects(effect_id, conflicting_effect_id)
            await self.revoke_effect(session_id, entity_id, conflicting_effect_id)
            await self.grant_effect(session_id, entity_id, merged_effect["effect_id"])
        
        return resolution
```

---

## 🧪 **테스트 및 검증**

### **Effect Carrier 테스트**

```python
class EffectCarrierTest:
    def __init__(self):
        self.test_results = []
    
    async def test_effect_creation(self):
        """Effect Carrier 생성 테스트"""
        
        # 스킬 생성 테스트
        skill = await self.create_test_skill()
        assert skill["carrier_type"] == "skill"
        assert skill["effect_json"]["damage"] == 50
        
        # 버프 생성 테스트
        buff = await self.create_test_buff()
        assert buff["carrier_type"] == "buff"
        assert buff["effect_json"]["stat_modifier"]["strength"] == 5
        
        # 아이템 생성 테스트
        item = await self.create_test_item()
        assert item["carrier_type"] == "item"
        assert item["effect_json"]["heal_amount"] == 50
        
        return True
    
    async def test_effect_ownership(self):
        """Effect Carrier 소유 관계 테스트"""
        
        # 엔티티에 Effect Carrier 부여
        await self.grant_effect("session_001", "entity_001", "effect_001")
        
        # 소유 관계 확인
        ownership = await self.get_ownership("session_001", "entity_001", "effect_001")
        assert ownership is not None
        
        # Effect Carrier 제거
        await self.revoke_effect("session_001", "entity_001", "effect_001")
        
        # 소유 관계 제거 확인
        ownership = await self.get_ownership("session_001", "entity_001", "effect_001")
        assert ownership is None
        
        return True
    
    async def test_effect_application(self):
        """Effect Carrier 적용 테스트"""
        
        # 스킬 적용 테스트
        skill_result = await self.apply_skill("session_001", "entity_001", "target_001")
        assert skill_result["success"] == True
        assert skill_result["damage_dealt"] == 50
        
        # 버프 적용 테스트
        buff_result = await self.apply_buff("session_001", "entity_001", "target_001")
        assert buff_result["success"] == True
        assert buff_result["stat_modifier"]["strength"] == 5
        
        # 아이템 적용 테스트
        item_result = await self.apply_item("session_001", "entity_001", "target_001")
        assert item_result["success"] == True
        assert item_result["heal_amount"] == 50
        
        return True
```

---

## 📋 **구현 체크리스트**

### **데이터베이스 설계**
- [ ] effect_carriers 테이블 생성
- [ ] entity_effect_ownership 테이블 생성
- [ ] 인덱스 생성 (GIN, B-Tree)
- [ ] 외래 키 제약조건 설정

### **Effect Carrier 관리**
- [ ] Effect Carrier 생성/수정/삭제
- [ ] 소유 관계 관리
- [ ] 제약 조건 검증
- [ ] 태그 시스템

### **Effect Carrier 적용**
- [ ] 타입별 적용 로직
- [ ] 제약 조건 확인
- [ ] 효과 계산
- [ ] 결과 로깅

### **게임플레이 통합**
- [ ] Effect Carrier 조회
- [ ] 상호작용 처리
- [ ] 충돌 해결
- [ ] 조합 시스템

### **테스트**
- [ ] 생성 테스트
- [ ] 소유 관계 테스트
- [ ] 적용 테스트
- [ ] 상호작용 테스트

---

## 🚀 **다음 단계**

1. **데이터베이스 스키마 구현**: 테이블 생성 및 인덱스 설정
2. **Effect Carrier 관리 시스템**: CRUD 기능 구현
3. **게임플레이 통합**: 게임 로직과 연동
4. **테스트 구현**: 포괄적인 테스트 케이스 작성
5. **성능 최적화**: 캐시 및 쿼리 최적화

---

**문서 작성자**: RPG Engine Development Team  
**최종 검토**: 2025-10-18  
**다음 검토 예정**: 2025-11-18
