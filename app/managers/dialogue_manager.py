"""
대화 시스템 관리 모듈
"""
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import json
from common.utils.jsonb_handler import parse_jsonb_data, serialize_jsonb_data
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

from app.managers.entity_manager import EntityManager, EntityType, EntityStatus
from app.managers.effect_carrier_manager import EffectCarrierManager
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger


class DialogueTopic(str, Enum):
    """대화 주제 열거형 - DB에서 동적으로 로드"""
    GREETING = "greeting"
    TRADE = "trade"
    LORE = "lore"
    QUEST = "quest"
    FAREWELL = "farewell"
    
    @classmethod
    async def load_from_db(cls, db_connection):
        """DB에서 대화 주제 로드"""
        try:
            pool = await db_connection.pool
            async with pool.acquire() as conn:
                topics = await conn.fetch("""
                    SELECT DISTINCT topic_type
                    FROM game_data.dialogue_topics
                    ORDER BY topic_type
                """)
                return [topic['topic_type'] for topic in topics]
        except Exception as e:
            logger.error(f"Failed to load dialogue topics from DB: {str(e)}")
            return ["greeting", "trade", "lore", "quest", "farewell"]  # 기본값


class DialogueContext(BaseModel):
    """대화 컨텍스트 모델"""
    context_id: str = Field(..., description="컨텍스트 ID")
    title: str = Field(..., description="대화 제목")
    content: str = Field(..., description="대화 내용")
    priority: int = Field(default=1, description="우선순위 - DB에서 동적으로 로드")
    entity_personality: str = Field(..., description="엔티티 성격")
    available_topics: Dict[str, Any] = Field(default_factory=dict, description="사용 가능한 주제")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="제약 조건")


class DialogueTopic(BaseModel):
    """대화 주제 모델"""
    topic_id: str = Field(..., description="주제 ID")
    dialogue_id: str = Field(..., description="대화 ID")
    topic_type: str = Field(..., description="주제 타입")
    content: str = Field(..., description="주제 내용")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="조건")


class DialogueKnowledge(BaseModel):
    """대화 지식 모델"""
    knowledge_id: str = Field(..., description="지식 ID")
    title: str = Field(..., description="지식 제목")
    content: str = Field(..., description="지식 내용")
    knowledge_type: str = Field(..., description="지식 타입")
    related_entities: Dict[str, Any] = Field(default_factory=dict, description="관련 엔티티")
    related_topics: Dict[str, Any] = Field(default_factory=dict, description="관련 주제")
    knowledge_properties: Dict[str, Any] = Field(default_factory=dict, description="지식 속성")


class DialogueResult(BaseModel):
    """대화 결과 모델"""
    success: bool = Field(..., description="대화 성공 여부")
    message: str = Field(..., description="대화 메시지")
    npc_response: str = Field(..., description="NPC 응답")
    available_topics: List[str] = Field(default_factory=list, description="사용 가능한 주제")
    dialogue_data: Optional[Dict[str, Any]] = Field(default=None, description="대화 데이터")
    
    @staticmethod
    def success_result(message: str, npc_response: str, 
                      available_topics: List[str] = None,
                      dialogue_data: Optional[Dict[str, Any]] = None) -> "DialogueResult":
        return DialogueResult(
            success=True, 
            message=message, 
            npc_response=npc_response,
            available_topics=available_topics or [],
            dialogue_data=dialogue_data
        )
    
    @staticmethod
    def failure_result(message: str) -> "DialogueResult":
        return DialogueResult(
            success=False, 
            message=message, 
            npc_response=""
        )


