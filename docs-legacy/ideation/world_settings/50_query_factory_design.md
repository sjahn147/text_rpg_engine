# Query Factory 설계

> **최신화 날짜**: 2025-12-28  
> **현재 상태**: Query Factory 패턴 적용, GameDataFactory, InstanceFactory, WorldDataFactory 구현 완료

## 개요

설정 자료(Configuration Data)를 받아서 데이터베이스 쿼리로 자동 변환하는 Factory 시스템을 설계합니다.

## 현재 Factory 구조

### 위치
- `database/factories/game_data_factory.py` - 게임 데이터 템플릿 생성
- `database/factories/instance_factory.py` - 런타임 인스턴스 생성

### 현재 방식
- 각 메서드마다 하드코딩된 SQL 쿼리
- 설정 데이터를 받아서 직접 `conn.execute()` 호출
- 타입별 특수 로직이 메서드 내부에 포함

### 문제점
- 새로운 엔티티 타입 추가 시 코드 수정 필요
- 쿼리 생성 로직이 분산되어 있음
- 설정 데이터 구조 변경 시 여러 곳 수정 필요

## 제안: Query Factory 시스템

### 목적
설정 자료를 받아서 자동으로 SQL 쿼리를 생성하고 실행하는 범용 Factory

### 구조

```
QueryFactory (기본 Factory)
├─ build_insert_query() - INSERT 쿼리 생성
├─ build_update_query() - UPDATE 쿼리 생성
├─ build_select_query() - SELECT 쿼리 생성
└─ execute_query() - 쿼리 실행

EntityQueryFactory (Entity 전용)
├─ create_entity() - Entity 생성
└─ update_entity() - Entity 업데이트

WorldObjectQueryFactory (World Object 전용)
├─ create_world_object() - World Object 생성
└─ update_world_object() - World Object 업데이트
```

### 설정 자료 구조 예시

```python
# 설정 자료 예시
entity_config = {
    "table": "game_data.entities",
    "entity_id": "NPC_MERCHANT_001",
    "entity_type": "npc",
    "entity_name": "상인 토마스",
    "base_stats": {"hp": 100, "mp": 50},
    "entity_properties": {
        "template_type": "merchant",
        "shop_inventory": []
    }
}

# QueryFactory가 자동으로 변환
# INSERT INTO game_data.entities (entity_id, entity_type, entity_name, base_stats, entity_properties)
# VALUES ($1, $2, $3, $4, $5)
```

## 설계 방향

### 옵션 1: 범용 Query Builder
- 테이블 스키마 정보를 받아서 자동으로 쿼리 생성
- JSONB 필드 자동 처리
- 타입 변환 자동 처리

### 옵션 2: 엔티티별 특화 Factory
- 각 엔티티 타입별 Factory 클래스
- 공통 로직은 BaseFactory에서 상속
- 타입별 특수 로직은 각 Factory에서 구현

### 옵션 3: 하이브리드
- 범용 Query Builder + 엔티티별 Factory
- 기본 CRUD는 Query Builder로 자동 생성
- 복잡한 로직은 Factory에서 처리

## 다음 단계

사용자가 제공할 설정 자료 구조를 확인한 후 구체적인 설계 진행

