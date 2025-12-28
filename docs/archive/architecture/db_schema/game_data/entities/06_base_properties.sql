-- Game Entities: Base Properties
-- ID 명명 규칙: PROP_[속성분류]_[세부속성]_[일련번호]
-- 예시:
--   - PROP_COMBAT_DAMAGE_001 (전투 데미지)
--   - PROP_MAGIC_RESIST_001 (마법 저항)
--   - PROP_CRAFT_SKILL_001 (제작 기술)
--   - PROP_TRADE_BARGAIN_001 (거래 흥정)
CREATE TABLE game_data.base_properties (
    property_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL, -- equipment, ability, item, effect
    base_effects JSONB, -- 기본 효과 정의
    requirements JSONB, -- 사용/장착 요구사항
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 속성 타입 인덱스
CREATE INDEX idx_base_properties_type ON game_data.base_properties(type);

COMMENT ON TABLE game_data.base_properties IS '게임 내 모든 속성들의 기본 정의';
COMMENT ON COLUMN game_data.base_properties.base_effects IS 'JSONB 구조: {"damage": 10, "defense": 5, "duration": 30, ...}';
COMMENT ON COLUMN game_data.base_properties.requirements IS 'JSONB 구조: {"level": 5, "strength": 10, "skills": ["SKILL_WARRIOR_BASIC"], ...}'; 