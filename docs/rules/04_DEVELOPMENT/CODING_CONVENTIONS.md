
# RPG Engine 코딩 컨벤션 및 품질 가이드

> **문서 버전**: v1.1  
> **작성일**: 2025-10-18  
> **최종 수정**: 2025-10-19  
> **적용 범위**: RPG Engine MVP 개발

## ✅ Priority & Scope Model (MVP)

본 규약은 규칙마다 중요도(Priority)와 적용 범위(Scope)를 명시합니다.

- Priority
  - MUST: 미준수 시 시스템 위험·차단 사유
  - SHOULD: 권장. 상황/성숙도에 따라 유연 적용
  - MAY: 선택. 팀/프로젝트 성숙도에 따라 채택

- Scope
  - runtime: 게임 런타임 경로(프레임/틱 내 로직)
  - tooling: 시스템/도구/데이터 파이프라인/DB 작업
  - both: 런타임과 도구 모두 해당

### MVP Priority Map
- Data-Centric Development: MUST, scope: tooling
- Database Safety (Backup + Human Confirm): MUST, scope: tooling
- Type-Safety (공개 API 100% 타입/명시적 예외): MUST, scope: both
- Async-First I/O (동기 I/O 금지): MUST, scope: both
- Test-First (최소 1개 실패 테스트 → Green): MUST, scope: both
- Enum/Literal로 허용값 한정: SHOULD, scope: both
- CI 자동화 (black/isort/flake8/mypy/coverage≥80%): SHOULD, scope: tooling
- 구조화 로깅: SHOULD, scope: both
- 고급 최적화/정적 분석 확장(예: 불변성 정적검사): MAY, scope: runtime
- 캐시/풀링 고급 전략(2단 캐시, 오브젝트 풀): MAY, scope: runtime

각 섹션의 규칙은 위 우선순위/스코프 해석을 따릅니다. MUST 항목은 PR 차단 조건과 직접 연결되며, SHOULD/MAY는 권고·경고 레벨로 보고됩니다.

## 🎯 **정책 및 설계 철학**

### **핵심 개발 철학**

RPG Engine의 모든 코딩 관행은 다음 **개발 철학**을 기반으로 합니다.

#### **1. 데이터 중심 개발 (Data-Centric Development)**
- **DO**: 데이터베이스 스키마를 먼저 설계하고, 코드는 이를 반영
- **DO**: 모든 비즈니스 로직을 데이터베이스 트랜잭션으로 표현
- **DO NOT**: 코드에서 데이터 구조를 임의로 정의하고 나중에 DB에 맞추기
- **DO NOT**: 데이터베이스 없이 코드만으로 비즈니스 로직 구현

#### **2. 불변성 우선 개발 (Immutability-First Development)**
- **DO**: 불변 객체를 기본으로 하고, 변경이 필요한 경우에만 가변 객체 사용
- **DO**: 상태 변경 시 새로운 객체를 생성하여 반환
- **DO NOT**: 기존 객체를 직접 수정하여 사이드 이펙트 발생
- **DO NOT**: 전역 상태나 싱글톤 패턴으로 상태 공유

#### **3. 타입 안전성 우선 개발 (Type-Safety-First Development)**
- **DO**: 모든 함수와 클래스에 타입 힌트 추가
- **DO**: Pydantic 모델로 런타임 검증 강화
- **DO**: Enum과 Literal 타입으로 허용 값 제한
- **DO NOT**: 타입 힌트 없이 코드 작성
- **DO NOT**: Any 타입으로 타입 검사 우회

#### **4. 비동기 우선 개발 (Async-First Development)**
- **DO**: 모든 I/O 작업을 비동기로 구현
- **DO**: 동시성 문제를 락과 세마포어로 해결
- **DO**: 리소스 관리를 컨텍스트 매니저로 처리
- **DO NOT**: 동기 함수에서 비동기 함수 호출
- **DO NOT**: 전역 락으로 성능 저하 발생

#### **5. 테스트 주도 개발 (Test-Driven Development)**
- **DO**: 기능 구현 전에 테스트 작성
- **DO**: Mock을 사용하여 외부 의존성 격리
- **DO**: 시나리오 기반 통합 테스트 작성
- **DO NOT**: 테스트 없이 기능 구현
- **DO NOT**: 테스트에서 실제 데이터베이스나 외부 서비스 사용

#### **6. 모듈화 우선 개발 (Modularity-First Development)**
- **DO**: 단일 책임 원칙을 엄격히 준수
- **DO**: 인터페이스를 통한 의존성 주입
- **DO**: 각 모듈을 독립적으로 테스트 가능하게 설계
- **DO NOT**: 하나의 클래스에 여러 책임 혼재
- **DO NOT**: 하드코딩된 의존성으로 테스트 불가능한 구조

#### **7. 에러 처리 우선 개발 (Error-Handling-First Development)**
- **DO**: 모든 예외를 명시적으로 처리
- **DO**: 계층별로 적절한 에러 타입 정의
- **DO**: 구조화된 로깅으로 디버깅 정보 제공
- **DO NOT**: 예외를 무시하거나 기본값으로 대체
- **DO NOT**: 광범위한 except 절로 에러 정보 손실

#### **8. 데이터베이스 안전성 우선 개발 (Database-Safety-First Development)**
- **DO**: 개발 정의서에 정의되지 않은 DB 쓰기 작업 시 반드시 사용자 컨펌 요청
- **DO**: 데이터베이스 조작 전 백업 생성 및 복구 계획 수립
- **DO**: 위험한 작업(삭제, 수정, 스키마 변경)에 대한 명시적 경고
- **DO NOT**: 사용자 컨펌 없이 데이터베이스 구조나 데이터 변경
- **DO NOT**: 프로덕션 환경에서 테스트 데이터 조작
- **DO NOT**: 백업 없이 대량 데이터 삭제나 스키마 변경

#### **9. 비판적 성과 평가 우선 개발 (Critical-Review-First Development)**
- **DO**: 모든 개발 결과에 대해 비판적이고 객관적인 검토 수행
- **DO**: 성과를 낙관적으로 해석하지 않고 실제 동작과 문제점 중심으로 평가
- **DO**: 개발 과정에서의 실수와 위험 요소를 솔직하게 기록하고 개선
- **DO**: 사용자 피드백과 실제 테스트 결과를 우선시하여 판단
- **DO NOT**: 예상 결과나 이론적 가능성에만 의존한 낙관적 평가
- **DO NOT**: 문제점을 숨기거나 과소평가하여 보고
- **DO NOT**: 테스트 실패나 오류를 무시하고 진행

### **코딩 정책**

#### **1. 품질 기준 (Quality Standards)**
- **DO**: 코드 커버리지 80% 이상 유지
- **DO**: 모든 함수와 클래스에 타입 힌트 100% 적용
- **DO**: 모든 공개 API에 docstring 필수 작성
- **DO**: UI 응답 시간 < 100ms, DB 쿼리 < 100ms 달성
- **DO NOT**: 테스트 커버리지 80% 미만으로 코드 작성
- **DO NOT**: 타입 힌트 없이 코드 작성
- **DO NOT**: 문서화 없이 공개 API 노출

