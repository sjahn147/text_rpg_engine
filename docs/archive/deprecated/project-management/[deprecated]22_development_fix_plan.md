# [deprecated] 개발 수정 계획서

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 이유**: 개발 수정 작업이 완료되어 더 이상 진행 중인 작업이 아님. 현재는 Phase 4+ 개발이 진행 중이며, 이 계획서의 목표들은 대부분 달성되었음.  
**작성일**: 2025-10-19  
**프로젝트**: RPG Engine - Story Engine  
**버전**: v0.2.1 → v0.3.0  
**목표**: 코딩 컨벤션 준수 및 안정적인 프레임워크 구축

## 🎯 **수정 목표**

### **핵심 목표**
1. **API 통일**: Manager 클래스 간 인터페이스 일관성 확보
2. **스키마 정합성**: 데이터베이스 스키마와 코드 완전 일치
3. **에러 처리 시스템**: 체계적인 에러 처리 및 로깅 구축
4. **테스트 시스템**: 실제 문제 해결 기반 테스트 구축

### **품질 목표**
- **코드 커버리지**: 80% 이상
- **타입 안전성**: 100% 타입 힌트 적용
- **에러 처리**: 모든 예외 명시적 처리
- **API 일관성**: Manager 클래스 간 인터페이스 통일

## 📋 **단계별 수정 계획**

### **Phase 1: API 통일 (1-2주)**

#### **1.1 EntityManager 수정**

**현재 문제점**:
```python
# ❌ 현재 구현
async def create_entity(self, static_entity_id: str, session_id: str) -> EntityResult:
    # EntityResult 객체를 반환하는데, 다른 Manager들이 엔티티 ID 문자열을 기대
    return EntityResult.success(entity=entity_data, message="생성 완료")
```

**수정 방안**:
```python
# ✅ 수정된 구현
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class EntityCreationStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    VALIDATION_ERROR = "validation_error"
    DATABASE_ERROR = "database_error"

class EntityCreationResult(BaseModel):
    status: EntityCreationStatus
    entity_id: Optional[str] = None
    entity_data: Optional[EntityData] = None
    message: str
    error_code: Optional[str] = None
    
    @classmethod
    def success(cls, entity_id: str, entity_data: EntityData, message: str = "엔티티 생성 성공") -> "EntityCreationResult":
        return cls(
            status=EntityCreationStatus.SUCCESS,
            entity_id=entity_id,
            entity_data=entity_data,
            message=message
        )
    
    @classmethod
    def error(cls, message: str, error_code: str = "UNKNOWN_ERROR") -> "EntityCreationResult":
        return cls(
            status=EntityCreationStatus.ERROR,
            message=message,
            error_code=error_code
        )

async def create_entity(self, static_entity_id: str, session_id: str) -> EntityCreationResult:
    """엔티티 생성 - 명확한 반환 타입과 일관성"""
    try:
        # 1. 입력 검증
        if not static_entity_id or not session_id:
            return EntityCreationResult.error("필수 매개변수가 누락되었습니다", "MISSING_PARAMETERS")
        
        # 2. 정적 템플릿 로드
        template = await self._load_entity_template(static_entity_id)
        if not template:
            return EntityCreationResult.error("엔티티 템플릿을 찾을 수 없습니다", "TEMPLATE_NOT_FOUND")
        
        # 3. 런타임 엔티티 생성
        entity_id = str(uuid.uuid4())
        entity_data = await self._create_runtime_entity(entity_id, template, session_id)
        
        # 4. 참조 레이어 생성
        await self._create_entity_reference(entity_id, static_entity_id, session_id)
        
        return EntityCreationResult.success(
            entity_id=entity_id,
            entity_data=entity_data,
            message="엔티티가 성공적으로 생성되었습니다"
        )
        
    except ValidationError as e:
        logger.warning(f"엔티티 생성 검증 실패: {e}")
        return EntityCreationResult.error(f"입력 데이터 검증 실패: {e}", "VALIDATION_ERROR")
    except DatabaseError as e:
        logger.error(f"엔티티 생성 DB 오류: {e}")
        return EntityCreationResult.error("데이터베이스 오류로 엔티티 생성 실패", "DATABASE_ERROR")
    except Exception as e:
        logger.error(f"엔티티 생성 예상치 못한 오류: {e}")
        return EntityCreationResult.error("엔티티 생성 중 예상치 못한 오류 발생", "UNKNOWN_ERROR")
```

