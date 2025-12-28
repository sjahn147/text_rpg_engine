# [deprecated] 보안 가이드

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: 보안 관련 내용이 구현 완료되었으며, 실제 구현과 다릅니다. 현재는 World Editor API 기반 보안이 적용됩니다.

> **문서 버전**: v1.0  
> **작성일**: 2025-10-18  
> **최종 수정**: 2025-10-18

## 🔐 **보안 시스템 개요**

RPG Engine의 보안 시스템은 LLM→SQL 경로 차단, 입력 검증, RBAC(Role-Based Access Control)를 통해 시스템의 무결성과 안전성을 보장합니다.

### **핵심 보안 원칙**
- **LLM→SQL 경로 차단**: LLM이 직접 SQL을 실행하지 못하도록 차단
- **입력 검증**: whitelist 스키마, 수치 범위, 상태 머신 전이 검사
- **권한 관리**: DevMode 격리, 승격/스키마 변경 권한 제한
- **감사 로그**: 모든 promote, 삭제, 롤백 기록

---

## 🚫 **LLM→SQL 경로 차단**

### **DSL 기반 행동 시스템**

#### **행동 DSL 정의**
```python
class ActionDSL:
    def __init__(self):
        self.allowed_actions = {
            "investigate": self.investigate_action,
            "dialogue": self.dialogue_action,
            "trade": self.trade_action,
            "move": self.move_action,
            "wait": self.wait_action
        }
    
    async def process_llm_output(self, llm_output: str, session_id: str):
        """LLM 출력을 DSL로 변환"""
        
        # LLM 출력 파싱
        parsed_action = await self.parse_llm_output(llm_output)
        
        # 행동 타입 검증
        if parsed_action["type"] not in self.allowed_actions:
            raise SecurityError(f"Invalid action type: {parsed_action['type']}")
        
        # 행동 실행
        action_handler = self.allowed_actions[parsed_action["type"]]
        result = await action_handler(session_id, parsed_action["parameters"])
        
        return result
    
    async def investigate_action(self, session_id: str, parameters: dict):
        """조사 행동 처리"""
        
        # 매개변수 검증
        if not self.validate_investigate_parameters(parameters):
            raise SecurityError("Invalid investigate parameters")
        
        # 안전한 조사 로직 실행
        result = await self.safe_investigate(session_id, parameters)
        
        return result
```

### **SQL 인젝션 방지**

#### **매개변수화된 쿼리**
```python
class SecureQueryExecutor:
    def __init__(self):
        self.connection_pool = None
    
    async def execute_secure_query(self, query: str, parameters: dict):
        """안전한 쿼리 실행"""
        
        # 쿼리 화이트리스트 검증
        if not self.is_whitelisted_query(query):
            raise SecurityError(f"Query not in whitelist: {query}")
        
        # 매개변수 검증
        if not self.validate_parameters(parameters):
            raise SecurityError("Invalid query parameters")
        
        # 매개변수화된 쿼리 실행
        result = await self.execute_parameterized_query(query, parameters)
        
        return result
    
    def is_whitelisted_query(self, query: str):
        """쿼리 화이트리스트 검증"""
        
        allowed_queries = [
            "SELECT * FROM game_data.entities WHERE entity_id = $1",
            "SELECT * FROM runtime_data.entity_states WHERE session_id = $1",
            "INSERT INTO runtime_data.player_actions (session_id, action_type, parameters) VALUES ($1, $2, $3)",
            "UPDATE runtime_data.entity_states SET properties = $1 WHERE entity_id = $2"
        ]
        
        return query in allowed_queries
    
    def validate_parameters(self, parameters: dict):
        """매개변수 검증"""
        
        for key, value in parameters.items():
            # 타입 검증
            if not isinstance(value, (str, int, float, bool, list, dict)):
                return False
            
            # 길이 제한
            if isinstance(value, str) and len(value) > 1000:
                return False
            
            # 특수 문자 검증
            if isinstance(value, str) and self.contains_sql_keywords(value):
                return False
        
        return True
    
    def contains_sql_keywords(self, value: str):
        """SQL 키워드 포함 여부 검사"""
        
        dangerous_keywords = [
            "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE",
            "TRUNCATE", "EXEC", "EXECUTE", "UNION", "SELECT"
        ]
        
        value_upper = value.upper()
        for keyword in dangerous_keywords:
            if keyword in value_upper:
                return True
        
        return False
```

