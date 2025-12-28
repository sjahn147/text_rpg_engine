"""
대화 처리 서비스
"""
from typing import Dict, Any, Optional
from app.core.game_session import GameSession
from app.services.gameplay.base_service import BaseGameplayService
from common.utils.logger import logger


class DialogueService(BaseGameplayService):
    """대화 처리 서비스"""
    
    async def start_dialogue(
        self,
        session_id: str,
        npc_id: str
    ) -> Dict[str, Any]:
        """
        대화 시작
        
        Returns:
            {
                "success": bool,
                "dialogue": {...},
                "message": str
            }
        """
        try:
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("세션을 찾을 수 없습니다.")
            
            player_id = player_entities[0]['runtime_entity_id']
            
            # 대화 시작 (GameSession 사용)
            dialogue_id = await session.start_npc_dialogue(player_id, npc_id)
            
            if not dialogue_id:
                raise ValueError("대화를 시작할 수 없습니다.")
            
            # 대화 정보 조회 (임시)
            dialogue = {
                "dialogue_id": dialogue_id,
                "npc_name": "NPC",
                "messages": [
                    {
                        "text": "안녕하세요!",
                        "character_name": "NPC",
                        "message_id": "msg_1"
                    }
                ],
                "choices": []
            }
            
            return {
                "success": True,
                "dialogue": dialogue,
                "message": "대화를 시작했습니다."
            }
            
        except Exception as e:
            self.logger.error(f"대화 시작 실패: {str(e)}")
            raise
    
    async def process_dialogue_choice(
        self,
        session_id: str,
        dialogue_id: str,
        choice_id: str
    ) -> Dict[str, Any]:
        """
        대화 선택지 처리
        
        Returns:
            {
                "success": bool,
                "dialogue": {...}
            }
        """
        try:
            # TODO: 대화 선택지 처리 로직 구현
            # 현재는 ActionHandler에 해당 메서드가 없을 수 있음
            return {
                "success": True,
                "dialogue": {},
                "message": "대화 선택지가 처리되었습니다."
            }
        except Exception as e:
            self.logger.error(f"대화 선택지 처리 실패: {str(e)}")
            raise

