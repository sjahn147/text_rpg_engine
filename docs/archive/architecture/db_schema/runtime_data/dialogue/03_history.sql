-- 대화 로그
-- ID 명명 규칙: UUID v4 사용
CREATE TABLE runtime_data.dialogue_history (
    history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    runtime_entity_id UUID NOT NULL, -- 대화 상대 NPC
    context_id VARCHAR(50) NOT NULL,
    speaker_type VARCHAR(50), -- 'player', 'npc', 'system'
    message TEXT,
    relevant_knowledge JSONB, -- 이 대화에서 사용된 지식 (json_schemas.md 참조)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (runtime_entity_id) REFERENCES reference_layer.entity_references(runtime_entity_id),
    FOREIGN KEY (context_id) REFERENCES game_data.dialogue_contexts(dialogue_id),
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id)
);

-- 히스토리 추가 시 세션 활성 시간 갱신 트리거
CREATE TRIGGER tr_dialogue_history_update_session
AFTER INSERT ON runtime_data.dialogue_history
FOR EACH ROW
EXECUTE FUNCTION runtime_data.update_session_last_active();

COMMENT ON COLUMN runtime_data.dialogue_history.relevant_knowledge IS 'JSON 구조: {"knowledge_id": 123, "used_content": "content", "context_flags": ["flag1", "flag2"]}'; 