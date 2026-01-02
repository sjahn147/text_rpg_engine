-- =====================================================
-- SSOT Phase 3.2: 고아 참조 정리 마이그레이션
-- =====================================================
-- 목적: 존재하지 않는 entity_id나 cell_id를 참조하는 
--       location_properties와 cell_properties 정리
-- 
-- 실행 전 주의사항:
-- 1. 백업 필수
-- 2. 고아 참조는 null로 설정 (데이터 손실 방지)
-- =====================================================

-- 1. Location의 고아 owner_entity_id 정리
UPDATE game_data.world_locations
SET location_properties = jsonb_set(
    location_properties,
    '{ownership,owner_entity_id}',
    'null'::jsonb
)
WHERE location_properties->'ownership'->>'owner_entity_id' IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM game_data.entities 
      WHERE entity_id = location_properties->'ownership'->>'owner_entity_id'
  );

-- 2. Cell의 고아 owner_entity_id 정리
UPDATE game_data.world_cells
SET cell_properties = jsonb_set(
    cell_properties,
    '{ownership,owner_entity_id}',
    'null'::jsonb
)
WHERE cell_properties->'ownership'->>'owner_entity_id' IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM game_data.entities 
      WHERE entity_id = cell_properties->'ownership'->>'owner_entity_id'
  );

-- 3. Location의 고아 quest_givers 정리
UPDATE game_data.world_locations
SET location_properties = jsonb_set(
    location_properties,
    '{quests,quest_givers}',
    (
        SELECT jsonb_agg(elem)
        FROM jsonb_array_elements(
            COALESCE(location_properties->'quests'->'quest_givers', '[]'::jsonb)
        ) AS elem
        WHERE EXISTS (
            SELECT 1 FROM game_data.entities 
            WHERE entity_id = elem::text
        )
    )
)
WHERE location_properties->'quests'->'quest_givers' IS NOT NULL
  AND EXISTS (
      SELECT 1 
      FROM jsonb_array_elements(
          location_properties->'quests'->'quest_givers'
      ) AS elem
      WHERE NOT EXISTS (
          SELECT 1 FROM game_data.entities 
          WHERE entity_id = elem::text
      )
  );

-- 4. Location의 고아 entry_points.cell_id 정리
UPDATE game_data.world_locations
SET location_properties = jsonb_set(
    location_properties,
    '{accessibility,entry_points}',
    (
        SELECT jsonb_agg(elem)
        FROM jsonb_array_elements(
            COALESCE(location_properties->'accessibility'->'entry_points', '[]'::jsonb)
        ) AS elem
        WHERE EXISTS (
            SELECT 1 FROM game_data.world_cells 
            WHERE cell_id = elem->>'cell_id'
        )
    )
)
WHERE location_properties->'accessibility'->'entry_points' IS NOT NULL
  AND EXISTS (
      SELECT 1 
      FROM jsonb_array_elements(
          location_properties->'accessibility'->'entry_points'
      ) AS elem
      WHERE elem->>'cell_id' IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM game_data.world_cells 
            WHERE cell_id = elem->>'cell_id'
        )
  );

-- 5. Cell의 고아 structure.exits.cell_id 정리
UPDATE game_data.world_cells
SET cell_properties = jsonb_set(
    cell_properties,
    '{structure,exits}',
    (
        SELECT jsonb_agg(elem)
        FROM jsonb_array_elements(
            COALESCE(cell_properties->'structure'->'exits', '[]'::jsonb)
        ) AS elem
        WHERE elem->>'cell_id' IS NULL
           OR EXISTS (
               SELECT 1 FROM game_data.world_cells 
               WHERE cell_id = elem->>'cell_id'
           )
    )
)
WHERE cell_properties->'structure'->'exits' IS NOT NULL
  AND EXISTS (
      SELECT 1 
      FROM jsonb_array_elements(
          cell_properties->'structure'->'exits'
      ) AS elem
      WHERE elem->>'cell_id' IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM game_data.world_cells 
            WHERE cell_id = elem->>'cell_id'
        )
  );

-- 6. Cell의 고아 structure.entrances.cell_id 정리
UPDATE game_data.world_cells
SET cell_properties = jsonb_set(
    cell_properties,
    '{structure,entrances}',
    (
        SELECT jsonb_agg(elem)
        FROM jsonb_array_elements(
            COALESCE(cell_properties->'structure'->'entrances', '[]'::jsonb)
        ) AS elem
        WHERE elem->>'cell_id' IS NULL
           OR EXISTS (
               SELECT 1 FROM game_data.world_cells 
               WHERE cell_id = elem->>'cell_id'
           )
    )
)
WHERE cell_properties->'structure'->'entrances' IS NOT NULL
  AND EXISTS (
      SELECT 1 
      FROM jsonb_array_elements(
          cell_properties->'structure'->'entrances'
      ) AS elem
      WHERE elem->>'cell_id' IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM game_data.world_cells 
            WHERE cell_id = elem->>'cell_id'
        )
  );

