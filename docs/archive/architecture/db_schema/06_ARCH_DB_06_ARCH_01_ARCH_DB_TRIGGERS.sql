-- =====================================================
-- 트리거 함수 수정 스크립트
-- 무한 재귀 문제 해결
-- =====================================================

-- 1. 기존 트리거 삭제
-- =====================================================

DROP TRIGGER IF EXISTS tr_sessions_update_last_active ON runtime_data.active_sessions;
DROP TRIGGER IF EXISTS tr_dialogue_states_update_session ON runtime_data.dialogue_states;
DROP TRIGGER IF EXISTS tr_entity_references_update_session ON reference_layer.entity_references;
DROP TRIGGER IF EXISTS tr_sessions_update_timestamp ON runtime_data.active_sessions;

-- 2. 트리거 함수 수정
-- =====================================================

-- 세션 상태 업데이트 트리거 함수 (무한 재귀 방지)
CREATE OR REPLACE FUNCTION runtime_data.update_session_last_active()
RETURNS TRIGGER AS $$
BEGIN
    -- 자기 자신을 업데이트하는 경우는 제외
    IF TG_TABLE_NAME = 'active_sessions' THEN
        -- active_sessions 테이블에서 직접 업데이트하는 경우는 무시
        RETURN NEW;
    END IF;
    
    -- 다른 테이블에서 세션 활성 시간 업데이트
    UPDATE runtime_data.active_sessions
    SET last_active_at = CURRENT_TIMESTAMP
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 참조 업데이트 시 세션 활성 시간 갱신 트리거 함수 (무한 재귀 방지)
CREATE OR REPLACE FUNCTION reference_layer.update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    -- 세션 활성 시간 업데이트 (무한 재귀 방지)
    UPDATE runtime_data.active_sessions
    SET last_active_at = CURRENT_TIMESTAMP
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. 트리거 재생성 (조건부)
-- =====================================================

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

-- 4. 세션 테이블 자체 업데이트 트리거 (조건부)
-- =====================================================

-- 세션 테이블 업데이트 시 last_active_at 갱신 (다른 컬럼 변경 시에만)
CREATE OR REPLACE FUNCTION runtime_data.update_session_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    -- session_state나 다른 컬럼이 변경된 경우에만 last_active_at 업데이트
    IF OLD.session_state != NEW.session_state OR 
       OLD.metadata IS DISTINCT FROM NEW.metadata THEN
        NEW.last_active_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 세션 테이블 업데이트 트리거
CREATE TRIGGER tr_sessions_update_timestamp
BEFORE UPDATE ON runtime_data.active_sessions
FOR EACH ROW
EXECUTE FUNCTION runtime_data.update_session_timestamp();

-- =====================================================
-- 스크립트 완료
-- ===================================================== 