#### **1.2 DialogueManager 수정**

**현재 문제점**:
```python
# ❌ 현재 구현
async def continue_dialogue(self, player_id: str, npc_id: str, 
                          topic: str, session_id: str,
                          player_message: str = "") -> DialogueResult:
    # topic이 필수 매개변수인데 테스트에서는 선택적으로 사용
    # session_id가 중간에 위치하여 일관성 부족
```

**수정 방안**:
```python
# ✅ 수정된 구현
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class DialogueResult(BaseModel):
    success: bool
    message: str
    npc_response: str = ""
    available_topics: List[str] = Field(default_factory=list)
    dialogue_data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    
    @classmethod
    def success_result(cls, message: str, npc_response: str = "", 
                      available_topics: List[str] = None, 
                      dialogue_data: Dict[str, Any] = None) -> "DialogueResult":
        return cls(
            success=True,
            message=message,
            npc_response=npc_response,
            available_topics=available_topics or [],
            dialogue_data=dialogue_data or {}
        )
    
    @classmethod
    def error_result(cls, message: str, error_code: str = "UNKNOWN_ERROR") -> "DialogueResult":
        return cls(
            success=False,
            message=message,
            error_code=error_code
        )

async def continue_dialogue(self, 
                          player_id: str, 
                          npc_id: str, 
                          session_id: str,
                          topic: Optional[str] = None,
                          player_message: str = "") -> DialogueResult:
    """대화 계속 - 명확한 매개변수 순서와 타입"""
    try:
        # 1. 입력 검증
        if not player_id or not npc_id or not session_id:
            return DialogueResult.error_result("필수 매개변수가 누락되었습니다", "MISSING_PARAMETERS")
        
        # 2. 플레이어 엔티티 조회
        player_result = await self.entity_manager.get_entity(player_id)
        if not player_result.success:
            return DialogueResult.error_result("플레이어를 찾을 수 없습니다", "PLAYER_NOT_FOUND")
        
        # 3. NPC 엔티티 조회
        npc_result = await self.entity_manager.get_entity(npc_id)
        if not npc_result.success:
            return DialogueResult.error_result("NPC를 찾을 수 없습니다", "NPC_NOT_FOUND")
        
        # 4. 대화 주제 결정
        if not topic:
            topic = await self._get_default_topic(npc_id)
        
        # 5. 대화 로직 실행
        dialogue_context = await self._load_dialogue_context(npc_id)
        npc_response = await self._generate_npc_response(npc_result.entity, topic, dialogue_context)
        
        # 6. 대화 기록 저장
        await self._save_dialogue_history(session_id, player_id, npc_id, topic, player_message, npc_response)
        
        # 7. 사용 가능한 주제 업데이트
        available_topics = await self._get_available_topics(npc_id, player_id)
        
        return DialogueResult.success_result(
            message=f"{npc_result.entity.name}과의 대화가 계속됩니다",
            npc_response=npc_response,
            available_topics=available_topics,
            dialogue_data={
                "player_id": player_id,
                "npc_id": npc_id,
                "topic": topic,
                "player_message": player_message,
                "npc_response": npc_response,
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except ValidationError as e:
        logger.warning(f"대화 계속 검증 실패: {e}")
        return DialogueResult.error_result(f"입력 데이터 검증 실패: {e}", "VALIDATION_ERROR")
    except DatabaseError as e:
        logger.error(f"대화 계속 DB 오류: {e}")
        return DialogueResult.error_result("데이터베이스 오류로 대화 계속 실패", "DATABASE_ERROR")
    except Exception as e:
        logger.error(f"대화 계속 예상치 못한 오류: {e}")
        return DialogueResult.error_result("대화 계속 중 예상치 못한 오류 발생", "UNKNOWN_ERROR")
```

#### **1.3 ActionHandler 수정**

**현재 문제점**:
```python
# ❌ 현재 구현
async def get_available_actions(self, player_id: str) -> List[Dict[str, Any]]:
    # current_cell_id 매개변수가 누락되어 테스트 실패
```