-- 7. Cell의 고아 structure.connections.cell_id 정리
UPDATE game_data.world_cells
SET cell_properties = jsonb_set(
    cell_properties,
    '{structure,connections}',
    (
        SELECT jsonb_agg(elem)
        FROM jsonb_array_elements(
            COALESCE(cell_properties->'structure'->'connections', '[]'::jsonb)
        ) AS elem
        WHERE elem->>'cell_id' IS NULL
           OR EXISTS (
               SELECT 1 FROM game_data.world_cells 
               WHERE cell_id = elem->>'cell_id'
           )
    )
)
WHERE cell_properties->'structure'->'connections' IS NOT NULL
  AND EXISTS (
      SELECT 1 
      FROM jsonb_array_elements(
          cell_properties->'structure'->'connections'
      ) AS elem
      WHERE elem->>'cell_id' IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM game_data.world_cells 
            WHERE cell_id = elem->>'cell_id'
        )
  );

-- 검증: 고아 참조가 남아있는지 확인
DO $$
DECLARE
    orphan_location_owners INTEGER;
    orphan_cell_owners INTEGER;
    orphan_quest_givers INTEGER;
    orphan_entry_points INTEGER;
    orphan_exits INTEGER;
    orphan_entrances INTEGER;
    orphan_connections INTEGER;
BEGIN
    -- Location의 고아 owner_entity_id 확인
    SELECT COUNT(*) INTO orphan_location_owners
    FROM game_data.world_locations
    WHERE location_properties->'ownership'->>'owner_entity_id' IS NOT NULL
      AND NOT EXISTS (
          SELECT 1 FROM game_data.entities 
          WHERE entity_id = location_properties->'ownership'->>'owner_entity_id'
      );
    
    -- Cell의 고아 owner_entity_id 확인
    SELECT COUNT(*) INTO orphan_cell_owners
    FROM game_data.world_cells
    WHERE cell_properties->'ownership'->>'owner_entity_id' IS NOT NULL
      AND NOT EXISTS (
          SELECT 1 FROM game_data.entities 
          WHERE entity_id = cell_properties->'ownership'->>'owner_entity_id'
      );
    
    -- Location의 고아 quest_givers 확인
    SELECT COUNT(*) INTO orphan_quest_givers
    FROM game_data.world_locations
    WHERE location_properties->'quests'->'quest_givers' IS NOT NULL
      AND EXISTS (
          SELECT 1 
          FROM jsonb_array_elements(
              location_properties->'quests'->'quest_givers'
          ) AS elem
          WHERE NOT EXISTS (
              SELECT 1 FROM game_data.entities 
              WHERE entity_id = elem::text
          )
      );
    
    -- Location의 고아 entry_points 확인
    SELECT COUNT(*) INTO orphan_entry_points
    FROM game_data.world_locations
    WHERE location_properties->'accessibility'->'entry_points' IS NOT NULL
      AND EXISTS (
          SELECT 1 
          FROM jsonb_array_elements(
              location_properties->'accessibility'->'entry_points'
          ) AS elem
          WHERE elem->>'cell_id' IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM game_data.world_cells 
                WHERE cell_id = elem->>'cell_id'
            )
      );
    
    -- Cell의 고아 exits 확인
    SELECT COUNT(*) INTO orphan_exits
    FROM game_data.world_cells
    WHERE cell_properties->'structure'->'exits' IS NOT NULL
      AND EXISTS (
          SELECT 1 
          FROM jsonb_array_elements(
              cell_properties->'structure'->'exits'
          ) AS elem
          WHERE elem->>'cell_id' IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM game_data.world_cells 
                WHERE cell_id = elem->>'cell_id'
            )
      );
    
    -- Cell의 고아 entrances 확인
    SELECT COUNT(*) INTO orphan_entrances
    FROM game_data.world_cells
    WHERE cell_properties->'structure'->'entrances' IS NOT NULL
      AND EXISTS (
          SELECT 1 
          FROM jsonb_array_elements(
              cell_properties->'structure'->'entrances'
          ) AS elem
          WHERE elem->>'cell_id' IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM game_data.world_cells 
                WHERE cell_id = elem->>'cell_id'
            )
      );
    
    -- Cell의 고아 connections 확인
    SELECT COUNT(*) INTO orphan_connections
    FROM game_data.world_cells
    WHERE cell_properties->'structure'->'connections' IS NOT NULL
      AND EXISTS (
          SELECT 1 
          FROM jsonb_array_elements(
              cell_properties->'structure'->'connections'
          ) AS elem
          WHERE elem->>'cell_id' IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM game_data.world_cells 
                WHERE cell_id = elem->>'cell_id'
            )
      );
    
    -- 결과 출력
    IF orphan_location_owners > 0 OR orphan_cell_owners > 0 OR 
       orphan_quest_givers > 0 OR orphan_entry_points > 0 OR
       orphan_exits > 0 OR orphan_entrances > 0 OR orphan_connections > 0 THEN
        RAISE WARNING '고아 참조가 남아있습니다: Location owners: %, Cell owners: %, Quest givers: %, Entry points: %, Exits: %, Entrances: %, Connections: %',
            orphan_location_owners, orphan_cell_owners, orphan_quest_givers,
            orphan_entry_points, orphan_exits, orphan_entrances, orphan_connections;
    ELSE
        RAISE NOTICE '✓ 고아 참조 정리 완료: 모든 참조가 유효합니다';
    END IF;
END $$;

