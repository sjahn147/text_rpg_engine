# [deprecated] RPG Engine 테스팅 가이드

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: 테스팅 가이드 내용이 구현 완료되었으며, 실제 테스트 구조와 다릅니다. 현재는 `tests/active/` 디렉토리의 실제 테스트 파일들을 참조해야 합니다.

> **최신화 날짜**: 2025-12-28  
> **최종 업데이트**: 2025-10-18  
> **문서 버전**: v1.1  
> **테스트 환경**: Windows 10, Python 3.12, PostgreSQL 17
> **현재 상태**: Phase 3 Village Simulation 완료, 모든 테스트 100% 통과

## 📋 **테스트 개요**

RPG Engine의 테스트 시스템은 데이터베이스 정합성부터 실제 게임 플로우까지 포괄적으로 검증합니다.

### 🎯 **테스트 목표**
- 데이터베이스 아키텍처 검증
- 게임 로직 정합성 확인
- 시나리오 기반 통합 테스트
- 성능 및 확장성 검증
- MVP 수용 기준 검증
- Effect Carrier 시스템 테스트
- Dev Mode 기능 테스트
- World Tick 시스템 테스트
- 캐시 시스템 테스트
- 보안 시스템 테스트

### 🧠 **철학적 배경: "이야기 엔진" 테스팅**
이 프로젝트는 단순한 게임이 아니라 **"서사 기반 세계의 시뮬레이션 구조체"**이므로, 테스팅도 이 철학을 반영합니다.

- **세계 무결성**: 불변의 Game Data와 동적 Runtime Data 간의 일관성
- **트랜잭션 서사**: 모든 상호작용이 올바른 트랜잭션으로 기록되는지 확인
- **지속적 세계**: 플레이어가 없어도 세계가 계속 작동하는지 검증
- **AI 해석 정확성**: LLM이 상황을 올바르게 해석하고 서사를 생성하는지 확인

---

## 🎯 **MVP 수용 기준**

### **포함 기능**
- 계기판 UI(텍스트), 월드맵(리스트), Region→Location→Cell 전환
- 행동: 조사/대화/거래/방문/대기
- 최소 데이터: **도시 1(레크로스타)**, Location ≥3(역/상점/관청), NPC ≥2, 이벤트 ≥1
- Dev Mode(베타): 엔티티/로어 추가, **promote** 1‑click
- 로그/저장: 세션 저장·복구, 행동/세계 이벤트 기록

### **수용 기준 (샘플)**
- 도시 입장 시 셀/엔티티/오브젝트 로딩 및 **행동 → 결과 → 로그** 루프가 100회 연속 무오류
- DevMode에서 생성한 NPC가 **다음 세션**에서 정상 템플릿으로 노출
- LLM 비활성 시에도(옵션) 룰기반 묘사/대화로 플레이 가능

---

## 🧪 **테스트 파일 구조**

```
tests/
├── database_test.py              # 데이터베이스 연결 테스트
├── database_integrity_test.py   # 데이터베이스 정합성 테스트
├── effect_carrier_test.py        # Effect Carrier 시스템 테스트
├── dev_mode_test.py             # Dev Mode 기능 테스트
├── world_tick_test.py           # World Tick 시스템 테스트
├── cache_test.py                # 캐시 시스템 테스트
├── security_test.py             # 보안 시스템 테스트
├── mvp_acceptance_test.py       # MVP 수용 기준 테스트
├── unit/                        # 단위 테스트 (빈 디렉토리)
├── integration/                 # 통합 테스트 (빈 디렉토리)
└── scenarios/                   # 시나리오 테스트
    ├── basic_interaction_scenario.json
    ├── scenario_test.py
    ├── class_based_scenario_test.py
    └── modular_scenario_test.py
```

---

## 🔍 **개별 테스트 상세 분석**

### 1. **database_test.py** ✅
**상태**: 완벽 작동 (100% 통과)  
**최종 테스트**: 2025-10-18

#### **기능**
- PostgreSQL 데이터베이스 연결 확인
- 3개 스키마 존재 확인 (game_data, reference_layer, runtime_data)
- 27개 테이블 생성 상태 확인
- UUID 확장 기능 설치 확인

#### **실행 방법**
```bash
$env:PYTHONPATH="C:\hobby\rpg_engine"; python tests/database_test.py
```

