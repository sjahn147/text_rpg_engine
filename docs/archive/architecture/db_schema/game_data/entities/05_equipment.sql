-- Game Entities: Equipment - Weapons
-- ID 명명 규칙: WEAPON_[무기종류]_[등급]_[일련번호]
-- 예시:
--   - WEAPON_SWORD_NORMAL_001 (일반 검)
--   - WEAPON_BOW_RARE_001 (희귀 활)
--   - WEAPON_STAFF_UNIQUE_001 (유니크 지팡이)
--   - WEAPON_DAGGER_LEGEND_001 (전설 단검)
CREATE TABLE game_data.equipment_weapons (
    weapon_id VARCHAR(50) PRIMARY KEY,
    base_property_id VARCHAR(50) NOT NULL,
    damage INTEGER,
    weapon_type VARCHAR(50),
    durability INTEGER,
    weapon_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 무기 타입 인덱스
CREATE INDEX idx_weapons_type ON game_data.equipment_weapons(weapon_type);

-- Foreign Key 제약조건 추가
ALTER TABLE game_data.equipment_weapons
ADD CONSTRAINT fk_weapon_base_property
FOREIGN KEY (base_property_id) 
REFERENCES game_data.base_properties(property_id);

COMMENT ON TABLE game_data.equipment_weapons IS '게임 내 무기 장비 정의';
COMMENT ON COLUMN game_data.equipment_weapons.weapon_properties IS 'JSONB 구조: {"element": "fire", "critical_chance": 10, "special_effects": ["bleeding"], ...}';

-- Game Entities: Equipment - Armors
-- ID 명명 규칙: ARMOR_[방어구종류]_[등급]_[일련번호]
-- 예시:
--   - ARMOR_PLATE_NORMAL_001 (일반 판금갑옷)
--   - ARMOR_ROBE_RARE_001 (희귀 로브)
--   - ARMOR_LEATHER_UNIQUE_001 (유니크 가죽갑옷)
--   - ARMOR_SHIELD_LEGEND_001 (전설 방패)
CREATE TABLE game_data.equipment_armors (
    armor_id VARCHAR(50) PRIMARY KEY,
    base_property_id VARCHAR(50) NOT NULL,
    defense INTEGER,
    armor_type VARCHAR(50),
    weight INTEGER,
    armor_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 방어구 타입 인덱스
CREATE INDEX idx_armors_type ON game_data.equipment_armors(armor_type);

-- Foreign Key 제약조건 추가
ALTER TABLE game_data.equipment_armors
ADD CONSTRAINT fk_armor_base_property
FOREIGN KEY (base_property_id) 
REFERENCES game_data.base_properties(property_id);

COMMENT ON TABLE game_data.equipment_armors IS '게임 내 방어구 장비 정의';
COMMENT ON COLUMN game_data.equipment_armors.armor_properties IS 'JSONB 구조: {"element_resist": {"fire": 10, "ice": 5}, "movement_penalty": 2, ...}'; 