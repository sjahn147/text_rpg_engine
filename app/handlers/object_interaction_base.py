"""
오브젝트 상호작용 핸들러 베이스 클래스
"""
from typing import Dict, Any, Optional, Tuple, Union
from uuid import UUID
from abc import ABC, abstractmethod
from app.managers.object_state_manager import ObjectStateManager
from app.managers.entity_manager import EntityManager
from app.managers.inventory_manager import InventoryManager
from app.managers.effect_carrier_manager import EffectCarrierManager
from database.connection import DatabaseConnection
from common.utils.logger import logger
from app.handlers.action_result import ActionResult
from app.common.utils.uuid_helper import normalize_uuid, to_uuid


class ObjectInteractionHandlerBase(ABC):
    """오브젝트 상호작용 핸들러 베이스 클래스"""
    
    def __init__(
        self,
        db_connection: DatabaseConnection,
        object_state_manager: Optional[ObjectStateManager] = None,
        entity_manager: Optional[EntityManager] = None,
        inventory_manager: Optional[InventoryManager] = None,
        effect_carrier_manager: Optional[EffectCarrierManager] = None
    ):
        """
        초기화
        
        Args:
            db_connection: 데이터베이스 연결
            object_state_manager: 오브젝트 상태 관리자 (선택사항)
            entity_manager: 엔티티 관리자 (선택사항)
            inventory_manager: 인벤토리 관리자 (선택사항)
            effect_carrier_manager: Effect Carrier 관리자 (선택사항)
        """
        self.db = db_connection
        self.object_state_manager = object_state_manager
        self.entity_manager = entity_manager
        self.inventory_manager = inventory_manager
        self.effect_carrier_manager = effect_carrier_manager
        self.logger = logger
    
    async def _parse_object_id(
        self,
        target_id: Union[str, UUID],
        session_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        오브젝트 ID 파싱 (runtime_object_id, game_object_id 반환)
        
        Args:
            target_id: 대상 오브젝트 ID (UUID 또는 game_object_id)
            session_id: 세션 ID
        
        Returns:
            (runtime_object_id, game_object_id) 튜플
        """
        # UUID 헬퍼 함수로 정규화 (문자열로 통일)
        target_id_str = normalize_uuid(target_id) if target_id else None
        
        # UUID 형식인지 확인 (36자리 하이픈 포함 문자열)
        is_uuid = target_id_str is not None and len(target_id_str) == 36 and '-' in target_id_str
        
        runtime_object_id = target_id_str if is_uuid else None
        game_object_id = target_id_str if not is_uuid else None
        
        self.logger.debug(f"오브젝트 ID 파싱: target_id={target_id} (type={type(target_id)}), target_id_str={target_id_str}, is_uuid={is_uuid}, runtime_object_id={runtime_object_id}, game_object_id={game_object_id}")
        
        # game_object_id가 없으면 reference_layer에서 조회
        if runtime_object_id and not game_object_id:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # runtime_object_id를 UUID 객체로 변환 (DB 쿼리용 - asyncpg가 UUID 타입으로 자동 변환)
                runtime_uuid = to_uuid(runtime_object_id)
                session_uuid = to_uuid(session_id)
                
                if not runtime_uuid or not session_uuid:
                    self.logger.warning(f"유효하지 않은 UUID: runtime_object_id={runtime_object_id}, session_id={session_id}")
                    return None, None
                
                ref = await conn.fetchrow(
                    """
                    SELECT game_object_id FROM reference_layer.object_references
                    WHERE runtime_object_id = $1 AND session_id = $2
                    """,
                    runtime_uuid,  # UUID 객체로 전달 (asyncpg 자동 변환)
                    session_uuid   # UUID 객체로 전달 (asyncpg 자동 변환)
                )
                if ref:
                    game_object_id = ref['game_object_id']
                    self.logger.debug(f"reference_layer에서 game_object_id 조회 성공: {game_object_id}")
                else:
                    self.logger.warning(f"reference_layer에서 game_object_id를 찾을 수 없음: runtime_object_id={runtime_object_id}, session_id={session_id}")
        
        self.logger.debug(f"오브젝트 ID 파싱 결과: runtime_object_id={runtime_object_id}, game_object_id={game_object_id}")
        return runtime_object_id, game_object_id
    
    async def _get_object_state(
        self,
        runtime_object_id: Optional[str],
        game_object_id: str,
        session_id: str
    ):
        """오브젝트 상태 조회 헬퍼"""
        if not game_object_id:
            self.logger.warning(f"game_object_id가 없어 오브젝트 상태를 조회할 수 없음: runtime_object_id={runtime_object_id}, session_id={session_id}")
            return None
        
        if not self.object_state_manager:
            self.logger.error("object_state_manager가 None이어서 오브젝트 상태를 조회할 수 없음")
            return None
        
        self.logger.debug(f"오브젝트 상태 조회 시도: runtime_object_id={runtime_object_id}, game_object_id={game_object_id}, session_id={session_id}")
        
        state_result = await self.object_state_manager.get_object_state(
            runtime_object_id,
            game_object_id,
            session_id
        )
        
        if not state_result.success:
            self.logger.warning(f"오브젝트 상태 조회 실패: {state_result.message}")
            return None
        
        self.logger.debug(f"오브젝트 상태 조회 성공: object_name={state_result.object_state.get('object_name', 'N/A')}")
        return state_result.object_state
    
    async def _update_object_state(
        self,
        runtime_object_id: Optional[str],
        game_object_id: str,
        session_id: str,
        state: Optional[str] = None,
        contents: Optional[list] = None,
        properties: Optional[Dict[str, Any]] = None
    ):
        """오브젝트 상태 업데이트 헬퍼"""
        if not game_object_id:
            return None
        
        update_result = await self.object_state_manager.update_object_state(
            runtime_object_id,
            game_object_id,
            session_id,
            state=state,
            contents=contents,
            properties=properties
        )
        
        if not update_result.success:
            return None
        
        return update_result.object_state
    
    def _handle_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        user_message: Optional[str] = None
    ) -> ActionResult:
        """
        에러 처리 헬퍼 메서드
        
        Args:
            error: 발생한 예외
            context: 컨텍스트 정보 (entity_id, target_id, session_id 등)
            user_message: 사용자에게 표시할 메시지 (None이면 자동 생성)
        
        Returns:
            ActionResult: 실패 결과
        """
        # 상세한 에러 로그 기록
        self.logger.error(
            f"오브젝트 상호작용 에러 발생: {type(error).__name__}: {str(error)}",
            exc_info=True,
            extra={
                "context": context,
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
        )
        
        # 사용자 친화적인 메시지 생성
        if not user_message:
            if isinstance(error, ValueError):
                user_message = f"입력값 오류: {str(error)}"
            elif isinstance(error, KeyError):
                user_message = "필수 정보가 누락되었습니다."
            elif isinstance(error, AttributeError):
                user_message = "시스템 오류가 발생했습니다. 관리자에게 문의하세요."
            else:
                user_message = "상호작용 처리 중 오류가 발생했습니다."
        
        return ActionResult.failure_result(user_message)
    
    def _validate_required_managers(
        self,
        required_managers: Dict[str, Any],
        operation_name: str
    ) -> Optional[ActionResult]:
        """
        필수 매니저 검증
        
        Args:
            required_managers: 필수 매니저 딕셔너리 (이름: 매니저 객체)
            operation_name: 작업 이름
        
        Returns:
            None: 모든 매니저가 있음
            ActionResult: 매니저가 없으면 실패 결과
        """
        missing_managers = []
        for name, manager in required_managers.items():
            if manager is None:
                missing_managers.append(name)
        
        if missing_managers:
            manager_names = ", ".join(missing_managers)
            self.logger.error(
                f"{operation_name} 실패: 필수 매니저가 초기화되지 않음: {manager_names}",
                extra={"missing_managers": missing_managers, "operation": operation_name}
            )
            return ActionResult.failure_result(
                f"시스템 오류: {manager_names}가 초기화되지 않았습니다."
            )
        
        return None
    
    def _validate_parameters(
        self,
        parameters: Optional[Dict[str, Any]],
        required_keys: list,
        operation_name: str
    ) -> Optional[ActionResult]:
        """
        파라미터 검증
        
        Args:
            parameters: 파라미터 딕셔너리
            required_keys: 필수 키 목록
            operation_name: 작업 이름
        
        Returns:
            None: 모든 파라미터가 있음
            ActionResult: 파라미터가 없으면 실패 결과
        """
        if not parameters:
            self.logger.warning(
                f"{operation_name} 실패: 파라미터가 없음",
                extra={"operation": operation_name, "required_keys": required_keys}
            )
            key_names = ", ".join(required_keys)
            return ActionResult.failure_result(f"필수 파라미터가 제공되지 않았습니다: {key_names}")
        
        missing_keys = [key for key in required_keys if key not in parameters or parameters[key] is None]
        
        if missing_keys:
            key_names = ", ".join(missing_keys)
            self.logger.warning(
                f"{operation_name} 실패: 필수 파라미터 누락: {key_names}",
                extra={"missing_keys": missing_keys, "operation": operation_name}
            )
            return ActionResult.failure_result(f"필수 파라미터가 누락되었습니다: {key_names}")
        
        return None
    
    @abstractmethod
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """
        상호작용 처리
        
        Args:
            entity_id: 엔티티 ID
            target_id: 대상 오브젝트 ID
            parameters: 추가 파라미터 (session_id 포함)
        
        Returns:
            ActionResult: 처리 결과
        """
        pass