**수정 방안**:
```python
# ✅ 수정된 구현
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ActionInfo(BaseModel):
    type: str
    name: str
    description: str
    requirements: Dict[str, Any] = Field(default_factory=dict)
    cooldown: Optional[int] = None

class ActionResult(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    effects: List[Dict[str, Any]] = Field(default_factory=list)
    error_code: Optional[str] = None
    
    @classmethod
    def success_result(cls, message: str, data: Dict[str, Any] = None, 
                      effects: List[Dict[str, Any]] = None) -> "ActionResult":
        return cls(
            success=True,
            message=message,
            data=data or {},
            effects=effects or []
        )
    
    @classmethod
    def error_result(cls, message: str, error_code: str = "UNKNOWN_ERROR") -> "ActionResult":
        return cls(
            success=False,
            message=message,
            error_code=error_code
        )

async def get_available_actions(self, player_id: str, current_cell_id: Optional[str] = None) -> List[ActionInfo]:
    """사용 가능한 행동 조회 - 명확한 매개변수와 반환 타입"""
    try:
        # 1. 입력 검증
        if not player_id:
            logger.warning("플레이어 ID가 누락되었습니다")
            return []
        
        # 2. 플레이어 엔티티 조회
        player_result = await self.entity_manager.get_entity(player_id)
        if not player_result.success:
            logger.warning(f"플레이어를 찾을 수 없습니다: {player_id}")
            return []
        
        # 3. 기본 행동 목록
        basic_actions = [
            ActionInfo(type="wait", name="대기", description="시간을 기다립니다"),
            ActionInfo(type="investigate", name="조사", description="현재 위치를 조사합니다")
        ]
        
        # 4. 셀 기반 행동 추가
        if current_cell_id:
            cell_actions = await self._get_cell_specific_actions(current_cell_id)
            basic_actions.extend(cell_actions)
        
        # 5. 플레이어 상태 기반 행동 추가
        player_actions = await self._get_player_specific_actions(player_result.entity)
        basic_actions.extend(player_actions)
        
        return basic_actions
        
    except Exception as e:
        logger.error(f"사용 가능한 행동 조회 중 오류: {e}")
        return []

async def execute_action(self, action_type: str, player_id: str, session_id: str,
                        target_id: Optional[str] = None, **kwargs) -> ActionResult:
    """행동 실행 - 명확한 매개변수와 반환 타입"""
    try:
        # 1. 입력 검증
        if not action_type or not player_id or not session_id:
            return ActionResult.error_result("필수 매개변수가 누락되었습니다", "MISSING_PARAMETERS")
        
        # 2. 플레이어 엔티티 조회
        player_result = await self.entity_manager.get_entity(player_id)
        if not player_result.success:
            return ActionResult.error_result("플레이어를 찾을 수 없습니다", "PLAYER_NOT_FOUND")
        
        # 3. 행동 타입별 처리
        if action_type == "wait":
            return await self._handle_wait_action(player_id, session_id, **kwargs)
        elif action_type == "investigate":
            return await self._handle_investigate_action(player_id, session_id, **kwargs)
        elif action_type == "move":
            if not target_id:
                return ActionResult.error_result("이동 행동에는 대상 셀 ID가 필요합니다", "MISSING_TARGET")
            return await self._handle_move_action(player_id, target_id, session_id, **kwargs)
        elif action_type == "dialogue":
            if not target_id:
                return ActionResult.error_result("대화 행동에는 대상 NPC ID가 필요합니다", "MISSING_TARGET")
            return await self._handle_dialogue_action(player_id, target_id, session_id, **kwargs)
        else:
            return ActionResult.error_result(f"지원하지 않는 행동 타입: {action_type}", "INVALID_ACTION_TYPE")
        
    except ValidationError as e:
        logger.warning(f"행동 실행 검증 실패: {e}")
        return ActionResult.error_result(f"입력 데이터 검증 실패: {e}", "VALIDATION_ERROR")
    except DatabaseError as e:
        logger.error(f"행동 실행 DB 오류: {e}")
        return ActionResult.error_result("데이터베이스 오류로 행동 실행 실패", "DATABASE_ERROR")
    except Exception as e:
        logger.error(f"행동 실행 예상치 못한 오류: {e}")
        return ActionResult.error_result("행동 실행 중 예상치 못한 오류 발생", "UNKNOWN_ERROR")
```

### **Phase 2: 스키마 정합성 (1주)**

#### **2.1 스키마 검증 도구 개발**