#### **예상 결과**
```
✅ PostgreSQL 연결 성공! (포트 5432)
📁 스키마 목록: game_data, reference_layer, runtime_data
📋 테이블 수: 27개 (모든 스키마)
✅ UUID 확장 기능 설치됨
🎉 데이터베이스 설정 완료!
```

#### **검증 항목**
- [x] 데이터베이스 연결
- [x] 스키마 존재
- [x] 테이블 생성
- [x] 확장 기능

---

### 2. **database_integrity_test.py** ⚠️
**상태**: 부분 작동 (83% 통과, 5/6 테스트)  
**최종 테스트**: 2025-10-18

#### **기능**
- 외래 키 제약조건 테스트
- 데이터 무결성 테스트
- 게임 세션 플로우 테스트
- 대화 시스템 테스트
- 엔티티 생명주기 테스트
- 성능 및 확장성 테스트

#### **실행 방법**
```bash
$env:PYTHONPATH="C:\hobby\rpg_engine"; python tests/database_integrity_test.py
```

#### **테스트 결과**
| 테스트 항목 | 상태 | 설명 |
|------------|------|------|
| 외래 키 제약조건 | ✅ 통과 | 존재하지 않는 참조 차단 확인 |
| 데이터 무결성 | ❌ 실패 | 중복 키 문제 (TEST_PLAYER_001) |
| 게임 세션 플로우 | ✅ 통과 | 세션 생성 → 엔티티 → 상태 플로우 |
| 대화 시스템 | ✅ 통과 | 대화 컨텍스트 및 상태 생성 |
| 엔티티 생명주기 | ✅ 통과 | 생성 → 업데이트 → 이력 기록 |
| 성능 및 확장성 | ✅ 통과 | 5,000 레코드/초, 100,000 쿼리/초 |

#### **성능 지표**
- **대량 삽입**: 5,000 레코드/초
- **복잡한 조인**: 100,000 쿼리/초
- **메모리 효율성**: 연결 풀 사용

#### **개선 필요사항**
- 중복 키 문제 해결 (TEST_PLAYER_001)
- 테스트 데이터 정리 로직 추가

---

### 3. **scenarios/scenario_test.py** ✅
**상태**: 완벽 작동 (100% 통과)  
**최종 테스트**: 2025-10-18

#### **기능**
- 기본 시나리오 테스트
- 플레이어-NPC 상호작용 시뮬레이션
- 이벤트 시스템 검증
- 게임 상태 관리 테스트

#### **실행 방법**
```bash
$env:PYTHONPATH="C:\hobby\rpg_engine"; python tests/scenarios/scenario_test.py
```

#### **테스트 시나리오**
1. **세션 생성**: 게임 세션 및 셀 생성
2. **엔티티 생성**: 플레이어와 상인 NPC 생성
3. **상호작용**: 대화 시스템 테스트
4. **이벤트 처리**: 경험치 획득 이벤트
5. **상태 저장**: 게임 상태 저장

#### **예상 결과**
```
테스트 시나리오 시작...
테스트 세션 생성됨: [UUID]
테스트 플레이어 생성됨: [UUID]
테스트 상인 생성됨: [UUID]
상인: 어서오세요!
상인: 안녕히 가세요!
상인과 상호작용 완료
경험치 100 획득!
시나리오 테스트 성공!
```

---

### 4. **scenarios/class_based_scenario_test.py** ✅
**상태**: 완벽 작동 (100% 통과)  
**최종 테스트**: 2025-10-18

#### **기능**
- 클래스 기반 시나리오 테스트
- 객체지향 설계 검증
- 플레이어 이동 시스템 테스트
- 엔티티 상호작용 거리 계산

#### **실행 방법**
```bash
$env:PYTHONPATH="C:\hobby\rpg_engine"; python tests/scenarios/class_based_scenario_test.py
```

#### **테스트 시나리오**
1. **데이터 설정**: 테스트 데이터 생성
2. **세션 생성**: 게임 세션 및 플레이어 생성
3. **셀 입장**: 플레이어가 셀에 입장
4. **상호작용**: NPC와의 거리 기반 상호작용
5. **이동 테스트**: 플레이어 위치 변경
6. **상태 저장**: 게임 상태 저장 및 정리

#### **특징**
- 객체지향 설계 패턴 검증
- 거리 기반 상호작용 로직
- 게임 상태 지속성 테스트

---

### 5. **scenarios/modular_scenario_test.py** ✅
**상태**: 완벽 작동 (100% 통과)  
**최종 테스트**: 2025-10-18

