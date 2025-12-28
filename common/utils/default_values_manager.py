"""
기본값 관리 유틸리티
DB에서 기본값을 동적으로 로드하고 관리
"""
import json
from typing import Dict, Any, Optional, List
from database.connection import DatabaseConnection
from common.utils.logger import logger


class DefaultValuesManager:
    """기본값 관리 클래스"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self._cache: Dict[str, Any] = {}
        self._cache_loaded = False
    
    async def load_default_values(self):
        """DB에서 모든 기본값 로드"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                settings = await conn.fetch("""
                    SELECT setting_id, category, setting_name, setting_value, description
                    FROM game_data.default_values
                    WHERE is_active = TRUE
                    ORDER BY category, setting_name
                """)
                
                for setting in settings:
                    self._cache[setting['setting_id']] = {
                        'category': setting['category'],
                        'name': setting['setting_name'],
                        'value': json.loads(setting['setting_value']) if isinstance(setting['setting_value'], str) else setting['setting_value'],
                        'description': setting['description']
                    }
                
                self._cache_loaded = True
                logger.info(f"Loaded {len(settings)} default values from database")
                
        except Exception as e:
            logger.error(f"Failed to load default values: {str(e)}")
            self._set_fallback_values()
    
    def _set_fallback_values(self):
        """폴백 기본값 설정"""
        self._cache = {
            'CELL_DEFAULT_SIZE': {'value': {'width': 20, 'height': 20}},
            'CELL_DEFAULT_STATUS': {'value': 'active'},
            'CELL_DEFAULT_TYPE': {'value': 'indoor'},
            'ENTITY_DEFAULT_POSITION': {'value': {'x': 0.0, 'y': 0.0}},
            'ENTITY_DEFAULT_STATUS': {'value': 'active'},
            'ENTITY_DEFAULT_TYPE': {'value': 'npc'}
        }
        self._cache_loaded = True
        logger.warning("Using fallback default values")
    
    async def get_default_value(self, setting_id: str) -> Any:
        """특정 기본값 조회"""
        if not self._cache_loaded:
            await self.load_default_values()
        
        return self._cache.get(setting_id, {}).get('value')
    
    async def get_default_values_by_category(self, category: str) -> Dict[str, Any]:
        """카테고리별 기본값 조회"""
        if not self._cache_loaded:
            await self.load_default_values()
        
        category_values = {}
        for setting_id, setting_data in self._cache.items():
            if setting_data.get('category') == category:
                category_values[setting_id] = setting_data['value']
        
        return category_values
    
    async def get_cell_defaults(self) -> Dict[str, Any]:
        """셀 관련 기본값 조회"""
        return await self.get_default_values_by_category('cell')
    
    async def get_entity_defaults(self) -> Dict[str, Any]:
        """엔티티 관련 기본값 조회"""
        return await self.get_default_values_by_category('entity')
    
    async def get_time_defaults(self) -> Dict[str, Any]:
        """시간 시스템 관련 기본값 조회"""
        return await self.get_default_values_by_category('time')
    
    async def get_dialogue_defaults(self) -> Dict[str, Any]:
        """대화 시스템 관련 기본값 조회"""
        return await self.get_default_values_by_category('dialogue')
    
    async def get_action_defaults(self) -> Dict[str, Any]:
        """액션 시스템 관련 기본값 조회"""
        return await self.get_default_values_by_category('action')
    
    async def update_default_value(self, setting_id: str, new_value: Any, description: str = None):
        """기본값 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                await conn.execute("""
                    UPDATE game_data.default_values
                    SET setting_value = $1, description = COALESCE($2, description), updated_at = CURRENT_TIMESTAMP
                    WHERE setting_id = $3
                """, json.dumps(new_value), description, setting_id)
                
                # 캐시 업데이트
                if setting_id in self._cache:
                    self._cache[setting_id]['value'] = new_value
                    if description:
                        self._cache[setting_id]['description'] = description
                
                logger.info(f"Updated default value: {setting_id}")
                
        except Exception as e:
            logger.error(f"Failed to update default value {setting_id}: {str(e)}")
    
    async def add_default_value(self, setting_id: str, category: str, setting_name: str, 
                               setting_value: Any, description: str = None):
        """새로운 기본값 추가"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO game_data.default_values 
                    (setting_id, category, setting_name, setting_value, description)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (setting_id) DO UPDATE SET
                    setting_value = EXCLUDED.setting_value,
                    description = COALESCE(EXCLUDED.description, game_data.default_values.description),
                    updated_at = CURRENT_TIMESTAMP
                """, setting_id, category, setting_name, json.dumps(setting_value), description)
                
                # 캐시 업데이트
                self._cache[setting_id] = {
                    'category': category,
                    'name': setting_name,
                    'value': setting_value,
                    'description': description
                }
                
                logger.info(f"Added default value: {setting_id}")
                
        except Exception as e:
            logger.error(f"Failed to add default value {setting_id}: {str(e)}")
    
    def get_cached_value(self, setting_id: str) -> Any:
        """캐시된 기본값 조회 (동기)"""
        return self._cache.get(setting_id, {}).get('value')
    
    def clear_cache(self):
        """캐시 초기화"""
        self._cache.clear()
        self._cache_loaded = False
        logger.info("Default values cache cleared")