#### **2. 금지 사항 (Prohibited Practices)**
- **DO NOT**: 프로덕션 코드에 Mock 사용
- **DO NOT**: 하드코딩된 설정값 사용
- **DO NOT**: 예외를 무시하거나 기본값으로 대체
- **DO NOT**: 전역 변수나 전역 상태 사용
- **DO NOT**: 문자열 포맷팅으로 SQL 구성
- **DO NOT**: eval() 함수 사용
- **DO NOT**: 전역 락으로 성능 저하 발생
- **DO NOT**: 사용자 컨펌 없이 데이터베이스 구조나 데이터 변경
- **DO NOT**: 백업 없이 위험한 데이터베이스 작업 수행
- **DO NOT**: 개발 결과를 낙관적으로 해석하여 실제 문제점 은폐

#### **2-1. 트러블슈팅 경험 기반 금지 사항 (Troubleshooting-Based Prohibitions)**

##### **인코딩 및 문자 처리 관련**
- **DO NOT**: 로깅 메시지나 출력에 이모지(✅❌🔍📊🧠🎉 등) 사용
  - *이유*: Windows 환경에서 Unicode 인코딩 오류 발생, 나중에 모든 이모지를 제거해야 함
  - *대안*: 텍스트 기반 상태 표시 사용 (예: "[SUCCESS]", "[ERROR]", "[INFO]")

##### **모듈 임포트 및 의존성 관리**
- **DO NOT**: 모듈 경로를 확인하지 않고 임포트 시도
  - *이유*: 잘못된 경로로 인한 ImportError 발생, 나중에 수정해야 함
  - *대안*: 임포트 전에 파일 존재 여부 확인, 정확한 경로 사용
- **DO NOT**: 모듈 의존성 순서를 무시하고 초기화
  - *이유*: 의존성 순환 참조나 초기화 실패 발생
  - *대안*: 의존성 그래프를 기반으로 한 순차적 초기화
- **DO NOT**: 싱글톤 패턴으로 인스턴스 재사용 시 상태 충돌 방지 실패
  - *이유*: 여러 테스트나 세션 간 상태가 섞여 예상치 못한 동작 발생
  - *대안*: 각 세션별 독립적인 인스턴스 생성 또는 상태 초기화

##### **테스트 및 품질 관리**
- **DO NOT**: 테스트만 통과하기 위해 근본적 해결을 미루는 임시방편 사용
  - *이유*: 근본 원인이 해결되지 않아 나중에 더 큰 문제 발생
  - *대안*: 임시방편 사용 시 known_issues.md에 반드시 기록하고 근본 해결 계획 수립
- **DO NOT**: pytest를 사용하지 않고 자체 테스트 프레임워크 구축
  - *이유*: 표준 도구 미사용으로 인한 유지보수성 저하 및 커뮤니티 지원 부족
  - *대안*: pytest를 기본 테스트 프레임워크로 사용

##### **문서화 및 프로젝트 관리**
- **DO NOT**: 개발 진행 현황 문서 제목을 순서를 알 수 없게 작성
  - *이유*: 나중에 최신 문서를 찾기 어려워 프로젝트 진행 상황 파악 곤란
  - *대안*: 날짜나 버전 번호를 포함한 명확한 명명 규칙 사용 (예: "2025-10-19_phase5_development_log.md")
- **DO NOT**: 문서 버전 관리 없이 파일 수정
  - *이유*: 변경 이력 추적 불가, 롤백 시 어려움
  - *대안*: Git을 통한 버전 관리 및 변경 이력 명확한 문서화

##### **에러 처리 및 디버깅**
- **DO NOT**: 에러 메시지에 구체적인 컨텍스트 정보 누락
  - *이유*: 디버깅 시 원인 파악 어려움, 문제 해결 시간 증가
  - *대안*: 에러 발생 시점, 입력값, 상태 정보를 포함한 상세한 에러 메시지 작성
- **DO NOT**: 예외 처리 시 에러를 숨기고 기본값으로 대체
  - *이유*: 실제 문제가 숨겨져 근본 원인 파악 불가
  - *대안*: 에러 로깅 후 명시적인 에러 전파 또는 복구 시도

##### **성능 및 리소스 관리**
- **DO NOT**: 메모리 사용량 모니터링 없이 대용량 데이터 처리
  - *이유*: 메모리 누수나 OOM 에러 발생 가능성
  - *대안*: 메모리 사용량 모니터링 및 적절한 가비지 컬렉션
- **DO NOT**: 데이터베이스 연결 풀 크기 설정 없이 동시 접속 처리
  - *이유*: 연결 부족으로 인한 타임아웃 또는 성능 저하
  - *대안*: 예상 동시 접속 수를 고려한 연결 풀 크기 설정

#### **3. 필수 사항 (Required Practices)**
- **DO**: 모든 예외를 명시적으로 처리
- **DO**: 구조화된 로깅으로 디버깅 정보 제공
- **DO**: 모든 입력 데이터 검증
- **DO**: 코드의 의도와 사용법을 명시
- **DO**: 의존성 주입을 통한 테스트 가능한 구조
- **DO**: 불변성을 우선으로 한 객체 설계
- **DO**: 데이터베이스 쓰기 작업 전 사용자 컨펌 요청
- **DO**: 모든 개발 결과에 대한 비판적 검토 및 솔직한 평가
- **DO**: 실제 테스트 결과와 사용자 피드백을 우선시한 판단

### **아키텍처 설계 방법론**

#### **1. 3계층 아키텍처**
```
┌─────────────────┐
│   UI Layer      │ ← 사용자 인터페이스
├─────────────────┤
│ Business Logic  │ ← 게임 로직, 비즈니스 규칙
├─────────────────┤
│  Data Layer     │ ← 데이터베이스, 영속성
└─────────────────┘
```

#### **2. 의존성 방향**
- **상위 → 하위**: UI는 Business Logic에만 의존
- **인터페이스 의존**: 구체 클래스가 아닌 인터페이스에 의존
- **의존성 주입**: 생성자를 통한 의존성 주입

#### **3. 데이터 흐름**
```
User Input → Validation → Business Logic → Data Layer → Database
     ↑                                                      ↓
User Output ← UI Layer ← Business Logic ← Data Layer ← Database
```

#### **4. 에러 처리 전략**
- **계층별 에러**: 각 계층에서 적절한 에러 처리
- **에러 전파**: 상위 계층으로 의미 있는 에러 전달
- **로깅**: 모든 에러를 구조화된 로그로 기록

#### **5. 성능 최적화**
- **캐싱**: 자주 사용되는 데이터는 캐시
- **지연 로딩**: 필요할 때만 데이터 로드
- **배치 처리**: 여러 작업을 한 번에 처리
- **인덱싱**: 데이터베이스 쿼리 최적화

참고: RNG/시뮬레이션 테스트 지침은 `docs/ARCHITECTURE.md` 4장과 `docs/rules/02_WORKFLOW_TDD.md`의 RNG 섹션을 참조하세요.

### **개발 프로세스**

#### **1. 코드 작성 순서 (Code Writing Order)**
- **DO**: 인터페이스를 먼저 정의하고 구현
- **DO**: TDD 방식으로 테스트를 먼저 작성
- **DO**: 테스트를 통과하는 최소 구현부터 시작
- **DO**: 구현 후 리팩토링으로 코드 품질 개선
- **DO**: 사용법과 예시를 포함한 문서화
- **DO NOT**: 테스트 없이 기능 구현
- **DO NOT**: 인터페이스 없이 바로 구현 시작
- **DO NOT**: 한 번에 모든 기능을 구현

