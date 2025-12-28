"""
NPC 자동 행동 시스템
- 기존 Manager 클래스들을 조합하여 NPC 행동 구현
- 시간대별 행동 패턴 실행
- DB 트랜잭션을 통한 모든 행동 기록
"""
import asyncio
import logging
import random
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.managers.entity_manager import EntityManager, EntityType, EntityStatus
from app.managers.cell_manager import CellManager, CellType, CellStatus
from app.managers.dialogue_manager import DialogueManager
from app.handlers.action_handler import ActionHandler
from app.systems.time_system import TimeSystem, TimePeriod
from database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class NPCBehavior:
    """NPC 자동 행동 시스템"""
    
    def __init__(self, 
                 db_connection: DatabaseConnection,
                 entity_manager: EntityManager,
                 cell_manager: CellManager,
                 dialogue_manager: DialogueManager,
                 action_handler: ActionHandler,
                 time_system: TimeSystem):
        """
        NPC 행동 시스템 초기화
        
        Args:
            db_connection: 데이터베이스 연결
            entity_manager: 엔티티 관리자
            cell_manager: 셀 관리자
            dialogue_manager: 대화 관리자
            action_handler: 액션 핸들러
            time_system: 시간 시스템
        """
        self.db = db_connection
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
        self.dialogue_manager = dialogue_manager
        self.action_handler = action_handler
        self.time_system = time_system
        
        # NPC 정보는 DB에서 동적으로 로드
        self.npc_routines = {}
        self.cell_mapping = {}
        
        logger.info("NPCBehavior system initialized")
    
    async def load_npc_behavior_schedules(self, session_id: str):
        """DB에서 NPC 행동 스케줄 로드"""
        try:
            # 게임 데이터에서 엔티티 행동 스케줄 조회
            # 테스트 환경에서는 모든 NPC 스케줄을 로드
            query = """
                SELECT 
                    ebs.entity_id,
                    ebs.time_period,
                    ebs.action_type,
                    ebs.action_priority,
                    ebs.conditions,
                    ebs.action_data,
                    e.entity_name,
                    e.entity_type
                FROM game_data.entity_behavior_schedules ebs
                JOIN game_data.entities e ON ebs.entity_id = e.entity_id
                WHERE e.entity_type = 'npc'
                ORDER BY ebs.entity_id, ebs.time_period, ebs.action_priority
            """
            
            schedules = await self.db.execute_query(query)
            
            # NPC별로 스케줄 정리
            for schedule in schedules:
                entity_id = schedule["entity_id"]
                if entity_id not in self.npc_routines:
                    self.npc_routines[entity_id] = {
                        "name": schedule["entity_name"],
                        "type": schedule["entity_type"],
                        "schedules": {}
                    }
                
                time_period = schedule["time_period"]
                if time_period not in self.npc_routines[entity_id]["schedules"]:
                    self.npc_routines[entity_id]["schedules"][time_period] = []
                
                # JSONB 데이터 파싱
                import json
                conditions = schedule["conditions"]
                action_data = schedule["action_data"]
                
                # 문자열인 경우 JSON으로 파싱
                if isinstance(conditions, str):
                    conditions = json.loads(conditions)
                if isinstance(action_data, str):
                    action_data = json.loads(action_data)
                
                self.npc_routines[entity_id]["schedules"][time_period].append({
                    "action_type": schedule["action_type"],
                    "priority": schedule["action_priority"],
                    "conditions": conditions,
                    "action_data": action_data
                })
            
            logger.info(f"Loaded behavior schedules for {len(self.npc_routines)} NPCs")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load NPC behavior schedules: {str(e)}")
            return False
    
    def set_cell_mapping(self, cell_mapping: Dict[str, str]):
        """셀 ID 매핑 설정"""
        self.cell_mapping = cell_mapping
        logger.info(f"Cell mapping set: {cell_mapping}")
    
    async def execute_daily_routine(self, npc_id: str) -> bool:
        """
        NPC의 하루 일과 실행 (DB 기반)
        
        Args:
            npc_id: NPC ID
            
        Returns:
            실행 성공 여부
        """
        if npc_id not in self.npc_routines:
            logger.error(f"Unknown NPC: {npc_id}")
            return False
        
        try:
            npc_info = self.npc_routines[npc_id]
            time_period = self.time_system.get_time_period()
            
            logger.info(f"Executing routine for {npc_info['name']} during {time_period.value}")
            
            # DB에서 로드한 스케줄에 따라 행동 실행
            success = await self._execute_scheduled_actions(npc_id, time_period)
            
            if success:
                logger.info(f"Routine completed for {npc_info['name']}")
            else:
                logger.warning(f"Routine failed for {npc_info['name']}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error executing routine for {npc_id}: {str(e)}")
            return False
    
    async def _execute_scheduled_actions(self, npc_id: str, time_period: TimePeriod) -> bool:
        """DB 스케줄에 따른 행동 실행"""
        try:
            npc_info = self.npc_routines[npc_id]
            time_period_str = time_period.value
            
            # 해당 시간대의 스케줄이 있는지 확인
            if time_period_str not in npc_info["schedules"]:
                logger.info(f"No scheduled actions for {npc_id} during {time_period_str}")
                return True
            
            schedules = npc_info["schedules"][time_period_str]
            
            # 우선순위 순으로 정렬
            schedules.sort(key=lambda x: x["priority"])
            
            for schedule in schedules:
                action_type = schedule["action_type"]
                conditions = schedule["conditions"]
                action_data = schedule["action_data"]
                
                # 조건 확인
                if not await self._check_conditions(npc_id, conditions):
                    logger.info(f"Conditions not met for {npc_id} action {action_type}")
                    continue
                
                # 행동 실행
                success = await self._execute_action(npc_id, action_type, action_data)
                if not success:
                    logger.warning(f"Failed to execute {action_type} for {npc_id}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing scheduled actions for {npc_id}: {str(e)}")
            return False
    
    async def _check_conditions(self, npc_id: str, conditions: Dict[str, Any]) -> bool:
        """행동 조건 확인"""
        if not conditions:
            return True
        
        # 기본 조건들 (에너지, 기분 등) - 향후 확장 가능
        # 현재는 모든 조건을 통과로 처리
        return True
    
    async def _execute_action(self, npc_id: str, action_type: str, action_data: Dict[str, Any]) -> bool:
        """구체적인 행동 실행"""
        try:
            # action_data에서 목표 셀 정보 추출
            target_cell = action_data.get("location")
            target_cell_id = None
            if target_cell and target_cell in self.cell_mapping:
                target_cell_id = self.cell_mapping[target_cell]
                if target_cell_id:
                    # 셀 이동
                    await self.move_to_cell(npc_id, target_cell_id)
            
            # 액션 핸들러를 통한 행동 실행
            result = await self.action_handler.execute_action(action_type, npc_id, target_cell_id if target_cell_id else "current_cell")
            
            if result.success:
                logger.info(f"Successfully executed {action_type} for {npc_id}")
                return True
            else:
                logger.warning(f"Failed to execute {action_type} for {npc_id}: {result.message}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing action {action_type} for {npc_id}: {str(e)}")
            return False
    
    async def move_to_cell(self, npc_id: str, target_cell_id: str) -> bool:
        """
        NPC 셀 이동
        
        Args:
            npc_id: NPC ID
            target_cell_id: 목표 셀 ID
            
        Returns:
            이동 성공 여부
        """
        try:
            # 현재 셀에서 나가기
            current_cell_result = await self.cell_manager.leave_cell("current_cell", npc_id)
            
            # 새 셀에 들어가기
            enter_result = await self.cell_manager.enter_cell(target_cell_id, npc_id)
            
            if enter_result.success:
                logger.info(f"{npc_id} moved to {target_cell_id}")
                return True
            else:
                logger.warning(f"Failed to move {npc_id} to {target_cell_id}: {enter_result.message}")
                return False
                
        except Exception as e:
            logger.error(f"Error moving {npc_id} to {target_cell_id}: {str(e)}")
            return False
    
    async def interact_with_others(self, npc_id: str, current_cell_id: str) -> bool:
        """
        다른 NPC와 상호작용
        
        Args:
            npc_id: NPC ID
            current_cell_id: 현재 셀 ID
            
        Returns:
            상호작용 성공 여부
        """
        try:
            # 같은 셀에 있는 다른 NPC들 찾기
            cell_content = await self.cell_manager.load_cell_content(current_cell_id)
            if not cell_content.success:
                return False
            
            other_entities = [e for e in cell_content.content.entities if e != npc_id]
            
            if not other_entities:
                logger.info(f"No other entities in {current_cell_id} for {npc_id} to interact with")
                return True
            
            # 상호작용 확률 확인
            time_period = self.time_system.get_time_period()
            interaction_prob = self.time_system.get_interaction_probability(time_period)
            
            if random.random() > interaction_prob:
                logger.info(f"{npc_id} chose not to interact (probability: {interaction_prob})")
                return True
            
            # 랜덤하게 다른 NPC 선택
            target_npc = random.choice(other_entities)
            
            # 대화 시작
            dialogue_result = await self.dialogue_manager.start_dialogue(
                player_id=npc_id,
                npc_id=target_npc
            )
            
            if dialogue_result.success:
                logger.info(f"{npc_id} started dialogue with {target_npc}")
                
                # 대화 계속 (간단한 응답)
                continue_result = await self.dialogue_manager.continue_dialogue(
                    player_id=npc_id,
                    npc_id=target_npc,
                    topic="greeting",
                    player_message="Hello! How are you?"
                )
                
                if continue_result.success:
                    logger.info(f"Dialogue continued between {npc_id} and {target_npc}")
                
                # 대화 종료
                await self.dialogue_manager.end_dialogue(dialogue_result.session_id)
                logger.info(f"Dialogue ended between {npc_id} and {target_npc}")
                
                return True
            else:
                logger.warning(f"Failed to start dialogue between {npc_id} and {target_npc}")
                return False
                
        except Exception as e:
            logger.error(f"Error in interaction between {npc_id} and others: {str(e)}")
            return False