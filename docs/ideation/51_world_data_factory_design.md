# World Data Factory 설계

> **최신화 날짜**: 2025-12-28  
> **현재 상태**: WorldDataFactory 구현 완료, 계층적 세계 데이터 생성 지원

## Factory 패턴 적용 여부

### ✅ Factory 패턴에 부합합니다

**Factory 패턴의 목적:**
- 복잡한 객체 생성 로직을 캡슐화
- 생성 과정의 복잡성을 숨기고 단순한 인터페이스 제공
- 생성 로직의 변경이 사용자 코드에 영향을 주지 않도록 분리

**현재 코드베이스의 Factory 사용:**
1. **`GameDataFactory`** - 정적 게임 데이터 템플릿 생성 (`game_data` 스키마)
   - `create_npc_template()`, `create_world_region()`, `create_world_location()` 등
   - 개발 단계에서 사용하는 정적 데이터 생성

2. **`InstanceFactory`** - 런타임 인스턴스 생성 (`runtime_data` 스키마)
   - `create_npc_instance()`, `create_cell_instance()` 등
   - 게임 실행 중 동적으로 생성되는 인스턴스

### 결론

**정적 객체를 입력하는 개발 단계용 Factory는 Factory 패턴에 완벽히 부합합니다.**

- Factory는 "동적 런타임 객체"만을 위한 것이 아닙니다
- 복잡한 생성 로직을 캡슐화하는 것이 목적이므로, 정적 데이터 생성에도 적합합니다
- 현재 `GameDataFactory`가 이미 정적 데이터 생성에 사용되고 있습니다

## World Data Factory 설계

### 목적

`world_design.md` 파일의 설정 자료를 받아서:
- Region 단위로 하위 Location, Cell, Character 등을 일괄 생성
- 계층적 구조를 자동으로 처리
- ID 생성 규칙 자동 적용 (`REG_`, `LOC_`, `CELL_`, `NPC_` 등)

### 구조

```
WorldDataFactory (GameDataFactory 확장)
├─ create_region_with_children() - Region + 하위 엔티티 일괄 생성
│   ├─ create_region() - Region 생성
│   ├─ create_locations() - Location들 생성 (region_id 연결)
│   ├─ create_cells() - Cell들 생성 (location_id 연결)
│   ├─ create_characters() - Character들 생성 (cell_id 연결)
│   └─ create_world_objects() - World Object들 생성 (cell_id 연결)
│
├─ parse_world_design() - world_design.md 파싱
└─ validate_hierarchy() - 계층 구조 검증
```

### 설정 자료 구조 (world_design.md 기반)

```python
region_config = {
    "region_id": "REG_아발룸_안브레티아_01",
    "region_name": "안브레티아",
    "region_type": "empire",
    "description": "...",
    "properties": {...},
    
    "locations": [
        {
            "location_id": "LOC_안브레티아_헬라로스_01",
            "location_name": "헬라로스",
            "description": "...",
            "properties": {...},
            
            "cells": [
                {
                    "cell_id": "CELL_항구_부두_01",
                    "cell_name": "부두",
                    "description": "...",
                    "properties": {...},
                    
                    "characters": [
                        {
                            "entity_id": "NPC_선장_토마스_01",
                            "entity_name": "토마스 선장",
                            "base_stats": {...},
                            "entity_properties": {...}
                        }
                    ],
                    
                    "world_objects": [
                        {
                            "object_id": "...",
                            "object_type": "chest",
                            "properties": {...}
                        }
                    ]
                }
            ]
        }
    ]
}
```

### 구현 방향

#### 옵션 1: GameDataFactory 확장 (권장)
- `GameDataFactory`를 상속하여 `WorldDataFactory` 생성
- 기존 메서드 재사용
- Region 단위 일괄 생성 메서드 추가

#### 옵션 2: 독립적인 Factory
- `WorldDataFactory`를 별도로 생성
- `GameDataFactory`의 메서드를 내부적으로 호출
- 더 명확한 책임 분리

### ID 생성 규칙

```python
# Region: REG_[대륙]_[지역]_[일련번호]
"REG_마케나_안브레티아_01"

# Location: LOC_[지역]_[장소]_[일련번호]
"LOC_안브레티아_헬라로스_01"

# Cell: CELL_[위치타입]_[세부위치]_[일련번호]
"CELL_항구_부두_01"

# NPC: NPC_[이름]_[일련번호]
"NPC_선장_토마스_01"
```

### 트랜잭션 처리

Region 단위로 모든 하위 엔티티를 하나의 트랜잭션으로 처리:
- Region 생성 실패 시 전체 롤백
- Location 생성 실패 시 Region과 함께 롤백
- 부분 실패 방지

### 다음 단계

1. `world_design.md` 파일 구조 분석
2. 파싱 로직 설계
3. `WorldDataFactory` 구현
4. 테스트 케이스 작성

