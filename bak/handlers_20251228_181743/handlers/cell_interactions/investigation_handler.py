"""
조사 핸들러
셀 조사 처리
"""
from typing import Dict, Any, Optional
from app.handlers.action_handler_base import ActionHandlerBase
from app.handlers.action_handler import ActionResult


class InvestigationHandler(ActionHandlerBase):
    """조사 핸들러"""
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """셀 조사"""
        try:
            if not self.entity_manager:
                return ActionResult.failure_result("EntityManager가 초기화되지 않았습니다.")
            
            if not self.cell_manager:
                return ActionResult.failure_result("CellManager가 초기화되지 않았습니다.")
            
            # 플레이어 엔티티 조회
            player_result = await self.entity_manager.get_entity(entity_id)
            if not player_result.success or not player_result.entity:
                return ActionResult.failure_result("플레이어를 찾을 수 없습니다.")
            
            player = player_result.entity
            
            # 현재 셀 조회
            current_cell_id = parameters.get("cell_id") if parameters else None
            if not current_cell_id:
                return ActionResult.failure_result("현재 셀 정보가 없습니다.")
            
            cell_result = await self.cell_manager.get_cell(current_cell_id)
            if not cell_result.success or not cell_result.cell:
                return ActionResult.failure_result("현재 셀을 찾을 수 없습니다.")
            
            cell = cell_result.cell
            
            # 셀 컨텐츠 로드
            content_result = await self.cell_manager.load_cell_content(current_cell_id)
            if not content_result.success:
                return ActionResult.failure_result("셀 컨텐츠를 로드할 수 없습니다.")
            
            content = content_result.content
            
            # 조사 결과 생성
            investigation_data = {
                "cell_name": cell.name,
                "cell_description": cell.description,
                "entities": content.entities,
                "objects": content.objects,
                "events": content.events,
                "cell_properties": cell.properties
            }
            
            # 조사 결과 메시지 생성
            message = f"조사 결과: {cell.name}\n"
            message += f"설명: {cell.description}\n"
            
            if content.entities:
                message += f"\n발견된 엔티티 ({len(content.entities)}개):\n"
                for entity in content.entities:
                    entity_name = getattr(entity, 'name', 'Unknown')
                    entity_type = getattr(entity, 'entity_type', 'unknown')
                    message += f"- {entity_name} ({entity_type})\n"
            
            if content.objects:
                message += f"\n발견된 오브젝트 ({len(content.objects)}개):\n"
                for obj in content.objects:
                    message += f"- {obj.get('name', 'Unknown')} ({obj.get('object_type', 'unknown')})\n"
            
            if content.events:
                message += f"\n활성 이벤트 ({len(content.events)}개):\n"
                for event in content.events:
                    message += f"- {event.get('title', 'Unknown')}\n"
            
            # 특별한 발견이 있는지 확인
            special_findings = []
            for entity in content.entities:
                entity_properties = getattr(entity, 'properties', {})
                if isinstance(entity_properties, dict) and entity_properties.get('hidden', False):
                    entity_name = getattr(entity, 'name', 'Unknown')
                    special_findings.append(f"숨겨진 {entity_name}을 발견했습니다!")
            
            if special_findings:
                message += f"\n특별한 발견:\n" + "\n".join(special_findings)
            
            return ActionResult.success_result(
                message=message,
                data=investigation_data,
                effects=[{"type": "investigation", "cell_id": current_cell_id}]
            )
            
        except Exception as e:
            self.logger.error(f"Investigate action failed: {str(e)}")
            return ActionResult.failure_result(f"조사 실패: {str(e)}")