#### **2. 코드 리뷰 기준 (Code Review Criteria)**
- **DO**: 코드가 의도를 명확히 표현하는지 확인
- **DO**: 불필요한 연산이나 메모리 사용이 없는지 검토
- **DO**: 입력 검증과 SQL 인젝션 방지가 되어 있는지 확인
- **DO**: 테스트 커버리지와 품질이 충분한지 검토
- **DO NOT**: 가독성 없이 복잡한 로직 승인
- **DO NOT**: 성능 문제가 있는 코드 승인
- **DO NOT**: 보안 취약점이 있는 코드 승인

#### **3. 품질 관리 (Quality Management)**
- **DO**: mypy, flake8, black을 자동으로 실행
- **DO**: CI/CD 파이프라인에서 자동 테스트 실행
- **DO**: 응답 시간과 메모리 사용량을 지속적으로 모니터링
- **DO**: 의존성 취약점을 정기적으로 스캔
- **DO NOT**: 정적 분석 없이 코드 배포
- **DO NOT**: 테스트 실패 시 코드 배포
- **DO NOT**: 성능 모니터링 없이 운영

#### **4. 데이터베이스 안전 관리 (Database Safety Management)**
- **DO**: 모든 DB 쓰기 작업 전 사용자에게 명확한 경고와 컨펌 요청
- **DO**: 위험한 작업 목록을 명시하고 각 작업별 위험도 표시
- **DO**: 데이터베이스 조작 전 자동 백업 생성
- **DO**: 개발/테스트/프로덕션 환경을 명확히 구분하여 작업
- **DO NOT**: 사용자 컨펌 없이 데이터베이스 구조 변경
- **DO NOT**: 백업 없이 대량 데이터 삭제나 스키마 변경
- **DO NOT**: 프로덕션 환경에서 테스트 데이터 조작

#### **5. 비판적 성과 평가 관리 (Critical Review Management)**
- **DO**: 모든 개발 결과에 대해 실제 동작 테스트를 통한 검증
- **DO**: 성공과 실패를 객관적으로 기록하고 분석
- **DO**: 사용자 피드백과 실제 사용 시나리오를 우선시
- **DO**: 문제점과 한계를 솔직하게 인정하고 개선 방안 제시
- **DO NOT**: 예상 결과나 이론적 가능성에만 의존한 평가
- **DO NOT**: 테스트 실패나 오류를 무시하고 낙관적으로 해석
- **DO NOT**: 사용자 피드백을 무시하고 개발자 관점에서만 판단

---

## 📝 **코딩 컨벤션 및 품질 가이드**

### **🚫 나쁜 코딩 관행 (Anti-Patterns)**

#### **1. 데이터베이스 관련**
```python
# ❌ 나쁜 예시
def get_user_data(user_id):
    conn = psycopg2.connect("host=localhost dbname=test user=postgres password=1234")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    conn.close()
    return result

# ✅ 좋은 예시
async def get_user_data(user_id: str) -> Optional[UserData]:
    async with get_db_connection() as conn:
        query = "SELECT * FROM users WHERE id = $1"
        result = await conn.fetchrow(query, user_id)
        return UserData.from_dict(result) if result else None
```

#### **2. 에러 처리**
```python
# ❌ 나쁜 예시
def process_data(data):
    try:
        result = complex_operation(data)
        return result
    except:
        return None

# ✅ 좋은 예시
async def process_data(data: Dict[str, Any]) -> ProcessResult:
    try:
        result = await complex_operation(data)
        return ProcessResult.success(result)
    except ValidationError as e:
        logger.warning(f"Validation failed: {e}")
        return ProcessResult.error(f"Invalid data: {e}")
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        return ProcessResult.error("Database operation failed")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return ProcessResult.error("Internal server error")
```

#### **3. 비동기 처리**
```python
# ❌ 나쁜 예시
def sync_function():
    result = requests.get("https://api.example.com/data")
    return result.json()

# ✅ 좋은 예시
async def async_function() -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com/data") as response:
            return await response.json()
```

#### **4. 타입 안전성**
```python
# ❌ 나쁜 예시
def create_entity(name, entity_type, data):
    entity = {
        "name": name,
        "type": entity_type,
        "data": data
    }
    return entity

# ✅ 좋은 예시
from typing import Dict, Any, Optional
from pydantic import BaseModel

class EntityData(BaseModel):
    name: str
    entity_type: EntityType
    data: Dict[str, Any]
    
    class Config:
        use_enum_values = True

def create_entity(name: str, entity_type: EntityType, data: Dict[str, Any]) -> EntityData:
    return EntityData(
        name=name,
        entity_type=entity_type,
        data=data
    )
```

#### **5. 설정 관리**
```python
# ❌ 나쁜 예시
DATABASE_URL = "postgresql://user:pass@localhost:5432/db"
API_KEY = "sk-1234567890abcdef"
DEBUG = True

# ✅ 좋은 예시
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

#### **6. 프로덕션 코드에 Mock 사용**
```python
# ❌ 나쁜 예시
def get_user_data(user_id):
    # 프로덕션에서 Mock 사용
    if user_id == "test":
        return {"id": "test", "name": "Test User"}
    return None

# ✅ 좋은 예시
async def get_user_data(user_id: str) -> Optional[UserData]:
    async with get_db_connection() as conn:
        query = "SELECT * FROM users WHERE id = $1"
        result = await conn.fetchrow(query, user_id)
        return UserData.from_dict(result) if result else None
```

#### **7. 하드코딩된 값**
```python
# ❌ 나쁜 예시
def process_payment(amount):
    if amount > 1000:  # 하드코딩된 임계값
        return "High value transaction"
    return "Normal transaction"

# ✅ 좋은 예시
class PaymentConfig:
    HIGH_VALUE_THRESHOLD = 1000
    
def process_payment(amount: float, config: PaymentConfig) -> str:
    if amount > config.HIGH_VALUE_THRESHOLD:
        return "High value transaction"
    return "Normal transaction"
```

#### **8. 예시적인 기본값으로 에러 뭉개기**
```python
# ❌ 나쁜 예시
def get_user_balance(user_id):
    try:
        # 실제 DB 조회
        return database.get_balance(user_id)
    except:
        # 에러를 뭉개고 기본값 반환
        return 0

# ✅ 좋은 예시
async def get_user_balance(user_id: str) -> BalanceResult:
    try:
        balance = await database.get_balance(user_id)
        return BalanceResult.success(balance)
    except DatabaseError as e:
        logger.error(f"Failed to get balance for user {user_id}: {e}")
        return BalanceResult.error("Failed to retrieve balance")
    except Exception as e:
        logger.error(f"Unexpected error getting balance: {e}")
        return BalanceResult.error("Internal server error")
```

#### **9. GUI 와이어프레임 없이 개발**
```python
# ❌ 나쁜 예시
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 와이어프레임 없이 임의로 UI 구성
        self.setup_ui()
    
    def setup_ui(self):
        # 레이아웃 없이 임의로 위젯 배치
        self.button1 = QPushButton("Button 1")
        self.button2 = QPushButton("Button 2")
        self.text = QTextEdit()
        # ... 임의의 배치

# ✅ 좋은 예시
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        # 와이어프레임 기반 레이아웃
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 명확한 레이아웃 구조
        main_layout = QHBoxLayout()
        left_panel = self.create_left_panel()
        center_panel = self.create_center_panel()
        right_panel = self.create_right_panel()
        
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(center_panel, 3)
        main_layout.addWidget(right_panel, 1)
        
        central_widget.setLayout(main_layout)
