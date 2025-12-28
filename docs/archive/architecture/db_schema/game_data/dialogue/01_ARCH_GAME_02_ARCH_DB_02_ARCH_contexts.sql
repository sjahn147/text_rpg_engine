-- 대화 컨텍스트 정의
CREATE TABLE game_data.dialogue_contexts (
    dialogue_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,                    -- 대화 제목 (예: "상점 인사")
    content TEXT NOT NULL,                          -- 실제 대화 내용
    entity_id VARCHAR(50),                          -- NULL 허용 (모든 entity 해당)
    cell_id VARCHAR(50),                            -- NULL 허용 (모든 위치 해당)
    time_category VARCHAR(20),                      -- NULL 허용 (모든 시간 해당)
    event_id VARCHAR(50),                           -- NULL 허용 (이벤트 무관)
    priority INTEGER DEFAULT 0,                     -- 우선순위 (높을수록 우선)
    available_topics JSONB,                         -- 사용 가능한 주제 목록
    entity_personality TEXT,                        -- NPC의 성격, 말투 등 특성
    constraints JSONB,                              -- LLM 응답 제약사항
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for better query performance
CREATE INDEX idx_dialogue_contexts_composite 
ON game_data.dialogue_contexts(entity_id, cell_id, time_category, event_id);

-- 우선순위 인덱스
CREATE INDEX idx_dialogue_priority 
ON game_data.dialogue_contexts(priority DESC);

COMMENT ON TABLE game_data.dialogue_contexts IS '대화 컨텍스트와 조건을 통합 관리하는 테이블 (NULL 조건은 해당 조건이 없음을 의미)';
COMMENT ON COLUMN game_data.dialogue_contexts.available_topics IS 'JSONB 구조: {"topics": ["topic1", "topic2"], "default_topic": "greeting", "topic_requirements": {...}}';
COMMENT ON COLUMN game_data.dialogue_contexts.constraints IS 'JSONB 구조: {"max_response_length": 100, "tone": "friendly", "required_keywords": [...]}';

-- Example insertion
INSERT INTO game_data.dialogue_contexts 
(dialogue_id, title, content, entity_id, cell_id, time_category, event_id, priority, entity_personality) 
VALUES
('SHOP_GREETING_1', '상점 인사', '어서오세요. 무기 상점입니다.', 
'WEAPON_SHOP_KEEPER', 'WEAPON_SHOP', 'MORNING', NULL, 1,
'친절하고 전문적인 태도를 가진 상인. 무기에 대한 해박한 지식을 가지고 있음.'); 