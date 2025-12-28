"""
오브젝트 상태 관리 모듈
"""
from typing import Dict, List, Optional, Any
import uuid
import asyncio
import json
from datetime import datetime
from common.utils.jsonb_handler import parse_jsonb_data, serialize_jsonb_data
from common.utils.error_handler import handle_database_error
from enum import Enum
from pydantic import BaseModel, Field
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger


class ObjectStateResult(BaseModel):
    """오브젝트 상태 조작 결과"""
    success: bool = Field(..., description="작업 성공 여부")
    message: str = Field(default="", description="결과 메시지")
    object_state: Optional[Dict[str, Any]] = Field(default=None, description="오브젝트 상태 정보")
    error: Optional[str] = Field(default=None, description="에러 메시지")
    
    @classmethod
    def success_result(cls, object_state: Dict[str, Any], message: str = "성공") -> "ObjectStateResult":
        """성공 결과 생성"""
        return cls(success=True, message=message, object_state=object_state)
    
    @classmethod
    def error_result(cls, message: str, error: str = None) -> "ObjectStateResult":
        """에러 결과 생성"""
        return cls(success=False, message=message, error=error)


class ObjectStateManager:
    """오브젝트 상태 관리 클래스"""
    
    def __init__(self,
                 db_connection: DatabaseConnection,
                 game_data_repo: GameDataRepository,
                 runtime_data_repo: RuntimeDataRepository,
                 reference_layer_repo: ReferenceLayerRepository):
        """
        ObjectStateManager 초기화
        
        Args:
            db_connection: 데이터베이스 연결
            game_data_repo: 게임 데이터 저장소
            runtime_data_repo: 런타임 데이터 저장소
            reference_layer_repo: 참조 레이어 저장소
        """
        self.db = db_connection
        self.game_data = game_data_repo
        self.runtime_data = runtime_data_repo
        self.reference_layer = reference_layer_repo
        self.logger = logger
        
        # 오브젝트 상태 캐시
        self._state_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = asyncio.Lock()
    
    async def get_object_state(
        self,
        runtime_object_id: Optional[str],
        game_object_id: str,
        session_id: str
    ) -> ObjectStateResult:
        """
        오브젝트의 현재 상태 조회 (런타임 + 기본값 병합)
        
        Args:
            runtime_object_id: 런타임 오브젝트 ID (없으면 생성)
            game_object_id: 게임 오브젝트 템플릿 ID
            session_id: 세션 ID
        
        Returns:
            ObjectStateResult: 오브젝트 상태 정보
        """
        try:
            # 1. 캐시 확인
            cache_key = f"{session_id}:{game_object_id}"
            async with self._cache_lock:
                if cache_key in self._state_cache:
                    cached_state = self._state_cache[cache_key]
                    return ObjectStateResult.success_result(cached_state, "캐시에서 조회")
            
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 2. runtime_object_id가 없으면 레퍼런스 레이어에서 조회/생성
                if not runtime_object_id:
                    object_ref = await conn.fetchrow(
                        """
                        SELECT runtime_object_id, object_type
                        FROM reference_layer.object_references
                        WHERE game_object_id = $1 AND session_id = $2
                        """,
                        game_object_id,
                        session_id
                    )
                    
                    if object_ref:
                        runtime_object_id = str(object_ref['runtime_object_id'])
                    else:
                        # 런타임 오브젝트 인스턴스 생성
                        runtime_object_id = str(uuid.uuid4())
                        
                        # 게임 오브젝트 템플릿에서 object_type 조회
                        game_object = await conn.fetchrow(
                            """
                            SELECT object_type FROM game_data.world_objects
                            WHERE object_id = $1
                            """,
                            game_object_id
                        )
                        object_type = game_object['object_type'] if game_object else 'interactive'
                        
                        # object_references에 등록
                        await conn.execute(
                            """
                            INSERT INTO reference_layer.object_references
                            (runtime_object_id, game_object_id, session_id, object_type)
                            VALUES ($1, $2, $3, $4)
                            ON CONFLICT (runtime_object_id) DO NOTHING
                            """,
                            runtime_object_id,
                            game_object_id,
                            session_id,
                            object_type
                        )
                        
                        # runtime_objects에도 생성
                        await conn.execute(
                            """
                            INSERT INTO runtime_data.runtime_objects
                            (runtime_object_id, game_object_id, session_id)
                            VALUES ($1, $2, $3)
                            ON CONFLICT (runtime_object_id) DO NOTHING
                            """,
                            runtime_object_id,
                            game_object_id,
                            session_id
                        )
                
                # 3. runtime_data.object_states에서 런타임 상태 조회
                runtime_state = await conn.fetchrow(
                    """
                    SELECT current_state FROM runtime_data.object_states
                    WHERE runtime_object_id = $1
                    """,
                    runtime_object_id
                )
                
                # 4. game_data.world_objects에서 기본값 조회
                game_object = await conn.fetchrow(
                    """
                    SELECT 
                        object_id, object_type, object_name, object_description,
                        interaction_type, possible_states, properties
                    FROM game_data.world_objects
                    WHERE object_id = $1
                    """,
                    game_object_id
                )
                
                if not game_object:
                    return ObjectStateResult.error_result(
                        f"게임 오브젝트를 찾을 수 없습니다: {game_object_id}"
                    )
                
                # 5. 병합하여 반환
                base_properties = parse_jsonb_data(game_object.get('properties', {}))
                base_possible_states = parse_jsonb_data(game_object.get('possible_states', {}))
                
                # 런타임 상태 파싱
                runtime_state_dict = {}
                if runtime_state and runtime_state.get('current_state'):
                    runtime_state_dict = parse_jsonb_data(runtime_state['current_state'])
                
                # 기본값과 런타임 값 병합 (런타임 값이 우선)
                merged_state = {
                    "object_id": game_object['object_id'],
                    "object_type": game_object['object_type'],
                    "object_name": game_object['object_name'],
                    "object_description": game_object.get('object_description'),
                    "interaction_type": game_object.get('interaction_type'),
                    "possible_states": base_possible_states,
                    "properties": {**base_properties, **runtime_state_dict}
                }
                
                # current_state는 runtime_state_dict에서 가져오거나 기본값 사용
                if 'state' in runtime_state_dict:
                    merged_state['current_state'] = runtime_state_dict['state']
                elif 'default_state' in base_properties:
                    merged_state['current_state'] = base_properties['default_state']
                else:
                    merged_state['current_state'] = 'default'
                
                # contents는 runtime_state_dict에서 가져오거나 기본값 사용
                if 'contents' in runtime_state_dict:
                    merged_state['contents'] = runtime_state_dict['contents']
                elif 'contents' in base_properties:
                    merged_state['contents'] = base_properties['contents']
                else:
                    merged_state['contents'] = []
                
                # 캐시에 저장
                async with self._cache_lock:
                    self._state_cache[cache_key] = merged_state
                
                return ObjectStateResult.success_result(
                    merged_state,
                    f"오브젝트 상태 조회 완료: {game_object['object_name']}"
                )
                
        except Exception as e:
            self.logger.error(f"오브젝트 상태 조회 실패: {str(e)}")
            return ObjectStateResult.error_result(
                f"오브젝트 상태 조회 실패: {str(e)}",
                error=str(e)
            )
    
    async def update_object_state(
        self,
        runtime_object_id: Optional[str],
        game_object_id: str,
        session_id: str,
        state: Optional[str] = None,
        contents: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> ObjectStateResult:
        """
        오브젝트 상태 업데이트
        
        Args:
            runtime_object_id: 런타임 오브젝트 ID (없으면 생성)
            game_object_id: 게임 오브젝트 템플릿 ID
            session_id: 세션 ID
            state: 상태 값 (예: "open", "closed", "lit", "unlit")
            contents: contents 리스트 (아이템 ID 목록)
            properties: 추가 속성
        
        Returns:
            ObjectStateResult: 업데이트 결과
        """
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                async with conn.transaction():
                    # 1. runtime_object_id가 없으면 생성
                    if not runtime_object_id:
                        object_ref = await conn.fetchrow(
                            """
                            SELECT runtime_object_id, object_type
                            FROM reference_layer.object_references
                            WHERE game_object_id = $1 AND session_id = $2
                            """,
                            game_object_id,
                            session_id
                        )
                        
                        if object_ref:
                            runtime_object_id = str(object_ref['runtime_object_id'])
                        else:
                            # 런타임 오브젝트 인스턴스 생성
                            runtime_object_id = str(uuid.uuid4())
                            
                            # 게임 오브젝트 템플릿에서 object_type 조회
                            game_object = await conn.fetchrow(
                                """
                                SELECT object_type FROM game_data.world_objects
                                WHERE object_id = $1
                                """,
                                game_object_id
                            )
                            object_type = game_object['object_type'] if game_object else 'interactive'
                            
                            # object_references에 등록
                            await conn.execute(
                                """
                                INSERT INTO reference_layer.object_references
                                (runtime_object_id, game_object_id, session_id, object_type)
                                VALUES ($1, $2, $3, $4)
                                ON CONFLICT (runtime_object_id) DO NOTHING
                                """,
                                runtime_object_id,
                                game_object_id,
                                session_id,
                                object_type
                            )
                            
                            # runtime_objects에도 생성
                            await conn.execute(
                                """
                                INSERT INTO runtime_data.runtime_objects
                                (runtime_object_id, game_object_id, session_id)
                                VALUES ($1, $2, $3)
                                ON CONFLICT (runtime_object_id) DO NOTHING
                                """,
                                runtime_object_id,
                                game_object_id,
                                session_id
                            )
                    
                    # 2. 기존 상태 조회
                    existing_state = await conn.fetchrow(
                        """
                        SELECT current_state FROM runtime_data.object_states
                        WHERE runtime_object_id = $1
                        """,
                        runtime_object_id
                    )
                    
                    # 3. 상태 병합
                    if existing_state and existing_state.get('current_state'):
                        current_state_dict = parse_jsonb_data(existing_state['current_state'])
                    else:
                        current_state_dict = {}
                    
                    # 업데이트할 값들 병합
                    if state is not None:
                        current_state_dict['state'] = state
                    
                    if contents is not None:
                        current_state_dict['contents'] = contents
                    
                    if properties:
                        current_state_dict.update(properties)
                    
                    # 4. runtime_data.object_states에 저장
                    if existing_state:
                        # 기존 상태 업데이트
                        await conn.execute(
                            """
                            UPDATE runtime_data.object_states
                            SET current_state = $1::jsonb, updated_at = NOW()
                            WHERE runtime_object_id = $2
                            """,
                            serialize_jsonb_data(current_state_dict),
                            runtime_object_id
                        )
                    else:
                        # 새 상태 생성
                        await conn.execute(
                            """
                            INSERT INTO runtime_data.object_states
                            (runtime_object_id, current_state, created_at, updated_at)
                            VALUES ($1, $2::jsonb, NOW(), NOW())
                            """,
                            runtime_object_id,
                            serialize_jsonb_data(current_state_dict)
                        )
                    
                    # 5. 캐시 업데이트
                    cache_key = f"{session_id}:{game_object_id}"
                    async with self._cache_lock:
                        if cache_key in self._state_cache:
                            # 캐시된 상태도 업데이트
                            self._state_cache[cache_key].update({
                                'current_state': current_state_dict.get('state', 'default'),
                                'contents': current_state_dict.get('contents', []),
                                **current_state_dict
                            })
                    
                    self.logger.info(f"오브젝트 상태 업데이트 완료: {game_object_id} -> {state}")
                    
                    return ObjectStateResult.success_result(
                        {
                            "runtime_object_id": runtime_object_id,
                            "game_object_id": game_object_id,
                            "state": current_state_dict.get('state'),
                            "contents": current_state_dict.get('contents', []),
                            **current_state_dict
                        },
                        f"오브젝트 상태 업데이트 완료"
                    )
                    
        except Exception as e:
            self.logger.error(f"오브젝트 상태 업데이트 실패: {str(e)}")
            return ObjectStateResult.error_result(
                f"오브젝트 상태 업데이트 실패: {str(e)}",
                error=str(e)
            )
    
    async def get_object_contents(
        self,
        runtime_object_id: Optional[str],
        game_object_id: str,
        session_id: str
    ) -> ObjectStateResult:
        """
        오브젝트의 contents 조회 (런타임 상태 반영)
        
        Args:
            runtime_object_id: 런타임 오브젝트 ID
            game_object_id: 게임 오브젝트 템플릿 ID
            session_id: 세션 ID
        
        Returns:
            ObjectStateResult: contents 리스트 포함
        """
        state_result = await self.get_object_state(runtime_object_id, game_object_id, session_id)
        
        if not state_result.success:
            return state_result
        
        contents = state_result.object_state.get('contents', [])
        
        return ObjectStateResult.success_result(
            {"contents": contents},
            f"오브젝트 contents 조회 완료 ({len(contents)}개 항목)"
        )
    
    async def remove_from_contents(
        self,
        runtime_object_id: Optional[str],
        game_object_id: str,
        session_id: str,
        item_id: str
    ) -> ObjectStateResult:
        """
        contents에서 아이템 제거
        
        Args:
            runtime_object_id: 런타임 오브젝트 ID
            game_object_id: 게임 오브젝트 템플릿 ID
            session_id: 세션 ID
            item_id: 제거할 아이템 ID
        
        Returns:
            ObjectStateResult: 업데이트된 contents 포함
        """
        try:
            # 1. 현재 contents 조회
            contents_result = await self.get_object_contents(runtime_object_id, game_object_id, session_id)
            
            if not contents_result.success:
                return contents_result
            
            contents = contents_result.object_state.get('contents', [])
            
            # 2. item_id 제거
            if item_id not in contents:
                return ObjectStateResult.error_result(
                    f"아이템을 찾을 수 없습니다: {item_id}"
                )
            
            contents.remove(item_id)
            
            # 3. 상태 업데이트
            return await self.update_object_state(
                runtime_object_id,
                game_object_id,
                session_id,
                contents=contents
            )
            
        except Exception as e:
            self.logger.error(f"contents에서 아이템 제거 실패: {str(e)}")
            return ObjectStateResult.error_result(
                f"contents에서 아이템 제거 실패: {str(e)}",
                error=str(e)
            )
    
    async def add_to_contents(
        self,
        runtime_object_id: Optional[str],
        game_object_id: str,
        session_id: str,
        item_id: str
    ) -> ObjectStateResult:
        """
        contents에 아이템 추가
        
        Args:
            runtime_object_id: 런타임 오브젝트 ID
            game_object_id: 게임 오브젝트 템플릿 ID
            session_id: 세션 ID
            item_id: 추가할 아이템 ID
        
        Returns:
            ObjectStateResult: 업데이트된 contents 포함
        """
        try:
            # 1. 현재 contents 조회
            contents_result = await self.get_object_contents(runtime_object_id, game_object_id, session_id)
            
            if not contents_result.success:
                return contents_result
            
            contents = contents_result.object_state.get('contents', [])
            
            # 2. item_id 추가 (중복 방지)
            if item_id in contents:
                return ObjectStateResult.error_result(
                    f"이미 존재하는 아이템입니다: {item_id}"
                )
            
            contents.append(item_id)
            
            # 3. 상태 업데이트
            return await self.update_object_state(
                runtime_object_id,
                game_object_id,
                session_id,
                contents=contents
            )
            
        except Exception as e:
            self.logger.error(f"contents에 아이템 추가 실패: {str(e)}")
            return ObjectStateResult.error_result(
                f"contents에 아이템 추가 실패: {str(e)}",
                error=str(e)
            )

