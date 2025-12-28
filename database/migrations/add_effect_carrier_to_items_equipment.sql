-- 아이템/장비에 Effect Carrier 참조 추가
-- 하이브리드 접근법: 아이템/장비가 Effect Carrier를 소유 (선택적)

-- 1. items 테이블에 effect_carrier_id 추가
ALTER TABLE game_data.items
ADD COLUMN IF NOT EXISTS effect_carrier_id UUID,
ADD CONSTRAINT fk_items_effect_carrier
    FOREIGN KEY (effect_carrier_id) 
    REFERENCES game_data.effect_carriers(effect_id) 
    ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_items_effect_carrier 
ON game_data.items(effect_carrier_id);

COMMENT ON COLUMN game_data.items.effect_carrier_id IS 
'아이템의 효과를 담당하는 Effect Carrier ID (Optional). 효과가 있는 아이템만 참조.';

-- 2. equipment_weapons 테이블에 effect_carrier_id 추가
ALTER TABLE game_data.equipment_weapons
ADD COLUMN IF NOT EXISTS effect_carrier_id UUID,
ADD CONSTRAINT fk_weapons_effect_carrier
    FOREIGN KEY (effect_carrier_id) 
    REFERENCES game_data.effect_carriers(effect_id) 
    ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_weapons_effect_carrier 
ON game_data.equipment_weapons(effect_carrier_id);

COMMENT ON COLUMN game_data.equipment_weapons.effect_carrier_id IS 
'무기의 효과를 담당하는 Effect Carrier ID (Optional). 효과가 있는 무기만 참조.';

-- 3. equipment_armors 테이블에 effect_carrier_id 추가
ALTER TABLE game_data.equipment_armors
ADD COLUMN IF NOT EXISTS effect_carrier_id UUID,
ADD CONSTRAINT fk_armors_effect_carrier
    FOREIGN KEY (effect_carrier_id) 
    REFERENCES game_data.effect_carriers(effect_id) 
    ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_armors_effect_carrier 
ON game_data.equipment_armors(effect_carrier_id);

COMMENT ON COLUMN game_data.equipment_armors.effect_carrier_id IS 
'방어구의 효과를 담당하는 Effect Carrier ID (Optional). 효과가 있는 방어구만 참조.';

