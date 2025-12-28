-- Runtime Data: Active Sessions
-- ID 명명 규칙: UUID v4 사용
CREATE TABLE runtime_data.active_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_runtime_entity_id UUID NOT NULL,
    session_state VARCHAR(50) NOT NULL DEFAULT 'active',    -- 'active', 'paused', 'ending', 'closed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    metadata JSONB,                                          -- 추가 세션 정보
    FOREIGN KEY (player_runtime_entity_id) REFERENCES reference_layer.entity_references(runtime_entity_id)
);

-- 세션 상태 업데이트 트리거
CREATE OR REPLACE FUNCTION runtime_data.update_session_last_active()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE runtime_data.active_sessions
    SET last_active_at = CURRENT_TIMESTAMP
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 세션 정리 프로시저
CREATE OR REPLACE PROCEDURE runtime_data.cleanup_session(p_session_id UUID)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 트랜잭션 시작
    BEGIN
        -- 세션 상태를 ending으로 변경
        UPDATE runtime_data.active_sessions
        SET session_state = 'ending',
            closed_at = CURRENT_TIMESTAMP
        WHERE session_id = p_session_id;

        -- dialogue_history는 보존 (나중에 분석이나 복구에 필요할 수 있음)
        
        -- dialogue_states 삭제
        DELETE FROM runtime_data.dialogue_states
        WHERE session_id = p_session_id;
        
        -- triggered_events 삭제
        DELETE FROM runtime_data.triggered_events
        WHERE session_id = p_session_id;
        
        -- reference_layer 정리
        DELETE FROM reference_layer.entity_references
        WHERE session_id = p_session_id;
        
        DELETE FROM reference_layer.object_references
        WHERE session_id = p_session_id;
        
        DELETE FROM reference_layer.cell_references
        WHERE session_id = p_session_id;
        
        -- 세션 상태를 closed로 변경
        UPDATE runtime_data.active_sessions
        SET session_state = 'closed'
        WHERE session_id = p_session_id;
        
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            -- 오류 발생 시 롤백
            ROLLBACK;
            RAISE;
    END;
END;
$$;

-- 오래된 세션 자동 정리 프로시저
CREATE OR REPLACE PROCEDURE runtime_data.cleanup_inactive_sessions(p_hours INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    v_session_id UUID;
    v_cursor CURSOR FOR
        SELECT session_id
        FROM runtime_data.active_sessions
        WHERE session_state = 'active'
        AND last_active_at < (CURRENT_TIMESTAMP - (p_hours || ' hours')::interval);
BEGIN
    OPEN v_cursor;
    LOOP
        FETCH v_cursor INTO v_session_id;
        EXIT WHEN NOT FOUND;
        
        -- 각 세션 정리
        CALL runtime_data.cleanup_session(v_session_id);
    END LOOP;
    CLOSE v_cursor;
END;
$$;

-- 인덱스 생성
CREATE INDEX idx_sessions_state ON runtime_data.active_sessions(session_state);
CREATE INDEX idx_sessions_last_active ON runtime_data.active_sessions(last_active_at);

COMMENT ON TABLE runtime_data.active_sessions IS '게임 세션 관리 테이블';
COMMENT ON COLUMN runtime_data.active_sessions.session_state IS '세션 상태: active(활성), paused(일시중지), ending(종료중), closed(종료됨)';
COMMENT ON COLUMN runtime_data.active_sessions.metadata IS 'JSON 구조: {"client_info": {}, "connection_data": {}, "game_settings": {}}'; 