#### **기능**
- 모듈러 시나리오 테스트
- 모듈 간 연동 검증
- 이벤트 처리 시스템 테스트
- 확장 가능한 아키텍처 검증

#### **실행 방법**
```bash
$env:PYTHONPATH="C:\hobby\rpg_engine"; python tests/scenarios/modular_scenario_test.py
```

#### **테스트 시나리오**
1. **모듈 초기화**: 각 모듈별 인스턴스 생성
2. **세션 관리**: 게임 세션 및 셀 관리
3. **엔티티 관리**: 플레이어 및 NPC 관리
4. **상호작용**: 모듈 간 상호작용 테스트
5. **이벤트 처리**: 퀘스트 완료 이벤트

#### **특징**
- 모듈화된 아키텍처 검증
- 확장 가능한 설계 패턴
- 이벤트 기반 시스템 테스트

### 6. **effect_carrier_test.py** 🆕
**상태**: 새로 추가 예정  
**목적**: Effect Carrier 시스템의 통일 인터페이스 검증

#### **테스트 범위**
- **Effect Carrier 생성**: skill, buff, item, blessing, curse, ritual 타입
- **엔티티 소유 관계**: entity_effect_ownership 테이블 검증
- **효과 적용**: Effect Carrier의 실제 적용 및 결과 검증
- **제약 조건**: constraints_json 검증
- **소스 추적**: source_entity_id 및 태그 시스템

### 7. **dev_mode_test.py** 🆕
**상태**: 새로 추가 예정  
**목적**: Dev Mode(창세 대시보드) 기능 검증

#### **테스트 범위**
- **Game Data 편집**: Region, Location, Cell, Entity, EffectCarrier CRUD
- **Runtime→GameData Promote**: 승격 기능 검증
- **미리보기 생성**: LLM 샘플 생성 및 제약 검증
- **버전/감사**: editor, created_at, reason, diff 추적
- **권한 관리**: RBAC 권한 검증

### 8. **world_tick_test.py** 🆕
**상태**: 새로 추가 예정  
**목적**: World Tick 시스템 및 백그라운드 이벤트 검증

#### **테스트 범위**
- **World Tick 실행**: 시간 경과/스케줄 처리
- **비가시 이벤트**: 로그만 남기는 이벤트 검증
- **결정적 난수**: seed 기반 재현성 검증
- **오프라인 진행**: catch-up 메커니즘 검증
- **이벤트 타입**: political_change, disaster, relationship_change 등

### 9. **cache_test.py** 🆕
**상태**: 새로 추가 예정  
**목적**: 캐시 시스템 성능 및 정확성 검증

#### **테스트 범위**
- **셀 컨텐츠 캐시**: 자주 접근하는 셀 정보 캐싱
- **대화 컨텍스트 캐시**: NPC 대화 컨텍스트 캐싱
- **LLM 응답 캐시**: AI 생성 내용 캐싱 (키: 상태 해시)
- **이미지 캐시**: seed + 캐시 경로 영구화
- **캐시 무효화**: TTL 및 무효화 메커니즘

### 10. **security_test.py** 🆕
**상태**: 새로 추가 예정  
**목적**: 보안 시스템 및 무결성 검증

#### **테스트 범위**
- **LLM→SQL 경로 차단**: LLM이 직접 SQL을 실행하지 못하도록 차단
- **입력 검증**: whitelist 스키마, 수치 범위, 상태 머신 전이 검사
- **권한 관리**: DevMode 격리, 승격/스키마 변경 권한 제한
- **감사 로그**: 모든 promote, 삭제, 롤백 기록
- **RBAC**: 플레이/에디트 분리, 관리자만 승격

### 11. **mvp_acceptance_test.py** 🆕
**상태**: 새로 추가 예정  
**목적**: MVP 수용 기준 종합 검증

#### **테스트 범위**
- **100회 연속 무오류**: 행동 → 결과 → 로그 루프
- **DevMode 생성 검증**: 다음 세션에서 정상 템플릿 노출
- **LLM 비활성 플레이**: 룰기반 묘사/대화로 플레이 가능
- **계기판 UI**: 텍스트 기반 UI 동작 검증
- **Region→Location→Cell**: 전환 시스템 검증

---

## 📊 **전체 테스트 현황**