```python
# ✅ 스키마 검증 도구
class SchemaValidator:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    async def validate_schema_consistency(self) -> ValidationResult:
        """스키마 일관성 검증"""
        issues = []
        
        # 1. 존재하지 않는 칼럼 참조 검사
        column_issues = await self._check_column_references()
        issues.extend(column_issues)
        
        # 2. JSONB 타입 검증
        jsonb_issues = await self._check_jsonb_types()
        issues.extend(jsonb_issues)
        
        # 3. 인덱스 검증
        index_issues = await self._check_indexes()
        issues.extend(index_issues)
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            summary=f"총 {len(issues)}개 문제 발견"
        )
    
    async def _check_column_references(self) -> List[SchemaIssue]:
        """존재하지 않는 칼럼 참조 검사"""
        issues = []
        
        # 문제가 있는 쿼리들 검사
        problematic_queries = [
            {
                "query": "SELECT * FROM game_data.dialogue_topics ORDER BY priority",
                "issue": "priority 칼럼이 존재하지 않음",
                "fix": "ORDER BY topic_id 사용"
            },
            {
                "query": "SELECT * FROM runtime_data.dialogue_sessions",
                "issue": "dialogue_sessions 테이블이 존재하지 않음",
                "fix": "dialogue_history 테이블 사용"
            }
        ]
        
        for query_info in problematic_queries:
            try:
                await self.db.execute_query(query_info["query"])
            except Exception as e:
                issues.append(SchemaIssue(
                    type="COLUMN_REFERENCE_ERROR",
                    severity="HIGH",
                    description=query_info["issue"],
                    query=query_info["query"],
                    fix_suggestion=query_info["fix"]
                ))
        
        return issues
```

#### **2.2 쿼리 수정**

```python
# ✅ 수정된 쿼리들
class FixedQueries:
    @staticmethod
    async def get_dialogue_topics(db: DatabaseConnection) -> List[Dict[str, Any]]:
        """수정된 대화 주제 조회"""
        return await db.execute_query("""
            SELECT topic_type, topic_id, content
            FROM game_data.dialogue_topics
            ORDER BY topic_id
            LIMIT 10
        """)
    
    @staticmethod
    async def get_dialogue_history(db: DatabaseConnection, session_id: str, 
                                 player_id: str, npc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """수정된 대화 기록 조회"""
        if npc_id:
            return await db.execute_query("""
                SELECT speaker_type, message, timestamp
                FROM runtime_data.dialogue_history
                WHERE session_id = $1 AND runtime_entity_id = $2 AND context_id LIKE $3
                ORDER BY timestamp DESC
            """, session_id, player_id, f"%{npc_id}%")
        else:
            return await db.execute_query("""
                SELECT speaker_type, message, timestamp
                FROM runtime_data.dialogue_history
                WHERE session_id = $1 AND runtime_entity_id = $2
                ORDER BY timestamp DESC
            """, session_id, player_id)
```

### **Phase 3: 에러 처리 시스템 (1주)**

#### **3.1 에러 타입 정의**

```python
# ✅ 계층별 에러 타입
class ValidationError(Exception):
    """데이터 검증 에러"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(message)

class DatabaseError(Exception):
    """데이터베이스 에러"""
    def __init__(self, message: str, query: str = None, parameters: List[Any] = None):
        self.message = message
        self.query = query
        self.parameters = parameters
        super().__init__(message)

class BusinessLogicError(Exception):
    """비즈니스 로직 에러"""
    def __init__(self, message: str, operation: str = None, context: Dict[str, Any] = None):
        self.message = message
        self.operation = operation
        self.context = context
        super().__init__(message)
```

#### **3.2 구조화된 로깅**

```python
# ✅ 구조화된 로깅 시스템
import structlog
from typing import Dict, Any, Optional

class GameLogger:
    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)
    
    def log_entity_creation(self, entity_id: str, entity_type: str, 
                           session_id: str, success: bool, error: Optional[str] = None):
        """엔티티 생성 로그"""
        self.logger.info(
            "Entity creation",
            entity_id=entity_id,
            entity_type=entity_type,
            session_id=session_id,
            success=success,
            error=error
        )
    
    def log_dialogue_interaction(self, player_id: str, npc_id: str, 
                               topic: str, session_id: str, success: bool, error: Optional[str] = None):
        """대화 상호작용 로그"""
        self.logger.info(
            "Dialogue interaction",
            player_id=player_id,
            npc_id=npc_id,
            topic=topic,
            session_id=session_id,
            success=success,
            error=error
        )
    
    def log_action_execution(self, action_type: str, player_id: str, 
                           session_id: str, success: bool, error: Optional[str] = None):
        """행동 실행 로그"""
        self.logger.info(
            "Action execution",
            action_type=action_type,
            player_id=player_id,
            session_id=session_id,
            success=success,
            error=error
        )
```

