-- =====================================================
-- JSONB 구조 검증 CHECK 제약조건 추가
-- =====================================================
-- 목적: DB 레벨에서 JSONB 필드 구조 검증
-- 작성일: 2025-12-31
-- =====================================================

-- 1. entity_states.current_position 검증
-- 필수 키: x, y (number), runtime_cell_id (UUID 형식 문자열)
DO $$
BEGIN
    -- 기존 제약조건이 있는지 확인
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_position_structure' 
        AND conrelid = 'runtime_data.entity_states'::regclass
    ) THEN
        ALTER TABLE runtime_data.entity_states
        ADD CONSTRAINT chk_position_structure 
        CHECK (
            current_position IS NULL OR
            (
                -- x, y는 number 타입이어야 함
                jsonb_typeof(current_position -> 'x') IN ('number', 'null') AND
                jsonb_typeof(current_position -> 'y') IN ('number', 'null') AND
                -- runtime_cell_id는 UUID 형식 문자열이어야 함 (없을 수도 있음)
                (
                    NOT (current_position ? 'runtime_cell_id') OR
                    (
                        jsonb_typeof(current_position -> 'runtime_cell_id') = 'string' AND
                        (current_position->>'runtime_cell_id') ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
                    )
                )
            )
        );
        
        RAISE NOTICE '제약조건 chk_position_structure 추가 완료';
    ELSE
        RAISE NOTICE '제약조건 chk_position_structure 이미 존재함';
    END IF;
END $$;

-- 2. entity_states.inventory 검증
-- 기본 구조: object 타입, items는 array (선택적)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_inventory_structure' 
        AND conrelid = 'runtime_data.entity_states'::regclass
    ) THEN
        ALTER TABLE runtime_data.entity_states
        ADD CONSTRAINT chk_inventory_structure
        CHECK (
            inventory IS NULL OR
            (
                jsonb_typeof(inventory) = 'object' AND
                (
                    NOT (inventory ? 'items') OR
                    jsonb_typeof(inventory -> 'items') = 'array'
                )
            )
        );
        
        RAISE NOTICE '제약조건 chk_inventory_structure 추가 완료';
    ELSE
        RAISE NOTICE '제약조건 chk_inventory_structure 이미 존재함';
    END IF;
END $$;

-- 3. entity_states.current_stats 검증
-- 기본 구조: object 타입, hp, mp는 number (선택적)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_stats_structure' 
        AND conrelid = 'runtime_data.entity_states'::regclass
    ) THEN
        ALTER TABLE runtime_data.entity_states
        ADD CONSTRAINT chk_stats_structure
        CHECK (
            current_stats IS NULL OR
            (
                jsonb_typeof(current_stats) = 'object' AND
                (
                    NOT (current_stats ? 'hp') OR
                    jsonb_typeof(current_stats -> 'hp') IN ('number', 'null')
                ) AND
                (
                    NOT (current_stats ? 'mp') OR
                    jsonb_typeof(current_stats -> 'mp') IN ('number', 'null')
                )
            )
        );
        
        RAISE NOTICE '제약조건 chk_stats_structure 추가 완료';
    ELSE
        RAISE NOTICE '제약조건 chk_stats_structure 이미 존재함';
    END IF;
END $$;

-- 4. object_states.current_state 검증
-- 필수 키: state (string)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_object_state_structure' 
        AND conrelid = 'runtime_data.object_states'::regclass
    ) THEN
        ALTER TABLE runtime_data.object_states
        ADD CONSTRAINT chk_object_state_structure
        CHECK (
            current_state IS NULL OR
            (
                jsonb_typeof(current_state) = 'object' AND
                (
                    NOT (current_state ? 'state') OR
                    jsonb_typeof(current_state -> 'state') = 'string'
                )
            )
        );
        
        RAISE NOTICE '제약조건 chk_object_state_structure 추가 완료';
    ELSE
        RAISE NOTICE '제약조건 chk_object_state_structure 이미 존재함';
    END IF;
END $$;

-- 5. object_states.current_position 검증 (entity_states와 동일)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_object_position_structure' 
        AND conrelid = 'runtime_data.object_states'::regclass
    ) THEN
        ALTER TABLE runtime_data.object_states
        ADD CONSTRAINT chk_object_position_structure 
        CHECK (
            current_position IS NULL OR
            (
                jsonb_typeof(current_position -> 'x') IN ('number', 'null') AND
                jsonb_typeof(current_position -> 'y') IN ('number', 'null')
            )
        );
        
        RAISE NOTICE '제약조건 chk_object_position_structure 추가 완료';
    ELSE
        RAISE NOTICE '제약조건 chk_object_position_structure 이미 존재함';
    END IF;
END $$;

-- 검증 쿼리: 제약조건이 제대로 추가되었는지 확인
SELECT 
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid IN (
    'runtime_data.entity_states'::regclass,
    'runtime_data.object_states'::regclass
)
AND conname LIKE 'chk_%_structure'
ORDER BY conname;