```

#### **10. 모듈 분리 없이 모든 기능을 한 곳에**
```python
# ❌ 나쁜 예시
class GameEngine:
    def __init__(self):
        self.db_connection = None
        self.ui_components = {}
        self.game_state = {}
        self.dialogue_system = {}
        self.inventory_system = {}
        self.combat_system = {}
        # 모든 기능을 하나의 클래스에
    
    def handle_database(self):
        # DB 관련 코드
        pass
    
    def handle_ui(self):
        # UI 관련 코드
        pass
    
    def handle_game_logic(self):
        # 게임 로직
        pass
    
    def handle_dialogue(self):
        # 대화 시스템
        pass
    # ... 수백 개의 메서드

# ✅ 좋은 예시
# 모듈별 분리
class DatabaseManager:
    """데이터베이스 관련 기능만 담당"""
    pass

class UIManager:
    """UI 관련 기능만 담당"""
    pass

class GameLogicManager:
    """게임 로직만 담당"""
    pass

class DialogueManager:
    """대화 시스템만 담당"""
    pass

class GameEngine:
    """각 매니저들을 조합하여 전체 게임 관리"""
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.ui_manager = UIManager()
        self.game_logic = GameLogicManager()
        self.dialogue = DialogueManager()
```

#### **11. 명확하지 않은 메서드명**
```python
# ❌ 나쁜 예시
def do_stuff(data):
    """뭘 하는지 알 수 없는 메서드명"""
    pass

def process(data):
    """너무 일반적인 이름"""
    pass

def handle(user, action):
    """구체적이지 않은 이름"""
    pass

def get_data(id):
    """어떤 데이터인지 불명확"""
    pass

# ✅ 좋은 예시
def create_entity_from_template(template_data: EntityTemplate) -> Entity:
    """엔티티 템플릿으로부터 엔티티 생성"""
    pass

def process_player_action(action: PlayerAction) -> ActionResult:
    """플레이어 행동 처리"""
    pass

def handle_dialogue_interaction(npc_id: str, dialogue_id: str) -> DialogueResult:
    """NPC와의 대화 상호작용 처리"""
    pass

def get_entity_by_id(entity_id: str) -> Optional[Entity]:
    """ID로 엔티티 조회"""
    pass
```

#### **12. 매직 넘버 사용**
```python
# ❌ 나쁜 예시
def calculate_damage(attack, defense):
    damage = attack - defense
    if damage < 0:
        damage = 0
    if damage > 999:  # 매직 넘버
        damage = 999
    return damage

def check_level_up(exp):
    if exp >= 1000:  # 매직 넘버
        return True
    return False

# ✅ 좋은 예시
class GameConstants:
    MAX_DAMAGE = 999
    LEVEL_UP_EXP = 1000
    MIN_DAMAGE = 0

def calculate_damage(attack: int, defense: int) -> int:
    damage = max(attack - defense, GameConstants.MIN_DAMAGE)
    return min(damage, GameConstants.MAX_DAMAGE)

def check_level_up(exp: int) -> bool:
    return exp >= GameConstants.LEVEL_UP_EXP
```

#### **13. 긴 메서드와 복잡한 로직**
```python
# ❌ 나쁜 예시
def process_game_turn(player, npcs, world_state):
    """200줄이 넘는 복잡한 메서드"""
    # 플레이어 행동 처리
    if player.action == "attack":
        target = find_target(player, npcs)
        if target:
            damage = calculate_damage(player.attack, target.defense)
            target.health -= damage
            if target.health <= 0:
                target.alive = False
                player.exp += target.exp_value
                if player.exp >= 1000:
                    player.level += 1
                    player.health = player.max_health
                    player.mana = player.max_mana
    elif player.action == "move":
        new_position = calculate_new_position(player.position, player.direction)
        if is_valid_position(new_position, world_state):
            player.position = new_position
            # 위치 변경에 따른 이벤트 처리
            events = check_location_events(new_position, world_state)
            for event in events:
                if event.type == "treasure":
                    player.inventory.append(event.item)
                elif event.type == "trap":
                    player.health -= event.damage
    # ... 수백 줄의 복잡한 로직

# ✅ 좋은 예시
class GameTurnProcessor:
    def __init__(self, action_handler: ActionHandler, event_processor: EventProcessor):
        self.action_handler = action_handler
        self.event_processor = event_processor
    
    async def process_turn(self, player: Player, npcs: List[NPC], world_state: WorldState) -> TurnResult:
        """게임 턴 처리"""
        try:
            # 플레이어 행동 처리
            action_result = await self.action_handler.handle_player_action(player, npcs, world_state)
            
            # 결과에 따른 이벤트 처리
            event_result = await self.event_processor.process_events(action_result, world_state)
            
            # 턴 결과 생성
            return TurnResult.success(action_result, event_result)
            
        except Exception as e:
            logger.error(f"Turn processing failed: {e}")
            return TurnResult.error(str(e))
```

#### **14. 전역 변수 남용**
```python
# ❌ 나쁜 예시
# 전역 변수로 상태 관리
current_player = None
current_world = None
game_state = "playing"
ui_components = {}

def start_game():
    global current_player, current_world, game_state
    current_player = create_player()
    current_world = create_world()
    game_state = "playing"

def update_ui():
    global ui_components
    ui_components["health"].setText(str(current_player.health))

# ✅ 좋은 예시
class GameState:
    def __init__(self):
        self.player: Optional[Player] = None
        self.world: Optional[World] = None
        self.state: GameStateEnum = GameStateEnum.MENU
        self.ui_components: Dict[str, QWidget] = {}
    
    def start_game(self):
        self.player = create_player()
        self.world = create_world()
        self.state = GameStateEnum.PLAYING
    
    def update_ui(self):
        if self.player:
            self.ui_components["health"].setText(str(self.player.health))
```

#### **15. 예외 처리 부재**
```python
# ❌ 나쁜 예시
def load_game_data():
    file = open("game_data.json", "r")
    data = json.load(file)
    file.close()
    return data

def connect_database():
    conn = psycopg2.connect("postgresql://user:pass@localhost/db")
    return conn

# ✅ 좋은 예시
async def load_game_data() -> GameDataResult:
    try:
        async with aiofiles.open("game_data.json", "r") as file:
            content = await file.read()
            data = json.loads(content)
            return GameDataResult.success(data)
    except FileNotFoundError:
        logger.error("Game data file not found")
        return GameDataResult.error("Game data file not found")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        return GameDataResult.error("Invalid game data format")
    except Exception as e:
        logger.error(f"Unexpected error loading game data: {e}")
        return GameDataResult.error("Failed to load game data")

async def connect_database() -> DatabaseResult:
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        return DatabaseResult.success(conn)
    except asyncpg.ConnectionError as e:
        logger.error(f"Database connection failed: {e}")
        return DatabaseResult.error("Database connection failed")
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        return DatabaseResult.error("Database error")
```

### **✅ 좋은 코딩 관행 (Best Practices)**

#### **1. 함수 설계 원칙**
```python
# ✅ 단일 책임 원칙 (SRP)
class EntityManager:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    async def create_entity(self, entity_data: EntityData) -> Entity:
        """엔티티 생성만 담당"""
        pass
    
    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        """엔티티 조회만 담당"""
        pass

