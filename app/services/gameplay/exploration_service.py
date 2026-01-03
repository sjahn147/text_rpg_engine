"""
탐험 시스템 서비스
"""
from typing import Dict, Any, List, Optional
from app.services.gameplay.base_service import BaseGameplayService
from common.utils.logger import logger
from app.common.utils.uuid_helper import normalize_uuid, to_uuid


class ExplorationService(BaseGameplayService):
    """탐험 시스템 서비스"""
    
    async def get_exploration_progress(self, session_id: str) -> Dict[str, Any]:
        """
        탐험 진행도 조회
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 탐험 진행도 (발견한 셀 수 / 전체 셀 수)
        """
        try:
            session_id = normalize_uuid(session_id)
            
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 전체 셀 수 조회
                total_cells_result = await conn.fetchrow(
                    """
                    SELECT COUNT(*) as total
                    FROM game_data.world_cells
                    """
                )
                total_cells = total_cells_result['total'] if total_cells_result else 0
                
                # 발견한 셀 수 조회 (action_logs 기반 추론)
                # 실제로는 별도 테이블이 필요하지만, 현재는 action_logs 기반으로 추론
                discovered_cells_result = await conn.fetchrow(
                    """
                    SELECT COUNT(DISTINCT message) as discovered
                    FROM runtime_data.action_logs
                    WHERE session_id = $1 
                        AND (action = 'move' OR action = 'visit' OR action = 'investigate')
                        AND success = true
                    """,
                    to_uuid(session_id)
                )
                discovered_cells = discovered_cells_result['discovered'] if discovered_cells_result else 0
                
                # 현재 위치의 셀도 포함
                current_cell = await conn.fetchrow(
                    """
                    SELECT COUNT(*) as count
                    FROM runtime_data.entity_states es
                    WHERE es.session_id = $1
                        AND es.runtime_entity_id IN (
                            SELECT runtime_entity_id 
                            FROM reference_layer.entity_references 
                            WHERE session_id = $1 
                                AND entity_type = 'player'
                            LIMIT 1
                        )
                        AND es.current_position IS NOT NULL
                    """,
                    to_uuid(session_id)
                )
                
                if current_cell and current_cell['count'] > 0:
                    discovered_cells = max(discovered_cells, 1)
                
                # 탐험 진행도 계산
                progress_percentage = 0.0
                if total_cells > 0:
                    progress_percentage = (discovered_cells / total_cells) * 100
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "exploration_progress": {
                        "discovered_cells": discovered_cells,
                        "total_cells": total_cells,
                        "progress_percentage": round(progress_percentage, 2)
                    }
                }
                
        except Exception as e:
            self.logger.error(f"탐험 진행도 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"탐험 진행도 조회 중 오류가 발생했습니다: {str(e)}")

