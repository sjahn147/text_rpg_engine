-- =====================================================
-- 테이블 삭제 및 재생성 스크립트
-- 순환 참조 문제 해결을 위한 세션 중심 설계 적용
-- =====================================================

-- 1. 기존 테이블 삭제 (의존성 순서 고려)
-- =====================================================

-- 1.1 runtime_data 관련 테이블 삭제
DROP TABLE IF EXISTS runtime_data.dialogue_states CASCADE;
DROP TABLE IF EXISTS runtime_data.triggered_events CASCADE;
DROP TABLE IF EXISTS runtime_data.entity_states CASCADE;
DROP TABLE IF EXISTS runtime_data.object_states CASCADE;
DROP TABLE IF EXISTS runtime_data.active_sessions CASCADE;

-- 1.2 reference_layer 관련 테이블 삭제
DROP TABLE IF EXISTS reference_layer.entity_references CASCADE;
DROP TABLE IF EXISTS reference_layer.object_references CASCADE;
DROP TABLE IF EXISTS reference_layer.cell_references CASCADE;

-- 1.3 함수 및 프로시저 삭제
DROP FUNCTION IF EXISTS runtime_data.update_session_last_active() CASCADE;
DROP FUNCTION IF EXISTS reference_layer.update_session_activity() CASCADE;
DROP PROCEDURE IF EXISTS runtime_data.cleanup_session(UUID) CASCADE;
DROP PROCEDURE IF EXISTS runtime_data.cleanup_inactive_sessions(INTEGER) CASCADE;

-- 2. 새로운 테이블 생성 (세션 중심 설계)
-- =====================================================

-- 2.1 세션 테이블 (플레이어 참조 제거)
CREATE TABLE runtime_data.active_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_state VARCHAR(50) NOT NULL DEFAULT 'active',    -- 'active', 'paused', 'ending', 'closed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    metadata JSONB,                                          -- 추가 세션 정보
    player_runtime_entity_id UUID                            -- 선택적 플레이어 참조 (나중에 추가)
);

-- 2.2 엔티티 참조 테이블 (플레이어 여부 표시)
CREATE TABLE reference_layer.entity_references (
    runtime_entity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_entity_id VARCHAR(50) NOT NULL,    -- Game DB의 entity_id
    session_id UUID NOT NULL,               -- 세션 식별자
    entity_type VARCHAR(50) NOT NULL,       -- 'player', 'npc', 'monster'
    is_player BOOLEAN DEFAULT FALSE,        -- 플레이어 여부 표시
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_entity_id) REFERENCES game_data.entities(entity_id),
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id)
);

-- 2.3 오브젝트 참조 테이블
CREATE TABLE reference_layer.object_references (
    runtime_object_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_object_id VARCHAR(50) NOT NULL,    -- Game DB의 object_id
    session_id UUID NOT NULL,               -- 세션 식별자
    object_type VARCHAR(50) NOT NULL,       -- 'static', 'interactive'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_object_id) REFERENCES game_data.world_objects(object_id),
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id)
);

-- 2.4 셀 참조 테이블
CREATE TABLE reference_layer.cell_references (
    runtime_cell_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_cell_id VARCHAR(50) NOT NULL,      -- Game DB의 cell_id
    session_id UUID NOT NULL,               -- 세션 식별자
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_cell_id) REFERENCES game_data.world_cells(cell_id),
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id)
);

-- 2.5 엔티티 상태 테이블
CREATE TABLE runtime_data.entity_states (
    state_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    runtime_entity_id UUID NOT NULL,
    runtime_cell_id UUID NOT NULL,
    current_stats JSONB,                    -- 현재 스탯
    current_position JSONB,                 -- 현재 위치
    active_effects JSONB,                   -- 활성 효과
    inventory JSONB,                        -- 인벤토리
    equipped_items JSONB,                   -- 장착 아이템
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (runtime_entity_id) REFERENCES reference_layer.entity_references(runtime_entity_id),
    FOREIGN KEY (runtime_cell_id) REFERENCES reference_layer.cell_references(runtime_cell_id)
);

-- 2.6 오브젝트 상태 테이블
CREATE TABLE runtime_data.object_states (
    state_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    runtime_object_id UUID NOT NULL,
    current_state JSONB,                    -- 현재 상태
    current_position JSONB,                 -- 현재 위치
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (runtime_object_id) REFERENCES reference_layer.object_references(runtime_object_id)
);

-- 2.7 대화 상태 테이블
CREATE TABLE runtime_data.dialogue_states (
    state_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    runtime_entity_id UUID NOT NULL,
    current_context_id VARCHAR(50),
    conversation_state JSONB,               -- 현재 대화 상태
    active_topics JSONB,                    -- 현재 활성화된 대화 주제들
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (runtime_entity_id) REFERENCES reference_layer.entity_references(runtime_entity_id),
    FOREIGN KEY (current_context_id) REFERENCES game_data.dialogue_contexts(dialogue_id),
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id)
);

