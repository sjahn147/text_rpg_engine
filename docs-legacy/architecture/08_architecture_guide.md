# RPG Engine 아키텍처 가이드

> **최신화 날짜**: 2025-12-28  
> **문서 버전**: v1.1  
> **작성일**: 2025-10-18  
> **최종 수정**: 2025-12-28  
> **현재 상태**: Phase 3 완료, World Editor 80% 완료, 모든 Manager 클래스 구현 완료

## 🏗️ **시스템 아키텍처 개요**

RPG Engine은 3계층 아키텍처와 세션 중심 설계를 기반으로 한 확장 가능한 게임 엔진입니다.

### **핵심 설계 원칙**
1. **세션 중심 설계**: 각 게임 세션은 독립적인 데이터 공간
2. **3계층 구조**: Game Data → Reference Layer → Runtime Data
3. **모듈화**: 느슨한 결합, 높은 응집도
4. **확장성**: 플러그인 방식의 기능 확장
5. **Effect Carrier 시스템**: 통일 인터페이스로 모든 효과 관리
6. **EventBus 시스템**: 비동기 이벤트 처리 및 백그라운드 세계 진행

### **철학적 배경: "이야기 엔진"**
이 시스템은 단순한 게임 엔진이 아니라 **"서사 기반 세계의 시뮬레이션 구조체"**입니다.

#### **존재론적 설계**
- **불변의 진실**: Game Data는 세계의 창세기, 신화, 역사
- **동적 현실**: Runtime Data는 플레이어가 경험하는 살아있는 세계
- **연결의 다리**: Reference Layer는 두 세계를 이어주는 중간다리

#### **트랜잭션 기반 서사**
- **모든 상황을 셀·엔티티·오브젝트·이벤트의 트랜잭션으로 묘사**
- **현실은 원본 데이터의 복제물인 인스턴스**
- **플레이어는 세계를 조우할 뿐, 통제하지 않음**

---

## 📊 **데이터베이스 아키텍처**

### **3계층 구조**

#### **Game Data Layer (불변 게임 데이터)**
```
game_data/
├── world_regions          # 지역 정보
├── world_locations        # 장소 정보
├── world_cells           # 셀 정보
├── entities              # 엔티티 템플릿
├── base_properties       # 기본 속성
├── abilities_*           # 능력 시스템
├── equipment_*           # 장비 시스템
├── inventory_items       # 아이템 시스템
├── dialogue_*            # 대화 시스템
└── world_objects         # 월드 오브젝트
```

**철학적 의미**: Game Data는 세계의 창세기입니다. 신화, 역사, 기본 설정이 담긴 불변의 진실이 저장되는 곳입니다.

#### **Reference Layer (참조 관계 관리)**
```
reference_layer/
├── entity_references     # 엔티티 참조
├── object_references     # 오브젝트 참조
└── cell_references       # 셀 참조
```

**철학적 의미**: Reference Layer는 두 세계를 연결하는 중간다리입니다. 불변의 진실과 동적 현실을 이어주는 존재론적 다리입니다.

#### **Runtime Data Layer (실행 중인 게임 상태)**
```
runtime_data/
├── active_sessions        # 활성 세션
├── entity_states         # 엔티티 상태
├── object_states         # 오브젝트 상태
├── dialogue_*            # 대화 상태
├── triggered_events      # 이벤트 시스템
└── player_choices        # 플레이어 선택
```

**철학적 의미**: Runtime Data는 플레이어가 경험하는 살아있는 현실입니다. 모든 상태 변화, 선택, 결과가 기록되는 동적 세계입니다.

---

## 🎮 **애플리케이션 아키텍처**

### **계층 구조**

#### **Presentation Layer (표현 계층)**
```
app/ui/
├── main_window.py        # 메인 윈도우
├── screens/              # 게임 화면
│   ├── dialogue_screen.py
│   ├── map_screen.py
│   ├── status_screen.py
│   └── inventory_screen.py
└── components/           # UI 컴포넌트
```

