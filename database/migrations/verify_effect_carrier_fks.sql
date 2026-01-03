-- =====================================================
-- Effect Carrier FK 검증 및 추가
-- =====================================================
-- 목적: items, equipment_weapons, equipment_armors 테이블에 effect_carrier_id FK 확인 및 추가
-- 작성일: 2026-01-04
-- =====================================================

-- 사전 검증: effect_carriers 테이블이 존재하는지 확인
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'game_data' 
        AND table_name = 'effect_carriers'
    ) THEN
        RAISE EXCEPTION 'game_data.effect_carriers 테이블이 존재하지 않습니다. 먼저 effect_carriers 테이블을 생성해야 합니다.';
    END IF;
END $$;

-- 1. items 테이블에 effect_carrier_id FK 확인 및 추가
DO $$
BEGIN
    -- 컬럼 존재 여부 확인
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'game_data' 
        AND table_name = 'items' 
        AND column_name = 'effect_carrier_id'
    ) THEN
        -- 컬럼 추가
        ALTER TABLE game_data.items
        ADD COLUMN effect_carrier_id UUID;
        
        RAISE NOTICE 'game_data.items.effect_carrier_id 컬럼이 추가되었습니다.';
    ELSE
        RAISE NOTICE 'game_data.items.effect_carrier_id 컬럼이 이미 존재합니다.';
    END IF;
    
    -- FK 제약조건 확인 및 추가
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE constraint_schema = 'game_data' 
        AND table_name = 'items' 
        AND constraint_name = 'fk_items_effect_carrier'
    ) THEN
        ALTER TABLE game_data.items
        ADD CONSTRAINT fk_items_effect_carrier
            FOREIGN KEY (effect_carrier_id) 
            REFERENCES game_data.effect_carriers(effect_id) 
            ON DELETE SET NULL;
        
        RAISE NOTICE 'game_data.items.fk_items_effect_carrier 제약조건이 추가되었습니다.';
    ELSE
        RAISE NOTICE 'game_data.items.fk_items_effect_carrier 제약조건이 이미 존재합니다.';
    END IF;
    
    -- 인덱스 확인 및 추가
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE schemaname = 'game_data' 
        AND tablename = 'items' 
        AND indexname = 'idx_items_effect_carrier'
    ) THEN
        CREATE INDEX idx_items_effect_carrier 
        ON game_data.items(effect_carrier_id);
        
        RAISE NOTICE 'game_data.items.idx_items_effect_carrier 인덱스가 추가되었습니다.';
    ELSE
        RAISE NOTICE 'game_data.items.idx_items_effect_carrier 인덱스가 이미 존재합니다.';
    END IF;
END $$;

-- 2. equipment_weapons 테이블에 effect_carrier_id FK 확인 및 추가
DO $$
BEGIN
    -- 컬럼 존재 여부 확인
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'game_data' 
        AND table_name = 'equipment_weapons' 
        AND column_name = 'effect_carrier_id'
    ) THEN
        -- 컬럼 추가
        ALTER TABLE game_data.equipment_weapons
        ADD COLUMN effect_carrier_id UUID;
        
        RAISE NOTICE 'game_data.equipment_weapons.effect_carrier_id 컬럼이 추가되었습니다.';
    ELSE
        RAISE NOTICE 'game_data.equipment_weapons.effect_carrier_id 컬럼이 이미 존재합니다.';
    END IF;
    
    -- FK 제약조건 확인 및 추가
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE constraint_schema = 'game_data' 
        AND table_name = 'equipment_weapons' 
        AND constraint_name = 'fk_weapons_effect_carrier'
    ) THEN
        ALTER TABLE game_data.equipment_weapons
        ADD CONSTRAINT fk_weapons_effect_carrier
            FOREIGN KEY (effect_carrier_id) 
            REFERENCES game_data.effect_carriers(effect_id) 
            ON DELETE SET NULL;
        
        RAISE NOTICE 'game_data.equipment_weapons.fk_weapons_effect_carrier 제약조건이 추가되었습니다.';
    ELSE
        RAISE NOTICE 'game_data.equipment_weapons.fk_weapons_effect_carrier 제약조건이 이미 존재합니다.';
    END IF;
    
    -- 인덱스 확인 및 추가
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE schemaname = 'game_data' 
        AND tablename = 'equipment_weapons' 
        AND indexname = 'idx_weapons_effect_carrier'
    ) THEN
        CREATE INDEX idx_weapons_effect_carrier 
        ON game_data.equipment_weapons(effect_carrier_id);
        
        RAISE NOTICE 'game_data.equipment_weapons.idx_weapons_effect_carrier 인덱스가 추가되었습니다.';
    ELSE
        RAISE NOTICE 'game_data.equipment_weapons.idx_weapons_effect_carrier 인덱스가 이미 존재합니다.';
    END IF;
