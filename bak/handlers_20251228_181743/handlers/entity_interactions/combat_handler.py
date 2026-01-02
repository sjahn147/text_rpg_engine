"""
전투 핸들러
엔티티 공격 처리
"""
from typing import Dict, Any, Optional
from app.handlers.action_handler_base import ActionHandlerBase
from app.handlers.action_handler import ActionResult
from app.managers.entity_manager import EntityType


class CombatHandler(ActionHandlerBase):
    """전투 핸들러"""
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """엔티티 공격"""
        try:
            if not target_id:
                return ActionResult.failure_result("공격할 대상을 지정해주세요.")
            
            if not self.entity_manager:
                return ActionResult.failure_result("EntityManager가 초기화되지 않았습니다.")
            
            # 대상 엔티티 조회
            target_result = await self.entity_manager.get_entity(target_id)
            if not target_result.success or not target_result.entity:
                return ActionResult.failure_result("공격 대상을 찾을 수 없습니다.")
            
            target = target_result.entity
            
            # 공격 가능 여부 확인
            if target.entity_type not in [EntityType.MONSTER, EntityType.NPC, EntityType.ENEMY]:
                return ActionResult.failure_result(f"{target.name}을(를) 공격할 수 없습니다.")
            
            # 공격 데이터 생성
            attack_data = {
                "entity_id": entity_id,
                "target_id": target_id,
                "target_name": target.name,
                "damage": parameters.get("damage", 10) if parameters else 10
            }
            
            message = f"{target.name}을(를) 공격했습니다!"
            
            return ActionResult.success_result(
                message=message,
                data=attack_data,
                effects=[{"type": "attack", "target_id": target_id}]
            )
            
        except Exception as e:
            self.logger.error(f"Attack action failed: {str(e)}")
            return ActionResult.failure_result(f"공격 실패: {str(e)}")

