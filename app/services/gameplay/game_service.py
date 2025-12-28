"""
게임 시작 및 상태 관리 서비스
"""
from typing import Dict, Any, Optional
import json
from app.core.game_manager import GameManager
from app.core.game_session import GameSession
from database.factories.game_data_factory import GameDataFactory
from database.factories.instance_factory import InstanceFactory
from app.services.gameplay.base_service import BaseGameplayService
from common.utils.logger import logger


class GameService(BaseGameplayService):
    """게임 시작 및 상태 관리 서비스"""
    
    def __init__(self, db_connection=None):
        super().__init__(db_connection)
        # GameManager 초기화
        self._game_manager = None
    
    @property
    def game_manager(self) -> GameManager:
        """GameManager 지연 초기화"""
        if self._game_manager is None:
            game_data_factory = GameDataFactory(self.db)
            instance_factory = InstanceFactory(self.db)
            self._game_manager = GameManager(
                db_connection=self.db,
                game_data_repo=self.game_data_repo,
                runtime_data_repo=self.runtime_data_repo,
                reference_layer_repo=self.reference_layer_repo,
                game_data_factory=game_data_factory,
                instance_factory=instance_factory
            )
        return self._game_manager
    
    async def start_game(
        self,
        player_template_id: str,
        start_cell_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        새 게임 시작
        
        Returns:
            {
                "session_id": str,
                "player_id": str,
                "current_cell_id": str,
                "game_state": {...}
            }
        """
        try:
            session_id = await self.game_manager.start_new_game(
                player_template_id=player_template_id,
                start_cell_id=start_cell_id
            )
            
            # 게임 상태 조회
            session = GameSession(session_id)
            await session.initialize_session()
            
            # 플레이어 엔티티 정보 조회
            player_entities = await session.get_player_entities()
            if not player_entities:
                raise ValueError("플레이어 엔티티를 찾을 수 없습니다.")
            
            player_id = player_entities[0]['runtime_entity_id']
            current_cell_id = player_entities[0].get('runtime_cell_id')
            
            # 게임 상태 구성
            game_state = {
                "session_id": session_id,
                "player_id": player_id,
                "current_cell_id": current_cell_id,
                "current_location": "",
                "play_time": 0,
                "flags": {},
                "variables": {},
                "save_date": "",
                "version": "1.0.0"
            }
            
            return {
                "success": True,
                "game_state": game_state,
                "message": "게임이 시작되었습니다."
            }
        except Exception as e:
            self.logger.error(f"게임 시작 실패: {str(e)}")
            raise
    
    async def get_game_state(self, session_id: str) -> Dict[str, Any]:
        """
        현재 게임 상태 조회
        
        Returns:
            {
                "session_id": str,
                "player_id": str,
                "current_cell_id": str,
                ...
            }
        """
        try:
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("세션을 찾을 수 없습니다.")
            
            player_id = player_entities[0]['runtime_entity_id']
            # current_position JSONB에서 runtime_cell_id 추출
            current_position = player_entities[0].get('current_position', {})
            if isinstance(current_position, str):
                current_position = json.loads(current_position)
            current_cell_id = current_position.get('runtime_cell_id')
            
            game_state = {
                "session_id": session_id,
                "player_id": player_id,
                "current_cell_id": current_cell_id,
                "current_location": "",
                "play_time": 0,
                "flags": {},
                "variables": {},
                "save_date": "",
                "version": "1.0.0"
            }
            
            return game_state
        except Exception as e:
            self.logger.error(f"상태 조회 실패: {str(e)}")
            raise
    
    async def get_player_inventory(self, session_id: str) -> Dict[str, Any]:
        """
        플레이어 인벤토리 조회
        
        Returns:
            {
                "success": bool,
                "inventory": List[Dict[str, Any]]
            }
        """
        try:
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("세션을 찾을 수 없습니다.")
            
            player_id = player_entities[0]['runtime_entity_id']
            
            # 인벤토리 조회
            entity_state = await self.runtime_data_repo.get_entity_state(player_id)
            
            if not entity_state:
                raise ValueError("엔티티 상태를 찾을 수 없습니다.")
            
            # 인벤토리 파싱
            inventory = entity_state.get('inventory', {})
            if isinstance(inventory, str):
                inventory = json.loads(inventory)
            
            quantities = inventory.get('quantities', {})
            
            # 아이템 정보 조회
            inventory_items = []
            for item_id, quantity in quantities.items():
                if quantity > 0:
                    item_template = await self.game_data_repo.get_item(item_id)
                    item_name = item_id
                    if item_template:
                        # base_properties에서 이름 가져오기
                        base_property_id = item_template.get('base_property_id')
                        if base_property_id:
                            pool = await self.db.pool
                            async with pool.acquire() as conn:
                                bp_row = await conn.fetchrow(
                                    """
                                    SELECT name FROM game_data.base_properties WHERE property_id = $1
                                    """,
                                    base_property_id
                                )
                                if bp_row:
                                    item_name = bp_row['name']
                    
                    inventory_items.append({
                        "item_id": item_id,
                        "quantity": quantity,
                        "name": item_name
                    })
            
            # 장착 중인 아이템 조회
            equipped_items = entity_state.get('equipped_items', {})
            if isinstance(equipped_items, str):
                equipped_items = json.loads(equipped_items)
            
            equipped_items_list = []
            for slot, item_id in equipped_items.items():
                if item_id:
                    item_template = await self.game_data_repo.get_item(item_id)
                    item_name = item_id
                    if item_template:
                        base_property_id = item_template.get('base_property_id')
                        if base_property_id:
                            pool = await self.db.pool
                            async with pool.acquire() as conn:
                                bp_row = await conn.fetchrow(
                                    """
                                    SELECT name FROM game_data.base_properties WHERE property_id = $1
                                    """,
                                    base_property_id
                                )
                                if bp_row:
                                    item_name = bp_row['name']
                    
                    equipped_items_list.append({
                        "slot": slot,
                        "item_id": item_id,
                        "name": item_name
                    })
            
            return {
                "success": True,
                "inventory": inventory_items,
                "equipped_items": equipped_items_list
            }
            
        except Exception as e:
            self.logger.error(f"인벤토리 조회 실패: {str(e)}")
            raise
    
    async def get_player_character_info(self, session_id: str) -> Dict[str, Any]:
        """
        플레이어 캐릭터 정보 조회 (스탯, HP/MP, 장비 등)
        
        Returns:
            {
                "success": bool,
                "character": {
                    "name": str,
                    "entity_type": str,
                    "level": int,
                    "stats": {...},
                    "current_hp": int,
                    "max_hp": int,
                    "current_mp": int,
                    "max_mp": int,
                    "equipped_items": [...],
                    "active_effects": [...]
                }
            }
        """
        try:
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("세션을 찾을 수 없습니다.")
            
            player_id = player_entities[0]['runtime_entity_id']
            game_entity_id = player_entities[0]['game_entity_id']
            
            # 엔티티 상태 조회
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 런타임 상태
                entity_state = await conn.fetchrow(
                    """
                    SELECT current_stats, active_effects, equipped_items
                    FROM runtime_data.entity_states
                    WHERE runtime_entity_id = $1
                    """,
                    player_id
                )
                
                # 게임 데이터 (기본 템플릿)
                game_entity = await conn.fetchrow(
                    """
                    SELECT entity_name, entity_type, entity_properties, base_stats
                    FROM game_data.entities
                    WHERE entity_id = $1
                    """,
                    game_entity_id
                )
                
                if not entity_state or not game_entity:
                    raise ValueError("캐릭터 정보를 찾을 수 없습니다.")
                
                # 스탯 파싱
                current_stats = entity_state['current_stats']
                if isinstance(current_stats, str):
                    current_stats = json.loads(current_stats)
                
                base_stats = game_entity['base_stats']
                if isinstance(base_stats, str):
                    base_stats = json.loads(base_stats)
                
                entity_properties = game_entity['entity_properties']
                if isinstance(entity_properties, str):
                    entity_properties = json.loads(entity_properties)
                
                # 활성 효과 파싱
                active_effects = entity_state['active_effects']
                if isinstance(active_effects, str):
                    active_effects = json.loads(active_effects)
                
                # 장착 아이템 파싱
                equipped_items = entity_state['equipped_items']
                if isinstance(equipped_items, str):
                    equipped_items = json.loads(equipped_items)
                
                # 장착 아이템 정보 조회
                equipped_items_info = []
                if equipped_items and isinstance(equipped_items, dict):
                    for slot, item_id in equipped_items.items():
                        if item_id:
                            item_template = await self.game_data_repo.get_item(item_id)
                            item_name = item_id
                            if item_template:
                                base_property_id = item_template.get('base_property_id')
                                if base_property_id:
                                    bp_row = await conn.fetchrow(
                                        """
                                        SELECT name FROM game_data.base_properties WHERE property_id = $1
                                        """,
                                        base_property_id
                                    )
                                    if bp_row:
                                        item_name = bp_row['name']
                            
                            equipped_items_info.append({
                                "slot": slot,
                                "item_id": item_id,
                                "name": item_name
                            })
                
                # HP/MP 계산
                current_hp = current_stats.get('hp', base_stats.get('hp', 100))
                current_mp = current_stats.get('mp', base_stats.get('mp', 50))
                max_hp = current_stats.get('max_hp', base_stats.get('hp', 100))
                max_mp = current_stats.get('max_mp', base_stats.get('mp', 50))
                
                character_info = {
                    "name": game_entity['entity_name'],
                    "entity_type": game_entity['entity_type'],
                    "level": entity_properties.get('level', 1) if entity_properties else 1,
                    "occupation": entity_properties.get('occupation', '') if entity_properties else '',
                    "stats": {
                        "strength": current_stats.get('strength', base_stats.get('strength', 10)),
                        "dexterity": current_stats.get('dexterity', base_stats.get('dexterity', 10)),
                        "constitution": current_stats.get('constitution', base_stats.get('constitution', 10)),
                        "intelligence": current_stats.get('intelligence', base_stats.get('intelligence', 10)),
                        "wisdom": current_stats.get('wisdom', base_stats.get('wisdom', 10)),
                        "charisma": current_stats.get('charisma', base_stats.get('charisma', 10)),
                    },
                    "current_hp": current_hp,
                    "max_hp": max_hp,
                    "current_mp": current_mp,
                    "max_mp": max_mp,
                    "equipped_items": equipped_items_info,
                    "active_effects": active_effects if active_effects else []
                }
                
                return {
                    "success": True,
                    "character": character_info
                }
                
        except Exception as e:
            self.logger.error(f"캐릭터 정보 조회 실패: {str(e)}")
            raise

