-- =====================================================
-- 핀 이름 필드 추가 마이그레이션
-- =====================================================

-- pin_name 컬럼 추가
ALTER TABLE game_data.pin_positions
ADD COLUMN IF NOT EXISTS pin_name VARCHAR(100) DEFAULT '새 핀 01';

-- 기존 데이터에 기본 이름 설정 (CTE 사용)
WITH numbered_pins AS (
    SELECT 
        pin_id,
        '새 핀 ' || LPAD(ROW_NUMBER() OVER (ORDER BY created_at)::text, 2, '0') AS new_name
    FROM game_data.pin_positions
    WHERE pin_name IS NULL OR pin_name = '새 핀 01'
)
UPDATE game_data.pin_positions
SET pin_name = numbered_pins.new_name
FROM numbered_pins
WHERE pin_positions.pin_id = numbered_pins.pin_id;

-- NOT NULL 제약조건 추가
ALTER TABLE game_data.pin_positions
ALTER COLUMN pin_name SET NOT NULL;

COMMENT ON COLUMN game_data.pin_positions.pin_name IS '핀 표시 이름 (사용자 친화적 이름)';

