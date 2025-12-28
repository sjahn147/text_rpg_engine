# [deprecated] 데이터 일관성 이슈 분석

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: 이 문서에서 분석한 데이터 일관성 이슈들이 모두 해결되었습니다. 현재는 40개 테이블이 완성되고 모든 외래키 제약조건이 설정 완료되었습니다.

## 1. ID 타입 불일치 문제

### Game Data Layer
| 테이블 | 현재 ID 타입 | 관련 테이블 | 잠재적 문제 |
|--------|--------------|--------------|-------------|
| dialogue_contexts | VARCHAR(50) | dialogue_topics (FK) | dialogue_topics와 조인 시 타입 변환 오버헤드 |
| entities | VARCHAR(50) | entity_states (FK) | Runtime Layer와 조인 시 타입 변환 필요 |
| base_properties | INTEGER | abilities_magic, abilities_skills, equipment_weapons, equipment_armors, effects, inventory_items (FK) | 여러 테이블에서 참조되는 핵심 ID가 다른 테이블의 VARCHAR와 불일치 |
| regions | INTEGER | locations (FK) | World 관련 테이블 간 일관성 부족 |
| cells | INTEGER | dialogue_contexts (FK) | dialogue_contexts의 cell_id(VARCHAR)와 불일치 |

### Reference Layer & Runtime Data
| 테이블 | 현재 ID 타입 | 관련 테이블 | 잠재적 문제 |
|--------|--------------|--------------|-------------|
| entity_references | VARCHAR(50) | entities (FK) | Game Data Layer와 일치하나 다른 reference 테이블과 불일치 |
| cell_references | INTEGER | cells (FK) | cells 테이블과 일치하나 dialogue_contexts 참조 시 문제 |
| entity_states | VARCHAR(50) | entity_references (FK) | Runtime Layer 내 일관성은 유지되나 다른 레이어와 불일치 |

## 2. 인덱스 누락 문제

### 자주 조회되는 필드 인덱스 누락
| 테이블 | 누락된 인덱스 | 영향 |
|--------|---------------|------|
| entities | entity_type | NPC, 몬스터 타입별 조회 시 성능 저하 |
| base_properties | type | 장비, 능력, 아이템 타입별 조회 시 성능 저하 |
| cells | location_id | 특정 location의 모든 cell 조회 시 성능 저하 |
| equipment_weapons | weapon_type | 무기 타입별 조회 시 성능 저하 |
| equipment_armors | armor_type | 방어구 타입별 조회 시 성능 저하 |
| inventory_items | item_type | 아이템 타입별 조회 시 성능 저하 |

### 복합 인덱스 필요 테이블
| 테이블 | 필요한 복합 인덱스 | 사용 케이스 |
|--------|-------------------|-------------|
| entity_states | (entity_id, current_position) | 특정 위치의 엔티티 조회 |
| object_states | (object_id, current_state) | 특정 상태의 오브젝트 조회 |

## 3. 타임스탬프 불일치 문제

### 타임스탬프 필드 누락 테이블
| 테이블 | 누락된 필드 | 영향 |
|--------|-------------|------|
| entities | created_at, updated_at | 엔티티 생성/수정 시점 추적 불가 |
| regions | created_at, updated_at | 지역 데이터 변경 이력 추적 불가 |
| locations | created_at, updated_at | 장소 데이터 변경 이력 추적 불가 |
| cells | created_at, updated_at | 셀 데이터 변경 이력 추적 불가 |
| equipment_weapons | created_at, updated_at | 무기 데이터 변경 이력 추적 불가 |
| equipment_armors | created_at, updated_at | 방어구 데이터 변경 이력 추적 불가 |
| inventory_items | created_at, updated_at | 아이템 데이터 변경 이력 추적 불가 |

## 권장 해결 방안

1. **ID 타입 통일**
   - 모든 ID를 VARCHAR(50)으로 통일
   - UUID 사용 고려 (데이터 이전 및 병합 용이)

2. **인덱스 추가**
   - 누락된 단일 컬럼 인덱스 추가
   - 자주 사용되는 조회 패턴에 대한 복합 인덱스 추가

3. **타임스탬프 필드 추가**
   - 모든 테이블에 created_at, updated_at 필드 추가
   - DEFAULT CURRENT_TIMESTAMP 제약조건 추가 