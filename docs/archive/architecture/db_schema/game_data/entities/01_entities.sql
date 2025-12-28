-- Game Entities: Core
-- ID 명명 규칙: [종족]_[직업/역할]_[일련번호]
-- 예시: 
--   - HUMAN_WARRIOR_001 (플레이어/NPC)
--   - ORC_MERCHANT_001 (NPC)
--   - DRAGON_BOSS_001 (몬스터)
--   - SLIME_NORMAL_001 (일반 몬스터)
CREATE TABLE game_data.entities (
    entity_id VARCHAR(50) PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL, -- player, npc, monster
    entity_name VARCHAR(100) NOT NULL,
    entity_description TEXT,
    base_stats JSONB, -- HP, MP, 기본 능력치 등
    default_equipment JSONB, -- 기본 장착 장비
    default_abilities JSONB, -- 기본 보유 능력
    default_inventory JSONB, -- 기본 보유 아이템
    entity_properties JSONB, -- 엔티티 특수 속성
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 엔티티 타입 인덱스
CREATE INDEX idx_entities_type ON game_data.entities(entity_type);

COMMENT ON TABLE game_data.entities IS '게임 내 모든 엔티티(캐릭터, NPC, 몬스터 등)의 기본 정의';
COMMENT ON COLUMN game_data.entities.base_stats IS 'JSONB 구조: {"hp": 100, "mp": 50, "strength": 10, ...}';
COMMENT ON COLUMN game_data.entities.default_equipment IS 'JSONB 구조: {"weapon": "WEAPON_SWORD_NORMAL_001", "armor": "ARMOR_PLATE_NORMAL_001", ...}';
COMMENT ON COLUMN game_data.entities.default_abilities IS 'JSONB 구조: {"skills": ["SKILL_WARRIOR_SLASH_001"], "magic": ["MAGIC_FIRE_BALL_001"], ...}';
COMMENT ON COLUMN game_data.entities.default_inventory IS 'JSONB 구조: {"items": ["ITEM_POTION_HEAL_001"], "quantities": {"ITEM_POTION_HEAL_001": 5}, ...}';
COMMENT ON COLUMN game_data.entities.entity_properties IS 'JSONB 구조: {"is_hostile": false, "interaction_flags": ["can_trade", "can_talk"], ...}'; 