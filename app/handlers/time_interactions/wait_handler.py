"""
대기 핸들러
시간 대기 처리
"""
from typing import Dict, Any, Optional
from datetime import datetime
from app.handlers.action_handler_base import ActionHandlerBase
from app.handlers.action_result import ActionResult


class WaitHandler(ActionHandlerBase):
    """대기 핸들러"""
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """시간 대기"""
        try:
            # 대기 시간 설정 (기본 1시간)
            wait_hours = parameters.get("hours", 1) if parameters else 1
            
            # TimeSystem 연동
            if self.time_system:
                wait_minutes = wait_hours * 60
                await self._apply_time_cost(wait_minutes)
            
            # 대기 데이터 생성
            wait_data = {
                "entity_id": entity_id,
                "wait_hours": wait_hours,
                "timestamp": datetime.now().isoformat()
            }
            
            message = f"{wait_hours}시간 대기했습니다.\n"
            message += "시간이 흘렀고, 주변 상황이 조금씩 변했습니다."
            
            return ActionResult.success_result(
                message=message,
                data=wait_data,
                effects=[{"type": "wait", "hours": wait_hours}]
            )
            
        except Exception as e:
            self.logger.error(f"Wait action failed: {str(e)}")
            return ActionResult.failure_result(f"대기 실패: {str(e)}")

