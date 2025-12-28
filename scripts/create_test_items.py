"""
테스트용 아이템 생성 스크립트
여관 방 오브젝트의 contents에 사용할 아이템들을 생성합니다.
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection

async def create_test_items():
    """테스트용 아이템 생성"""
    db = DatabaseConnection()
    pool = await db.pool
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Base Properties 생성
            base_properties = [
                ('PROP_ITEM_CLOTHING_001', '기본 의복', '평범한 여행자용 의복입니다.', 'item', '{}', '{}'),
                ('PROP_ITEM_TOOL_001', '여행용 도구', '여행에 필요한 기본 도구 세트입니다.', 'item', '{}', '{}'),
                ('PROP_ITEM_COIN_001', '소량의 금화', '여행에 필요한 기본 금화입니다.', 'item', '{}', '{}'),
                ('PROP_ITEM_MAP_001', '지도', '레크로스타 지역의 간단한 지도입니다.', 'item', '{}', '{}'),
                ('PROP_ITEM_PAPER_001', '종이', '빈 종이입니다.', 'item', '{}', '{}'),
                ('PROP_ITEM_PEN_001', '펜', '글을 쓸 수 있는 펜입니다.', 'item', '{}', '{}'),
            ]
            
            for prop_id, name, desc, prop_type, base_effects, requirements in base_properties:
                await conn.execute("""
                    INSERT INTO game_data.base_properties 
                    (property_id, name, description, type, base_effects, requirements)
                    VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb)
                    ON CONFLICT (property_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        type = EXCLUDED.type,
                        base_effects = EXCLUDED.base_effects,
                        requirements = EXCLUDED.requirements
                """, prop_id, name, desc, prop_type, base_effects, requirements)
            
            print("✅ Base Properties 생성 완료")
            
            # Items 생성
            items = [
                ('ITEM_CLOTHING_BASIC_001', 'PROP_ITEM_CLOTHING_001', 'clothing', 1, False, '{"description": "평범한 여행자용 의복입니다. 편안하고 실용적입니다."}'),
                ('ITEM_TOOL_TRAVEL_001', 'PROP_ITEM_TOOL_001', 'tool', 1, False, '{"description": "여행에 필요한 기본 도구 세트입니다. 밧줄, 칼, 성냥 등이 들어있습니다."}'),
                ('ITEM_COIN_GOLD_001', 'PROP_ITEM_COIN_001', 'currency', 100, False, '{"amount": 50, "description": "소량의 금화입니다."}'),
                ('ITEM_MAP_RECROSTAR_001', 'PROP_ITEM_MAP_001', 'map', 1, False, '{"region": "레크로스타", "description": "레크로스타 지역의 간단한 지도입니다."}'),
                ('ITEM_PAPER_BLANK_001', 'PROP_ITEM_PAPER_001', 'material', 10, False, '{"description": "빈 종이입니다. 메모나 편지를 쓸 수 있습니다."}'),
                ('ITEM_PEN_BASIC_001', 'PROP_ITEM_PEN_001', 'tool', 1, False, '{"description": "글을 쓸 수 있는 펜입니다."}'),
            ]
            
            for item_id, base_prop_id, item_type, stack_size, consumable, item_properties in items:
                await conn.execute("""
                    INSERT INTO game_data.items 
                    (item_id, base_property_id, item_type, stack_size, consumable, item_properties)
                    VALUES ($1, $2, $3, $4, $5, $6::jsonb)
                    ON CONFLICT (item_id) DO UPDATE SET
                        base_property_id = EXCLUDED.base_property_id,
                        item_type = EXCLUDED.item_type,
                        stack_size = EXCLUDED.stack_size,
                        consumable = EXCLUDED.consumable,
                        item_properties = EXCLUDED.item_properties
                """, item_id, base_prop_id, item_type, stack_size, consumable, item_properties)
            
            print("✅ Items 생성 완료")
            
            # 오브젝트 contents 업데이트
            # 책상: 종이, 펜
            await conn.execute("""
                UPDATE game_data.world_objects 
                SET properties = jsonb_set(
                    properties, 
                    '{contents}', 
                    '["ITEM_PAPER_BLANK_001", "ITEM_PEN_BASIC_001"]'::jsonb
                )
                WHERE object_id = 'OBJ_INN_DESK_001'
            """)
            
            # 여행 가방: 기본 의복, 여행용 도구, 소량의 금화, 지도
            await conn.execute("""
                UPDATE game_data.world_objects 
                SET properties = jsonb_set(
                    properties, 
                    '{contents}', 
                    '["ITEM_CLOTHING_BASIC_001", "ITEM_TOOL_TRAVEL_001", "ITEM_COIN_GOLD_001", "ITEM_MAP_RECROSTAR_001"]'::jsonb
                )
                WHERE object_id = 'OBJ_INN_BAG_001'
            """)
            
            print("✅ 오브젝트 contents 업데이트 완료")
            print("\n📋 생성된 아이템:")
            print("  - ITEM_CLOTHING_BASIC_001: 기본 의복")
            print("  - ITEM_TOOL_TRAVEL_001: 여행용 도구")
            print("  - ITEM_COIN_GOLD_001: 소량의 금화")
            print("  - ITEM_MAP_RECROSTAR_001: 지도")
            print("  - ITEM_PAPER_BLANK_001: 종이")
            print("  - ITEM_PEN_BASIC_001: 펜")

if __name__ == "__main__":
    asyncio.run(create_test_items())

