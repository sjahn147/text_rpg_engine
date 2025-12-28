# 데이터베이스 마이그레이션 계획

> **작성일**: 2025-10-18  
> **목적**: 기존 스키마 리셋 및 새로운 MVP v2 스키마 적용  
> **버전 관리**: 스키마 버전 추적 및 롤백 지원

## 🎯 **마이그레이션 목표**

### **1. 스키마 버전 관리**
- 기존 스키마 백업 및 버전 기록
- 새로운 MVP v2 스키마 적용
- 롤백 가능한 마이그레이션 시스템

### **2. 데이터 무결성 보장**
- 외래키 제약조건 검증
- 데이터 정규화 검증
- 참조 무결성 테스트

### **3. 통합 테스트 연동**
- DB 스키마와 모듈 간 연동 테스트
- 단위/시나리오/통합 테스트 실행
- MVP 목표 달성 검증

## 📋 **마이그레이션 단계**

### **Phase 1: 기존 스키마 백업 및 리셋**

#### **1.1 현재 스키마 백업**
```sql
-- 현재 스키마 구조 백업
pg_dump -h localhost -p 5432 -U postgres -d rpg_engine --schema-only > backup/schema_v1_$(date +%Y%m%d_%H%M%S).sql

-- 현재 데이터 백업 (필요시)
pg_dump -h localhost -p 5432 -U postgres -d rpg_engine --data-only > backup/data_v1_$(date +%Y%m%d_%H%M%S).sql
```

#### **1.2 스키마 리셋**
```sql
-- 모든 스키마 삭제
DROP SCHEMA IF EXISTS game_data CASCADE;
DROP SCHEMA IF EXISTS reference_layer CASCADE;
DROP SCHEMA IF EXISTS runtime_data CASCADE;
DROP SCHEMA IF EXISTS simulation_data CASCADE;

-- 확장 프로그램 재설치
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

### **Phase 2: 새로운 스키마 적용**

#### **2.1 MVP v2 스키마 생성**
```bash
# 새로운 스키마 적용
psql -h localhost -p 5432 -U postgres -d rpg_engine -f database/mvp_schema.sql
```

#### **2.2 스키마 버전 기록**
```sql
-- 스키마 버전 테이블 생성
CREATE TABLE IF NOT EXISTS schema_versions (
    version_id SERIAL PRIMARY KEY,
    version_number VARCHAR(20) NOT NULL,
    description TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_by VARCHAR(100) DEFAULT 'system'
);

-- 현재 버전 기록
INSERT INTO schema_versions (version_number, description) 
VALUES ('v2.0.0', 'MVP v2 스키마 - 3계층 구조, 정규화 완료');
```

### **Phase 3: 데이터 무결성 검증**

#### **3.1 외래키 제약조건 검증**
```sql
-- 외래키 제약조건 확인
SELECT 
    tc.table_schema,
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_schema, tc.table_name;
```

#### **3.2 인덱스 검증**
```sql
-- 인덱스 상태 확인
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname IN ('game_data', 'reference_layer', 'runtime_data')
ORDER BY schemaname, tablename, indexname;
```

### **Phase 4: 테스트 데이터 삽입**

#### **4.1 기본 게임 데이터**
```sql
-- 지역 데이터
INSERT INTO game_data.world_regions (region_id, region_name, region_description, region_type, region_properties)
VALUES 
('REG_NORTH_FOREST_001', '북부 숲', '평화로운 숲 지역', 'forest', 
 '{"climate": "temperate", "danger_level": 2, "recommended_level": {"min": 1, "max": 10}}');

-- 위치 데이터
INSERT INTO game_data.world_locations (location_id, region_id, location_name, location_description, location_type, location_properties)
VALUES 
('LOC_FOREST_VILLAGE_001', 'REG_NORTH_FOREST_001', '숲의 마을', '숲 속의 평화로운 마을', 'village',
 '{"background_music": "peaceful_village", "ambient_effects": ["birds", "wind"]}');

-- 셀 데이터
INSERT INTO game_data.world_cells (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, cell_properties)
VALUES 
('CELL_VILLAGE_CENTER_001', 'LOC_FOREST_VILLAGE_001', '마을 광장', 20, 20, '마을의 중심 광장',
 '{"terrain": "stone", "weather": "clear"}');
```

#### **4.2 엔티티 템플릿**
```sql
-- 플레이어 템플릿
INSERT INTO game_data.entities (entity_id, entity_name, entity_type, entity_description, entity_properties)
VALUES 
('PLAYER_TEMPLATE_001', '플레이어', 'player', '기본 플레이어 템플릿',
 '{"level": 1, "gold": 100, "inventory": [], "equipped_items": []}');

