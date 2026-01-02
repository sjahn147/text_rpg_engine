-- =====================================================
-- ENUM 타입 생성 마이그레이션
-- =====================================================
-- 목적: VARCHAR + CHECK 제약조건을 ENUM 타입으로 변경하여 타입 안전성 향상
-- 작성일: 2025-12-31
-- =====================================================

-- 1. entity_type_enum 생성
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'entity_type_enum') THEN
        CREATE TYPE entity_type_enum AS ENUM (
            'player',
            'npc',
            'monster',
            'creature'
        );
        RAISE NOTICE 'ENUM 타입 entity_type_enum 생성 완료';
    ELSE
        RAISE NOTICE 'ENUM 타입 entity_type_enum 이미 존재함';
    END IF;
END $$;

-- 2. carrier_type_enum 생성
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'carrier_type_enum') THEN
        CREATE TYPE carrier_type_enum AS ENUM (
            'skill',
            'buff',
            'item',
            'blessing',
            'curse',
            'ritual'
        );
        RAISE NOTICE 'ENUM 타입 carrier_type_enum 생성 완료';
    ELSE
        RAISE NOTICE 'ENUM 타입 carrier_type_enum 이미 존재함';
    END IF;
END $$;

-- 3. effect_type_enum 생성 (향후 사용을 위해)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'effect_type_enum') THEN
        CREATE TYPE effect_type_enum AS ENUM (
            'damage',
            'heal',
            'buff',
            'debuff',
            'status'
        );
        RAISE NOTICE 'ENUM 타입 effect_type_enum 생성 완료';
    ELSE
        RAISE NOTICE 'ENUM 타입 effect_type_enum 이미 존재함';
    END IF;
END $$;

-- =====================================================
-- 컬럼 타입 변경
-- =====================================================

-- 1. game_data.entities.entity_type 변경
DO $$
BEGIN
    -- 기존 CHECK 제약조건 제거 (있다면)
    ALTER TABLE game_data.entities DROP CONSTRAINT IF EXISTS chk_entity_type;
    
    -- 컬럼 타입 변경
    ALTER TABLE game_data.entities
    ALTER COLUMN entity_type TYPE entity_type_enum 
    USING entity_type::entity_type_enum;
    
    RAISE NOTICE 'game_data.entities.entity_type을 entity_type_enum으로 변경 완료';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'game_data.entities.entity_type 변경 실패: %', SQLERRM;
END $$;

-- 2. reference_layer.entity_references.entity_type 변경
DO $$
BEGIN
    ALTER TABLE reference_layer.entity_references
    ALTER COLUMN entity_type TYPE entity_type_enum 
    USING entity_type::entity_type_enum;
    
    RAISE NOTICE 'reference_layer.entity_references.entity_type을 entity_type_enum으로 변경 완료';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'reference_layer.entity_references.entity_type 변경 실패: %', SQLERRM;
END $$;

-- 3. runtime_data.cell_occupants.entity_type 변경
DO $$
BEGIN
    ALTER TABLE runtime_data.cell_occupants
    ALTER COLUMN entity_type TYPE entity_type_enum 
    USING entity_type::entity_type_enum;
    
    RAISE NOTICE 'runtime_data.cell_occupants.entity_type을 entity_type_enum으로 변경 완료';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'runtime_data.cell_occupants.entity_type 변경 실패: %', SQLERRM;
END $$;

-- 4. game_data.effect_carriers.carrier_type 변경
DO $$
BEGIN
    -- 기존 CHECK 제약조건 제거
    ALTER TABLE game_data.effect_carriers DROP CONSTRAINT IF EXISTS effect_carriers_carrier_type_check;
    
    -- 컬럼 타입 변경
    ALTER TABLE game_data.effect_carriers
    ALTER COLUMN carrier_type TYPE carrier_type_enum 
    USING carrier_type::carrier_type_enum;
    
    RAISE NOTICE 'game_data.effect_carriers.carrier_type을 carrier_type_enum으로 변경 완료';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'game_data.effect_carriers.carrier_type 변경 실패: %', SQLERRM;
END $$;

-- =====================================================
-- 검증 쿼리
-- =====================================================

-- ENUM 타입 확인
SELECT 
    typname AS enum_name,
    array_agg(enumlabel ORDER BY enumsortorder) AS enum_values
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
WHERE typname IN ('entity_type_enum', 'carrier_type_enum', 'effect_type_enum')
GROUP BY typname
ORDER BY typname;

