"""
ID 생성기 - 게임 데이터 ID 생성 규칙
"""
import re
from typing import Optional, Tuple
from database.connection import DatabaseConnection
from common.utils.logger import logger


class IDGenerator:
    """게임 데이터 ID 생성기"""
    
    # ID 명명 규칙 검증 패턴
    VALIDATION_PATTERNS = {
        'region': r'^REG_[A-Z0-9_]+_\d{3}$',  # REG_[대륙]_[지역]_[일련번호]
        'location': r'^LOC_[A-Z0-9_]+_\d{3}$',  # LOC_[지역]_[장소]_[일련번호]
        'cell': r'^CELL_[A-Z0-9_]+_\d{3}$',  # CELL_[위치타입]_[세부위치]_[일련번호]
        'entity': r'^[A-Z]+_[A-Z0-9_]+_\d{3}$',  # [종족]_[직업/역할]_[일련번호]
        'object': r'^OBJ_[A-Z0-9_]+_\d{3}$',  # OBJ_[타입]_[이름]_[일련번호]
        'item': r'^ITEM_[A-Z0-9_]+_\d{3}$',  # ITEM_[타입]_[이름]_[일련번호]
        'pin': r'^PIN_[A-Z0-9_]+_\d{3}$',  # PIN_[타입]_[이름]_[일련번호]
    }
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
    
    @classmethod
    def validate_id(cls, entity_type: str, entity_id: str) -> Tuple[bool, Optional[str]]:
        """
        ID가 명명 규칙을 따르는지 검증
        
        Args:
            entity_type: 엔티티 타입 ('region', 'location', 'cell', 'entity', 'object', 'item', 'pin')
            entity_id: 검증할 ID
        
        Returns:
            (검증 성공 여부, 에러 메시지) 튜플
        """
        pattern = cls.VALIDATION_PATTERNS.get(entity_type)
        if not pattern:
            return False, f"Unknown entity type: {entity_type}. Valid types: {list(cls.VALIDATION_PATTERNS.keys())}"
        
        if not re.match(pattern, entity_id):
            expected_format = {
                'region': 'REG_[대륙]_[지역]_[일련번호]',
                'location': 'LOC_[지역]_[장소]_[일련번호]',
                'cell': 'CELL_[위치타입]_[세부위치]_[일련번호]',
                'entity': '[종족]_[직업/역할]_[일련번호]',
                'object': 'OBJ_[타입]_[이름]_[일련번호]',
                'item': 'ITEM_[타입]_[이름]_[일련번호]',
                'pin': 'PIN_[타입]_[이름]_[일련번호]',
            }.get(entity_type, '알 수 없는 형식')
            
            return False, f"Invalid {entity_type} ID format. Expected: {expected_format}, Got: {entity_id}"
        
        return True, None
    
    async def generate_location_id(self, region_id: str, location_name: str) -> str:
        """
        Location ID 생성: LOC_[지역]_[장소]_[일련번호]
        
        Args:
            region_id: 상위 Region ID (예: REG_NORTH_FOREST_001)
            location_name: Location 이름
        
        Returns:
            생성된 Location ID
        """
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # Region ID에서 지역명 추출 (REG_NORTH_FOREST_001 -> NORTH_FOREST)
                region_parts = region_id.split('_')
                if len(region_parts) < 3:
                    region_name = region_id.replace('REG_', '').split('_')[0]
                else:
                    region_name = '_'.join(region_parts[1:-1])  # REG_와 마지막 번호 제외
                
                # Location 이름을 ID 형식으로 변환 (공백 제거, 대문자)
                location_part = location_name.upper().replace(' ', '_').replace('-', '_')
                # 특수문자 제거
                location_part = ''.join(c for c in location_part if c.isalnum() or c == '_')
                
                # 기존 Location ID 조회하여 일련번호 결정
                existing_ids = await conn.fetch("""
                    SELECT location_id
                    FROM game_data.world_locations
                    WHERE location_id LIKE $1
                    ORDER BY location_id DESC
                    LIMIT 1
                """, f"LOC_{region_name}_{location_part}_%")
                
                if existing_ids:
                    last_id = existing_ids[0]['location_id']
                    # 마지막 일련번호 추출
                    last_num = int(last_id.split('_')[-1])
                    new_num = last_num + 1
                else:
                    new_num = 1
                
                # 3자리 숫자로 포맷팅
                seq = f"{new_num:03d}"
                
                return f"LOC_{region_name}_{location_part}_{seq}"
        except Exception as e:
            logger.error(f"Location ID 생성 실패: {e}")
            raise
    
    async def generate_cell_id(self, location_id: str, cell_name: str) -> str:
        """
        Cell ID 생성: CELL_[위치타입]_[세부위치]_[일련번호]
        
        Args:
            location_id: 상위 Location ID (예: LOC_NORTH_FOREST_TOWN_001)
            cell_name: Cell 이름
        
        Returns:
            생성된 Cell ID
        """
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # Location 정보 조회
                location = await conn.fetchrow("""
                    SELECT location_type, location_name
                    FROM game_data.world_locations
                    WHERE location_id = $1
                """, location_id)
                
                if not location:
                    raise ValueError(f"Location을 찾을 수 없습니다: {location_id}")
                
                # Location 타입을 위치타입으로 사용
                location_type = location['location_type'] or 'UNKNOWN'
                location_type = location_type.upper().replace(' ', '_').replace('-', '_')
                location_type = ''.join(c for c in location_type if c.isalnum() or c == '_')
                
                # Cell 이름을 세부위치로 변환
                cell_part = cell_name.upper().replace(' ', '_').replace('-', '_')
                cell_part = ''.join(c for c in cell_part if c.isalnum() or c == '_')
                
                # 기존 Cell ID 조회하여 일련번호 결정
                existing_ids = await conn.fetch("""
                    SELECT cell_id
                    FROM game_data.world_cells
                    WHERE cell_id LIKE $1
                    ORDER BY cell_id DESC
                    LIMIT 1
                """, f"CELL_{location_type}_{cell_part}_%")
                
                if existing_ids:
                    last_id = existing_ids[0]['cell_id']
                    last_num = int(last_id.split('_')[-1])
                    new_num = last_num + 1
                else:
                    new_num = 1
                
                seq = f"{new_num:03d}"
                
                return f"CELL_{location_type}_{cell_part}_{seq}"
        except Exception as e:
            logger.error(f"Cell ID 생성 실패: {e}")
            raise
    
    async def generate_entity_id(self, entity_type: str, entity_name: str) -> str:
        """
        Entity ID 생성: [종족]_[직업/역할]_[일련번호]
        
        Args:
            entity_type: 엔티티 타입 (예: npc, monster)
            entity_name: 엔티티 이름
        
        Returns:
            생성된 Entity ID
        """
        try:
            # 엔티티 이름을 ID 형식으로 변환
            name_part = entity_name.upper().replace(' ', '_').replace('-', '_')
            name_part = ''.join(c for c in name_part if c.isalnum() or c == '_')
            
            # 타입 접두사
            type_prefix = entity_type.upper()
            
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 기존 Entity ID 조회
                existing_ids = await conn.fetch("""
                    SELECT entity_id
                    FROM game_data.entities
                    WHERE entity_id LIKE $1
                    ORDER BY entity_id DESC
                    LIMIT 1
                """, f"{type_prefix}_{name_part}_%")
                
                if existing_ids:
                    last_id = existing_ids[0]['entity_id']
                    last_num = int(last_id.split('_')[-1])
                    new_num = last_num + 1
                else:
                    new_num = 1
                
                seq = f"{new_num:03d}"
                
                return f"{type_prefix}_{name_part}_{seq}"
        except Exception as e:
            logger.error(f"Entity ID 생성 실패: {e}")
            raise