### **LLM 출력 검증**

#### **출력 검증 시스템**
```python
class LLMOutputValidator:
    def __init__(self):
        self.validation_rules = {
            "max_length": 1000,
            "allowed_characters": "가-힣a-zA-Z0-9 .,!?",
            "forbidden_patterns": [
                r"DROP\s+TABLE",
                r"DELETE\s+FROM",
                r"UPDATE\s+.*\s+SET",
                r"INSERT\s+INTO"
            ]
        }
    
    async def validate_llm_output(self, output: str):
        """LLM 출력 검증"""
        
        # 길이 검증
        if len(output) > self.validation_rules["max_length"]:
            raise SecurityError("Output too long")
        
        # 문자 검증
        if not self.validate_characters(output):
            raise SecurityError("Invalid characters in output")
        
        # 패턴 검증
        if not self.validate_patterns(output):
            raise SecurityError("Dangerous patterns detected")
        
        return True
    
    def validate_characters(self, text: str):
        """문자 검증"""
        
        allowed_chars = set(self.validation_rules["allowed_characters"])
        text_chars = set(text)
        
        return text_chars.issubset(allowed_chars)
    
    def validate_patterns(self, text: str):
        """패턴 검증"""
        
        import re
        
        for pattern in self.validation_rules["forbidden_patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        return True
```

---

## ✅ **입력 검증**

### **화이트리스트 스키마**

#### **입력 스키마 정의**
```python
class InputSchemaValidator:
    def __init__(self):
        self.schemas = {
            "player_action": {
                "type": "object",
                "properties": {
                    "action_type": {
                        "type": "string",
                        "enum": ["investigate", "dialogue", "trade", "move", "wait"]
                    },
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target_id": {"type": "string", "maxLength": 50},
                            "message": {"type": "string", "maxLength": 500},
                            "coordinates": {
                                "type": "object",
                                "properties": {
                                    "x": {"type": "integer", "minimum": 0, "maximum": 1000},
                                    "y": {"type": "integer", "minimum": 0, "maximum": 1000}
                                }
                            }
                        }
                    }
                },
                "required": ["action_type"]
            },
            "dev_mode_edit": {
                "type": "object",
                "properties": {
                    "entity_type": {
                        "type": "string",
                        "enum": ["region", "location", "cell", "entity", "effect_carrier"]
                    },
                    "entity_id": {"type": "string", "maxLength": 50},
                    "changes": {"type": "object"}
                },
                "required": ["entity_type", "entity_id", "changes"]
            }
        }
    
    async def validate_input(self, input_data: dict, schema_name: str):
        """입력 데이터 검증"""
        
        if schema_name not in self.schemas:
            raise SecurityError(f"Unknown schema: {schema_name}")
        
        schema = self.schemas[schema_name]
        
        # JSON 스키마 검증
        if not self.validate_json_schema(input_data, schema):
            raise SecurityError("Input validation failed")
        
        # 추가 보안 검증
        if not self.validate_security_constraints(input_data, schema_name):
            raise SecurityError("Security constraints violated")
        
        return True
    
    def validate_json_schema(self, data: dict, schema: dict):
        """JSON 스키마 검증"""
        
        # 간단한 JSON 스키마 검증 구현
        # 실제로는 jsonschema 라이브러리 사용 권장
        
        if "type" in schema:
            if schema["type"] == "object" and not isinstance(data, dict):
                return False
            elif schema["type"] == "string" and not isinstance(data, str):
                return False
            elif schema["type"] == "integer" and not isinstance(data, int):
                return False
        
        if "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                if prop_name in data:
                    if not self.validate_json_schema(data[prop_name], prop_schema):
                        return False
        
        if "required" in schema:
            for required_field in schema["required"]:
                if required_field not in data:
                    return False
        
        return True
    
    def validate_security_constraints(self, data: dict, schema_name: str):
        """보안 제약 조건 검증"""
        
        if schema_name == "player_action":
            # 플레이어 행동 보안 검증
            return self.validate_player_action_security(data)
        elif schema_name == "dev_mode_edit":
            # Dev Mode 편집 보안 검증
            return self.validate_dev_mode_security(data)
        
        return True
    
    def validate_player_action_security(self, data: dict):
        """플레이어 행동 보안 검증"""
        
        # 행동 타입 검증
        allowed_actions = ["investigate", "dialogue", "trade", "move", "wait"]
        if data.get("action_type") not in allowed_actions:
            return False
        
        # 매개변수 검증
        if "parameters" in data:
            params = data["parameters"]
            
            # 좌표 검증
            if "coordinates" in params:
                coords = params["coordinates"]
                if not (0 <= coords.get("x", 0) <= 1000):
                    return False
                if not (0 <= coords.get("y", 0) <= 1000):
                    return False
            
            # 메시지 길이 검증
            if "message" in params:
                if len(params["message"]) > 500:
                    return False
        
        return True
    
    def validate_dev_mode_security(self, data: dict):
        """Dev Mode 보안 검증"""
        
        # 엔티티 타입 검증
        allowed_types = ["region", "location", "cell", "entity", "effect_carrier"]
        if data.get("entity_type") not in allowed_types:
            return False
        
        # 엔티티 ID 검증
        entity_id = data.get("entity_id", "")
        if len(entity_id) > 50:
            return False
        
        # 변경사항 검증
        changes = data.get("changes", {})
        if not isinstance(changes, dict):
            return False
        
        return True
```

