# [deprecated] 알려진 이슈 및 해결 방안

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 이유**: 이 문서의 대부분 이슈가 해결되어 더 이상 진행 중인 작업이 아님. 현재 발생하는 이슈는 별도로 추적되며, 더 최신 상태 정보는 readme.md와 최신 문서들을 참조해야 함.  
> **문서 버전**: v2.0
> **작성일**: 2025-10-18
> **최종 수정**: 2025-10-21

## 🚨 **현재 발생 중인 이슈들**

### **1. ✅ 해결됨: Entity Manager 업데이트 문제**
- **문제**: `EntityManager.update_entity()` 메서드 매개변수 순서 오류
- **해결 상태**: ✅ 완료 (2025-10-18)
- **해결 방법**: `update_entity_stats` 메서드에서 매개변수 순서 수정
- **영향**: Entity Manager 스탯 업데이트 기능 정상 작동

### **2. ✅ 해결됨: Entity Manager 삭제 문제**
- **문제**: `delete_entity` 메서드가 실제 삭제하지 않고 상태만 변경
- **해결 상태**: ✅ 완료 (2025-10-18)
- **해결 방법**: `_delete_entity_from_db` 메서드 구현으로 실제 DB 삭제
- **영향**: Entity Manager 삭제 기능 정상 작동

### **3. ✅ 해결됨: Cell Manager delete_cell 메서드 누락**
- **문제**: `CellManager`에 `delete_cell` 메서드가 없음
- **해결 상태**: ✅ 완료 (2025-10-21)
- **해결 방법**: `CellManager`에 `delete_cell` 메서드 구현 완료
- **영향**: 셀 관리 기능 정상 작동

### **4. 🔄 진행 중: 유니코드 이모지 인코딩 문제**
- **문제**: Windows 콘솔에서 유니코드 이모지 표시 오류
- **발생 위치**: 모든 시나리오 테스트 파일
- **원인**: Windows cp949 인코딩과 유니코드 이모지 호환성 문제
- **영향**: 로그 출력 오류, 테스트 실행에는 영향 없음
- **해결 방안**: 
  - 이모지 문자를 텍스트로 대체
  - 로깅 설정에서 인코딩 변경
  - 테스트 환경 설정 조정
- **진행 상황**: 시나리오 테스트 실행 중 (2025-10-18)

### **5. ⚠️ 미해결: Pydantic V2 경고**
- **문제**: "Pydantic V1 style `@validator` validators are deprecated"
- **발생 위치**: `app/effect_carrier/effect_carrier_manager.py` (라인 41, 47, 53)
- **원인**: Pydantic V1 스타일 validator 사용
- **영향**: 경고 발생, 기능에는 영향 없음
- **해결 방안**: 
  - `@validator` → `@field_validator`로 변경
  - Pydantic V2 마이그레이션 가이드 참조

### **6. ✅ 해결됨: Dialogue Manager 경고**
- **문제**: "coroutine 'DatabaseConnection.pool' was never awaited"
- **해결 상태**: ✅ 완료 (2025-10-21)
- **해결 방법**: 모든 DB 접근에서 `await` 키워드 사용으로 통일
- **영향**: 경고 제거, 대화 시스템 정상 작동 (275 dialogues/sec)

### **7. ✅ 해결됨: Action Handler DB 스키마 문제**
- **문제**: "session_id" 칼럼의 null 값이 not null 제약조건을 위반
- **해결 상태**: ✅ 완료 (2025-10-21)
- **해결 방법**: `_log_action` 메서드에서 session_id 필수 처리 및 자동 세션 생성 구현
- **영향**: 행동 로그 저장 성공, 액션 시스템 정상 작동

### **8. ✅ 해결됨: Effect Carrier Manager DB 스키마 문제**
- **문제**: "'str' object has no attribute 'value'"
- **해결 상태**: ✅ 완료 (2025-10-21)
- **해결 방법**: `hasattr(effect_carrier.carrier_type, 'value')` 체크로 안전한 Enum 처리 구현
- **영향**: Effect Carrier 생성 성공, 시스템 정상 작동

### **9. ✅ 해결됨: DialogueManager FAREWELL 토픽 오류**
- **문제**: `end_dialogue` 메서드에서 "FAREWELL" 토픽을 찾지 못함
- **해결 상태**: ✅ 완료 (2025-10-21)
- **해결 방법**: `end_dialogue` 메서드에서 "farewell" 토픽으로 변경
- **영향**: 대화 시스템 성능 테스트 성공 (275 dialogues/sec)

### **10. ✅ 해결됨: DB 정리 순서 문제 (ForeignKey 제약 조건)**
- **문제**: 테스트 teardown 시 ForeignKey 제약 조건으로 인한 DB 정리 실패
- **해결 상태**: ✅ 완료 (2025-10-21)
- **해결 방법**: 테스트 간 DB 상태 격리 개선 및 CASCADE 옵션 활용
- **영향**: 모든 테스트 정상 실행, DB 정리 성공

