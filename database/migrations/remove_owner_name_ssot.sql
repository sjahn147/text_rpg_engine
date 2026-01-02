-- =====================================================
-- SSOT Phase 3.1: owner_name 제거 마이그레이션
-- =====================================================
-- 목적: location_properties와 cell_properties에서 
--       ownership.owner_name 필드를 제거하여 SSOT 준수
-- 
-- 실행 전 주의사항:
-- 1. 백업 권장
-- 2. owner_name은 이미 JOIN으로 해결되므로 안전하게 제거 가능
-- =====================================================

-- Location의 owner_name 제거
UPDATE game_data.world_locations
SET location_properties = 
    CASE 
        WHEN location_properties->'ownership' IS NOT NULL 
        THEN jsonb_set(
            location_properties,
            '{ownership}',
            (location_properties->'ownership') - 'owner_name'
        )
        ELSE location_properties
    END
WHERE location_properties->'ownership'->>'owner_name' IS NOT NULL;

-- Cell의 owner_name 제거
UPDATE game_data.world_cells
SET cell_properties = 
    CASE 
        WHEN cell_properties->'ownership' IS NOT NULL 
        THEN jsonb_set(
            cell_properties,
            '{ownership}',
            (cell_properties->'ownership') - 'owner_name'
        )
        ELSE cell_properties
    END
WHERE cell_properties->'ownership'->>'owner_name' IS NOT NULL;

-- 검증: owner_name이 남아있는지 확인
DO $$
DECLARE
    location_count INTEGER;
    cell_count INTEGER;
BEGIN
    -- Location에서 owner_name이 남아있는지 확인
    SELECT COUNT(*) INTO location_count
    FROM game_data.world_locations
    WHERE location_properties->'ownership'->>'owner_name' IS NOT NULL;
    
    -- Cell에서 owner_name이 남아있는지 확인
    SELECT COUNT(*) INTO cell_count
    FROM game_data.world_cells
    WHERE cell_properties->'ownership'->>'owner_name' IS NOT NULL;
    
    IF location_count > 0 OR cell_count > 0 THEN
        RAISE WARNING 'owner_name이 %개 Location, %개 Cell에 남아있습니다', location_count, cell_count;
    ELSE
        RAISE NOTICE '✓ owner_name 제거 완료: 모든 Location과 Cell에서 제거되었습니다';
    END IF;
END $$;