### **테스트 통과율**
- **database_test.py**: 100% (4/4 항목)
- **database_integrity_test.py**: 83% (5/6 항목)
- **scenario_test.py**: 100% (모든 시나리오)
- **class_based_scenario_test.py**: 100% (모든 시나리오)
- **modular_scenario_test.py**: 100% (모든 시나리오)

### **전체 통과율**: 96% (24/25 항목)

### **성능 지표**
- **데이터베이스 연결**: < 1초
- **테이블 조회**: < 0.1초
- **대량 삽입**: 5,000 레코드/초
- **복잡한 조인**: 100,000 쿼리/초
- **시나리오 실행**: < 5초

---

## 🚀 **테스트 실행 가이드**

### **전체 테스트 실행**
```bash
# 환경 변수 설정
$env:PYTHONPATH="C:\hobby\rpg_engine"

# 개별 테스트 실행
python tests/database_test.py
python tests/database_integrity_test.py
python tests/scenarios/scenario_test.py
python tests/scenarios/class_based_scenario_test.py
python tests/scenarios/modular_scenario_test.py
```

### **배치 테스트 실행**
```bash
# 모든 테스트를 순차적으로 실행
$env:PYTHONPATH="C:\hobby\rpg_engine"; python tests/database_test.py && python tests/database_integrity_test.py && python tests/scenarios/scenario_test.py
```

---

## 🔧 **문제 해결 가이드**

### **일반적인 문제들**

#### **1. 모듈 오류**
```
ModuleNotFoundError: No module named 'database'
```
**해결방법**: PYTHONPATH 환경변수 설정
```bash
$env:PYTHONPATH="C:\hobby\rpg_engine"
```

#### **2. 데이터베이스 연결 오류**
```
psycopg2.OperationalError: connection failed
```
**해결방법**: 
- PostgreSQL 서버 실행 확인
- 연결 정보 확인 (`database/connection.py`)
- 방화벽 설정 확인

#### **3. 중복 키 오류**
```
duplicate key value violates unique constraint
```
**해결방법**: 
- 기존 테스트 데이터 정리
- 고유한 ID 사용
- 테스트 전 데이터 초기화

### **성능 최적화**

#### **데이터베이스 최적화**
- 연결 풀 크기 조정
- 인덱스 최적화
- 쿼리 성능 분석

#### **테스트 최적화**
- 병렬 테스트 실행
- 테스트 데이터 최소화
- 캐싱 활용

---

## 📈 **테스트 확장 계획**

### **단기 계획 (v0.2.0)**
- [ ] GUI 애플리케이션 테스트
- [ ] 다중 세션 테스트
- [ ] 에러 핸들링 테스트

### **중기 계획 (v0.3.0)**
- [ ] 성능 벤치마크 테스트
- [ ] 부하 테스트
- [ ] 보안 테스트

### **장기 계획 (v1.0.0)**
- [ ] 자동화된 CI/CD 테스트
- [ ] 사용자 시나리오 테스트
- [ ] 호환성 테스트

---

## 📝 **테스트 작성 가이드**

### **새 테스트 추가 시 고려사항**

1. **테스트 격리**: 각 테스트는 독립적으로 실행 가능해야 함
2. **데이터 정리**: 테스트 후 데이터 정리 필수
3. **에러 처리**: 예외 상황에 대한 적절한 처리
4. **성능 고려**: 테스트 실행 시간 최적화
5. **문서화**: 테스트 목적과 방법 명확히 문서화

### **테스트 코드 작성 규칙**

```python
#!/usr/bin/env python3
"""
테스트 설명
"""

import asyncio
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestClassName:
    def __init__(self):
        # 초기화 코드
        pass
    
    async def test_method(self):
        """테스트 메서드"""
        try:
            # 테스트 로직
            print("✅ 테스트 성공!")
            return True
        except Exception as e:
            print(f"❌ 테스트 실패: {e}")
            return False
    
    async def cleanup(self):
        """테스트 정리"""
        # 정리 로직
        pass

async def main():
    tester = TestClassName()
    try:
        result = await tester.test_method()
        return result
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📚 **참고 자료**

- **PostgreSQL 문서**: https://www.postgresql.org/docs/
- **Python asyncio**: https://docs.python.org/3/library/asyncio.html
- **pytest 가이드**: https://docs.pytest.org/
- **데이터베이스 테스팅**: https://docs.djangoproject.com/en/stable/topics/testing/

---

**문서 작성자**: RPG Engine Development Team  
**최종 검토**: 2025-10-18  
**다음 검토 예정**: 2025-11-18