# ✅ 의존성 주입 (DI)
class GameManager:
    def __init__(self, 
                 entity_manager: EntityManager,
                 cell_manager: CellManager,
                 dialogue_manager: DialogueManager):
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
        self.dialogue_manager = dialogue_manager
```

#### **2. 에러 처리 전략**
```python
# ✅ 계층별 에러 처리
class DatabaseError(Exception):
    """데이터베이스 관련 에러"""
    pass

class ValidationError(Exception):
    """데이터 검증 에러"""
    pass

class BusinessLogicError(Exception):
    """비즈니스 로직 에러"""
    pass

# ✅ 에러 처리 데코레이터
def handle_errors(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {func.__name__}: {e}")
            raise
        except DatabaseError as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise
    return wrapper
```

#### **3. 비동기 처리 패턴**
```python
# ✅ 비동기 컨텍스트 매니저
class DatabaseConnection:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
    
    async def __aenter__(self):
        self.connection = await asyncpg.connect(self.connection_string)
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            await self.connection.close()

# ✅ 비동기 배치 처리
async def process_entities_batch(entities: List[EntityData]) -> List[Entity]:
    tasks = [create_entity(entity) for entity in entities]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

#### **4. 타입 안전성**
```python
# ✅ Pydantic 모델 사용
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum

class EntityType(str, Enum):
    PLAYER = "player"
    NPC = "npc"
    MONSTER = "monster"

class EntityData(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    entity_type: EntityType
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    class Config:
        use_enum_values = True
        validate_assignment = True
```

#### **5. 설정 관리**
```python
# ✅ 환경별 설정 분리
class DevelopmentSettings(BaseSettings):
    database_url: str = "postgresql://localhost:5432/rpg_engine_dev"
    debug: bool = True
    log_level: str = "DEBUG"

class ProductionSettings(BaseSettings):
    database_url: str
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env.production"

# ✅ 설정 팩토리
def get_settings() -> BaseSettings:
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        return ProductionSettings()
    return DevelopmentSettings()
```

#### **6. 로깅 전략**
```python
# ✅ 구조화된 로깅
import structlog

logger = structlog.get_logger()

async def process_game_action(action: GameAction) -> ActionResult:
    logger.info(
        "Processing game action",
        action_type=action.type,
        player_id=action.player_id,
        session_id=action.session_id
    )
    
    try:
        result = await execute_action(action)
        logger.info(
            "Action processed successfully",
            action_type=action.type,
            result_status=result.status
        )
        return result
    except Exception as e:
        logger.error(
            "Action processing failed",
            action_type=action.type,
            error=str(e),
            exc_info=True
        )
        raise
```

#### **7. 테스트 작성**
```python
# ✅ 테스트 구조화
import pytest
from unittest.mock import AsyncMock, patch

class TestEntityManager:
    @pytest.fixture
    async def entity_manager(self):
        db_mock = AsyncMock()
        return EntityManager(db_mock)
    
    @pytest.fixture
    def sample_entity_data(self):
        return EntityData(
            name="Test Entity",
            entity_type=EntityType.NPC,
            properties={"health": 100}
        )
    
    async def test_create_entity_success(self, entity_manager, sample_entity_data):
        # Given
        entity_manager.db.fetchrow.return_value = {"id": "test-id"}
        
        # When
        result = await entity_manager.create_entity(sample_entity_data)
        
        # Then
        assert result.id == "test-id"
        assert result.name == "Test Entity"
        entity_manager.db.fetchrow.assert_called_once()
    
    async def test_create_entity_validation_error(self, entity_manager):
        # Given
        invalid_data = EntityData(name="", entity_type=EntityType.NPC)
        
        # When & Then
        with pytest.raises(ValidationError):
            await entity_manager.create_entity(invalid_data)
```


### **🚫 추가 나쁜 코딩 관행 (More Anti-Patterns)**

#### **16. 깊은 중첩과 복잡한 조건문**
```python
# ❌ 나쁜 예시
def process_entity_action(entity, action, world_state):
    if entity.alive:
        if action.type == "attack":
            if entity.weapon:
                if entity.weapon.durability > 0:
                    if entity.mana >= action.mana_cost:
                        if world_state.time_of_day == "day":
                            if entity.level >= action.level_required:
                                # 실제 로직
                                pass
                            else:
                                return "Level too low"
                        else:
                            return "Can only attack during day"
                    else:
                        return "Not enough mana"
                else:
                    return "Weapon broken"
            else:
                return "No weapon equipped"
        elif action.type == "move":
            # 또 다른 깊은 중첩...
    else:
        return "Entity is dead"

# ✅ 좋은 예시
class ActionValidator:
    def __init__(self, world_state: WorldState):
        self.world_state = world_state
    
    def validate_attack(self, entity: Entity, action: Action) -> ValidationResult:
        if not entity.alive:
            return ValidationResult.error("Entity is dead")
        
        if not entity.weapon:
            return ValidationResult.error("No weapon equipped")
        
        if entity.weapon.durability <= 0:
            return ValidationResult.error("Weapon broken")
        
        if entity.mana < action.mana_cost:
            return ValidationResult.error("Not enough mana")
        
        if not self.world_state.is_daytime():
            return ValidationResult.error("Can only attack during day")
        
        if entity.level < action.level_required:
            return ValidationResult.error("Level too low")
        
        return ValidationResult.success()
```

#### **17. 중복 코드와 복사-붙여넣기**
```python
# ❌ 나쁜 예시
def create_player_entity(name, level, health, mana, attack, defense):
    entity = {
        "id": generate_id(),
        "name": name,
        "type": "player",
        "level": level,
        "health": health,
        "mana": mana,
        "attack": attack,
        "defense": defense,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    return entity

def create_npc_entity(name, level, health, mana, attack, defense):
    entity = {
        "id": generate_id(),
        "name": name,
        "type": "npc",
        "level": level,
        "health": health,
        "mana": mana,
        "attack": attack,
        "defense": defense,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    return entity

# ✅ 좋은 예시
class EntityFactory:
    @staticmethod
    def create_entity(name: str, entity_type: EntityType, stats: EntityStats) -> Entity:
        return Entity(
            id=generate_id(),
            name=name,
            entity_type=entity_type,
            stats=stats,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @staticmethod
    def create_player(name: str, stats: EntityStats) -> Entity:
        return EntityFactory.create_entity(name, EntityType.PLAYER, stats)
    
    @staticmethod
    def create_npc(name: str, stats: EntityStats) -> Entity:
        return EntityFactory.create_entity(name, EntityType.NPC, stats)
```

#### **18. 불변성 무시와 사이드 이펙트**
```python
# ❌ 나쁜 예시
def process_inventory(player, item):
    # 원본 객체를 직접 수정
    player.inventory.append(item)
    player.inventory.sort()
    player.inventory = [item for item in player.inventory if item.quantity > 0]
    return player.inventory

def update_world_state(world, changes):
    # 전역 상태를 직접 수정
    world.entities.update(changes.entities)
    world.objects.update(changes.objects)
    world.events.extend(changes.events)
    return world

# ✅ 좋은 예시
def process_inventory(player: Player, item: Item) -> InventoryResult:
    # 불변성 유지
    new_inventory = player.inventory + [item]
    filtered_inventory = [item for item in new_inventory if item.quantity > 0]
    sorted_inventory = sorted(filtered_inventory, key=lambda x: x.name)
    
    return InventoryResult.success(
        player=player.with_inventory(sorted_inventory),
        changes=InventoryChanges(added=[item])
    )

def update_world_state(world: World, changes: WorldChanges) -> WorldResult:
    # 불변성 유지
    new_world = world.with_changes(changes)
    return WorldResult.success(new_world)
```

#### **19. 리소스 누수와 메모리 관리 부재**
```python
# ❌ 나쁜 예시
class GameEngine:
    def __init__(self):
        self.connections = []
        self.cache = {}
        self.listeners = []
    
    def load_world(self):
        # 연결을 닫지 않음
        conn = psycopg2.connect(DATABASE_URL)
        self.connections.append(conn)
        
        # 캐시를 무제한으로 증가
        for region in self.get_all_regions():
            self.cache[f"region_{region.id}"] = region
        
        # 이벤트 리스너를 정리하지 않음
        self.listeners.append(self.on_world_change)
    
    def cleanup(self):
        # 정리 코드가 없음
        pass

# ✅ 좋은 예시
class GameEngine:
    def __init__(self):
        self.connection_pool = None
        self.cache = LRUCache(maxsize=1000)
        self.listeners = []
        self._cleanup_registered = False
    
    async def load_world(self):
        async with self.get_db_connection() as conn:
            regions = await self.get_all_regions(conn)
            for region in regions:
                self.cache[f"region_{region.id}"] = region
        
        self.register_cleanup()
    
    def register_cleanup(self):
        if not self._cleanup_registered:
            atexit.register(self.cleanup)
            self._cleanup_registered = True
    
    def cleanup(self):
        if self.connection_pool:
            self.connection_pool.close()
        self.cache.clear()
        self.listeners.clear()
```

#### **20. 동시성 문제와 Race Condition**
```python
# ❌ 나쁜 예시
class GameState:
    def __init__(self):
        self.player_health = 100
        self.player_mana = 100
    
    def attack(self, damage):
        # Race condition 발생 가능
        if self.player_health > 0:
            self.player_health -= damage
    
    def heal(self, amount):
        # Race condition 발생 가능
        self.player_health += amount

# ✅ 좋은 예시
import asyncio
from asyncio import Lock

class GameState:
    def __init__(self):
        self.player_health = 100
        self.player_mana = 100
        self._lock = Lock()
    
    async def attack(self, damage: int) -> AttackResult:
        async with self._lock:
            if self.player_health > 0:
                self.player_health -= damage
                return AttackResult.success(self.player_health)
            return AttackResult.error("Player is already dead")
    
    async def heal(self, amount: int) -> HealResult:
        async with self._lock:
            if self.player_health > 0:
                self.player_health = min(100, self.player_health + amount)
                return HealResult.success(self.player_health)
            return HealResult.error("Cannot heal dead player")
```

#### **21. 테스트 불가능한 코드**
```python
# ❌ 나쁜 예시
class GameManager:
    def __init__(self):
        # 하드코딩된 의존성
        self.db = psycopg2.connect("postgresql://localhost:5432/game")
        self.ui = PyQt5.QMainWindow()
        self.logger = logging.getLogger("game")
    
    def process_action(self, action):
        # 테스트하기 어려운 코드
        if action.type == "attack":
            result = self.db.execute("SELECT * FROM entities WHERE id = %s", action.target_id)
            entity = result.fetchone()
            if entity:
                damage = random.randint(1, 10)  # 랜덤 값
                self.db.execute("UPDATE entities SET health = health - %s WHERE id = %s", 
                              (damage, action.target_id))
                self.ui.show_message(f"Dealt {damage} damage!")
                self.logger.info(f"Attack dealt {damage} damage")

# ✅ 좋은 예시
class GameManager:
    def __init__(self, db: DatabaseInterface, ui: UIInterface, logger: LoggerInterface):
        self.db = db
        self.ui = ui
        self.logger = logger
    
    async def process_action(self, action: Action) -> ActionResult:
        if action.type == "attack":
            entity = await self.db.get_entity(action.target_id)
            if entity:
                damage = self.calculate_damage(action, entity)
                await self.db.update_entity_health(action.target_id, -damage)
                await self.ui.show_message(f"Dealt {damage} damage!")
                self.logger.info(f"Attack dealt {damage} damage")
                return ActionResult.success(damage)
        return ActionResult.error("Invalid action")
    
    def calculate_damage(self, action: Action, entity: Entity) -> int:
        # 테스트 가능한 순수 함수
        base_damage = action.damage
        defense_factor = entity.defense / 100
        return max(1, int(base_damage * (1 - defense_factor)))
```

#### **22. 문서화 부재와 주석 남용**
```python
# ❌ 나쁜 예시
def process_data(data):
    # 데이터를 처리한다
    result = []
    for item in data:
        # 각 아이템을 처리한다
        if item.type == "weapon":
            # 무기인 경우
            if item.damage > 10:
                # 데미지가 10보다 큰 경우
                result.append(item)
        elif item.type == "armor":
            # 방어구인 경우
            if item.defense > 5:
                # 방어력이 5보다 큰 경우
                result.append(item)
    return result

# ✅ 좋은 예시
def filter_equipment_by_stats(equipment: List[Equipment]) -> List[Equipment]:
    """
    통계 기준으로 장비를 필터링합니다.
    
    Args:
        equipment: 필터링할 장비 목록
        
    Returns:
        필터링된 장비 목록
        
    Raises:
        ValueError: equipment가 None인 경우
    """
    if not equipment:
        raise ValueError("Equipment list cannot be None")
    
    return [
        item for item in equipment
        if self._meets_stat_requirements(item)
    ]
    
    def _meets_stat_requirements(self, item: Equipment) -> bool:
        """장비가 통계 요구사항을 만족하는지 확인"""
        if item.type == EquipmentType.WEAPON:
            return item.damage > self.WEAPON_DAMAGE_THRESHOLD
        elif item.type == EquipmentType.ARMOR:
            return item.defense > self.ARMOR_DEFENSE_THRESHOLD
        return False
```

#### **23. 성능 무시와 비효율적인 알고리즘**
```python
# ❌ 나쁜 예시
def find_entity_by_name(entities, name):
    # O(n) 선형 검색을 매번 수행
    for entity in entities:
        if entity.name == name:
            return entity
    return None

def get_entities_in_region(entities, region_id):
    # 매번 전체 엔티티를 순회
    result = []
    for entity in entities:
        if entity.region_id == region_id:
            result.append(entity)
    return result

# ✅ 좋은 예시
class EntityIndex:
    def __init__(self):
        self._name_index = {}
        self._region_index = defaultdict(list)
    
    def add_entity(self, entity: Entity):
        self._name_index[entity.name] = entity
        self._region_index[entity.region_id].append(entity)
    
    def find_by_name(self, name: str) -> Optional[Entity]:
        return self._name_index.get(name)
    
    def get_entities_in_region(self, region_id: str) -> List[Entity]:
        return self._region_index.get(region_id, [])
```

#### **24. 보안 취약점과 입력 검증 부재**
```python
# ❌ 나쁜 예시
def save_player_data(player_id, data):
    # SQL 인젝션 취약점
    query = f"UPDATE players SET data = '{data}' WHERE id = '{player_id}'"
    cursor.execute(query)

def process_user_input(user_input):
    # 입력 검증 없음
    return eval(user_input)  # 매우 위험!

# ✅ 좋은 예시
def save_player_data(player_id: str, data: PlayerData) -> SaveResult:
    # 입력 검증
    if not player_id or not isinstance(player_id, str):
        return SaveResult.error("Invalid player ID")
    
    if not data or not isinstance(data, PlayerData):
        return SaveResult.error("Invalid player data")
    
    try:
        # 매개변수화된 쿼리 사용
        query = "UPDATE players SET data = $1 WHERE id = $2"
        await db.execute(query, data.to_dict(), player_id)
        return SaveResult.success()
    except Exception as e:
        logger.error(f"Failed to save player data: {e}")
        return SaveResult.error("Failed to save data")

def process_user_input(user_input: str) -> ProcessResult:
    # 입력 검증
    if not user_input or not isinstance(user_input, str):
        return ProcessResult.error("Invalid input")
    
    # 화이트리스트 기반 검증
    allowed_commands = ["move", "attack", "heal", "inventory"]
    if user_input not in allowed_commands:
        return ProcessResult.error("Invalid command")
    
    return ProcessResult.success(user_input)
```

#### **25. 버전 관리와 의존성 관리 부재**
```python
# ❌ 나쁜 예시
# requirements.txt에 버전 없음
asyncpg
psycopg2
PyQt5
pytest

# 코드에서 하드코딩된 버전
if sys.version_info < (3, 8):
    raise RuntimeError("Python 3.8+ required")

# ✅ 좋은 예시
# requirements.txt에 정확한 버전 명시
asyncpg==0.28.0
psycopg2-binary==2.9.7
PyQt5==5.15.9
pytest==7.4.0

# 코드에서 적절한 버전 체크
import sys
from packaging import version

MIN_PYTHON_VERSION = "3.8.0"
if version.parse(sys.version) < version.parse(MIN_PYTHON_VERSION):
    raise RuntimeError(f"Python {MIN_PYTHON_VERSION}+ required")
```

#### **26. 데이터베이스 안전 조치 부재**
```python
# ❌ 나쁜 예시
async def reset_database():
    """사용자 컨펌 없이 데이터베이스 리셋"""
    await conn.execute("DROP SCHEMA IF EXISTS game_data CASCADE")
    await conn.execute("DROP SCHEMA IF EXISTS runtime_data CASCADE")
    # 위험한 작업을 경고 없이 실행

async def delete_all_entities():
    """백업 없이 모든 엔티티 삭제"""
    await conn.execute("DELETE FROM runtime_data.runtime_entities")
    # 복구 불가능한 데이터 손실

# ✅ 좋은 예시
class DatabaseSafetyManager:
    DANGEROUS_OPERATIONS = [
        "DROP_SCHEMA", "DELETE_ALL_DATA", "TRUNCATE_TABLES", 
        "DROP_TABLE", "ALTER_TABLE", "CREATE_INDEX"
    ]
    
    async def safe_database_operation(self, operation: str, sql: str, 
                                    user_confirmation: bool = False) -> OperationResult:
        """안전한 데이터베이스 작업"""
        if operation in self.DANGEROUS_OPERATIONS:
            if not user_confirmation:
                return OperationResult.error(
                    f"위험한 작업 '{operation}'은 사용자 컨펌이 필요합니다"
                )
            
            # 백업 생성
            backup_result = await self.create_backup()
            if not backup_result.success:
                return OperationResult.error("백업 생성 실패로 작업을 중단합니다")
            
            # 최종 확인 요청
            final_confirm = await self.request_final_confirmation(
                f"정말로 '{operation}' 작업을 수행하시겠습니까?\n"
                f"이 작업은 되돌릴 수 없습니다.\n"
                f"백업 위치: {backup_result.backup_path}"
            )
            
            if not final_confirm:
                return OperationResult.cancelled("사용자가 작업을 취소했습니다")
        
        # 작업 실행
        try:
            await conn.execute(sql)
            return OperationResult.success(f"'{operation}' 작업이 성공적으로 완료되었습니다")
        except Exception as e:
            return OperationResult.error(f"작업 실행 중 오류: {str(e)}")
    
    async def create_backup(self) -> BackupResult:
        """데이터베이스 백업 생성"""
        backup_path = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        try:
            # 실제 백업 로직
            await self.export_database(backup_path)
            return BackupResult.success(backup_path)
        except Exception as e:
            return BackupResult.error(f"백업 생성 실패: {str(e)}")
```

#### **27. 낙관적 성과 평가와 문제점 은폐**
```python
# ❌ 나쁜 예시
def evaluate_development_progress():
    """낙관적이고 부정확한 평가"""
    return {
        "completion_rate": "90%",  # 실제로는 60%
        "quality_score": "Excellent",  # 실제로는 많은 문제점 존재
        "issues": "Minor bugs only",  # 실제로는 심각한 문제들 존재
        "recommendation": "Ready for production"  # 실제로는 테스트 실패
    }

# ✅ 좋은 예시
class CriticalReviewManager:
    def __init__(self):
        self.test_results = []
        self.user_feedback = []
        self.actual_issues = []
    
    def evaluate_development_progress(self) -> CriticalEvaluation:
        """비판적이고 객관적인 평가"""
        # 실제 테스트 결과 기반 평가
        test_success_rate = self.calculate_actual_test_success_rate()
        critical_issues = self.identify_critical_issues()
        user_satisfaction = self.analyze_user_feedback()
        
        return CriticalEvaluation(
            actual_completion_rate=self.calculate_real_completion_rate(),
            test_success_rate=test_success_rate,
            critical_issues=critical_issues,
            user_satisfaction=user_satisfaction,
            blocking_issues=self.identify_blocking_issues(),
            realistic_assessment=self.provide_realistic_assessment(),
            improvement_priorities=self.identify_improvement_priorities()
        )
    
    def calculate_real_completion_rate(self) -> float:
        """실제 완성도 계산 (낙관적 해석 배제)"""
        # 실제 동작하는 기능만 카운트
        working_features = 0
        total_features = 0
        
        for feature in self.features:
            if self.is_feature_actually_working(feature):
                working_features += 1
            total_features += 1
        
        return (working_features / total_features) * 100 if total_features > 0 else 0
    
    def identify_critical_issues(self) -> List[CriticalIssue]:
        """실제 문제점 식별 (은폐하지 않음)"""
        issues = []
        
        # 테스트 실패 분석
        for test_failure in self.test_failures:
            issues.append(CriticalIssue(
                type="TEST_FAILURE",
                severity="HIGH",
                description=test_failure.description,
                impact=test_failure.impact
            ))
        
        # 사용자 피드백 분석
        for feedback in self.user_feedback:
            if feedback.rating < 3:  # 5점 만점에서 3점 미만
                issues.append(CriticalIssue(
                    type="USER_DISSATISFACTION",
                    severity="MEDIUM",
                    description=feedback.comment,
                    impact="사용자 경험 저하"
                ))
        
        return issues

---

## 🔄 **다음 에이전트를 위한 인수인계 가이드**

### **일반적인 개발 실수 방지 가이드**

다음 에이전트가 실수할 수 있는 일반적인 개발 원칙들을 정리합니다.

#### **1. 환경 설정 및 의존성 관리**
- **DO NOT**: 가상환경 활성화 없이 패키지 설치
  - *이유*: 시스템 Python 환경 오염, 패키지 충돌 발생
  - *대안*: 항상 가상환경(venv, conda) 사용 후 패키지 설치
- **DO NOT**: requirements.txt 없이 패키지 설치
  - *이유*: 재현 불가능한 환경, 의존성 지옥 발생
  - *대안*: 모든 패키지를 requirements.txt에 명시하고 버전 고정
- **DO NOT**: .env 파일을 Git에 커밋
  - *이유*: 민감한 정보(DB 비밀번호, API 키) 노출 위험
  - *대안*: .env.example 파일 생성, .env는 .gitignore에 추가

#### **2. 데이터베이스 작업**
- **DO NOT**: 프로덕션 DB에 직접 연결하여 테스트
  - *이유*: 데이터 손실 위험, 서비스 중단 가능성
  - *대안*: 테스트용 별도 DB 사용, 마이그레이션 스크립트 작성
- **DO NOT**: DROP TABLE 명령어를 스크립트에 포함
  - *이유*: 실수로 중요한 데이터 삭제 가능성
  - *대안*: 백업 후 안전한 삭제 절차 수립
- **DO NOT**: 트랜잭션 없이 여러 테이블 동시 수정
  - *이유*: 데이터 일관성 깨짐, 부분 실패 시 복구 어려움
  - *대안*: 트랜잭션으로 원자성 보장

#### **3. 코드 구조 및 설계**
- **DO NOT**: 하나의 파일에 모든 기능 구현
  - *이유*: 유지보수성 저하, 테스트 어려움
  - *대안*: 단일 책임 원칙에 따라 모듈 분리
- **DO NOT**: 하드코딩된 경로나 설정값 사용
  - *이유*: 환경별 설정 불가, 유연성 저하
  - *대안*: 설정 파일이나 환경변수 사용
- **DO NOT**: 전역 변수로 상태 관리
  - *이유*: 스레드 안전성 문제, 디버깅 어려움
  - *대안*: 의존성 주입이나 상태 관리 클래스 사용

#### **4. 테스트 및 품질 관리**
- **DO NOT**: 테스트 없이 기능 구현
  - *이유*: 버그 발견 어려움, 리팩토링 위험
  - *대안*: TDD 방식으로 테스트 우선 작성
- **DO NOT**: 테스트에서 실제 외부 서비스 호출
  - *이유*: 테스트 불안정성, 외부 의존성 문제
  - *대안*: Mock이나 Stub 사용으로 격리
- **DO NOT**: 테스트 데이터를 프로덕션 DB에 남겨둠
  - *이유*: 데이터 오염, 성능 저하
  - *대안*: 테스트 후 데이터 정리, 별도 테스트 DB 사용

#### **5. 에러 처리 및 로깅**
- **DO NOT**: except: pass로 모든 예외 무시
  - *이유*: 에러 원인 파악 불가, 디버깅 어려움
  - *대안*: 구체적인 예외 타입 처리, 로깅 추가
- **DO NOT**: print()로 디버깅 정보 출력
  - *이유*: 프로덕션에서 불필요한 출력, 로그 관리 어려움
  - *대안*: 적절한 로깅 레벨 사용 (DEBUG, INFO, WARNING, ERROR)
- **DO NOT**: 에러 메시지를 사용자에게 그대로 노출
  - *이유*: 보안 위험, 사용자 경험 저하
  - *대안*: 사용자 친화적 메시지로 변환

#### **6. 성능 및 보안**
- **DO NOT**: SQL 인젝션 취약점 방치
  - *이유*: 보안 취약점, 데이터 유출 위험
  - *대안*: 파라미터화된 쿼리 사용
- **DO NOT**: 대용량 데이터를 메모리에 한번에 로드
  - *이유*: 메모리 부족, 성능 저하
  - *대안*: 페이징이나 스트리밍 처리
- **DO NOT**: 비밀번호를 평문으로 저장
  - *이유*: 보안 위험, 개인정보 유출
  - *대안*: 해시 함수로 암호화 저장

#### **7. 문서화 및 협업**
- **DO NOT**: README 없이 프로젝트 시작
  - *이유*: 설치 및 실행 방법 불명, 협업 어려움
  - *대안*: 명확한 설치, 실행, 기여 가이드 작성
- **DO NOT**: 커밋 메시지를 "수정", "업데이트" 등으로 작성
  - *이유*: 변경 이력 추적 어려움, 롤백 시 문제
  - *대안*: 구체적인 변경 내용을 명시한 커밋 메시지
- **DO NOT**: 코드 리뷰 없이 메인 브랜치에 직접 푸시
  - *이유*: 코드 품질 저하, 버그 유입 위험
  - *대안*: Pull Request를 통한 코드 리뷰 프로세스

#### **8. 배포 및 운영**
- **DO NOT**: 프로덕션 환경에서 디버그 모드 실행
  - *이유*: 성능 저하, 보안 위험
  - *대안*: 환경별 설정 분리, 프로덕션 최적화
- **DO NOT**: 로그 파일을 무제한으로 쌓아둠
  - *이유*: 디스크 공간 부족, 성능 저하
  - *대안*: 로그 로테이션 설정, 오래된 로그 정리
- **DO NOT**: 백업 없이 중요한 작업 수행
  - *이유*: 데이터 손실 시 복구 불가
  - *대안*: 작업 전 백업 생성, 복구 계획 수립

### **프로젝트 특화 주의사항**

#### **RPG Engine 프로젝트 특화**
- **DO NOT**: 게임 데이터를 코드에 하드코딩
  - *이유*: 데이터 중심 설계 원칙 위반, 확장성 저하
  - *대안*: 모든 게임 데이터를 데이터베이스에 저장
- **DO NOT**: 동기 함수에서 비동기 함수 호출
  - *이유*: 이벤트 루프 블로킹, 성능 저하
  - *대안*: 모든 I/O 작업을 비동기로 구현
- **DO NOT**: 테스트에서 실제 게임 세션 데이터 사용
  - *이유*: 테스트 간섭, 데이터 오염
  - *대안*: 각 테스트마다 독립적인 세션 생성

이 가이드를 통해 다음 에이전트가 일반적인 실수를 방지하고, 프로젝트의 품질과 안정성을 유지할 수 있습니다.

---

## 📚 참고 문서

### 핵심 철학
- `docs/rules/01_PHILOSOPHY.md`: 핵심 개발 철학 및 불변 원칙

### 시스템별 가이드라인
- `docs/rules/EFFECT_CARRIER_GUIDELINES.md`: Effect Carrier 시스템 사용 가이드라인
- `docs/rules/ABILITIES_SYSTEM_GUIDELINES.md`: 스킬/주문 시스템 사용 가이드라인
- `docs/rules/DATABASE_SCHEMA_DESIGN_GUIDELINES.md`: 데이터베이스 스키마 설계 가이드라인

### 기술별 가이드라인
- `docs/rules/TYPE_SAFETY_GUIDELINES.md`: 타입 안전성 종합 가이드라인
- `docs/rules/UUID_USAGE_GUIDELINES.md`: UUID 사용 가이드라인
- `docs/rules/UUID_HANDLING_GUIDELINES.md`: UUID 처리 상세 가이드라인
- `docs/rules/TRANSACTION_GUIDELINES.md`: 트랜잭션 사용 가이드라인
- `docs/rules/MIGRATION_GUIDELINES.md`: 마이그레이션 가이드라인

### 프로젝트 관리
- `docs/rules/PROJECT_MANAGEMENT_WORKFLOW.md`: 프로젝트 관리 워크플로우
- `docs/rules/AGENT_DOCUMENT_MANAGEMENT_RULES.md`: 에이전트 문서 관리 규칙
- `docs/rules/README.md`: 모든 규칙 문서 인덱스