END $$;

-- 3. equipment_armors 테이블에 effect_carrier_id FK 확인 및 추가
DO $$
BEGIN
    -- 컬럼 존재 여부 확인
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'game_data' 
        AND table_name = 'equipment_armors' 
        AND column_name = 'effect_carrier_id'
    ) THEN
        -- 컬럼 추가
        ALTER TABLE game_data.equipment_armors
        ADD COLUMN effect_carrier_id UUID;
        
        RAISE NOTICE 'game_data.equipment_armors.effect_carrier_id 컬럼이 추가되었습니다.';
    ELSE
        RAISE NOTICE 'game_data.equipment_armors.effect_carrier_id 컬럼이 이미 존재합니다.';
    END IF;
    
    -- FK 제약조건 확인 및 추가
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE constraint_schema = 'game_data' 
        AND table_name = 'equipment_armors' 
        AND constraint_name = 'fk_armors_effect_carrier'
    ) THEN
        ALTER TABLE game_data.equipment_armors
        ADD CONSTRAINT fk_armors_effect_carrier
            FOREIGN KEY (effect_carrier_id) 
            REFERENCES game_data.effect_carriers(effect_id) 
            ON DELETE SET NULL;
        
        RAISE NOTICE 'game_data.equipment_armors.fk_armors_effect_carrier 제약조건이 추가되었습니다.';
    ELSE
        RAISE NOTICE 'game_data.equipment_armors.fk_armors_effect_carrier 제약조건이 이미 존재합니다.';
    END IF;
    
    -- 인덱스 확인 및 추가
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE schemaname = 'game_data' 
        AND tablename = 'equipment_armors' 
        AND indexname = 'idx_armors_effect_carrier'
    ) THEN
        CREATE INDEX idx_armors_effect_carrier 
        ON game_data.equipment_armors(effect_carrier_id);
        
        RAISE NOTICE 'game_data.equipment_armors.idx_armors_effect_carrier 인덱스가 추가되었습니다.';
    ELSE
        RAISE NOTICE 'game_data.equipment_armors.idx_armors_effect_carrier 인덱스가 이미 존재합니다.';
    END IF;
END $$;

-- 최종 검증
DO $$
BEGIN
    -- items 테이블 검증
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'game_data' 
        AND table_name = 'items' 
        AND column_name = 'effect_carrier_id'
    ) THEN
        RAISE EXCEPTION 'game_data.items.effect_carrier_id 컬럼 검증 실패';
    END IF;
    
    -- equipment_weapons 테이블 검증
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'game_data' 
        AND table_name = 'equipment_weapons' 
        AND column_name = 'effect_carrier_id'
    ) THEN
        RAISE EXCEPTION 'game_data.equipment_weapons.effect_carrier_id 컬럼 검증 실패';
    END IF;
    
    -- equipment_armors 테이블 검증
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'game_data' 
        AND table_name = 'equipment_armors' 
        AND column_name = 'effect_carrier_id'
    ) THEN
        RAISE EXCEPTION 'game_data.equipment_armors.effect_carrier_id 컬럼 검증 실패';
    END IF;
    
    RAISE NOTICE '모든 Effect Carrier FK가 성공적으로 검증되었습니다.';
END $$;

