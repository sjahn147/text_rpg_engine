"""
이동 핸들러
셀 이동 처리
"""
from typing import Dict, Any, Optional
from app.handlers.action_handler_base import ActionHandlerBase
from app.handlers.action_handler import ActionResult


class MovementHandler(ActionHandlerBase):
    """이동 핸들러"""
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """셀 이동"""
        try:
            if not target_id:
                return ActionResult.failure_result("이동할 대상을 지정해주세요.")
            
            if not self.cell_manager:
                return ActionResult.failure_result("CellManager가 초기화되지 않았습니다.")
            
            # 대상 셀 조회
            target_cell_result = await self.cell_manager.get_cell(target_id)
            if not target_cell_result.success or not target_cell_result.cell:
                return ActionResult.failure_result("이동할 셀을 찾을 수 없습니다.")
            
            target_cell = target_cell_result.cell
            
            # 이전 셀에서 엔티티 제거
            from_cell_id = parameters.get("from_cell_id") if parameters else None
            if from_cell_id:
                remove_result = await self.cell_manager.remove_entity_from_cell(entity_id, from_cell_id)
                if not remove_result.success:
                    self.logger.warning(f"Failed to remove entity from previous cell: {remove_result.message}")
            
            # 새 셀에 엔티티 추가
            add_result = await self.cell_manager.add_entity_to_cell(entity_id, target_id)
            if not add_result.success:
                return ActionResult.failure_result(f"새 셀에 엔티티를 추가할 수 없습니다: {add_result.message}")
            
            # 이동 데이터 생성
            move_data = {
                "entity_id": entity_id,
                "from_cell_id": from_cell_id,
                "to_cell_id": target_id,
                "to_cell_name": target_cell.name
            }
            
            message = f"{target_cell.name}으로 이동했습니다."
            
            return ActionResult.success_result(
                message=message,
                data=move_data,
                effects=[{"type": "move", "cell_id": target_id}]
            )
            
        except Exception as e:
            self.logger.error(f"Move action failed: {str(e)}")
            return ActionResult.failure_result(f"이동 실패: {str(e)}")