### **수치 범위 검증**

#### **수치 검증 시스템**
```python
class NumericValidator:
    def __init__(self):
        self.ranges = {
            "player_level": (1, 100),
            "entity_health": (0, 1000),
            "item_quantity": (0, 999),
            "coordinates_x": (0, 1000),
            "coordinates_y": (0, 1000),
            "dialogue_length": (0, 1000),
            "effect_duration": (0, 86400)  # 24시간
        }
    
    def validate_numeric_value(self, value: any, field_name: str):
        """수치 값 검증"""
        
        if field_name not in self.ranges:
            raise SecurityError(f"Unknown field: {field_name}")
        
        min_val, max_val = self.ranges[field_name]
        
        # 타입 검증
        if not isinstance(value, (int, float)):
            raise SecurityError(f"Invalid type for {field_name}: {type(value)}")
        
        # 범위 검증
        if not (min_val <= value <= max_val):
            raise SecurityError(f"Value out of range for {field_name}: {value}")
        
        return True
    
    def validate_coordinates(self, x: int, y: int):
        """좌표 검증"""
        
        self.validate_numeric_value(x, "coordinates_x")
        self.validate_numeric_value(y, "coordinates_y")
        
        return True
    
    def validate_entity_properties(self, properties: dict):
        """엔티티 속성 검증"""
        
        if "level" in properties:
            self.validate_numeric_value(properties["level"], "player_level")
        
        if "health" in properties:
            self.validate_numeric_value(properties["health"], "entity_health")
        
        return True
```

### **상태 머신 전이 검사**

#### **상태 전이 검증**
```python
class StateMachineValidator:
    def __init__(self):
        self.state_transitions = {
            "player_state": {
                "idle": ["moving", "dialogue", "combat"],
                "moving": ["idle", "dialogue"],
                "dialogue": ["idle", "trade"],
                "trade": ["idle"],
                "combat": ["idle", "defeated"]
            },
            "entity_state": {
                "active": ["inactive", "destroyed"],
                "inactive": ["active"],
                "destroyed": []
            },
            "session_state": {
                "active": ["paused", "ended"],
                "paused": ["active", "ended"],
                "ended": []
            }
        }
    
    def validate_state_transition(self, current_state: str, new_state: str, 
                                state_type: str):
        """상태 전이 검증"""
        
        if state_type not in self.state_transitions:
            raise SecurityError(f"Unknown state type: {state_type}")
        
        allowed_transitions = self.state_transitions[state_type].get(current_state, [])
        
        if new_state not in allowed_transitions:
            raise SecurityError(
                f"Invalid state transition: {current_state} -> {new_state}"
            )
        
        return True
    
    def validate_player_state_change(self, player_id: str, new_state: str):
        """플레이어 상태 변경 검증"""
        
        # 현재 상태 조회
        current_state = await self.get_player_state(player_id)
        
        # 상태 전이 검증
        self.validate_state_transition(current_state, new_state, "player_state")
        
        return True
```

