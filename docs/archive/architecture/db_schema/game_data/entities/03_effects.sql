-- Game Entities: Effects
-- ID 명명 규칙: EFFECT_[효과종류]_[상태]_[일련번호]
-- 예시:
--   - EFFECT_BUFF_STRENGTH_001 (힘 증가)
--   - EFFECT_DEBUFF_POISON_001 (독 상태)
--   - EFFECT_CONDITION_STUN_001 (기절)
--   - EFFECT_TEMP_INVISIBLE_001 (일시적 투명)
CREATE TABLE game_data.effects (
    effect_id VARCHAR(50) PRIMARY KEY,
    base_property_id VARCHAR(50) NOT NULL,
    effect_type VARCHAR(50), -- buff, debuff, condition, temporary
    duration INTEGER, -- -1 for permanent
    effect_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 효과 타입 인덱스
CREATE INDEX idx_effect_type ON game_data.effects(effect_type);

-- Foreign Key 제약조건 추가
ALTER TABLE game_data.effects
ADD CONSTRAINT fk_effect_base_property
FOREIGN KEY (base_property_id) 
REFERENCES game_data.base_properties(property_id);

COMMENT ON TABLE game_data.effects IS '게임 내 상태 효과 정의';
COMMENT ON COLUMN game_data.effects.effect_properties IS 'JSONB 구조: {"strength_mod": 10, "tick_damage": 5, "resist_chance": 20, ...}'; 