-- NPC 템플릿
INSERT INTO game_data.entities (entity_id, entity_name, entity_type, entity_description, entity_properties)
VALUES 
('NPC_MERCHANT_001', '상인 토마스', 'npc', '무기 상점 주인',
 '{"gold": 1000, "shop_items": ["iron_sword", "steel_axe"], "personality": "friendly"}');
```

### **Phase 5: 통합 테스트 실행**

#### **5.1 단위 테스트**
```bash
# 데이터베이스 연결 테스트
python -m pytest tests/unit/test_database_connection.py -v

# Manager 클래스 테스트
python -m pytest tests/unit/test_entity_manager.py -v
python -m pytest tests/unit/test_cell_manager.py -v
python -m pytest tests/unit/test_game_manager.py -v
```

#### **5.2 시나리오 테스트**
```bash
# 게임 플로우 시나리오 테스트
python -m pytest tests/scenarios/test_basic_interaction_scenario.py -v
python -m pytest tests/scenarios/test_dialogue_scenario.py -v
```

#### **5.3 통합 테스트**
```bash
# 전체 시스템 통합 테스트
python -m pytest tests/integration/test_game_flow.py -v
python -m pytest tests/integration/test_village_simulation.py -v
```

## 🔧 **마이그레이션 스크립트**

### **자동화 스크립트 생성**
```python
# database/migrate_to_mvp_v2.py
import asyncio
import asyncpg
from pathlib import Path
import subprocess
from datetime import datetime

class DatabaseMigrator:
    def __init__(self):
        self.connection_config = {
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'password': '2696Sjbj!',
            'database': 'rpg_engine'
        }
    
    async def backup_current_schema(self):
        """현재 스키마 백업"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backup/schema_v1_{timestamp}.sql"
        
        cmd = [
            'pg_dump',
            '-h', self.connection_config['host'],
            '-p', str(self.connection_config['port']),
            '-U', self.connection_config['user'],
            '-d', self.connection_config['database'],
            '--schema-only',
            '-f', backup_file
        ]
        
        subprocess.run(cmd, check=True)
        print(f"✅ 스키마 백업 완료: {backup_file}")
    
    async def reset_schemas(self):
        """기존 스키마 리셋"""
        conn = await asyncpg.connect(**self.connection_config)
        
        try:
            # 모든 스키마 삭제
            await conn.execute("DROP SCHEMA IF EXISTS game_data CASCADE")
            await conn.execute("DROP SCHEMA IF EXISTS reference_layer CASCADE")
            await conn.execute("DROP SCHEMA IF EXISTS runtime_data CASCADE")
            await conn.execute("DROP SCHEMA IF EXISTS simulation_data CASCADE")
            
            print("✅ 기존 스키마 삭제 완료")
        finally:
            await conn.close()
    
    async def apply_new_schema(self):
        """새로운 스키마 적용"""
        schema_file = Path("database/mvp_schema.sql")
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn = await asyncpg.connect(**self.connection_config)
        
        try:
            await conn.execute(schema_sql)
            print("✅ 새로운 스키마 적용 완료")
        finally:
            await conn.close()
    
    async def run_migration(self):
        """전체 마이그레이션 실행"""
        print("🚀 MVP v2 스키마 마이그레이션 시작")
        
        # 1. 백업
        await self.backup_current_schema()
        
        # 2. 리셋
        await self.reset_schemas()
        
        # 3. 적용
        await self.apply_new_schema()
        
        print("✅ 마이그레이션 완료!")

if __name__ == "__main__":
    migrator = DatabaseMigrator()
    asyncio.run(migrator.run_migration())
```

## 📊 **검증 체크리스트**

### **스키마 검증**
- [ ] 모든 테이블 생성 확인
- [ ] 외래키 제약조건 확인
- [ ] 인덱스 생성 확인
- [ ] 스키마 버전 기록 확인

### **데이터 무결성 검증**
- [ ] 참조 무결성 테스트
- [ ] 데이터 정규화 검증
- [ ] 제약조건 동작 확인

### **통합 테스트 검증**
- [ ] 단위 테스트 통과
- [ ] 시나리오 테스트 통과
- [ ] 통합 테스트 통과
- [ ] MVP 목표 달성 확인

## 🚨 **롤백 계획**

### **롤백 시나리오**
```bash
# 1. 백업된 스키마 복원
psql -h localhost -p 5432 -U postgres -d rpg_engine -f backup/schema_v1_YYYYMMDD_HHMMSS.sql

# 2. 데이터 복원 (필요시)
psql -h localhost -p 5432 -U postgres -d rpg_engine -f backup/data_v1_YYYYMMDD_HHMMSS.sql
```

### **롤백 트리거 조건**
- 스키마 적용 실패
- 데이터 무결성 오류
- 통합 테스트 실패
- MVP 목표 달성 불가

**예상 소요 시간**: 2-3시간  
**위험도**: 중간 (백업 및 롤백 지원)  
**성공 기준**: 모든 테스트 통과 및 MVP 목표 달성
