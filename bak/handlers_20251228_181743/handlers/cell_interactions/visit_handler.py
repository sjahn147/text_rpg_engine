"""
방문 핸들러
셀 방문 처리
"""
from typing import Dict, Any, Optional
from app.handlers.action_handler_base import ActionHandlerBase
from app.handlers.action_handler import ActionResult
from app.managers.cell_manager import CellStatus


class VisitHandler(ActionHandlerBase):
    """방문 핸들러"""
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """셀 방문"""
        try:
            if not target_id:
                return ActionResult.failure_result("방문할 대상을 지정해주세요.")
            
            if not self.cell_manager:
                return ActionResult.failure_result("CellManager가 초기화되지 않았습니다.")
            
            # 대상 셀 조회
            target_cell_result = await self.cell_manager.get_cell(target_id)
            if not target_cell_result.success or not target_cell_result.cell:
                return ActionResult.failure_result("방문할 셀을 찾을 수 없습니다.")
            
            target_cell = target_cell_result.cell
            
            # 셀 접근 가능 여부 확인
            if target_cell.status == CellStatus.LOCKED:
                return ActionResult.failure_result(f"{target_cell.name}은(는) 잠겨있습니다.")
            
            # 방문 데이터 생성
            visit_data = {
                "entity_id": entity_id,
                "target_cell_id": target_id,
                "target_cell_name": target_cell.name,
                "cell_description": target_cell.description
            }
            
            message = f"{target_cell.name}에 방문했습니다.\n"
            message += f"설명: {target_cell.description}"
            
            return ActionResult.success_result(
                message=message,
                data=visit_data,
                effects=[{"type": "visit", "cell_id": target_id}]
            )
            
        except Exception as e:
            self.logger.error(f"Visit action failed: {str(e)}")
            return ActionResult.failure_result(f"방문 실패: {str(e)}")

