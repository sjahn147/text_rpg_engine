-- Game Entities: Abilities - Magic
-- ID 명명 규칙: MAGIC_[속성]_[효과]_[일련번호]
-- 예시:
--   - MAGIC_FIRE_BALL_001 (화염구)
--   - MAGIC_ICE_SHIELD_001 (얼음 방패)
--   - MAGIC_LIGHT_HEAL_001 (빛의 치유)
--   - MAGIC_DARK_CURSE_001 (어둠의 저주)
CREATE TABLE game_data.abilities_magic (
    magic_id VARCHAR(50) PRIMARY KEY,
    base_property_id VARCHAR(50) NOT NULL,
    mana_cost INTEGER,
    cast_time INTEGER,
    magic_school VARCHAR(50),
    magic_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 마법 학파 인덱스
CREATE INDEX idx_magic_school ON game_data.abilities_magic(magic_school);

-- Foreign Key 제약조건 추가
ALTER TABLE game_data.abilities_magic
ADD CONSTRAINT fk_magic_base_property
FOREIGN KEY (base_property_id) 
REFERENCES game_data.base_properties(property_id);

COMMENT ON TABLE game_data.abilities_magic IS '게임 내 마법 능력 정의';
COMMENT ON COLUMN game_data.abilities_magic.magic_properties IS 'JSONB 구조: {"damage": 50, "area_effect": {"radius": 3, "type": "circle"}, "status_effects": ["burning"], ...}';

-- Game Entities: Abilities - Skills
-- ID 명명 규칙: SKILL_[직업/계열]_[효과]_[일련번호]
-- 예시:
--   - SKILL_WARRIOR_SLASH_001 (전사 베기)
--   - SKILL_ROGUE_STEALTH_001 (도적 은신)
--   - SKILL_ARCHER_SNIPE_001 (궁수 저격)
--   - SKILL_CRAFT_SMITH_001 (대장장이 제작)
CREATE TABLE game_data.abilities_skills (
    skill_id VARCHAR(50) PRIMARY KEY,
    base_property_id VARCHAR(50) NOT NULL,
    cooldown INTEGER,
    skill_type VARCHAR(50),
    skill_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 스킬 타입 인덱스
CREATE INDEX idx_skill_type ON game_data.abilities_skills(skill_type);

-- Foreign Key 제약조건 추가
ALTER TABLE game_data.abilities_skills
ADD CONSTRAINT fk_skill_base_property
FOREIGN KEY (base_property_id) 
REFERENCES game_data.base_properties(property_id);

COMMENT ON TABLE game_data.abilities_skills IS '게임 내 기술 능력 정의';
COMMENT ON COLUMN game_data.abilities_skills.skill_properties IS 'JSONB 구조: {"damage_multiplier": 1.5, "range": 2, "combo_bonus": {"hits": 3, "damage": 1.2}, ...}'; 