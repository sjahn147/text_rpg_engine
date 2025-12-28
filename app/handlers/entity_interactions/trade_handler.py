"""
거래 핸들러
NPC와의 거래 처리
"""
from typing import Dict, Any, Optional
from app.handlers.action_handler_base import ActionHandlerBase
from app.handlers.action_result import ActionResult
from app.managers.entity_manager import EntityType


class TradeHandler(ActionHandlerBase):
    """거래 핸들러"""
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """NPC와 거래"""
        try:
            if not target_id:
                return ActionResult.failure_result("거래할 대상을 지정해주세요.")
            
            if not self.entity_manager:
                return ActionResult.failure_result("EntityManager가 초기화되지 않았습니다.")
            
            # 대상 엔티티 조회
            target_result = await self.entity_manager.get_entity(target_id)
            if not target_result.success or not target_result.entity:
                return ActionResult.failure_result("거래 대상을 찾을 수 없습니다.")
            
            target = target_result.entity
            
            # 거래 가능 여부 확인
            if target.entity_type != EntityType.NPC:
                return ActionResult.failure_result(f"{target.name}과는 거래할 수 없습니다.")
            
            # 거래 데이터 생성
            trade_data = {
                "entity_id": entity_id,
                "target_id": target_id,
                "target_name": target.name,
                "items": target.properties.get("inventory", []),
                "gold": target.properties.get("gold", 0)
            }
            
            message = f"{target.name}과의 거래를 시작합니다.\n"
            message += f"보유 골드: {trade_data['gold']}\n"
            message += f"판매 아이템: {len(trade_data['items'])}개"
            
            return ActionResult.success_result(
                message=message,
                data=trade_data,
                effects=[{"type": "trade", "target_id": target_id}]
            )
            
        except Exception as e:
            self.logger.error(f"Trade action failed: {str(e)}")
            return ActionResult.failure_result(f"거래 실패: {str(e)}")