---

## 👥 **RBAC (Role-Based Access Control)**

### **권한 시스템**

#### **역할 정의**
```python
class RoleManager:
    def __init__(self):
        self.roles = {
            "player": {
                "permissions": [
                    "play_game",
                    "save_session",
                    "load_session"
                ]
            },
            "developer": {
                "permissions": [
                    "play_game",
                    "save_session",
                    "load_session",
                    "edit_game_data",
                    "create_entities",
                    "edit_entities",
                    "delete_entities"
                ]
            },
            "admin": {
                "permissions": [
                    "play_game",
                    "save_session",
                    "load_session",
                    "edit_game_data",
                    "create_entities",
                    "edit_entities",
                    "delete_entities",
                    "promote_to_game_data",
                    "manage_users",
                    "system_admin"
                ]
            }
        }
    
    async def assign_role(self, user_id: str, role: str):
        """역할 할당"""
        
        if role not in self.roles:
            raise SecurityError(f"Unknown role: {role}")
        
        # 역할 할당
        await self.save_user_role(user_id, role)
        
        return True
    
    async def check_permission(self, user_id: str, permission: str):
        """권한 확인"""
        
        # 사용자 역할 조회
        user_role = await self.get_user_role(user_id)
        
        if not user_role:
            return False
        
        # 권한 확인
        role_permissions = self.roles[user_role]["permissions"]
        
        return permission in role_permissions
```

### **Dev Mode 권한 관리**

#### **Dev Mode 권한 검증**
```python
class DevModeSecurity:
    def __init__(self):
        self.dev_mode_permissions = {
            "edit_game_data": ["developer", "admin"],
            "promote_to_game_data": ["admin"],
            "manage_users": ["admin"],
            "system_admin": ["admin"]
        }
    
    async def check_dev_mode_permission(self, user_id: str, action: str):
        """Dev Mode 권한 확인"""
        
        # 사용자 역할 조회
        user_role = await self.get_user_role(user_id)
        
        if not user_role:
            return False
        
        # Dev Mode 권한 확인
        if action not in self.dev_mode_permissions:
            return False
        
        allowed_roles = self.dev_mode_permissions[action]
        
        return user_role in allowed_roles
    
    async def validate_dev_mode_action(self, user_id: str, action: str, 
                                      target: str):
        """Dev Mode 행동 검증"""
        
        # 기본 권한 확인
        if not await self.check_dev_mode_permission(user_id, action):
            raise SecurityError(f"Permission denied for action: {action}")
        
        # 추가 보안 검증
        if action == "edit_game_data":
            await self.validate_game_data_edit(user_id, target)
        elif action == "promote_to_game_data":
            await self.validate_promotion(user_id, target)
        
        return True
    
    async def validate_game_data_edit(self, user_id: str, target: str):
        """Game Data 편집 검증"""
        
        # 편집 가능한 엔티티 타입 확인
        allowed_types = ["region", "location", "cell", "entity", "effect_carrier"]
        
        if target not in allowed_types:
            raise SecurityError(f"Cannot edit entity type: {target}")
        
        return True
    
    async def validate_promotion(self, user_id: str, target: str):
        """승격 검증"""
        
        # 승격 가능한 테이블 확인
        allowed_tables = ["entities", "items", "locations", "regions"]
        
        if target not in allowed_tables:
            raise SecurityError(f"Cannot promote to table: {target}")
        
        return True
```

### **세션 격리**