### **Phase 4: 테스트 시스템 개선 (1-2주)**

#### **4.1 통합 테스트 구축**

```python
# ✅ 통합 테스트
class ManagerIntegrationTest:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.entity_manager = None
        self.cell_manager = None
        self.dialogue_manager = None
        self.action_handler = None
    
    async def setup_managers(self):
        """Manager 클래스들 초기화"""
        # Repository 초기화
        game_data_repo = GameDataRepository(self.db)
        runtime_data_repo = RuntimeDataRepository(self.db)
        reference_layer_repo = ReferenceLayerRepository(self.db)
        
        # Effect Carrier Manager 초기화
        effect_carrier_manager = EffectCarrierManager(
            self.db, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        
        # Manager 클래스들 초기화
        self.entity_manager = EntityManager(
            self.db, game_data_repo, runtime_data_repo, reference_layer_repo, effect_carrier_manager
        )
        
        self.cell_manager = CellManager(
            self.db, game_data_repo, runtime_data_repo, reference_layer_repo, self.entity_manager
        )
        
        self.dialogue_manager = DialogueManager(
            self.db, game_data_repo, runtime_data_repo, reference_layer_repo, 
            self.entity_manager, effect_carrier_manager
        )
        
        self.action_handler = ActionHandler(
            self.db, game_data_repo, runtime_data_repo, reference_layer_repo,
            self.entity_manager, self.cell_manager, effect_carrier_manager
        )
    
    async def test_entity_creation_flow(self) -> TestResult:
        """엔티티 생성 플로우 테스트"""
        try:
            # 1. 엔티티 생성
            session_id = str(uuid.uuid4())
            entity_result = await self.entity_manager.create_entity("NPC_VILLAGER_001", session_id)
            
            # 2. 결과 검증
            assert entity_result.status == EntityCreationStatus.SUCCESS, f"엔티티 생성 실패: {entity_result.message}"
            assert entity_result.entity_id is not None, "엔티티 ID가 생성되지 않음"
            assert entity_result.entity_data is not None, "엔티티 데이터가 생성되지 않음"
            
            # 3. DB 검증
            db_entity = await self.db.execute_query(
                "SELECT * FROM runtime_data.runtime_entities WHERE runtime_entity_id = $1",
                entity_result.entity_id
            )
            assert len(db_entity) == 1, "DB에 엔티티가 저장되지 않음"
            
            return TestResult.success("엔티티 생성 플로우 테스트 통과")
            
        except Exception as e:
            return TestResult.error(f"엔티티 생성 플로우 테스트 실패: {e}")
    
    async def test_dialogue_interaction_flow(self) -> TestResult:
        """대화 상호작용 플로우 테스트"""
        try:
            # 1. 플레이어와 NPC 생성
            session_id = str(uuid.uuid4())
            player_result = await self.entity_manager.create_entity("NPC_VILLAGER_001", session_id)
            npc_result = await self.entity_manager.create_entity("NPC_MERCHANT_001", session_id)
            
            # 2. 대화 시작
            dialogue_result = await self.dialogue_manager.start_dialogue(
                player_result.entity_id, npc_result.entity_id, session_id
            )
            
            # 3. 결과 검증
            assert dialogue_result.success, f"대화 시작 실패: {dialogue_result.message}"
            assert len(dialogue_result.available_topics) > 0, "사용 가능한 대화 주제가 없음"
            
            # 4. 대화 계속
            continue_result = await self.dialogue_manager.continue_dialogue(
                player_result.entity_id, npc_result.entity_id, session_id, 
                topic="greeting", player_message="안녕하세요!"
            )
            
            # 5. 결과 검증
            assert continue_result.success, f"대화 계속 실패: {continue_result.message}"
            assert continue_result.npc_response != "", "NPC 응답이 없음"
            
            return TestResult.success("대화 상호작용 플로우 테스트 통과")
            
        except Exception as e:
            return TestResult.error(f"대화 상호작용 플로우 테스트 실패: {e}")
```

#### **4.2 시나리오 테스트 완성**

