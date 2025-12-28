"""
대화 핸들러
NPC와의 대화 처리
"""
from typing import Dict, Any, Optional
from app.handlers.action_handler_base import ActionHandlerBase
from app.handlers.action_result import ActionResult
from app.managers.entity_manager import EntityType


class DialogueHandler(ActionHandlerBase):
    """대화 핸들러"""
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """NPC와 대화"""
        try:
            if not target_id:
                return ActionResult.failure_result("대화할 대상을 지정해주세요.")
            
            if not self.entity_manager:
                return ActionResult.failure_result("EntityManager가 초기화되지 않았습니다.")
            
            # 플레이어 엔티티 조회
            player_result = await self.entity_manager.get_entity(entity_id)
            if not player_result.success or not player_result.entity:
                return ActionResult.failure_result("플레이어를 찾을 수 없습니다.")
            
            # 대상 엔티티 조회
            target_result = await self.entity_manager.get_entity(target_id)
            if not target_result.success or not target_result.entity:
                return ActionResult.failure_result("대화 대상을 찾을 수 없습니다.")
            
            target = target_result.entity
            
            # 대화 가능 여부 확인
            if target.entity_type not in [EntityType.NPC, EntityType.PLAYER]:
                return ActionResult.failure_result(f"{target.name}과는 대화할 수 없습니다.")
            
            # 대화 컨텍스트 생성
            dialogue_data = {
                "entity_id": entity_id,
                "target_id": target_id,
                "target_name": target.name,
                "target_type": target.entity_type,
                "dialogue_topic": parameters.get("topic", "greeting") if parameters else "greeting"
            }
            
            # DB에서 대화 응답 템플릿 로드
            responses = await self._load_action_responses(target.name)
            
            topic = dialogue_data["dialogue_topic"]
            response_list = responses.get(topic, responses["greeting"])
            response = response_list[0] if response_list else f"{target.name}: 안녕하세요!"
            
            return ActionResult.success_result(
                message=response,
                data=dialogue_data,
                effects=[{"type": "dialogue", "target_id": target_id, "topic": topic}]
            )
            
        except Exception as e:
            self.logger.error(f"Dialogue action failed: {str(e)}")
            return ActionResult.failure_result(f"대화 실패: {str(e)}")
    
    async def _load_action_responses(self, target_name: str) -> Dict[str, list]:
        """DB에서 액션별 응답 템플릿 로드"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                from common.utils.jsonb_handler import parse_jsonb_data
                
                # game_data.dialogue_contexts 테이블에서 액션별 응답 로드
                responses = await conn.fetch("""
                    SELECT title, content, available_topics
                    FROM game_data.dialogue_contexts
                    WHERE entity_id IS NULL OR entity_id = ''
                    ORDER BY priority DESC
                """)
                
                # 응답을 주제별로 분류
                action_responses = {
                    "greeting": [],
                    "trade": [],
                    "farewell": []
                }
                
                for response in responses:
                    title = response['title'].lower()
                    content = response['content']
                    topics = parse_jsonb_data(response['available_topics']) or {}
                    
                    # 주제별 응답 분류
                    if 'greeting' in title or 'greeting' in topics:
                        action_responses['greeting'].append(f"{target_name}: {content}")
                    
                    if 'trade' in title or 'trade' in topics:
                        action_responses['trade'].append(f"{target_name}: {content}")
                    
                    if 'farewell' in title or 'farewell' in topics:
                        action_responses['farewell'].append(f"{target_name}: {content}")
                
                # 기본 응답이 없으면 기본값 설정
                if not any(action_responses.values()):
                    action_responses = self._get_default_action_responses(target_name)
                
                return action_responses
                
        except Exception as e:
            self.logger.error(f"Failed to load action responses: {str(e)}")
            return self._get_default_action_responses(target_name)
    
    def _get_default_action_responses(self, target_name: str) -> Dict[str, list]:
        """기본 액션 응답 템플릿 반환"""
        return {
            "greeting": [
                f"{target_name}: 안녕하세요! 무엇을 도와드릴까요?",
                f"{target_name}: 오, 새로운 얼굴이군요!",
                f"{target_name}: 여기서 뭘 하고 계신가요?"
            ],
            "trade": [
                f"{target_name}: 거래를 원하시는군요. 무엇을 사고 싶으신가요?",
                f"{target_name}: 상점에 오신 것을 환영합니다!",
                f"{target_name}: 좋은 물건들이 많이 있습니다."
            ],
            "farewell": [
                f"{target_name}: 안녕히 가세요!",
                f"{target_name}: 또 만나요!",
                f"{target_name}: 조심히 가세요!"
            ]
        }