#### **세션 보안**
```python
class SessionSecurity:
    def __init__(self):
        self.session_locks = {}
        self.session_permissions = {}
    
    async def create_secure_session(self, user_id: str, session_type: str):
        """보안 세션 생성"""
        
        # 세션 ID 생성
        session_id = str(uuid.uuid4())
        
        # 세션 권한 설정
        session_permissions = await self.get_session_permissions(user_id, session_type)
        
        # 세션 보안 정보 저장
        await self.save_session_security(session_id, {
            "user_id": user_id,
            "session_type": session_type,
            "permissions": session_permissions,
            "created_at": datetime.now(),
            "last_activity": datetime.now()
        })
        
        return session_id
    
    async def validate_session_access(self, session_id: str, user_id: str, 
                                    action: str):
        """세션 접근 검증"""
        
        # 세션 보안 정보 조회
        security_info = await self.get_session_security(session_id)
        
        if not security_info:
            raise SecurityError("Session not found")
        
        # 사용자 확인
        if security_info["user_id"] != user_id:
            raise SecurityError("Session access denied")
        
        # 권한 확인
        if action not in security_info["permissions"]:
            raise SecurityError(f"Permission denied for action: {action}")
        
        # 세션 활성화 확인
        if not await self.is_session_active(session_id):
            raise SecurityError("Session not active")
        
        return True
    
    async def is_session_active(self, session_id: str):
        """세션 활성화 확인"""
        
        security_info = await self.get_session_security(session_id)
        
        if not security_info:
            return False
        
        # 마지막 활동 시간 확인 (30분 제한)
        last_activity = security_info["last_activity"]
        time_diff = datetime.now() - last_activity
        
        return time_diff.total_seconds() < 1800  # 30분
```

---

## 📊 **감사 로그**

### **감사 로그 시스템**

#### **감사 로그 생성**
```python
class AuditLogger:
    def __init__(self):
        self.log_entries = []
    
    async def log_action(self, user_id: str, action: str, target: str, 
                        details: dict = None):
        """감사 로그 생성"""
        
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": action,
            "target": target,
            "details": details or {},
            "timestamp": datetime.now(),
            "ip_address": await self.get_client_ip(),
            "user_agent": await self.get_user_agent()
        }
        
        # 로그 저장
        await self.save_audit_log(log_entry)
        
        return log_entry
    
    async def log_dev_mode_action(self, user_id: str, action: str, 
                                entity_type: str, entity_id: str, 
                                changes: dict = None):
        """Dev Mode 감사 로그"""
        
        return await self.log_action(
            user_id=user_id,
            action=f"dev_mode_{action}",
            target=f"{entity_type}:{entity_id}",
            details={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "changes": changes
            }
        )
    
    async def log_promotion(self, user_id: str, runtime_id: str, 
                           target_table: str, reason: str):
        """승격 감사 로그"""
        
        return await self.log_action(
            user_id=user_id,
            action="promote_to_game_data",
            target=f"{target_table}:{runtime_id}",
            details={
                "runtime_id": runtime_id,
                "target_table": target_table,
                "reason": reason
            }
        )
    
    async def log_security_event(self, event_type: str, details: dict):
        """보안 이벤트 로그"""
        
        return await self.log_action(
            user_id="system",
            action="security_event",
            target=event_type,
            details=details
        )
```

### **감사 로그 조회**

#### **로그 조회 시스템**
```python
class AuditLogQuery:
    def __init__(self):
        self.log_storage = {}
    
    async def get_audit_logs(self, user_id: str = None, action: str = None, 
                           start_date: datetime = None, end_date: datetime = None,
                           limit: int = 100):
        """감사 로그 조회"""
        
        # 필터 조건
        filters = {}
        
        if user_id:
            filters["user_id"] = user_id
        
        if action:
            filters["action"] = action
        
        if start_date:
            filters["start_date"] = start_date
        
        if end_date:
            filters["end_date"] = end_date
        
        # 로그 조회
        logs = await self.query_audit_logs(filters, limit)
        
        return logs
    
    async def get_user_activity(self, user_id: str, days: int = 7):
        """사용자 활동 조회"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logs = await self.get_audit_logs(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return logs
    
    async def get_security_events(self, event_type: str = None, 
                                days: int = 7):
        """보안 이벤트 조회"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logs = await self.get_audit_logs(
            user_id="system",
            action="security_event",
            start_date=start_date,
            end_date=end_date
        )
        
        if event_type:
            logs = [log for log in logs if log["target"] == event_type]
        
        return logs
```

