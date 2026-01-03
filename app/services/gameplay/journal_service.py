"""
저널 시스템 서비스
"""
from typing import Dict, Any, List, Optional
from app.services.gameplay.base_service import BaseGameplayService
from common.utils.logger import logger
from app.common.utils.uuid_helper import normalize_uuid, to_uuid
from common.utils.jsonb_handler import parse_jsonb_data


class JournalService(BaseGameplayService):
    """저널 시스템 서비스"""
    
    async def get_journal(self, session_id: str) -> Dict[str, Any]:
        """
        저널 데이터 통합 조회
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 저널 데이터 (퀘스트/이야기/발견/인물/장소)
        """
        try:
            session_id = normalize_uuid(session_id)
            
            # 모든 저널 데이터 조회
            story = await self.get_story_history(session_id)
            discoveries = await self.get_discoveries(session_id)
            characters = await self.get_characters(session_id)
            locations = await self.get_locations(session_id)
            
            return {
                "success": True,
                "session_id": session_id,
                "journal": {
                    "story": story.get("story", []),
                    "discoveries": discoveries.get("discoveries", []),
                    "characters": characters.get("characters", []),
                    "locations": locations.get("locations", [])
                }
            }
            
        except Exception as e:
            self.logger.error(f"저널 데이터 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"저널 데이터 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_story_history(self, session_id: str) -> Dict[str, Any]:
        """
        이야기 히스토리 조회
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 이야기 히스토리 (주요 이벤트, 선택한 분기)
        """
        try:
            session_id = normalize_uuid(session_id)
            
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # triggered_events에서 주요 이벤트 조회
                events = await conn.fetch(
                    """
                    SELECT 
                        event_id,
                        event_type,
                        event_data,
                        triggered_at,
                        source_entity_ref,
                        target_entity_ref
                    FROM runtime_data.triggered_events
                    WHERE session_id = $1
                    ORDER BY triggered_at DESC
                    LIMIT 100
                    """,
                    to_uuid(session_id)
                )
                
                # action_logs에서 주요 행동 조회
                actions = await conn.fetch(
                    """
                    SELECT 
                        log_id,
                        action,
                        success,
                        message,
                        timestamp
                    FROM runtime_data.action_logs
                    WHERE session_id = $1
                    ORDER BY timestamp DESC
                    LIMIT 50
                    """,
                    to_uuid(session_id)
                )
                
                story_entries = []
                
                # 이벤트를 이야기 항목으로 변환
                for event in events:
                    event_data = parse_jsonb_data(event.get('event_data', {}))
                    story_entries.append({
                        "id": str(event['event_id']),
                        "type": "event",
                        "event_type": event.get('event_type'),
                        "title": event_data.get('title', f"이벤트: {event.get('event_type')}"),
                        "description": event_data.get('description', ''),
                        "timestamp": event.get('triggered_at').isoformat() if event.get('triggered_at') else None,
                        "data": event_data
                    })
                
                # 행동을 이야기 항목으로 변환
                for action in actions:
                    story_entries.append({
                        "id": str(action['log_id']),
                        "type": "action",
                        "action": action.get('action'),
                        "title": f"행동: {action.get('action')}",
                        "description": action.get('message', ''),
                        "success": action.get('success'),
                        "timestamp": action.get('timestamp').isoformat() if action.get('timestamp') else None
                    })
                
                # 시간순 정렬
                story_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                return {
                    "success": True,
                    "story": story_entries
                }
                
        except Exception as e:
            self.logger.error(f"이야기 히스토리 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"이야기 히스토리 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_discoveries(self, session_id: str) -> Dict[str, Any]:
        """
        발견한 정보 조회
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 발견한 오브젝트, 셀, 엔티티
        """
        try:
            session_id = normalize_uuid(session_id)
            
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # action_logs에서 조사/검색 행동을 기반으로 발견한 항목 추론
                # 실제로는 별도 테이블이 필요하지만, 현재는 action_logs 기반으로 추론
                discoveries = await conn.fetch(
                    """
                    SELECT DISTINCT
                        message,
                        timestamp
                    FROM runtime_data.action_logs
                    WHERE session_id = $1 
                        AND (action = 'investigate' OR action = 'examine' OR action = 'search')
                        AND success = true
                    ORDER BY timestamp DESC
                    LIMIT 100
                    """,
                    to_uuid(session_id)
                )
                
                discovery_list = []
                for discovery in discoveries:
                    discovery_list.append({
                        "description": discovery.get('message', ''),
                        "timestamp": discovery.get('timestamp').isoformat() if discovery.get('timestamp') else None
                    })
                
                return {
                    "success": True,
                    "discoveries": discovery_list
                }
                
        except Exception as e:
            self.logger.error(f"발견한 정보 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"발견한 정보 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_characters(self, session_id: str) -> Dict[str, Any]:
        """
        만난 NPC 목록 및 대화 히스토리 조회
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 만난 NPC 목록 및 대화 히스토리
        """
        try:
            session_id = normalize_uuid(session_id)
            
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # dialogue_history에서 대화 기록 조회
                dialogues = await conn.fetch(
                    """
                    SELECT 
                        dh.history_id,
                        dh.runtime_entity_id,
                        dh.context_id,
                        dh.speaker_type,
                        dh.message,
                        dh.relevant_knowledge,
                        dh.timestamp,
                        er.game_entity_id,
                        e.entity_name,
                        e.entity_type
                    FROM runtime_data.dialogue_history dh
                    LEFT JOIN reference_layer.entity_references er 
                        ON dh.runtime_entity_id = er.runtime_entity_id 
                        AND dh.session_id = er.session_id
                    LEFT JOIN game_data.entities e 
                        ON er.game_entity_id = e.entity_id
                    WHERE dh.session_id = $1
                    ORDER BY dh.timestamp DESC
                    """,
                    to_uuid(session_id)
                )
                
                # NPC별로 그룹화
                npc_map = {}
                for dialogue in dialogues:
                    entity_id = str(dialogue.get('runtime_entity_id'))
                    game_entity_id = dialogue.get('game_entity_id')
                    entity_name = dialogue.get('entity_name', 'Unknown')
                    
                    if entity_id not in npc_map:
                        npc_map[entity_id] = {
                            "entity_id": entity_id,
                            "game_entity_id": game_entity_id,
                            "name": entity_name,
                            "type": dialogue.get('entity_type'),
                            "dialogues": []
                        }
                    
                    npc_map[entity_id]["dialogues"].append({
                        "history_id": str(dialogue['history_id']),
                        "context_id": dialogue.get('context_id'),
                        "speaker_type": dialogue.get('speaker_type'),
                        "message": dialogue.get('message'),
                        "relevant_knowledge": parse_jsonb_data(dialogue.get('relevant_knowledge', {})),
                        "timestamp": dialogue.get('timestamp').isoformat() if dialogue.get('timestamp') else None
                    })
                
                # 대화 시간순 정렬
                for npc in npc_map.values():
                    npc["dialogues"].sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                return {
                    "success": True,
                    "characters": list(npc_map.values())
                }
                
        except Exception as e:
            self.logger.error(f"만난 NPC 목록 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"만난 NPC 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_locations(self, session_id: str) -> Dict[str, Any]:
        """
        방문한 셀/위치 목록 조회
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 방문한 셀/위치 목록
        """
        try:
            session_id = normalize_uuid(session_id)
            
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # entity_states에서 플레이어의 위치 이력 조회
                # action_logs에서 이동 행동을 기반으로 방문한 셀 추론
                movements = await conn.fetch(
                    """
                    SELECT DISTINCT
                        message,
                        timestamp
                    FROM runtime_data.action_logs
                    WHERE session_id = $1 
                        AND (action = 'move' OR action = 'visit')
                        AND success = true
                    ORDER BY timestamp DESC
                    LIMIT 50
                    """,
                    to_uuid(session_id)
                )
                
                # 현재 위치 조회
                current_position = await conn.fetchrow(
                    """
                    SELECT 
                        es.current_position,
                        cr.game_cell_id,
                        c.cell_name,
                        c.cell_description,
                        l.location_name,
                        r.region_name
                    FROM runtime_data.entity_states es
                    LEFT JOIN reference_layer.cell_references cr 
                        ON (es.current_position->>'runtime_cell_id')::uuid = cr.runtime_cell_id
                        AND es.session_id = cr.session_id
                    LEFT JOIN game_data.world_cells c 
                        ON cr.game_cell_id = c.cell_id
                    LEFT JOIN game_data.world_locations l 
                        ON c.location_id = l.location_id
                    LEFT JOIN game_data.world_regions r 
                        ON l.region_id = r.region_id
                    WHERE es.session_id = $1
                        AND es.runtime_entity_id IN (
                            SELECT runtime_entity_id 
                            FROM reference_layer.entity_references 
                            WHERE session_id = $1 
                                AND entity_type = 'player'
                            LIMIT 1
                        )
                    LIMIT 1
                    """,
                    to_uuid(session_id)
                )
                
                locations = []
                
                # 현재 위치 추가
                if current_position:
                    locations.append({
                        "cell_id": current_position.get('game_cell_id'),
                        "cell_name": current_position.get('cell_name', 'Unknown'),
                        "location_name": current_position.get('location_name'),
                        "region_name": current_position.get('region_name'),
                        "is_current": True
                    })
                
                # 이동 이력 추가
                for movement in movements:
                    # message에서 셀 정보 추출 시도
                    message = movement.get('message', '')
                    if message:
                        locations.append({
                            "description": message,
                            "timestamp": movement.get('timestamp').isoformat() if movement.get('timestamp') else None,
                            "is_current": False
                        })
                
                return {
                    "success": True,
                    "locations": locations
                }
                
        except Exception as e:
            self.logger.error(f"방문한 위치 목록 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"방문한 위치 목록 조회 중 오류가 발생했습니다: {str(e)}")

