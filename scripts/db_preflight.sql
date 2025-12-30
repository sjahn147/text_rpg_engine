-- Preflight checks for runtime/reference integrity (read-only).
-- Run before applying migrations that enforce UUID constraints or cascades.
-- Usage: psql -f scripts/db_preflight.sql

-- 1) Non-UUID runtime_cell_id values inside entity_states.current_position
SELECT 
    COUNT(*) AS bad_runtime_cell_id_count
FROM runtime_data.entity_states es
WHERE current_position IS NOT NULL
  AND NOT (
    jsonb_typeof(current_position -> 'runtime_cell_id') = 'string'
    AND (current_position->>'runtime_cell_id') ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
  );

SELECT 
    es.state_id,
    es.runtime_entity_id,
    es.current_position
FROM runtime_data.entity_states es
WHERE current_position IS NOT NULL
  AND NOT (
    jsonb_typeof(current_position -> 'runtime_cell_id') = 'string'
    AND (current_position->>'runtime_cell_id') ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
  )
LIMIT 10;

-- 2) Orphans in reference_layer.*_references (session must exist)
SELECT 
    'entity_references' AS table_name,
    COUNT(*) AS orphan_count
FROM reference_layer.entity_references er
LEFT JOIN runtime_data.active_sessions s ON er.session_id = s.session_id
WHERE s.session_id IS NULL
UNION ALL
SELECT 
    'cell_references',
    COUNT(*)
FROM reference_layer.cell_references cr
LEFT JOIN runtime_data.active_sessions s ON cr.session_id = s.session_id
WHERE s.session_id IS NULL
UNION ALL
SELECT 
    'object_references',
    COUNT(*)
FROM reference_layer.object_references orf
LEFT JOIN runtime_data.active_sessions s ON orf.session_id = s.session_id
WHERE s.session_id IS NULL;

-- 3) Orphans in runtime_data.cell_occupants (runtime cell/entity must exist)
SELECT 
    COUNT(*) AS cell_occupant_orphans
FROM runtime_data.cell_occupants co
LEFT JOIN runtime_data.runtime_cells rc ON co.runtime_cell_id = rc.runtime_cell_id
LEFT JOIN runtime_data.runtime_entities re ON co.runtime_entity_id = re.runtime_entity_id
WHERE rc.runtime_cell_id IS NULL OR re.runtime_entity_id IS NULL;

SELECT 
    co.runtime_cell_id,
    co.runtime_entity_id,
    co.entity_type,
    co.position
FROM runtime_data.cell_occupants co
LEFT JOIN runtime_data.runtime_cells rc ON co.runtime_cell_id = rc.runtime_cell_id
LEFT JOIN runtime_data.runtime_entities re ON co.runtime_entity_id = re.runtime_entity_id
WHERE rc.runtime_cell_id IS NULL OR re.runtime_entity_id IS NULL
LIMIT 10;