---

## 🧪 **보안 테스트**

### **보안 테스트 시스템**

#### **보안 테스트 실행**
```python
class SecurityTest:
    def __init__(self):
        self.test_results = []
    
    async def test_llm_sql_path_blocking(self):
        """LLM→SQL 경로 차단 테스트"""
        
        # 위험한 LLM 출력 시뮬레이션
        dangerous_outputs = [
            "DROP TABLE entities;",
            "DELETE FROM runtime_data;",
            "UPDATE game_data SET properties = 'hacked';"
        ]
        
        for output in dangerous_outputs:
            try:
                # DSL 변환 시도
                result = await action_dsl.process_llm_output(output, "test_session")
                # 위험한 출력이 처리되면 실패
                assert False, f"Dangerous output processed: {output}"
            except SecurityError:
                # 보안 오류가 발생하면 성공
                pass
        
        return True
    
    async def test_input_validation(self):
        """입력 검증 테스트"""
        
        # 잘못된 입력 데이터
        invalid_inputs = [
            {"action_type": "hack", "parameters": {}},
            {"action_type": "investigate", "parameters": {"target_id": "'; DROP TABLE entities; --"}},
            {"action_type": "dialogue", "parameters": {"message": "A" * 1001}}
        ]
        
        for invalid_input in invalid_inputs:
            try:
                await input_validator.validate_input(invalid_input, "player_action")
                # 검증이 통과하면 실패
                assert False, f"Invalid input passed validation: {invalid_input}"
            except SecurityError:
                # 보안 오류가 발생하면 성공
                pass
        
        return True
    
    async def test_rbac_permissions(self):
        """RBAC 권한 테스트"""
        
        # 권한 없는 사용자로 Dev Mode 접근 시도
        try:
            await dev_mode_security.validate_dev_mode_action(
                user_id="player_001",
                action="promote_to_game_data",
                target="entities"
            )
            # 권한 없이 접근되면 실패
            assert False, "Unauthorized access allowed"
        except SecurityError:
            # 보안 오류가 발생하면 성공
            pass
        
        return True
    
    async def test_session_security(self):
        """세션 보안 테스트"""
        
        # 다른 사용자의 세션에 접근 시도
        try:
            await session_security.validate_session_access(
                session_id="session_001",
                user_id="hacker_001",
                action="edit_game_data"
            )
            # 다른 사용자 세션에 접근되면 실패
            assert False, "Cross-session access allowed"
        except SecurityError:
            # 보안 오류가 발생하면 성공
            pass
        
        return True
```

---

## 📋 **보안 체크리스트**

### **LLM 보안**
- [ ] LLM→SQL 경로 차단
- [ ] DSL 기반 행동 시스템
- [ ] 매개변수화된 쿼리
- [ ] LLM 출력 검증

### **입력 검증**
- [ ] 화이트리스트 스키마
- [ ] 수치 범위 검증
- [ ] 상태 머신 전이 검사
- [ ] SQL 인젝션 방지

### **RBAC**
- [ ] 역할 기반 권한 관리
- [ ] Dev Mode 권한 검증
- [ ] 세션 격리
- [ ] 권한 상속

### **감사 로그**
- [ ] 모든 행동 로깅
- [ ] 보안 이벤트 추적
- [ ] 로그 분석
- [ ] 위반 감지

---

## 🚀 **다음 단계**

1. **보안 시스템 구현**: LLM→SQL 차단, 입력 검증, RBAC
2. **감사 로그 시스템**: 모든 행동 추적 및 분석
3. **보안 테스트**: 포괄적인 보안 테스트 케이스
4. **모니터링 시스템**: 실시간 보안 위협 감지
5. **인시던트 대응**: 보안 사고 대응 절차

---

**문서 작성자**: RPG Engine Development Team  
**최종 검토**: 2025-10-18  
**다음 검토 예정**: 2025-11-18