```python
# ✅ 완전한 시나리오 테스트
class CompleteScenarioTest:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.test_session_id = str(uuid.uuid4())
        self.managers = None
    
    async def setup_test_environment(self):
        """테스트 환경 설정"""
        # Manager 클래스들 초기화
        self.managers = await self._initialize_managers()
        
        # 테스트 세션 생성
        await self.db.execute_query(
            "INSERT INTO runtime_data.active_sessions (session_id, session_name, session_state) VALUES ($1, $2, $3)",
            self.test_session_id, "통합 테스트", "active"
        )
    
    async def test_complete_game_flow(self) -> TestResult:
        """완전한 게임 플로우 테스트"""
        try:
            # 1. 엔티티 생성
            player_result = await self.managers.entity_manager.create_entity("NPC_VILLAGER_001", self.test_session_id)
            npc_result = await self.managers.entity_manager.create_entity("NPC_MERCHANT_001", self.test_session_id)
            
            # 2. 셀 생성
            cell_result = await self.managers.cell_manager.create_cell("CELL_VILLAGE_CENTER_001", self.test_session_id)
            
            # 3. 플레이어를 셀에 배치
            enter_result = await self.managers.cell_manager.enter_cell(player_result.entity_id, cell_result.cell_id)
            
            # 4. 행동 실행
            action_result = await self.managers.action_handler.execute_action(
                "investigate", player_result.entity_id, self.test_session_id
            )
            
            # 5. 대화 상호작용
            dialogue_result = await self.managers.dialogue_manager.start_dialogue(
                player_result.entity_id, npc_result.entity_id, self.test_session_id
            )
            
            # 6. 모든 결과 검증
            assert player_result.status == EntityCreationStatus.SUCCESS, "플레이어 생성 실패"
            assert npc_result.status == EntityCreationStatus.SUCCESS, "NPC 생성 실패"
            assert cell_result.success, "셀 생성 실패"
            assert enter_result.success, "셀 입장 실패"
            assert action_result.success, "행동 실행 실패"
            assert dialogue_result.success, "대화 시작 실패"
            
            return TestResult.success("완전한 게임 플로우 테스트 통과")
            
        except Exception as e:
            return TestResult.error(f"완전한 게임 플로우 테스트 실패: {e}")
```

## 📊 **수정 일정**

### **Week 1-2: API 통일**
- **Day 1-3**: EntityManager 수정
- **Day 4-6**: DialogueManager 수정
- **Day 7-10**: ActionHandler 수정
- **Day 11-14**: 통합 테스트 및 검증

### **Week 3: 스키마 정합성**
- **Day 1-2**: 스키마 검증 도구 개발
- **Day 3-4**: 쿼리 수정
- **Day 5-7**: 검증 및 테스트

### **Week 4: 에러 처리 시스템**
- **Day 1-2**: 에러 타입 정의
- **Day 3-4**: 로깅 시스템 구축
- **Day 5-7**: 에러 처리 통합

### **Week 5-6: 테스트 시스템 개선**
- **Day 1-3**: 통합 테스트 구축
- **Day 4-6**: 시나리오 테스트 완성
- **Day 7-10**: 성능 테스트 및 최적화

## 🎯 **성공 기준**

### **기능적 기준**
- ✅ 모든 Manager 클래스 API 통일
- ✅ 데이터베이스 스키마와 코드 완전 일치
- ✅ 체계적인 에러 처리 시스템
- ✅ 포괄적인 테스트 커버리지

### **품질 기준**
- ✅ 코드 커버리지 80% 이상
- ✅ 타입 안전성 100% 적용
- ✅ 에러 처리 100% 명시적 처리
- ✅ API 일관성 100% 달성

### **성능 기준**
- ✅ 단위 테스트 실행 시간 < 10초
- ✅ 통합 테스트 실행 시간 < 30초
- ✅ 시나리오 테스트 실행 시간 < 60초
- ✅ 메모리 사용량 안정적 유지

## 📝 **결론**

이 수정 계획을 통해 **코딩 컨벤션을 준수하는 안정적이고 확장 가능한 프레임워크**를 구축할 수 있습니다. 

**핵심 원칙**:
1. **근본 원인 해결**: 테스트 우회 대신 실제 문제 해결
2. **설계 원칙 준수**: 코딩 컨벤션에 따른 체계적 개발
3. **품질 우선**: 기능 구현보다 품질과 안정성 우선
4. **비판적 접근**: 낙관적 해석 배제하고 실제 문제 중심으로 접근

이러한 수정을 통해 RPG Engine이 **진정한 Story Engine**으로 발전할 수 있습니다.

---

**작성자**: AI Assistant  
**작성일**: 2025-10-19  
**승인**: ⚠️ 수정 필요
