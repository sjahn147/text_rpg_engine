import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import logging

from app.core.game_manager import GameManager
from app.game_session import GameSession
from app.managers.entity_manager import EntityManager
from app.managers.instance_manager import InstanceManager
from app.managers.cell_manager import CellManager
from app.managers.dialogue_manager import DialogueManager
from app.handlers.action_handler import ActionHandler

class ScenarioExecutor:
    """시나리오를 실행하는 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 매니저 클래스들
        self.game_manager = GameManager()
        self.entity_manager = EntityManager()
        self.instance_manager = InstanceManager()
        self.cell_manager = CellManager()
        self.dialogue_manager = DialogueManager()
        self.action_handler = ActionHandler()
        
        # 실행 상태
        self.current_session: Optional[GameSession] = None
        self.current_scenario: Optional[Dict[str, Any]] = None
        self.current_step_index: int = 0
        self.is_running: bool = False
        self.is_paused: bool = False
        
        # 콜백 함수들
        self.on_step_start: Optional[Callable] = None
        self.on_step_complete: Optional[Callable] = None
        self.on_scenario_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_log: Optional[Callable] = None
    
    def set_callbacks(self, 
                     on_step_start: Optional[Callable] = None,
                     on_step_complete: Optional[Callable] = None,
                     on_scenario_complete: Optional[Callable] = None,
                     on_error: Optional[Callable] = None,
                     on_log: Optional[Callable] = None):
        """콜백 함수들을 설정합니다."""
        self.on_step_start = on_step_start
        self.on_step_complete = on_step_complete
        self.on_scenario_complete = on_scenario_complete
        self.on_error = on_error
        self.on_log = on_log
    
    async def execute_scenario(self, scenario_data: Dict[str, Any]) -> bool:
        """
        시나리오를 실행합니다.
        
        Args:
            scenario_data: 실행할 시나리오 데이터
            
        Returns:
            실행 성공 여부
        """
        try:
            self.current_scenario = scenario_data
            self.current_step_index = 0
            self.is_running = True
            self.is_paused = False
            
            self.log_message(f"시나리오 실행 시작: {scenario_data.get('name', 'Unknown')}")
            
            steps = scenario_data.get('steps', [])
            
            for i, step in enumerate(steps):
                if not self.is_running:
                    break
                
                self.current_step_index = i
                
                # 일시정지 상태 확인
                while self.is_paused and self.is_running:
                    await asyncio.sleep(0.1)
                
                if not self.is_running:
                    break
                
                # step 실행
                await self.execute_step(step, i)
            
            if self.is_running:
                self.log_message("시나리오 실행 완료")
                if self.on_scenario_complete:
                    self.on_scenario_complete()
            
            return True
            
        except Exception as e:
            error_msg = f"시나리오 실행 중 오류: {str(e)}"
            self.log_message(error_msg)
            if self.on_error:
                self.on_error(error_msg)
            return False
        
        finally:
            self.is_running = False
            self.current_scenario = None
    
    async def execute_step(self, step: Dict[str, Any], step_index: int) -> None:
        """
        개별 step을 실행합니다.
        
        Args:
            step: 실행할 step 데이터
            step_index: step 인덱스
        """
        step_type = step['type']
        description = step['description']
        
        self.log_message(f"Step {step_index + 1}: {description}")
        
        if self.on_step_start:
            self.on_step_start(step_index, step)
        
        start_time = time.time()
        
        try:
            if step_type == 'setup_data':
                await self.execute_setup_data(step)
            elif step_type == 'create_session':
                await self.execute_create_session(step)
            elif step_type == 'create_entity':
                await self.execute_create_entity(step)
            elif step_type == 'move_entity':
                await self.execute_move_entity(step)
            elif step_type == 'start_dialogue':
                await self.execute_start_dialogue(step)
            elif step_type == 'interact':
                await self.execute_interact(step)
            elif step_type == 'update_stats':
                await self.execute_update_stats(step)
            elif step_type == 'complete_event':
                await self.execute_complete_event(step)
            elif step_type == 'cleanup':
                await self.execute_cleanup(step)
            else:
                raise ValueError(f"지원하지 않는 step 타입: {step_type}")
            
            execution_time = time.time() - start_time
            self.log_message(f"Step {step_index + 1} 완료 (소요시간: {execution_time:.2f}초)")
            
            if self.on_step_complete:
                self.on_step_complete(step_index, step, execution_time)
        
        except Exception as e:
            error_msg = f"Step {step_index + 1} 실행 실패: {str(e)}"
            self.log_message(error_msg)
            if self.on_error:
                self.on_error(error_msg)
            raise
    
    async def execute_setup_data(self, step: Dict[str, Any]) -> None:
        """테스트 데이터 설정 step 실행 (class 기반 테스트와 동일한 순서)"""
        from database.factories.game_data_factory import GameDataFactory
        from database.repositories.game_data import GameDataRepository
        factory = GameDataFactory()
        repo = GameDataRepository()

        # 1. (선택) events 테이블 생성
        db = factory.db
        pool = await db.pool
        async with pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'game_data' 
                    AND table_name = 'events'
                );
                """
            )
            if not result:
                await conn.execute(
                    """
                    CREATE TABLE game_data.events (
                        event_id VARCHAR(50) PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        properties JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )

        # 2. 월드 구조 생성 (region → location → cell)
        if 'world_structure' in step:
            world_data = step['world_structure']
            for region in world_data.get('regions', []):
                await factory.create_world_region(**region)
            for location in world_data.get('locations', []):
                await factory.create_world_location(**location)
            for cell in world_data.get('cells', []):
                await factory.create_world_cell(**cell)

        # 3. 엔티티 템플릿 생성 (player, npc)
        if 'entity_templates' in step:
            for entity in step['entity_templates']:
                entity_data = entity.copy()
                entity_data.pop('type', None)
                if entity.get('template_type') == 'player' or entity.get('type') == 'player':
                    await factory.create_player_template(**entity_data)
                else:
                    await factory.create_npc_template(**entity_data)

        # 4. 이벤트 생성
        if 'events' in step:
            for event in step['events']:
                await repo.create_event(event)

        # 5. 대화 컨텍스트 생성
        if 'dialogue_contexts' in step:
            for ctx in step['dialogue_contexts']:
                await factory.create_dialogue_context(**ctx)
    
    async def execute_create_session(self, step: Dict[str, Any]) -> None:
        """세션 생성 step 실행"""
        player_template_id = step.get('player_template_id')
        start_cell_id = step.get('start_cell_id')
        
        session_id = await self.game_manager.start_new_game(
            player_template_id=player_template_id,
            start_cell_id=start_cell_id
        )
        
        self.current_session = GameSession(session_id)
        await self.current_session.initialize_session()
        
        self.log_message(f"게임 세션 생성됨: {session_id}")
    
    async def execute_create_entity(self, step: Dict[str, Any]) -> None:
        """엔티티 생성 step 실행"""
        if not self.current_session:
            raise ValueError("세션이 생성되지 않았습니다.")
        
        game_entity_id = step['game_entity_id']
        entity_type = step.get('entity_type', 'npc')
        position = step.get('position', {"x": 50, "y": 0, "z": 50})
        
        # 플레이어 엔티티 정보 조회하여 현재 셀 ID 가져오기
        player_entities = await self.current_session.get_player_entities()
        if not player_entities:
            raise ValueError("플레이어 엔티티를 찾을 수 없습니다.")
        
        current_cell_id = player_entities[0].get('runtime_cell_id')
        
        runtime_entity_id = await self.instance_manager.create_entity_instance(
            game_entity_id=game_entity_id,
            session_id=self.current_session.session_id,
            runtime_cell_id=current_cell_id,
            position=position,
            entity_type=entity_type
        )
        
        self.log_message(f"엔티티 생성됨: {runtime_entity_id} ({entity_type})")
    
    async def execute_move_entity(self, step: Dict[str, Any]) -> None:
        """엔티티 이동 step 실행"""
        if not self.current_session:
            raise ValueError("세션이 생성되지 않았습니다.")
        
        entity_id = step['entity_id']
        target_position = step['target_position']
        
        # 플레이어 엔티티 정보 조회하여 현재 셀 ID 가져오기
        player_entities = await self.current_session.get_player_entities()
        if not player_entities:
            raise ValueError("플레이어 엔티티를 찾을 수 없습니다.")
        
        current_cell_id = player_entities[0].get('runtime_cell_id')
        
        success = await self.game_manager.move_player(current_cell_id, target_position)
        
        if success:
            self.log_message(f"엔티티 이동 완료: {target_position}")
        else:
            raise ValueError("엔티티 이동 실패")
    
    async def execute_start_dialogue(self, step: Dict[str, Any]) -> None:
        """대화 시작 step 실행"""
        if not self.current_session:
            raise ValueError("세션이 생성되지 않았습니다.")
        
        npc_id = step['npc_id']
        
        # 플레이어 엔티티 정보 조회
        player_entities = await self.current_session.get_player_entities()
        if not player_entities:
            raise ValueError("플레이어 엔티티를 찾을 수 없습니다.")
        
        player_id = player_entities[0]['runtime_entity_id']
        
        dialogue_id = await self.interaction_manager.start_dialogue(
            player_id, npc_id, self.current_session.session_id
        )
        
        if dialogue_id:
            self.log_message(f"대화 시작됨: {dialogue_id}")
        else:
            raise ValueError("대화를 시작할 수 없습니다.")
    
    async def execute_interact(self, step: Dict[str, Any]) -> None:
        """상호작용 step 실행"""
        if not self.current_session:
            raise ValueError("세션이 생성되지 않았습니다.")
        
        target_id = step['target_id']
        interaction_type = step.get('interaction_type', 'dialogue')
        
        # 플레이어 엔티티 정보 조회
        player_entities = await self.current_session.get_player_entities()
        if not player_entities:
            raise ValueError("플레이어 엔티티를 찾을 수 없습니다.")
        
        player_id = player_entities[0]['runtime_entity_id']
        
        if interaction_type == 'dialogue':
            player_input = step.get('player_input', '안녕하세요!')
            response = await self.interaction_manager.process_dialogue_input(
                player_input, target_id, self.current_session.session_id
            )
            self.log_message(f"대화 응답: {response}")
    
    async def execute_update_stats(self, step: Dict[str, Any]) -> None:
        """스탯 업데이트 step 실행"""
        if not self.current_session:
            raise ValueError("세션이 생성되지 않았습니다.")
        
        entity_id = step['entity_id']
        new_stats = step['new_stats']
        
        # 플레이어 엔티티 정보 조회
        player_entities = await self.current_session.get_player_entities()
        if not player_entities:
            raise ValueError("플레이어 엔티티를 찾을 수 없습니다.")
        
        player_id = player_entities[0]['runtime_entity_id']
        
        success = await self.current_session.update_player_stats(player_id, new_stats)
        
        if success:
            self.log_message(f"스탯 업데이트 완료: {new_stats}")
        else:
            raise ValueError("스탯 업데이트 실패")
    
    async def execute_complete_event(self, step: Dict[str, Any]) -> None:
        """이벤트 완료 step 실행"""
        event_id = step['event_id']
        self.log_message(f"이벤트 완료: {event_id}")
    
    async def execute_cleanup(self, step: Dict[str, Any]) -> None:
        """정리 step 실행"""
        if self.current_session:
            await self.current_session.end_session()
            self.current_session = None
        
        self.log_message("시나리오 정리 완료")
    
    def pause_scenario(self) -> None:
        """시나리오 실행을 일시정지합니다."""
        self.is_paused = True
        self.log_message("시나리오 일시정지")
    
    def resume_scenario(self) -> None:
        """시나리오 실행을 재개합니다."""
        self.is_paused = False
        self.log_message("시나리오 재개")
    
    def stop_scenario(self) -> None:
        """시나리오 실행을 중지합니다."""
        self.is_running = False
        self.log_message("시나리오 중지")
    
    def get_execution_status(self) -> Dict[str, Any]:
        """현재 실행 상태를 반환합니다."""
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'current_step_index': self.current_step_index,
            'total_steps': len(self.current_scenario.get('steps', [])) if self.current_scenario else 0,
            'scenario_name': self.current_scenario.get('name', 'Unknown') if self.current_scenario else None,
            'session_id': self.current_session.session_id if self.current_session else None
        }
    
    def log_message(self, message: str) -> None:
        """로그 메시지를 출력합니다."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        
        self.logger.info(log_msg)
        
        if self.on_log:
            self.on_log(log_msg) 