### **11. ⚠️ 미해결: Pydantic 모델 경고 (V2 마이그레이션)**
- **문제**: "Support for class-based `config` is deprecated, use ConfigDict instead"
- **발생 위치**: 모든 Pydantic 모델 파일
- **원인**: Pydantic V1 스타일 config 클래스 사용
- **영향**: 경고 발생, 기능에는 영향 없음
- **해결 방안**: 
  - 모든 Pydantic 모델의 `config` 클래스를 `ConfigDict`로 변경
  - Pydantic V2 마이그레이션 가이드 참조
  - 타입 힌트 및 검증 로직 업데이트

## 🔧 **해결 우선순위**

### **높은 우선순위 (즉시 해결 필요)**
1. **유니코드 이모지 인코딩 문제**: 로그 출력 오류, 사용자 경험 저하

### **현재 진행 상황 (2025-10-21)**
- **Phase 3 Village Simulation**: ✅ 완료 (100%)
  - 100일 시뮬레이션: ✅ 1.98초 실행
  - 총 대화: ✅ 228회 (목표 50회 초과)
  - 총 행동: ✅ 833회 (목표 100회 초과)
  - 시스템 안정성: ✅ 100% (오류 없이 완료)
- **Phase 2 성능 테스트**: ✅ 5/5 테스트 통과 (100%)
  - 대량 엔티티 생성: ✅ 1,226 entities/sec
  - 동시 세션 처리: ✅ 960 entities/sec
  - 셀 작업 성능: ✅ 413 cells/sec
  - 메모리 사용량: ✅ 1.0 MB (500개 엔티티)
  - 대화 시스템: ✅ 275 dialogues/sec
- **통합 테스트**: ✅ 10/10 통과
- **단위 테스트**: ✅ 52/52 통과

### **중간 우선순위 (기능에 영향 없음)**
- **모든 중간 우선순위 이슈 해결 완료** ✅

### **낮은 우선순위 (코드 현대화)**
1. **Pydantic V2 경고**: 코드 현대화
2. **Pydantic 모델 경고**: 코드 현대화

## 📋 **해결 계획**

### **✅ 완료된 Phase들**
- **Phase 1**: DialogueManager FAREWELL 토픽 오류 해결 ✅
- **Phase 2**: DB 정리 순서 문제 해결 ✅
- **Phase 3**: Cell Manager 완성 ✅
- **Phase 5**: DB 접근 패턴 통일 ✅
- **Phase 6**: Action Handler DB 스키마 문제 해결 ✅
- **Phase 7**: Effect Carrier Manager DB 스키마 문제 해결 ✅

### **🔄 진행 중인 Phase**
- **Phase 4**: 유니코드 문제 해결 (높은 우선순위)
  - 시나리오 테스트 파일에서 이모지 문자 제거
  - 로깅 설정에서 인코딩 변경
  - Windows 콘솔 호환성 개선
  - **진행 상황**: 시나리오 테스트 실행 중 (2025-10-18)

### **📋 예정된 Phase**
- **Phase 8**: Pydantic V2 마이그레이션 (낮은 우선순위)
  - Effect Carrier Manager의 validator 변경
  - 모든 Pydantic 모델의 메서드 변경
  - 타입 힌트 및 검증 로직 업데이트

## 🎯 **예상 결과**

### **✅ 달성된 효과**
- 통합 테스트 100% 통과 ✅
- 대부분의 경고 메시지 제거 ✅
- 시스템 안정성 및 성능 최적화 ✅
- Phase 3 Village Simulation 완료 ✅

### **📊 현재 테스트 커버리지**
- 단위 테스트: 100% 통과 ✅ (52/52)
- 통합 테스트: 100% 통과 ✅ (10/10)
- 시나리오 테스트: 100% 통과 ✅ (4/4)
- 성능 테스트: 100% 통과 ✅ (5/5)
- 100일 마을 시뮬레이션: 완료 ✅

### **현재 달성 상황 (2025-10-21)**
- **Phase 3 Village Simulation**: ✅ 완료 (100%)
  - 100일 시뮬레이션: ✅ 1.98초 실행
  - 총 대화: ✅ 228회 (목표 50회 초과)
  - 총 행동: ✅ 833회 (목표 100회 초과)
  - 시스템 안정성: ✅ 100% (오류 없이 완료)
- **Phase 2 성능 테스트**: ✅ 5/5 테스트 통과 (100%)
  - 대량 엔티티 생성: ✅ 1,226 entities/sec (목표 50 entities/sec 초과)
  - 동시 세션 처리: ✅ 960 entities/sec (목표 100 entities/sec 초과)
  - 셀 작업 성능: ✅ 413 cells/sec (목표 10 cells/sec 초과)
  - 메모리 사용량: ✅ 1.0 MB (목표 100 MB 이하)
  - 대화 시스템: ✅ 275 dialogues/sec (목표 10 dialogues/sec 초과)
- **통합 테스트**: ✅ 10/10 통과
- **단위 테스트**: ✅ 52/52 통과

## 📝 **참고 자료**

### **Pydantic V2 마이그레이션 가이드**
- https://errors.pydantic.dev/2.8/migration/
- `@validator` → `@field_validator`
- `.dict()` → `.model_dump()`

### **pytest-asyncio 설정**
- 이벤트 루프 격리 설정
- 테스트 간 의존성 제거
- 비동기 테스트 최적화

### **PostgreSQL asyncpg 패턴**
- `pool = await self.db.pool`
- `async with pool.acquire() as conn:`
- 트랜잭션 관리 최적화
