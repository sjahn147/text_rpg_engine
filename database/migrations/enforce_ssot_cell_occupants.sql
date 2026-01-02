-- =====================================================
-- SSOT 쓰기 경로 봉쇄: cell_occupants 직접 쓰기 방지
-- =====================================================
-- 목적: entity_states.current_position이 SSOT이므로
--       cell_occupants는 자동 동기화되어야 함
-- 작성일: 2025-12-31
-- =====================================================

-- 1. cell_occupants 직접 쓰기 방지 트리거 함수 생성
CREATE OR REPLACE FUNCTION runtime_data.prevent_cell_occupants_direct_write()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 
        'cell_occupants는 직접 수정할 수 없습니다. '
        'entity_states.current_position을 수정하면 자동으로 동기화됩니다. '
        '직접 INSERT/UPDATE/DELETE를 사용하지 마세요.';
END;
$$ LANGUAGE plpgsql;

-- 트리거 생성 (idempotent)
DROP TRIGGER IF EXISTS trg_prevent_cell_occupants_direct_write ON runtime_data.cell_occupants;
CREATE TRIGGER trg_prevent_cell_occupants_direct_write
BEFORE INSERT OR UPDATE OR DELETE ON runtime_data.cell_occupants
FOR EACH ROW EXECUTE FUNCTION runtime_data.prevent_cell_occupants_direct_write();

-- 2. entity_states.current_position 변경 시 cell_occupants 자동 동기화 함수 생성
CREATE OR REPLACE FUNCTION runtime_data.sync_cell_occupants_from_position()
RETURNS TRIGGER AS $$
DECLARE
    v_runtime_cell_id UUID;
    v_old_runtime_cell_id UUID;
    v_entity_type VARCHAR(50);
    v_position JSONB;
BEGIN
    -- current_position에서 runtime_cell_id 추출
    IF NEW.current_position IS NOT NULL 
       AND jsonb_typeof(NEW.current_position -> 'runtime_cell_id') = 'string' THEN
        v_runtime_cell_id := (NEW.current_position->>'runtime_cell_id')::uuid;
    ELSE
        v_runtime_cell_id := NULL;
    END IF;
    
    -- entity_type 조회
    SELECT er.entity_type INTO v_entity_type
    FROM reference_layer.entity_references er
    WHERE er.runtime_entity_id = NEW.runtime_entity_id
    LIMIT 1;
    
    -- position 추출 (셀 내 위치 정보)
    v_position := NEW.current_position;
    IF v_position IS NOT NULL THEN
        -- runtime_cell_id는 제외하고 position만 저장
        v_position := v_position - 'runtime_cell_id';
    END IF;
    
    -- UPDATE인 경우 이전 셀 ID 추출
    IF TG_OP = 'UPDATE' AND OLD.current_position IS NOT NULL THEN
        IF jsonb_typeof(OLD.current_position -> 'runtime_cell_id') = 'string' THEN
            v_old_runtime_cell_id := (OLD.current_position->>'runtime_cell_id')::uuid;
        END IF;
    END IF;
    
    -- cell_occupants 동기화
    -- 직접 쓰기 방지 트리거를 우회하기 위해 session_replication_role을 'replica'로 설정
    -- 이렇게 하면 트리거가 비활성화됨
    PERFORM set_config('session_replication_role', 'replica', true);
    
    -- UPDATE인 경우 이전 셀에서 제거
    IF TG_OP = 'UPDATE' AND v_old_runtime_cell_id IS NOT NULL AND 
       (v_runtime_cell_id IS NULL OR v_old_runtime_cell_id != v_runtime_cell_id) THEN
        DELETE FROM runtime_data.cell_occupants
        WHERE runtime_cell_id = v_old_runtime_cell_id
          AND runtime_entity_id = NEW.runtime_entity_id;
    END IF;
    
    -- 새 셀에 추가 또는 업데이트
    IF v_runtime_cell_id IS NOT NULL THEN
        INSERT INTO runtime_data.cell_occupants 
        (runtime_cell_id, runtime_entity_id, entity_type, position, entered_at)
        VALUES (
            v_runtime_cell_id,
            NEW.runtime_entity_id,
            COALESCE(v_entity_type, 'unknown'),
            v_position,
            COALESCE(NEW.updated_at, NOW())
        )
        ON CONFLICT (runtime_cell_id, runtime_entity_id)
        DO UPDATE SET
            entity_type = EXCLUDED.entity_type,
            position = EXCLUDED.position,
            entered_at = CASE 
                WHEN cell_occupants.runtime_cell_id != EXCLUDED.runtime_cell_id 
                THEN EXCLUDED.entered_at
                ELSE cell_occupants.entered_at
            END;
    ELSE
        -- runtime_cell_id가 없으면 cell_occupants에서 제거
        DELETE FROM runtime_data.cell_occupants
        WHERE runtime_entity_id = NEW.runtime_entity_id;
    END IF;
    
    PERFORM set_config('session_replication_role', 'origin', true);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 동기화 트리거 생성 (idempotent)
DROP TRIGGER IF EXISTS trg_sync_cell_occupants_from_position ON runtime_data.entity_states;
CREATE TRIGGER trg_sync_cell_occupants_from_position
AFTER INSERT OR UPDATE OF current_position ON runtime_data.entity_states
FOR EACH ROW
EXECUTE FUNCTION runtime_data.sync_cell_occupants_from_position();

-- 3. 트리거 비활성화 옵션 (개발/디버깅용)
-- 필요시 다음 명령으로 직접 쓰기 방지 트리거를 일시적으로 비활성화할 수 있음:
-- ALTER TABLE runtime_data.cell_occupants DISABLE TRIGGER trg_prevent_cell_occupants_direct_write;

-- 4. 트리거 확인 쿼리
SELECT 
    tgname AS trigger_name,
    tgtype::text AS trigger_type,
    tgenabled AS enabled,
    pg_get_triggerdef(oid) AS trigger_definition
FROM pg_trigger
WHERE tgrelid = 'runtime_data.cell_occupants'::regclass
   OR tgrelid = 'runtime_data.entity_states'::regclass
ORDER BY tgname;

