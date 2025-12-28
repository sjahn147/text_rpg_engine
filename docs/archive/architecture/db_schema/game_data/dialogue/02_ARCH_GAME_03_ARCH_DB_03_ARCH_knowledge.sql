-- 대화 주제 및 추가 정보
CREATE TABLE game_data.dialogue_topics (
    topic_id VARCHAR(50) PRIMARY KEY,
    dialogue_id VARCHAR(50) NOT NULL,
    topic_type VARCHAR(50),                         -- quest_info, world_lore, shop_items 등
    content TEXT,                                   -- 대화 관련 추가 정보
    conditions JSON,                                -- 추가 정보 제공 조건
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Foreign Key 제약조건 추가
ALTER TABLE game_data.dialogue_topics
ADD CONSTRAINT fk_topic_dialogue
FOREIGN KEY (dialogue_id) 
REFERENCES game_data.dialogue_contexts(dialogue_id);

COMMENT ON TABLE game_data.dialogue_topics IS '대화와 연관된 추가 정보나 분기를 저장하는 테이블';

-- Example insertion
INSERT INTO game_data.dialogue_topics 
(topic_id, dialogue_id, topic_type, content, conditions) 
VALUES
('SHOP_ITEMS_1', 'SHOP_GREETING_1', 'shop_items', 
'현재 판매 중인 무기 목록: 
- 철검 (100골드)
- 강철 도끼 (150골드)
- 청동 단검 (80골드)',
'{"player_level": {"min": 1, "max": 5}}'
); 

-- 대화 지식 베이스
CREATE TABLE game_data.dialogue_knowledge (
    knowledge_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,                    -- 지식 제목
    content TEXT NOT NULL,                          -- 지식 내용
    knowledge_type VARCHAR(50) NOT NULL,            -- 지식 종류 (world, quest, character 등)
    related_entities JSONB,                         -- 관련 엔티티 목록
    related_topics JSONB,                           -- 관련 대화 주제
    knowledge_properties JSONB,                     -- 지식 특수 속성
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 지식 타입 인덱스
CREATE INDEX idx_knowledge_type ON game_data.dialogue_knowledge(knowledge_type);

COMMENT ON TABLE game_data.dialogue_knowledge IS '대화 시스템에서 참조할 수 있는 지식 베이스';
COMMENT ON COLUMN game_data.dialogue_knowledge.related_entities IS 'JSONB 구조: {"npcs": ["NPC_001"], "locations": ["LOCATION_001"], ...}';
COMMENT ON COLUMN game_data.dialogue_knowledge.related_topics IS 'JSONB 구조: {"main_topics": ["topic1"], "sub_topics": ["sub1", "sub2"], ...}';
COMMENT ON COLUMN game_data.dialogue_knowledge.knowledge_properties IS 'JSONB 구조: {"importance": 5, "reveal_conditions": {"quest_stage": 2}, ...}'; 