#### **Business Logic Layer (비즈니스 로직 계층)**
```
app/core/
├── game_manager.py       # 게임 매니저 ✅ 구현 완료
├── scenario_loader.py    # 시나리오 로더 ✅ 구현 완료
├── scenario_executor.py  # 시나리오 실행기 ✅ 구현 완료
├── framework_manager.py  # 프레임워크 관리자 ✅ 구현 완료
└── event_bus.py         # 이벤트 시스템 (계획)

app/entity/
├── base.py              # 기본 엔티티 ✅ 구현 완료
├── entity_manager.py    # 엔티티 관리자 ✅ 구현 완료 (의존성 주입, 캐싱, 타입 안전)
├── instance_manager.py  # 인스턴스 관리자 ✅ 구현 완료
└── effect_carrier_manager.py  # Effect Carrier 관리자 ✅ 구현 완료 (6가지 타입)

app/world/
├── cell_manager.py      # 셀 관리자 ✅ 구현 완료 (CRUD, 이동, 캐싱)
└── cell_manager.py      # 셀 관리 (navigation 포함)

app/interaction/
├── dialogue_manager.py  # 대화 시스템 ✅ 구현 완료 (시작/계속/종료)
└── action_handler.py    # 액션 핸들러 ✅ 구현 완료 (8가지 핵심 액션)

app/systems/
├── npc_behavior.py      # NPC 행동 시스템 ✅ 구현 완료
└── time_system.py       # 시간 시스템 ✅ 구현 완료

app/world_editor/        # World Editor 모듈 ✅ 80% 완료
├── main.py              # FastAPI 메인 앱 ✅ 구현 완료
├── schemas.py           # Pydantic 스키마 ✅ 구현 완료
├── routes/              # API 라우터 ✅ 구현 완료
├── services/            # 비즈니스 로직 ✅ 구현 완료
└── frontend/            # React 프론트엔드 ✅ 구현 완료

app/ui/
├── main_window.py       # 메인 윈도우 ✅ 구현 완료
├── dashboard.py         # 계기판 UI ✅ 구현 완료
└── screens/             # 화면별 UI ✅ 구현 완료
```

#### **Data Access Layer (데이터 접근 계층)**
```
database/
├── connection.py         # 데이터베이스 연결 ✅ 구현 완료 (연결 풀 관리)
├── connection_manager.py # 연결 생명주기 관리 ✅ 구현 완료
├── repositories/         # 데이터 저장소 ✅ 구현 완료
│   ├── game_data.py     # Game Data Repository ✅ 구현 완료
│   ├── runtime_data.py  # Runtime Data Repository ✅ 구현 완료
│   └── reference_layer.py # Reference Layer Repository ✅ 구현 완료
└── factories/            # 객체 생성 팩토리 ✅ 구현 완료
    ├── game_data_factory.py    # Game Data Factory ✅ 구현 완료
    ├── instance_factory.py     # Instance Factory ✅ 구현 완료
    └── world_data_factory.py   # World Data Factory ✅ 구현 완료
```

---

## 🚌 **EventBus 시스템**

### **이벤트 처리 아키텍처**
- **in-proc 큐**: 메모리 내 이벤트 큐로 빠른 처리
- **예약 처리**: 백그라운드 이벤트 (세계 틱) 스케줄링
- **충돌 방지**: 세션 락 / 낙관적 버전 (버전 필드)
- **이벤트 타입**: cell_entered, entity_spawned, world_tick, dialogue_started

### **세션 락/낙관적 버전**
- **세션 락**: 동시 접근 방지로 데이터 일관성 보장
- **낙관적 버전**: 버전 필드로 충돌 감지 및 해결
- **충돌 해결**: 자동 재시도 또는 사용자 알림

### **캐시 전략**
- **셀 컨텐츠 캐시**: 자주 접근하는 셀 정보 캐싱
- **대화 컨텍스트 캐시**: NPC 대화 컨텍스트 캐싱
- **LLM 응답 캐시**: AI 생성 내용 캐싱 (키: 상태 해시)
- **이미지 캐시**: seed + 캐시 경로로 영구화

---

## ⚡ **Effect Carrier 아키텍처**

### **통일 인터페이스 설계**
- **skill / buff / item / blessing / curse / ritual** 등 **동일 인터페이스**로 소유·적용
- **특수성은 엔티티가 아니라 소유한 형식(오브젝트)에 있음**
- **유연한 효과 관리**: 다양한 효과를 일관된 방식으로 처리