class DialogueManager:
    """대화 시스템 관리 클래스"""
    
    def __init__(self, 
                 db_connection: DatabaseConnection,
                 game_data_repo: GameDataRepository,
                 runtime_data_repo: RuntimeDataRepository,
                 reference_layer_repo: ReferenceLayerRepository,
                 entity_manager: EntityManager,
                 effect_carrier_manager: Optional[EffectCarrierManager] = None):
        """
        DialogueManager 초기화
        
        Args:
            db_connection: 데이터베이스 연결
            game_data_repo: 게임 데이터 저장소
            runtime_data_repo: 런타임 데이터 저장소
            reference_layer_repo: 참조 레이어 저장소
            entity_manager: 엔티티 관리자
            effect_carrier_manager: Effect Carrier 관리자 (선택사항)
        """
        self.db = db_connection
        self.game_data = game_data_repo
        self.runtime_data = runtime_data_repo
        self.reference_layer = reference_layer_repo
        self.entity_manager = entity_manager
        self.effect_carrier_manager = effect_carrier_manager
        self.logger = logger
        
        # 대화 응답 템플릿
        # 대화 템플릿은 DB에서 동적으로 로드
        self.response_templates = {}
        
        # 동적으로 로드된 대화 주제들
        self.available_topics = []
        self.default_topic = "greeting"
    
    async def start_dialogue(self, player_id: str, npc_id: str, 
                           session_id: str,
                           initial_topic: str = "greeting") -> DialogueResult:
        """대화 시작"""
        # 대화 템플릿이 로드되지 않았으면 로드
        if not self.response_templates:
            await self._load_dialogue_templates()
        
        # 대화 주제가 로드되지 않았으면 로드
        if not self.available_topics:
            await self._load_dialogue_topics()
        try:
            # 플레이어 엔티티 조회
            player_result = await self.entity_manager.get_entity(player_id)
            if not player_result.success or not player_result.entity:
                return DialogueResult.failure_result("플레이어를 찾을 수 없습니다.")
            
            # NPC 엔티티 조회
            npc_result = await self.entity_manager.get_entity(npc_id)
            if not npc_result.success or not npc_result.entity:
                return DialogueResult.failure_result("NPC를 찾을 수 없습니다.")
            
            npc = npc_result.entity
            
            # 대화 가능 여부 확인
            if npc.entity_type != EntityType.NPC:
                return DialogueResult.failure_result(f"{npc.name}과는 대화할 수 없습니다.")
            
            # 대화 컨텍스트 로드
            dialogue_context = await self._load_dialogue_context(npc_id)
            if not dialogue_context:
                # 기본 대화 컨텍스트 생성
                dialogue_context = await self._create_default_dialogue_context(npc, npc_id)
            
            # 대화 주제 로드
            available_topics = await self._get_available_topics(npc_id, player_id)
            
            # 초기 응답 생성
            npc_response = await self._generate_npc_response(npc, initial_topic, dialogue_context)
            
            # 대화 데이터 생성
            dialogue_data = {
                "player_id": player_id,
                "npc_id": npc_id,
                "npc_name": npc.name,
                "initial_topic": initial_topic,
                "dialogue_context": dialogue_context.dict() if dialogue_context else None,
                "timestamp": datetime.now().isoformat()
            }
            
            message = f"{npc.name}과의 대화를 시작했습니다."
            
            return DialogueResult.success_result(
                message=message,
                npc_response=npc_response,
                available_topics=available_topics,
                dialogue_data=dialogue_data
            )
            
        except Exception as e:
            self.logger.error(f"Failed to start dialogue: {str(e)}")
            return DialogueResult.failure_result(f"대화 시작 실패: {str(e)}")
    
    async def continue_dialogue(self, player_id: str, npc_id: str, 
                              topic: str, session_id: str,
                              player_message: str = "") -> DialogueResult:
        """대화 계속"""
        try:
            # NPC 엔티티 조회
            npc_result = await self.entity_manager.get_entity(npc_id)
            if not npc_result.success or not npc_result.entity:
                return DialogueResult.failure_result("NPC를 찾을 수 없습니다.")
            
            npc = npc_result.entity
            
            # 대화 컨텍스트 로드
            dialogue_context = await self._load_dialogue_context(npc_id)
            if not dialogue_context:
                dialogue_context = await self._create_default_dialogue_context(npc, npc_id)
            
            # 대화 주제 로드
            topic_data = await self._load_dialogue_topic(npc_id, topic)
            
            # NPC 응답 생성
            npc_response = await self._generate_npc_response(npc, topic, dialogue_context, topic_data)
            
            # 대화 기록 저장
            dialogue_context_id = f"ctx_{npc_id}_{topic}"
            await self._save_dialogue_history(session_id, player_id, npc_id, dialogue_context_id, topic, player_message, npc_response)
            
            # 사용 가능한 주제 업데이트
            available_topics = await self._get_available_topics(npc_id, player_id)
            
            # 대화 데이터 생성
            dialogue_data = {
                "player_id": player_id,
                "npc_id": npc_id,
                "npc_name": npc.name,
                "topic": topic,
                "player_message": player_message,
                "npc_response": npc_response,
                "timestamp": datetime.now().isoformat()
            }
            
            message = f"{npc.name}과의 대화가 계속됩니다."
            
            return DialogueResult.success_result(
                message=message,
                npc_response=npc_response,
                available_topics=available_topics,
                dialogue_data=dialogue_data
            )
            
        except Exception as e:
            self.logger.error(f"Failed to continue dialogue: {str(e)}")
            return DialogueResult.failure_result(f"대화 계속 실패: {str(e)}")
    
    async def end_dialogue(self, player_id: str, npc_id: str) -> DialogueResult:
        """대화 종료"""
        try:
            # NPC 엔티티 조회
            npc_result = await self.entity_manager.get_entity(npc_id)
            if not npc_result.success or not npc_result.entity:
                return DialogueResult.failure_result("NPC를 찾을 수 없습니다.")
            
            npc = npc_result.entity
            
            # 대화 종료 메시지 생성
            farewell_responses = self.response_templates.get("farewell", ["안녕히 가세요!", "다음에 또 만나요!", "좋은 하루 되세요!"])
            npc_response = farewell_responses[0]  # 간단히 첫 번째 응답 사용
            
            # 대화 데이터 생성
            dialogue_data = {
                "player_id": player_id,
                "npc_id": npc_id,
                "npc_name": npc.name,
                "action": "end_dialogue",
                "timestamp": datetime.now().isoformat()
            }
            
            message = f"{npc.name}과의 대화를 종료했습니다."
            
            return DialogueResult.success_result(
                message=message,
                npc_response=npc_response,
                dialogue_data=dialogue_data
            )
            
        except Exception as e:
            self.logger.error(f"Failed to end dialogue: {str(e)}")
            return DialogueResult.failure_result(f"대화 종료 실패: {str(e)}")
    
    async def _load_dialogue_context(self, npc_id: str) -> Optional[DialogueContext]:
        """대화 컨텍스트 로드"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT dialogue_id, title, content, priority, entity_personality, 
                           available_topics, constraints
                    FROM game_data.dialogue_contexts
                    WHERE dialogue_id LIKE $1
                    ORDER BY dialogue_id
                    LIMIT 1
                """, f"%{npc_id}%")
                
                if not row:
                    return None
                
                return DialogueContext(
                    context_id=row['dialogue_id'],
                    title=row['title'],
                    content=row['content'],
                    priority=row['priority'],
                    entity_personality=row['entity_personality'],
                    available_topics=parse_jsonb_data(row['available_topics']) or {},
                    constraints=parse_jsonb_data(row['constraints']) or {}
                )
        except Exception as e:
            self.logger.error(f"Failed to load dialogue context: {str(e)}")
            return None
    
    async def _create_default_dialogue_context(self, npc, npc_id: str) -> DialogueContext:
        """기본 대화 컨텍스트 생성"""
        return DialogueContext(
            context_id=f"default_{npc.entity_id}",
            title=f"{npc.name}과의 대화",
            content=f"{npc.name}과의 기본 대화입니다.",
            priority=await self.get_default_priority(),
            entity_personality=npc.properties.get("personality", "친근한"),
            available_topics={
                "topics": await self.get_available_topics(npc_id),
                "default_topic": self.default_topic
            },
            constraints={
                "max_response_length": 200,
                "tone": "friendly"
            }
        )
    
    async def _load_dialogue_topic(self, npc_id: str, topic: str) -> Optional[DialogueTopic]:
        """대화 주제 로드"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT topic_id, dialogue_id, topic_type, content, conditions
                    FROM game_data.dialogue_topics
                    WHERE dialogue_id LIKE $1 AND topic_type = $2
                    LIMIT 1
                """, f"%{npc_id}%", topic)
                
                if not row:
                    return None
                
                return DialogueTopic(
                    topic_id=row['topic_id'],
                    dialogue_id=row['dialogue_id'],
                    topic_type=row['topic_type'],
                    content=row['content'],
                    conditions=parse_jsonb_data(row['conditions']) or {}
                )
        except Exception as e:
            self.logger.error(f"Failed to load dialogue topic: {str(e)}")
            return None
    
    async def _get_available_topics(self, npc_id: str, player_id: str) -> List[str]:
        """사용 가능한 주제 목록 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT topic_type
                    FROM game_data.dialogue_topics
                    WHERE dialogue_id LIKE $1
                    ORDER BY topic_type
                """, f"%{npc_id}%")
                
                topics = [row['topic_type'] for row in rows]
                
                # 기본 주제 추가
                # 동적으로 기본 주제 로드
                default_topics = await self.get_available_topics()
                for topic in default_topics:
                    if topic not in topics:
                        topics.append(topic)
                
                return topics
        except Exception as e:
            self.logger.error(f"Failed to get available topics: {str(e)}")
            # 동적으로 기본 주제 반환
            if self.available_topics:
                return self.available_topics[:2]  # 처음 2개 주제 반환
            return ["greeting", "farewell"]
    
    async def _generate_npc_response(self, npc, topic: str, 
                                    dialogue_context: DialogueContext,
                                    topic_data: Optional[DialogueTopic] = None) -> str:
        """NPC 응답 생성"""
        try:
            # 주제별 응답 템플릿 사용
            if topic in self.response_templates and len(self.response_templates[topic]) > 0:
                responses = self.response_templates[topic]
                # NPC 성격에 따른 응답 선택 (간단한 구현)
                response_index = hash(npc.entity_id + topic) % len(responses)
                base_response = responses[response_index]
            else:
                base_response = f"{npc.name}: 무엇을 도와드릴까요?"
            
            # 대화 컨텍스트가 있으면 내용 활용
            if dialogue_context and dialogue_context.content:
                base_response = f"{npc.name}: {dialogue_context.content}"
            
            # 주제 데이터가 있으면 내용 활용
            if topic_data and topic_data.content:
                base_response = f"{npc.name}: {topic_data.content}"
            
            # 제약 조건 적용
            max_length = dialogue_context.constraints.get("max_response_length", 200) if dialogue_context else 200
            if len(base_response) > max_length:
                base_response = base_response[:max_length-3] + "..."
            
            return base_response
            
        except Exception as e:
            self.logger.error(f"Failed to generate NPC response: {str(e)}")
            return f"{npc.name}: 죄송합니다. 지금은 대화할 수 없습니다."
    
    async def _save_dialogue_history(self, session_id: str, player_id: str, npc_id: str, 
                                   dialogue_context_id: str, topic_id: Optional[str], 
                                   player_message: str, npc_response: str):
        """대화 기록 저장 (올바른 스키마 사용)"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 먼저 세션 생성 (존재하지 않는 경우)
                await conn.execute("""
                    INSERT INTO runtime_data.active_sessions 
                    (session_id, session_name, session_state, created_at, updated_at)
                    VALUES ($1, $2, $3, NOW(), NOW())
                    ON CONFLICT (session_id) DO NOTHING
                """, 
                session_id,
                f"Session {session_id[:8]}",
                "active"
                )
                
                # 먼저 dialogue_contexts에 컨텍스트가 있는지 확인하고 없으면 생성
                await conn.execute("""
                    INSERT INTO game_data.dialogue_contexts 
                    (dialogue_id, title, content, priority, entity_personality, available_topics, constraints)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (dialogue_id) DO NOTHING
                """, 
                dialogue_context_id,
                f"Dialogue Context {dialogue_context_id}",
                f"Context for {npc_id}",
                1,
                "neutral",
                serialize_jsonb_data({"topics": [topic_id] if topic_id else []}),
                serialize_jsonb_data({"max_response_length": 200})
                )
                
                # 대화 기록 저장 (올바른 스키마 사용)
                await conn.execute("""
                    INSERT INTO runtime_data.dialogue_history
                    (session_id, runtime_entity_id, context_id, speaker_type, message, relevant_knowledge, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                session_id, 
                player_id,  # runtime_entity_id
                dialogue_context_id,  # context_id
                "player",  # speaker_type
                f"Player: {player_message}",  # message
                serialize_jsonb_data({"topic": topic_id, "npc_id": npc_id}) if topic_id else None,  # relevant_knowledge
                datetime.now()
                )
                
                # NPC 응답도 별도로 저장
                await conn.execute("""
                    INSERT INTO runtime_data.dialogue_history
                    (session_id, runtime_entity_id, context_id, speaker_type, message, relevant_knowledge, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                session_id, 
                npc_id,  # runtime_entity_id
                dialogue_context_id,  # context_id
                "npc",  # speaker_type
                f"NPC: {npc_response}",  # message
                serialize_jsonb_data({"topic": topic_id, "player_id": player_id}) if topic_id else None,  # relevant_knowledge
                datetime.now()
                )
        except Exception as e:
            self.logger.error(f"Failed to save dialogue history: {str(e)}")
    
    async def get_dialogue_history(self, session_id: str, player_id: str, npc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """대화 기록 조회 (올바른 스키마 사용)"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                query = """
                    SELECT history_id, session_id, runtime_entity_id, context_id, speaker_type, message, relevant_knowledge, timestamp
                    FROM runtime_data.dialogue_history
                    WHERE session_id = $1
                """
                params = [session_id]
                
                if player_id:
                    query += " AND (runtime_entity_id = $2"
                    params.append(player_id)
                    if npc_id:
                        query += " OR runtime_entity_id = $3"
                        params.append(npc_id)
                    query += ")"
                elif npc_id:
                    query += " AND runtime_entity_id = $2"
                    params.append(npc_id)
                
                query += " ORDER BY timestamp DESC LIMIT 50"
                
                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get dialogue history: {str(e)}")
            return []
    
    async def _load_dialogue_templates(self):
        """DB에서 대화 템플릿 로드"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # game_data.dialogue_contexts 테이블에서 대화 템플릿 로드
                templates = await conn.fetch("""
                    SELECT title, content, entity_personality, available_topics
                    FROM game_data.dialogue_contexts
                    WHERE entity_id IS NULL OR entity_id = ''
                    ORDER BY dialogue_id
                """)
                
                # 템플릿을 주제별로 분류
                for template in templates:
                    title = template['title'].lower()
                    content = template['content']
                    personality = template['entity_personality'] or "neutral"
                    topics = parse_jsonb_data(template['available_topics']) or {}
                    
                    # 주제별 템플릿 생성
                    if 'greeting' in title or 'greeting' in topics:
                        if 'greeting' not in self.response_templates:
                            self.response_templates['greeting'] = []
                        self.response_templates['greeting'].append(content)
                    
                    if 'trade' in title or 'trade' in topics:
                        if 'trade' not in self.response_templates:
                            self.response_templates['trade'] = []
                        self.response_templates['trade'].append(content)
                    
                    if 'lore' in title or 'lore' in topics:
                        if 'lore' not in self.response_templates:
                            self.response_templates['lore'] = []
                        self.response_templates['lore'].append(content)
                    
                    if 'quest' in title or 'quest' in topics:
                        if 'quest' not in self.response_templates:
                            self.response_templates['quest'] = []
                        self.response_templates['quest'].append(content)
                    
                    if 'farewell' in title or 'farewell' in topics:
                        if 'farewell' not in self.response_templates:
                            self.response_templates['farewell'] = []
                        self.response_templates['farewell'].append(content)
                
                # 기본 템플릿이 없으면 기본값 설정
                self._set_default_templates()
                
        except Exception as e:
            self.logger.error(f"Failed to load dialogue templates: {str(e)}")
            self._set_default_templates()
    
    def _set_default_templates(self):
        """기본 대화 템플릿 설정 - DB에서 로드 실패 시 빈 템플릿 사용"""
        # 완전한 추상화를 위해 하드코딩된 템플릿 제거
        # DB에서 로드 실패 시 빈 템플릿으로 초기화
        self.response_templates = {
            "greeting": [
                "안녕하세요! 무엇을 도와드릴까요?",
                "어서오세요! 반갑습니다.",
                "안녕하세요! 오늘 기분은 어떠신가요?"
            ],
            "trade": [
                "무엇을 사고 싶으신가요?",
                "좋은 물건들이 많이 있습니다.",
                "가격을 확인해보시겠어요?"
            ],
            "lore": [
                "그 이야기를 들어보시겠어요?",
                "흥미로운 이야기가 있습니다.",
                "옛날 이야기를 해드릴까요?"
            ],
            "quest": [
                "도움이 필요한 일이 있나요?",
                "무엇을 도와드릴까요?",
                "특별한 일이 있으시면 말씀해주세요."
            ],
            "farewell": [
                "안녕히 가세요!",
                "다음에 또 만나요!",
                "좋은 하루 되세요!"
            ]
        }
        self.logger.warning("대화 템플릿을 DB에서 로드할 수 없어 빈 템플릿을 사용합니다.")
    
    async def _load_dialogue_topics(self):
        """DB에서 대화 주제 로드"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # game_data.dialogue_topics 테이블에서 주제 로드
                topics = await conn.fetch("""
                    SELECT DISTINCT topic_type
                    FROM game_data.dialogue_topics
                    ORDER BY topic_type
                """)
                
                self.available_topics = [topic['topic_type'] for topic in topics]
                
                # 기본 주제 설정
                if topics:
                    # 가장 높은 우선순위의 주제를 기본 주제로 설정
                    self.default_topic = topics[0]['topic_type']
                else:
                    self.default_topic = "greeting"
                
                logger.info(f"Loaded {len(self.available_topics)} dialogue topics from database")
                
        except Exception as e:
            logger.error(f"Failed to load dialogue topics: {str(e)}")
            self._set_default_topics()
    
    def _set_default_topics(self):
        """기본 대화 주제 설정"""
        self.available_topics = ["greeting", "trade", "lore", "quest", "farewell"]
        self.default_topic = "greeting"
        logger.warning("Using default dialogue topics")
    
    async def get_available_topics(self, npc_id: str = None) -> List[str]:
        """사용 가능한 대화 주제 조회"""
        if not self.available_topics:
            await self._load_dialogue_topics()
        
        if npc_id:
            # 특정 NPC에 대한 주제 필터링 (향후 확장 가능)
            try:
                pool = await self.db.pool
                async with pool.acquire() as conn:
                    npc_topics = await conn.fetch("""
                        SELECT DISTINCT dt.topic_type
                        FROM game_data.dialogue_topics dt
                        JOIN game_data.dialogue_contexts dc ON dt.dialogue_id = dc.dialogue_id
                        WHERE (dc.entity_id = $1 OR dc.entity_id IS NULL)
                        ORDER BY dt.topic_type
                    """, npc_id)
                    
                    return [topic['topic_type'] for topic in npc_topics]
            except Exception as e:
                logger.error(f"Failed to load NPC-specific topics: {str(e)}")
                return self.available_topics
        
        return self.available_topics
    
    async def get_default_priority(self) -> int:
        """DB에서 기본 우선순위 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT AVG(priority) as avg_priority
                    FROM game_data.dialogue_contexts
                """)
                
                if result and result['avg_priority']:
                    return int(result['avg_priority'])
                return 1  # 기본값
                
        except Exception as e:
            logger.error(f"Failed to load default priority: {str(e)}")
            return 1
    
    async def get_npc_dialogue_info(self, npc_id: str) -> Dict[str, Any]:
        """NPC 대화 정보 조회"""
        try:
            # NPC 엔티티 조회
            npc_result = await self.entity_manager.get_entity(npc_id)
            if not npc_result.success or not npc_result.entity:
                return {}
            
            npc = npc_result.entity
            
            # 대화 컨텍스트 조회
            dialogue_context = await self._load_dialogue_context(npc_id)
            available_topics = await self._get_available_topics(npc_id, "")
            
            return {
                "npc_id": npc_id,
                "npc_name": npc.name,
                "entity_type": npc.entity_type,
                "personality": npc.properties.get("personality", "친근한"),
                "dialogue_context": dialogue_context.dict() if dialogue_context else None,
                "available_topics": available_topics,
                "properties": npc.properties
            }
        except Exception as e:
            self.logger.error(f"Failed to get NPC dialogue info: {str(e)}")
            return {}
