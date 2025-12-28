-- 대화 상태 업데이트 프로시저
CREATE OR REPLACE PROCEDURE runtime_data.update_dialogue_state(
    p_session_id VARCHAR(100),
    p_runtime_entity_id INTEGER,
    p_conversation_state JSON,
    p_active_topics JSON,
    p_message TEXT,
    p_speaker_type VARCHAR(50),
    p_relevant_knowledge JSON DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_context_id INTEGER;
BEGIN
    -- 트랜잭션 시작
    BEGIN
        -- 현재 컨텍스트 ID 조회
        SELECT current_context_id INTO v_context_id
        FROM runtime_data.dialogue_states
        WHERE session_id = p_session_id AND runtime_entity_id = p_runtime_entity_id;

        -- 대화 상태 업데이트
        UPDATE runtime_data.dialogue_states
        SET conversation_state = p_conversation_state,
            active_topics = p_active_topics,
            last_updated = CURRENT_TIMESTAMP
        WHERE session_id = p_session_id AND runtime_entity_id = p_runtime_entity_id;

        -- 대화 히스토리 기록
        INSERT INTO runtime_data.dialogue_history
        (session_id, runtime_entity_id, context_id, speaker_type, message, relevant_knowledge)
        VALUES
        (p_session_id, p_runtime_entity_id, v_context_id, p_speaker_type, p_message, p_relevant_knowledge);

        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END;
END;
$$;

-- JSON 상태 검증 함수
CREATE OR REPLACE FUNCTION runtime_data.validate_dialogue_state(state_json JSON)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    -- 필수 필드 존재 확인
    IF NOT (
        state_json ? 'current_topic' AND
        state_json ? 'emotion'
    ) THEN
        RETURN FALSE;
    END IF;

    -- current_topic이 문자열인지 확인
    IF NOT (jsonb_typeof(state_json->'current_topic') = 'string') THEN
        RETURN FALSE;
    END IF;

    -- emotion이 허용된 값인지 확인
    IF NOT (
        state_json->>'emotion' IN ('happy', 'neutral', 'sad', 'angry', 'surprised')
    ) THEN
        RETURN FALSE;
    END IF;

    -- context_memory가 있다면 배열인지 확인
    IF state_json ? 'context_memory' AND
       NOT (jsonb_typeof(state_json->'context_memory') = 'array') THEN
        RETURN FALSE;
    END IF;

    -- context_memory 배열의 각 항목 검증
    IF state_json ? 'context_memory' THEN
        -- 배열 크기 제한 확인
        IF jsonb_array_length(state_json->'context_memory') > 5 THEN
            RETURN FALSE;
        END IF;

        -- 각 항목의 구조 확인
        FOR i IN 0..jsonb_array_length(state_json->'context_memory')-1 LOOP
            IF NOT (
                (state_json->'context_memory'->i) ? 'topic' AND
                (state_json->'context_memory'->i) ? 'timestamp' AND
                (state_json->'context_memory'->i) ? 'summary'
            ) THEN
                RETURN FALSE;
            END IF;
        END LOOP;
    END IF;

    RETURN TRUE;
END;
$$;

-- 대화 주제 검증 함수
CREATE OR REPLACE FUNCTION runtime_data.validate_dialogue_topics(topics_json JSON)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    -- 필수 필드 존재 확인
    IF NOT (
        topics_json ? 'current_topics' AND
        topics_json ? 'available_topics'
    ) THEN
        RETURN FALSE;
    END IF;

    -- 배열 타입 확인
    IF NOT (
        jsonb_typeof(topics_json->'current_topics') = 'array' AND
        jsonb_typeof(topics_json->'available_topics') = 'array'
    ) THEN
        RETURN FALSE;
    END IF;

    -- locked_topics가 있다면 배열인지 확인
    IF topics_json ? 'locked_topics' AND
       NOT (jsonb_typeof(topics_json->'locked_topics') = 'array') THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$$;

-- 상태 업데이트 전 검증 트리거
CREATE OR REPLACE FUNCTION runtime_data.validate_dialogue_state_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- conversation_state 검증
    IF NOT runtime_data.validate_dialogue_state(NEW.conversation_state) THEN
        RAISE EXCEPTION 'Invalid conversation_state structure';
    END IF;

    -- active_topics 검증
    IF NOT runtime_data.validate_dialogue_topics(NEW.active_topics) THEN
        RAISE EXCEPTION 'Invalid active_topics structure';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_validate_dialogue_state
BEFORE INSERT OR UPDATE ON runtime_data.dialogue_states
FOR EACH ROW
EXECUTE FUNCTION runtime_data.validate_dialogue_state_trigger(); 