### **Effect Carrier 테이블 구조**
```sql
-- 이펙트 캐리어 (형식의 통일)
CREATE TABLE game_data.effect_carriers (
  effect_id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  carrier_type TEXT CHECK (carrier_type IN
    ('skill','buff','item','blessing','curse','ritual')),
  effect_json JSONB NOT NULL,       -- 수치/조건/지속시간 등
  constraints_json JSONB DEFAULT '{}'::jsonb,
  source_entity_id UUID NULL,       -- 신격/유래
  tags TEXT[]
);

-- 엔티티가 소유한 형식
CREATE TABLE reference_layer.entity_effect_ownership (
  session_id UUID NOT NULL,
  runtime_entity_id UUID NOT NULL,
  effect_id UUID NOT NULL,
  acquired_at TIMESTAMP NOT NULL DEFAULT now(),
  source TEXT,
  PRIMARY KEY (session_id, runtime_entity_id, effect_id)
);
```

---

## 🌍 **World Tick 시스템**

### **백그라운드 세계 진행**
- **world_tick()**: 시간 경과/스케줄 처리(내부 정치, 재난, 관계 변화)
- **비가시 이벤트**: 로그만 남김 → 플레이어가 나중에 "결과"와 조우
- **결정적 난수**: seed로 재현성 확보
- **오프라인 진행**: 마지막 활동 시각 기반 catch‑up

### **보안/무결성**
- **LLM→SQL 경로 차단**: LLM은 **행동 DSL**만 출력 → 서버에서 해석·검증 후 쿼리
- **입력 검증**: whitelist 스키마, 수치 범위, 상태 머신 전이 검사
- **권한**: DevMode 격리, 승격/스키마 변경 권한 제한
- **감사 로그**: 모든 promote, 삭제, 롤백 기록

### **인덱싱 전략**
- **JSONB 필드**: **GIN** 인덱스
- **조회 잦은 FK**: **B‑Tree** 인덱스
- **이벤트 시간**: `triggered_at`, `last_active_at` 인덱스
- **event_sourcing**: append‑only 로그 + 스냅샷(선택)

---

## 🔄 **데이터 플로우**

### **게임 세션 생성 플로우**
```
1. 세션 생성 (active_sessions)
2. 플레이어 엔티티 참조 생성 (entity_references)
3. 초기 셀 참조 생성 (cell_references)
4. 엔티티 상태 초기화 (entity_states)
5. 대화 상태 초기화 (dialogue_states)
```

### **게임플레이 플로우**
```
1. 플레이어 액션 입력
2. 비즈니스 로직 처리
3. 데이터베이스 상태 업데이트
4. 이벤트 발생 및 처리
5. UI 상태 업데이트
6. 플레이어 피드백
```

### **세션 종료 플로우**
```
1. 게임 상태 저장
2. 세션 상태 변경 (ending)
3. 런타임 데이터 정리
4. 세션 상태 변경 (closed)
```

---

## 🧩 **모듈 설계**

### **핵심 모듈**

#### **GameManager**
- **책임**: 게임 전체 상태 관리
- **기능**: 세션 생성/종료, 상태 저장/로드
- **의존성**: DatabaseConnection, ScenarioExecutor

#### **ScenarioExecutor**
- **책임**: 시나리오 실행 및 관리
- **기능**: 시나리오 로드, 단계 실행, 분기 처리
- **의존성**: ScenarioLoader, EventBus

#### **EntityManager** ✅ 구현 완료
- **책임**: 엔티티 상태 관리
- **기능**: 엔티티 생성/조회/수정/삭제, Effect Carrier 연동, 캐싱
- **의존성**: DatabaseConnection, GameDataRepository, RuntimeDataRepository, ReferenceLayerRepository, EffectCarrierManager
- **특징**: 의존성 주입, 타입 안전성 (Pydantic), 비동기 캐싱, 구조화된 에러 처리

#### **CellManager** ✅ 구현 완료
- **책임**: 게임 월드 관리
- **기능**: 셀 생성/조회/수정/삭제, 엔티티 이동, 컨텐츠 로딩, 캐싱
- **의존성**: DatabaseConnection, GameDataRepository, RuntimeDataRepository, ReferenceLayerRepository, EntityManager
- **특징**: 의존성 주입, 타입 안전성, 비동기 캐싱, 셀 컨텐츠 관리

