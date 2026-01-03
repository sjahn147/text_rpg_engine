"""
캐릭터 관련 서비스
"""
from typing import Dict, Any, List, Optional
import json
import uuid
from uuid import UUID
from app.core.game_session import GameSession
from app.services.gameplay.base_service import BaseGameplayService
from common.utils.logger import logger
from common.utils.jsonb_handler import parse_jsonb_data
from app.common.utils.uuid_helper import normalize_uuid, to_uuid


class CharacterService(BaseGameplayService):
    """캐릭터 관련 서비스"""
    
    async def get_character_stats(self, session_id: str) -> Dict[str, Any]:
        """
        캐릭터 능력치 조회
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 캐릭터 능력치 정보
        """
        try:
            # UUID 형식 검증
            session_id = normalize_uuid(session_id)
            
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("플레이어 엔티티를 찾을 수 없습니다.")
            
            player = player_entities[0]
            runtime_entity_id = player.get('runtime_entity_id')
            
            if not runtime_entity_id:
                raise ValueError("플레이어 엔티티 ID를 찾을 수 없습니다.")
            
            # UUID 객체를 문자열로 변환
            if isinstance(runtime_entity_id, UUID):
                runtime_entity_id = str(runtime_entity_id)
            elif not isinstance(runtime_entity_id, str):
                runtime_entity_id = str(runtime_entity_id)
            
            # 엔티티 정보 조회 (session_id 전달 필요)
            entity_result = await self.entity_manager.get_entity(runtime_entity_id, session_id)
            if not entity_result.success or not entity_result.entity:
                raise ValueError(f"엔티티 조회 실패: {entity_result.message}")
            
            entity = entity_result.entity
            
            # 런타임 상태에서 현재 스탯 조회
            pool = await self.db.pool
            async with pool.acquire() as conn:
                entity_state = await conn.fetchrow(
                    """
                    SELECT current_stats, current_position
                    FROM runtime_data.entity_states
                    WHERE runtime_entity_id = $1
                    """,
                    to_uuid(runtime_entity_id)
                )
            
            # 기본 스탯 (game_data.entities.base_stats)
            base_stats = entity.properties or {}
            
            # 현재 스탯 (runtime_data.entity_states.current_stats)
            current_stats = {}
            if entity_state and entity_state.get('current_stats'):
                current_stats = parse_jsonb_data(entity_state['current_stats'])
            
            # 기본 스탯과 현재 스탯 병합 (현재 스탯이 우선)
            stats = {**base_stats, **current_stats}
            
            return {
                "success": True,
                "entity_id": runtime_entity_id,
                "entity_name": entity.name,
                "stats": stats,
                "base_stats": base_stats,
                "current_stats": current_stats
            }
            
        except Exception as e:
            self.logger.error(f"캐릭터 능력치 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"캐릭터 능력치 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_character_inventory(self, session_id: str) -> Dict[str, Any]:
        """
        인벤토리 및 장착 아이템 조회 (Effect Carrier 포함)
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 인벤토리 및 장착 아이템 정보
        """
        try:
            # UUID 형식 검증
            session_id = normalize_uuid(session_id)
            
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("플레이어 엔티티를 찾을 수 없습니다.")
            
            player = player_entities[0]
            runtime_entity_id = player.get('runtime_entity_id')
            
            if not runtime_entity_id:
                raise ValueError("플레이어 엔티티 ID를 찾을 수 없습니다.")
            
            # UUID 객체를 문자열로 변환
            if isinstance(runtime_entity_id, UUID):
                runtime_entity_id = str(runtime_entity_id)
            elif not isinstance(runtime_entity_id, str):
                runtime_entity_id = str(runtime_entity_id)
            
            # 인벤토리 조회
            try:
                inventory = await self.inventory_manager.get_inventory(runtime_entity_id)
                items = inventory.get('items', [])
            except Exception as e:
                self.logger.warning(f"인벤토리 조회 실패 (기본값 사용): {str(e)}")
                items = []
            
            # 장착 아이템 조회 (entity_states.equipped_items)
            pool = await self.db.pool
            async with pool.acquire() as conn:
                entity_state = await conn.fetchrow(
                    """
                    SELECT equipped_items
                    FROM runtime_data.entity_states
                    WHERE runtime_entity_id = $1
                    """,
                    to_uuid(runtime_entity_id)
                )
            
            equipped_items = []
            if entity_state and entity_state.get('equipped_items'):
                equipped_data = parse_jsonb_data(entity_state['equipped_items'])
                # equipped_items는 {"slots": {"weapon": {...}, "armor": {...}}} 구조
                slots = equipped_data.get('slots', {})
                for slot_type, item_data in slots.items():
                    if item_data:
                        equipped_items.append({
                            "slot": slot_type,
                            **item_data
                        })
            
            # 아이템의 Effect Carrier 정보 조회
            items_with_effects = []
            for item in items:
                item_with_effect = item.copy()
                # TODO: items.effect_carrier_id FK가 추가되면 여기서 조회
                items_with_effect['effect_carrier'] = None
                items_with_effects.append(item_with_effect)
            
            equipped_with_effects = []
            for equipped in equipped_items:
                equipped_with_effect = equipped.copy()
                # TODO: equipment_weapons.effect_carrier_id, equipment_armors.effect_carrier_id FK가 추가되면 여기서 조회
                equipped_with_effect['effect_carrier'] = None
                equipped_with_effects.append(equipped_with_effect)
            
            return {
                "success": True,
                "entity_id": runtime_entity_id,
                "inventory": {
                    "items": items_with_effects,
                    "total_items": len(items)
                },
                "equipped": equipped_with_effects
            }
            
        except Exception as e:
            self.logger.error(f"인벤토리 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"인벤토리 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_character_equipped(self, session_id: str) -> Dict[str, Any]:
        """
        장착 아이템 조회 (Effect Carrier 포함)
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 장착 아이템 정보
        """
        try:
            # UUID 형식 검증
            session_id = normalize_uuid(session_id)
            
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("플레이어 엔티티를 찾을 수 없습니다.")
            
            player = player_entities[0]
            runtime_entity_id = player.get('runtime_entity_id')
            
            if not runtime_entity_id:
                raise ValueError("플레이어 엔티티 ID를 찾을 수 없습니다.")
            
            # UUID 객체를 문자열로 변환
            if isinstance(runtime_entity_id, UUID):
                runtime_entity_id = str(runtime_entity_id)
            elif not isinstance(runtime_entity_id, str):
                runtime_entity_id = str(runtime_entity_id)
            
            # 장착 아이템 조회 (entity_states.equipped_items)
            pool = await self.db.pool
            async with pool.acquire() as conn:
                entity_state = await conn.fetchrow(
                    """
                    SELECT equipped_items
                    FROM runtime_data.entity_states
                    WHERE runtime_entity_id = $1
                    """,
                    to_uuid(runtime_entity_id)
                )
            
            equipped_items = []
            if entity_state and entity_state.get('equipped_items'):
                equipped_data = parse_jsonb_data(entity_state['equipped_items'])
                # equipped_items는 {"slots": {"weapon": {...}, "armor": {...}}} 구조
                slots = equipped_data.get('slots', {})
                for slot_type, item_data in slots.items():
                    if item_data:
                        equipped_items.append({
                            "slot": slot_type,
                            **item_data
                        })
            
            # 장착 아이템의 Effect Carrier 정보 조회
            equipped_with_effects = []
            for equipped in equipped_items:
                equipped_with_effect = equipped.copy()
                # TODO: equipment_weapons.effect_carrier_id, equipment_armors.effect_carrier_id FK가 추가되면 여기서 조회
                equipped_with_effect['effect_carrier'] = None
                equipped_with_effects.append(equipped_with_effect)
            
            return {
                "success": True,
                "entity_id": runtime_entity_id,
                "equipped": equipped_with_effects
            }
            
        except Exception as e:
            self.logger.error(f"장착 아이템 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"장착 아이템 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_character_applied_effects(self, session_id: str) -> Dict[str, Any]:
        """
        적용 중인 Effect Carrier 조회
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 적용 중인 Effect Carrier 목록
        """
        try:
            # UUID 형식 검증
            session_id = normalize_uuid(session_id)
            
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("플레이어 엔티티를 찾을 수 없습니다.")
            
            player = player_entities[0]
            runtime_entity_id = player.get('runtime_entity_id')
            
            if not runtime_entity_id:
                raise ValueError("플레이어 엔티티 ID를 찾을 수 없습니다.")
            
            # UUID 객체를 문자열로 변환
            if isinstance(runtime_entity_id, UUID):
                runtime_entity_id = str(runtime_entity_id)
            elif not isinstance(runtime_entity_id, str):
                runtime_entity_id = str(runtime_entity_id)
            
            # 적용 중인 Effect Carrier 조회 (EffectCarrierManager 직접 사용)
            effects_result = await self.effect_carrier_manager.get_entity_effects(session_id, runtime_entity_id)
            if not effects_result.success:
                raise ValueError(f"Effect Carrier 조회 실패: {effects_result.message}")
            
            # EffectCarrierResult.data는 List[EffectCarrierData] 또는 None
            applied_effects = effects_result.data if effects_result.data else []
            # EffectCarrierData를 dict로 변환
            if applied_effects and isinstance(applied_effects, list):
                applied_effects = [effect.model_dump() if hasattr(effect, 'model_dump') else effect.dict() if hasattr(effect, 'dict') else effect for effect in applied_effects]
            
            return {
                "success": True,
                "entity_id": runtime_entity_id,
                "applied_effects": applied_effects
            }
            
        except Exception as e:
            self.logger.error(f"적용 중인 Effect Carrier 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"적용 중인 Effect Carrier 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_character_abilities(self, session_id: str) -> Dict[str, Any]:
        """
        엔티티의 스킬/주문 목록 조회
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 스킬 및 주문 목록
        """
        try:
            # UUID 형식 검증
            session_id = normalize_uuid(session_id)
            
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("플레이어 엔티티를 찾을 수 없습니다.")
            
            player = player_entities[0]
            runtime_entity_id = player.get('runtime_entity_id')
            game_entity_id = player.get('game_entity_id')
            
            if not runtime_entity_id or not game_entity_id:
                raise ValueError("플레이어 엔티티 ID를 찾을 수 없습니다.")
            
            # UUID 객체를 문자열로 변환
            if isinstance(runtime_entity_id, UUID):
                runtime_entity_id = str(runtime_entity_id)
            elif not isinstance(runtime_entity_id, str):
                runtime_entity_id = str(runtime_entity_id)
            
            # game_data.entities에서 default_abilities 조회
            pool = await self.db.pool
            async with pool.acquire() as conn:
                entity_data = await conn.fetchrow(
                    """
                    SELECT default_abilities
                    FROM game_data.entities
                    WHERE entity_id = $1
                    """,
                    game_entity_id
                )
                
                if not entity_data:
                    raise ValueError(f"엔티티 데이터를 찾을 수 없습니다: {game_entity_id}")
                
                default_abilities = parse_jsonb_data(entity_data.get('default_abilities', {}))
                skill_ids = default_abilities.get('skills', [])
                magic_ids = default_abilities.get('magic', [])
                
                # 스킬 상세 정보 조회
                skills = []
                if skill_ids:
                    skill_rows = await conn.fetch(
                        """
                        SELECT 
                            s.skill_id,
                            s.skill_type,
                            s.cooldown,
                            s.skill_properties,
                            bp.name as skill_name,
                            bp.description as skill_description
                        FROM game_data.abilities_skills s
                        JOIN game_data.base_properties bp ON s.base_property_id = bp.property_id
                        WHERE s.skill_id = ANY($1::VARCHAR[])
                        """,
                        skill_ids
                    )
                    for row in skill_rows:
                        skills.append({
                            "skill_id": row['skill_id'],
                            "name": row['skill_name'],
                            "description": row['skill_description'],
                            "type": row['skill_type'],
                            "cooldown": row['cooldown'],
                            "properties": parse_jsonb_data(row['skill_properties'])
                        })
                
                # 주문 상세 정보 조회
                spells = []
                if magic_ids:
                    magic_rows = await conn.fetch(
                        """
                        SELECT 
                            m.magic_id,
                            m.magic_school,
                            m.mana_cost,
                            m.cast_time,
                            m.magic_properties,
                            bp.name as magic_name,
                            bp.description as magic_description
                        FROM game_data.abilities_magic m
                        JOIN game_data.base_properties bp ON m.base_property_id = bp.property_id
                        WHERE m.magic_id = ANY($1::VARCHAR[])
                        """,
                        magic_ids
                    )
                    for row in magic_rows:
                        spells.append({
                            "magic_id": row['magic_id'],
                            "name": row['magic_name'],
                            "description": row['magic_description'],
                            "school": row['magic_school'],
                            "mana_cost": row['mana_cost'],
                            "cast_time": row['cast_time'],
                            "properties": parse_jsonb_data(row['magic_properties'])
                        })
            
            return {
                "success": True,
                "entity_id": runtime_entity_id,
                "abilities": {
                    "skills": skills,
                    "magic": spells
                }
            }
            
        except Exception as e:
            self.logger.error(f"스킬/주문 목록 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"스킬/주문 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_character_spells(self, session_id: str) -> Dict[str, Any]:
        """
        주문 목록 조회 (abilities_magic 테이블 기반)
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 주문 목록
        """
        try:
            # get_character_abilities를 호출하여 주문 목록만 반환
            abilities_result = await self.get_character_abilities(session_id)
            if not abilities_result.get('success'):
                raise ValueError(f"주문 목록 조회 실패: {abilities_result.get('message', 'Unknown error')}")
            
            return {
                "success": True,
                "entity_id": abilities_result['entity_id'],
                "spells": abilities_result['abilities']['magic']
            }
            
        except Exception as e:
            self.logger.error(f"주문 목록 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"주문 목록 조회 중 오류가 발생했습니다: {str(e)}")

