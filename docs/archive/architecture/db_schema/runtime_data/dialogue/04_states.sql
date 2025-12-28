-- 대화 상태
-- ID 명명 규칙: UUID v4 사용
CREATE TABLE runtime_data.dialogue_states (
    state_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    runtime_entity_id UUID NOT NULL,
    current_context_id VARCHAR(50),
    conversation_state JSONB,                        -- 현재 대화 상태 (json_schemas.md 참조)
    active_topics JSONB,                            -- 현재 활성화된 대화 주제들 (json_schemas.md 참조)
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (runtime_entity_id) REFERENCES reference_layer.entity_references(runtime_entity_id),
    FOREIGN KEY (current_context_id) REFERENCES game_data.dialogue_contexts(dialogue_id),
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id)
);

-- 상태 업데이트 시 세션 활성 시간 갱신 트리거
CREATE TRIGGER tr_dialogue_states_update_session
AFTER INSERT OR UPDATE ON runtime_data.dialogue_states
FOR EACH ROW
EXECUTE FUNCTION runtime_data.update_session_last_active();

COMMENT ON COLUMN runtime_data.dialogue_states.conversation_state IS 'JSON 구조: {"current_topic": "topic", "emotion": "neutral", "last_mentioned_item": null, "context_memory": [...]}';
COMMENT ON COLUMN runtime_data.dialogue_states.active_topics IS 'JSON 구조: {"current_topics": ["topic1"], "available_topics": ["topic2", "topic3"], "locked_topics": []}'; 