### **확장 모듈**

#### **DialogueManager** ✅ 구현 완료
- **책임**: 대화 시스템 관리
- **기능**: 대화 시작/계속/종료, NPC 응답 생성, 대화 기록 저장/조회
- **의존성**: DatabaseConnection, GameDataRepository, RuntimeDataRepository
- **특징**: 컨텍스트 기반 대화, 지식 베이스 연동, 대화 상태 관리

#### **CombatSystem**
- **책임**: 전투 시스템 관리
- **기능**: 전투 실행, 데미지 계산, 상태 효과
- **확장점**: 새로운 전투 규칙 추가

#### **QuestSystem**
- **책임**: 퀘스트 시스템 관리
- **기능**: 퀘스트 진행, 보상 지급, 완료 처리
- **확장점**: 새로운 퀘스트 타입 추가

---

## 🔌 **확장성 설계**

### **플러그인 시스템**

#### **플러그인 인터페이스**
```python
class GamePlugin:
    def __init__(self, game_manager):
        self.game_manager = game_manager
    
    def initialize(self):
        """플러그인 초기화"""
        pass
    
    def on_event(self, event_type, data):
        """이벤트 처리"""
        pass
    
    def cleanup(self):
        """플러그인 정리"""
        pass
```

#### **플러그인 등록**
```python
# 플러그인 등록 예시
game_manager.register_plugin("dialogue", DialoguePlugin())
game_manager.register_plugin("combat", CombatPlugin())
game_manager.register_plugin("quest", QuestPlugin())
```

### **이벤트 시스템**

#### **이벤트 타입**
- **entity_created**: 엔티티 생성
- **entity_moved**: 엔티티 이동
- **dialogue_started**: 대화 시작
- **combat_started**: 전투 시작
- **quest_completed**: 퀘스트 완료

#### **이벤트 처리**
```python
# 이벤트 발행
event_bus.publish("entity_moved", {
    "entity_id": entity_id,
    "from_cell": old_cell,
    "to_cell": new_cell
})

# 이벤트 구독
event_bus.subscribe("entity_moved", handle_entity_movement)
```

---

## 🚀 **성능 최적화**

### **데이터베이스 최적화**

#### **인덱스 전략**
- **기본 키**: 자동 인덱스
- **외래 키**: 자동 인덱스
- **검색 필드**: 수동 인덱스 생성
- **복합 인덱스**: 자주 함께 조회되는 필드

#### **쿼리 최적화**
- **연결 풀**: 비동기 연결 풀 사용
- **배치 처리**: 대량 데이터 처리 시 배치 사용
- **캐싱**: 자주 조회되는 데이터 캐싱

### **메모리 최적화**

#### **객체 풀링**
```python
class EntityPool:
    def __init__(self, max_size=1000):
        self.pool = []
        self.max_size = max_size
    
    def get_entity(self):
        if self.pool:
            return self.pool.pop()
        return Entity()
    
    def return_entity(self, entity):
        if len(self.pool) < self.max_size:
            entity.reset()
            self.pool.append(entity)
```

#### **지연 로딩**
```python
class LazyEntity:
    def __init__(self, entity_id):
        self.entity_id = entity_id
        self._entity = None
    
    @property
    def entity(self):
        if self._entity is None:
            self._entity = load_entity(self.entity_id)
        return self._entity
```

---

## 🔒 **보안 고려사항**

### **데이터 보안**

#### **입력 검증**
- **SQL 인젝션 방지**: 파라미터화된 쿼리 사용
- **XSS 방지**: 사용자 입력 이스케이프
- **데이터 검증**: Pydantic 모델 사용

#### **접근 제어**
- **세션 기반**: 세션별 데이터 격리
- **권한 관리**: 역할 기반 접근 제어
- **감사 로그**: 중요한 작업 로깅

### **네트워크 보안**

#### **통신 보안**
- **HTTPS**: 암호화된 통신
- **인증**: JWT 토큰 기반 인증
- **Rate Limiting**: 요청 제한

---

## 📈 **모니터링 및 로깅**

### **로깅 시스템**

