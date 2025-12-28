-- Game Entities: Items
-- ID 명명 규칙: ITEM_[아이템종류]_[용도]_[일련번호]
-- 예시:
--   - ITEM_POTION_HEAL_001 (체력 회복 포션)
--   - ITEM_SCROLL_TELEPORT_001 (텔레포트 스크롤)
--   - ITEM_KEY_QUEST_001 (퀘스트 열쇠)
--   - ITEM_MATERIAL_CRAFT_001 (제작 재료)
CREATE TABLE game_data.inventory_items (
    item_id VARCHAR(50) PRIMARY KEY,
    base_property_id VARCHAR(50) NOT NULL,
    item_type VARCHAR(50), -- consumable, quest, misc
    stack_limit INTEGER,
    item_properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 아이템 타입 인덱스
CREATE INDEX idx_item_type ON game_data.inventory_items(item_type);

-- Foreign Key 제약조건 추가
ALTER TABLE game_data.inventory_items
ADD CONSTRAINT fk_item_base_property
FOREIGN KEY (base_property_id) 
REFERENCES game_data.base_properties(property_id);

COMMENT ON TABLE game_data.inventory_items IS '게임 내 소비/퀘스트/기타 아이템 정의';
COMMENT ON COLUMN game_data.inventory_items.item_properties IS 'JSONB 구조: {"heal_amount": 50, "duration": 30, "quest_flags": ["main_quest_1"], ...}'; 