-- 2.8 트리거 이벤트 테이블
CREATE TABLE runtime_data.triggered_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,                       -- 이벤트 상세 데이터
    source_entity_ref UUID,                 -- 이벤트 발생 주체
    target_entity_ref UUID,                 -- 이벤트 대상
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES runtime_data.active_sessions(session_id),
    FOREIGN KEY (source_entity_ref) REFERENCES reference_layer.entity_references(runtime_entity_id),
    FOREIGN KEY (target_entity_ref) REFERENCES reference_layer.entity_references(runtime_entity_id)
);

-- 3. 외래키 제약조건 추가 (세션-플레이어)
-- =====================================================

-- 세션에 플레이어 참조 제약조건 추가
ALTER TABLE runtime_data.active_sessions 
ADD CONSTRAINT fk_session_player 
FOREIGN KEY (player_runtime_entity_id) 
REFERENCES reference_layer.entity_references(runtime_entity_id);

-- 4. 함수 및 프로시저 재생성
-- =====================================================

-- 세션 상태 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION runtime_data.update_session_last_active()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE runtime_data.active_sessions
    SET last_active_at = CURRENT_TIMESTAMP
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 참조 업데이트 시 세션 활성 시간 갱신 트리거 함수
CREATE OR REPLACE FUNCTION reference_layer.update_session_activity()
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
        
        -- entity_states 삭제
        DELETE FROM runtime_data.entity_states es
        USING reference_layer.entity_references er
        WHERE es.runtime_entity_id = er.runtime_entity_id
        AND er.session_id = p_session_id;
        
        -- object_states 삭제
        DELETE FROM runtime_data.object_states os
        USING reference_layer.object_references or_ref
        WHERE os.runtime_object_id = or_ref.runtime_object_id
        AND or_ref.session_id = p_session_id;
        
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

-- 5. 트리거 생성
-- =====================================================

-- 세션 상태 업데이트 트리거
CREATE TRIGGER tr_sessions_update_last_active
AFTER INSERT OR UPDATE ON runtime_data.active_sessions
FOR EACH ROW
EXECUTE FUNCTION runtime_data.update_session_last_active();

-- 대화 상태 업데이트 시 세션 활성 시간 갱신 트리거
CREATE TRIGGER tr_dialogue_states_update_session
AFTER INSERT OR UPDATE ON runtime_data.dialogue_states
FOR EACH ROW
EXECUTE FUNCTION runtime_data.update_session_last_active();

-- 엔티티 참조 업데이트 시 세션 활성 시간 갱신 트리거
CREATE TRIGGER tr_entity_references_update_session
AFTER INSERT OR UPDATE ON reference_layer.entity_references
FOR EACH ROW
EXECUTE FUNCTION reference_layer.update_session_activity();

-- 6. 인덱스 생성
-- =====================================================

-- 세션 관련 인덱스
CREATE INDEX idx_sessions_state ON runtime_data.active_sessions(session_state);
CREATE INDEX idx_sessions_last_active ON runtime_data.active_sessions(last_active_at);

-- 엔티티 참조 관련 인덱스
CREATE INDEX idx_entity_references_session ON reference_layer.entity_references(session_id);
CREATE INDEX idx_entity_references_type ON reference_layer.entity_references(entity_type);
CREATE INDEX idx_entity_references_player ON reference_layer.entity_references(is_player);

-- 오브젝트 참조 관련 인덱스
CREATE INDEX idx_object_references_session ON reference_layer.object_references(session_id);

-- 셀 참조 관련 인덱스
CREATE INDEX idx_cell_references_session ON reference_layer.cell_references(session_id);

-- 7. 코멘트 추가
-- =====================================================

COMMENT ON TABLE runtime_data.active_sessions IS '게임 세션 관리 테이블 (세션 중심 설계)';
COMMENT ON COLUMN runtime_data.active_sessions.session_state IS '세션 상태: active(활성), paused(일시중지), ending(종료중), closed(종료됨)';
COMMENT ON COLUMN runtime_data.active_sessions.metadata IS 'JSON 구조: {"client_info": {}, "connection_data": {}, "game_settings": {}}';
COMMENT ON COLUMN runtime_data.active_sessions.player_runtime_entity_id IS '선택적 플레이어 참조 (NULL 허용)';

COMMENT ON TABLE reference_layer.entity_references IS '엔티티 참조 테이블 (세션 중심 설계)';
COMMENT ON COLUMN reference_layer.entity_references.is_player IS '플레이어 여부 표시 (TRUE: 플레이어, FALSE: NPC/몬스터)';

COMMENT ON TABLE runtime_data.entity_states IS '엔티티 런타임 상태 테이블';
COMMENT ON TABLE runtime_data.object_states IS '오브젝트 런타임 상태 테이블';
COMMENT ON TABLE runtime_data.dialogue_states IS '대화 상태 테이블';
COMMENT ON TABLE runtime_data.triggered_events IS '트리거 이벤트 테이블';

-- =====================================================
-- 스크립트 완료
-- ===================================================== 