#### **로그 레벨**
- **DEBUG**: 개발 중 디버깅
- **INFO**: 일반적인 정보
- **WARNING**: 주의가 필요한 상황
- **ERROR**: 오류 발생
- **CRITICAL**: 심각한 오류

#### **로그 구조**
```python
logger.info("Game session started", extra={
    "session_id": session_id,
    "player_id": player_id,
    "timestamp": datetime.now()
})
```

### **모니터링 지표**

#### **성능 지표**
- **응답 시간**: API 응답 시간
- **처리량**: 초당 요청 수
- **에러율**: 에러 발생 비율
- **리소스 사용률**: CPU, 메모리, 디스크

#### **비즈니스 지표**
- **활성 세션 수**: 동시 게임 세션
- **플레이어 활동**: 플레이어 행동 패턴
- **콘텐츠 사용률**: 기능별 사용률

---

## 🧪 **테스트 아키텍처**

### **테스트 계층**

#### **단위 테스트**
- **범위**: 개별 함수/메서드
- **도구**: pytest
- **목표**: 90% 이상 커버리지

#### **통합 테스트**
- **범위**: 모듈 간 연동
- **도구**: pytest + testcontainers
- **목표**: 주요 플로우 검증

#### **시나리오 테스트**
- **범위**: 전체 게임 플로우
- **도구**: 커스텀 테스트 프레임워크
- **목표**: 실제 사용자 시나리오 검증

### **테스트 데이터 관리**

#### **테스트 데이터 생성**
```python
class TestDataFactory:
    def create_test_session(self):
        return {
            "session_id": str(uuid.uuid4()),
            "player_id": "test_player_001",
            "initial_cell": "test_cell_001"
        }
    
    def create_test_entity(self, entity_type="player"):
        return {
            "entity_id": f"test_{entity_type}_{uuid.uuid4().hex[:8]}",
            "entity_type": entity_type,
            "stats": {"hp": 100, "mp": 50}
        }
```

---

## 📚 **참고 자료**

### **아키텍처 패턴**
- **Clean Architecture**: https://blog.cleancoder.com/
- **Domain-Driven Design**: https://martinfowler.com/
- **Event-Driven Architecture**: https://microservices.io/

### **데이터베이스 설계**
- **PostgreSQL 문서**: https://www.postgresql.org/docs/
- **데이터베이스 정규화**: https://en.wikipedia.org/wiki/Database_normalization
- **인덱스 최적화**: https://use-the-index-luke.com/

### **성능 최적화**
- **Python 성능**: https://docs.python.org/3/library/profile.html
- **데이터베이스 튜닝**: https://www.postgresql.org/docs/current/performance-tips.html
- **메모리 관리**: https://docs.python.org/3/library/gc.html

---

**문서 작성자**: RPG Engine Development Team  
**최종 검토**: 2025-10-18  
**최신화**: 2025-12-28  
**다음 검토 예정**: 2026-01-28

---

## 📊 **현재 구현 상태 (2025-12-28)**

### ✅ **완료된 핵심 기능**
1. **Manager 클래스 시스템**: EntityManager, CellManager, DialogueManager, ActionHandler, EffectCarrierManager 모두 구현 완료
2. **데이터베이스 아키텍처**: 3계층 구조 완성 (40개 테이블, 완전한 외래키 제약조건)
3. **Effect Carrier 시스템**: 6가지 타입 (skill, buff, item, blessing, curse, ritual) 구현 완료
4. **World Editor**: 계층적 맵 뷰, Entity/Dialogue 편집, 실시간 동기화 (80% 완료)
5. **Phase 3 Village Simulation**: 100일 시뮬레이션 성공 (228 대화, 833 행동)

### 🏆 **성능 벤치마크 달성**
- 엔티티 생성: 1,226 entities/sec (목표 대비 2,352% 초과)
- 동시 세션: 960 entities/sec (목표 대비 860% 초과)
- 셀 작업: 413 cells/sec (목표 대비 4,030% 초과)
- 대화 시스템: 275 dialogues/sec (목표 대비 2,650% 초과)

### 🚧 **진행 중인 작업**
- World Editor 완성 (80% → 100%)
- 텍스트 어드벤처 게임 GUI
- 게임 세션 API
- TimeSystem 모듈 고도화
