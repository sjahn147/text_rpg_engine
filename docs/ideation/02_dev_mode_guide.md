# Dev Mode 사용자 가이드

> **문서 버전**: v1.0  
> **작성일**: 2025-10-18  
> **최종 수정**: 2025-10-18

## 🛠️ **Dev Mode 개요**

Dev Mode(창세 대시보드)는 RPG Engine의 핵심 기능으로, 플레이 중 떠오른 아이디어를 즉시 데이터화하고 Game Data로 승격할 수 있는 통합 개발 환경입니다.

### **핵심 철학**
> **"플레이 = 자료 수집, DevMode = 사료 편찬. 학예사겸 신."**

- **즉시 데이터화**: 플레이 중 아이디어를 바로 데이터로 변환
- **검증 시스템**: 데이터 품질 보장 및 일관성 유지
- **Game Data 승격**: Runtime에서 검증된 내용을 공식 데이터로 편입
- **버전 관리**: 모든 변경사항의 추적 및 롤백 가능

---

## 🎮 **Dev Mode 활성화**

### **Dev Mode 접근**

#### **1. Dev Mode 활성화**
```python
# Dev Mode 활성화
dev_mode = await DevModeManager.activate(session_id=session_id)

# 권한 확인
if not await dev_mode.check_permission(user_id, "dev_mode", "activate"):
    raise PermissionError("Dev Mode 권한이 없습니다.")
```

#### **2. Dev Mode UI 접근**
```python
# Dev Mode UI 열기
dev_mode_ui = DevModeUI(session_id=session_id)
await dev_mode_ui.show()

# Dev Mode 상태 확인
if dev_mode_ui.is_active():
    print("Dev Mode가 활성화되었습니다.")
```

### **Dev Mode 인터페이스**

#### **메인 대시보드**
```
┌─────────────────────────────────────────────────────────────┐
│                    🛠️ Dev Mode Dashboard                    │
├─────────────────────────────────────────────────────────────┤
│ 📊 현재 세션: session_001                                   │
│ 👤 플레이어: player_001                                     │
│ 🌍 현재 위치: Forest Village → Village Square              │
│ ⏰ 세션 시간: 2시간 30분                                    │
├─────────────────────────────────────────────────────────────┤
│ 🎯 빠른 작업                                                │
│ [새 NPC 생성] [새 아이템 생성] [새 지역 생성] [승격 대기]    │
├─────────────────────────────────────────────────────────────┤
│ 📋 최근 활동                                                │
│ • 14:30 - NPC "상인 토마스" 생성                            │
│ • 14:25 - 아이템 "마법 검" 승격                            │
│ • 14:20 - 지역 "숲의 신전" 편집                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ **Game Data 편집**

### **Region 편집**

#### **새 Region 생성**
```python
# Region 생성
region = await dev_mode.create_region(
    region_name="Northern Mountains",
    region_type="mountain",
    region_description="눈 덮인 북부 산맥",
    properties={
        "climate": "cold",
        "danger_level": 4,
        "recommended_level": {"min": 15, "max": 25}
    }
)

# Region 편집
await dev_mode.edit_region(
    region_id="REG_NORTH_MOUNTAIN_001",
    changes={
        "region_description": "눈 덮인 북부 산맥 (수정됨)",
        "properties": {
            "climate": "cold",
            "danger_level": 5,  # 위험도 증가
            "recommended_level": {"min": 20, "max": 30}
        }
    }
)
```

#### **Region UI**
```
┌─────────────────────────────────────────────────────────────┐
│                    🏔️ Region Editor                         │
├─────────────────────────────────────────────────────────────┤
│ 이름: Northern Mountains                                    │
│ 타입: mountain                                              │
│ 설명: 눈 덮인 북부 산맥                                    │
│                                                             │
│ 속성:                                                       │
│ • 기후: cold                                                │
│ • 위험도: 4                                                 │
│ • 권장 레벨: 15-25                                          │
│                                                             │
│ [저장] [미리보기] [취소]                                    │
└─────────────────────────────────────────────────────────────┘
```

### **Location 편집**

#### **새 Location 생성**
```python
# Location 생성
location = await dev_mode.create_location(
    region_id="REG_NORTH_MOUNTAIN_001",
    location_name="Mountain Temple",
    location_type="temple",
    location_description="고대 신전",
    properties={
        "background_music": "temple_theme",
        "ambient_effects": ["wind", "echo"]
    }
)

# Location 편집
await dev_mode.edit_location(
    location_id="LOC_MOUNTAIN_TEMPLE_001",
    changes={
        "location_description": "고대 신전 (수정됨)",
        "properties": {
            "background_music": "temple_theme",
            "ambient_effects": ["wind", "echo", "mystical"]
        }
    }
)
```

### **Cell 편집**

#### **새 Cell 생성**
```python
# Cell 생성
cell = await dev_mode.create_cell(
    location_id="LOC_MOUNTAIN_TEMPLE_001",
    cell_name="Temple Altar",
    matrix_width=15,
    matrix_height=15,
    cell_description="신전의 제단",
    properties={
        "terrain": "stone",
        "lighting": "dim",
        "atmosphere": "sacred"
    }
)

# Cell 편집
await dev_mode.edit_cell(
    cell_id="CELL_TEMPLE_ALTAR_001",
    changes={
        "cell_description": "신전의 제단 (수정됨)",
        "properties": {
            "terrain": "stone",
            "lighting": "bright",  # 조명 개선
            "atmosphere": "sacred"
        }
    }
)
```

### **Entity 편집**

#### **새 NPC 생성**
```python
# NPC 생성
npc = await dev_mode.create_entity(
    entity_name="Temple Priest",
    entity_type="npc",
    base_properties={
        "strength": 8,
        "intelligence": 15,
        "wisdom": 18,
        "charisma": 12
    },
    abilities=["heal", "bless", "divine_protection"],
    dialogue_contexts=["temple_greeting", "divine_guidance"],
    properties={
        "personality": "wise_and_gentle",
        "faction": "temple_order",
        "knowledge": ["ancient_lore", "divine_mysteries"]
    }
)

# NPC 편집
await dev_mode.edit_entity(
    entity_id="ENTITY_TEMPLE_PRIEST_001",
    changes={
        "base_properties": {
            "strength": 8,
            "intelligence": 16,  # 지능 증가
            "wisdom": 18,
            "charisma": 12
        },
        "properties": {
            "personality": "wise_and_gentle",
            "faction": "temple_order",
            "knowledge": ["ancient_lore", "divine_mysteries", "healing_arts"]
        }
    }
)
```

### **Effect Carrier 편집**

#### **새 Effect Carrier 생성**
```python
# Effect Carrier 생성
effect = await dev_mode.create_effect_carrier(
    name="Divine Blessing",
    carrier_type="blessing",
    effect_json={
        "stat_modifier": {
            "strength": 3,
            "wisdom": 2
        },
        "duration": 3600,
        "divine_source": "temple_priest"
    },
    constraints_json={
        "requires_faith": 50,
        "conflicts_with": ["curse"]
    },
    tags=["divine", "temporary", "stat_boost"]
)

# Effect Carrier 편집
await dev_mode.edit_effect_carrier(
    effect_id="EFFECT_DIVINE_BLESSING_001",
    changes={
        "effect_json": {
            "stat_modifier": {
                "strength": 4,  # 효과 증가
                "wisdom": 3
            },
            "duration": 3600,
            "divine_source": "temple_priest"
        }
    }
)
```

---

## 🚀 **Runtime → Game Data 승격**

### **승격 시스템**

#### **승격 대기 목록**
```python
# 승격 대기 항목 조회
pending_promotions = await dev_mode.get_pending_promotions()

# 승격 항목 예시
promotion_item = {
    "runtime_id": "RUNTIME_NPC_001",
    "target_table": "entities",
    "data": {
        "entity_name": "상인 토마스",
        "entity_type": "npc",
        "base_properties": {...},
        "dialogue_contexts": [...]
    },
    "created_at": "2025-10-18 14:30:00",
    "reason": "플레이어가 상호작용한 NPC",
    "validation_status": "pending"
}
```

#### **승격 실행**
```python
# 승격 실행
promotion_result = await dev_mode.promote_to_game_data(
    runtime_id="RUNTIME_NPC_001",
    target_table="entities",
    reason="플레이어가 상호작용한 NPC",
    validation_required=True
)

# 승격 결과
if promotion_result["success"]:
    print(f"승격 완료: {promotion_result['game_data_id']}")
else:
    print(f"승격 실패: {promotion_result['error']}")
```

### **승격 UI**
```
┌─────────────────────────────────────────────────────────────┐
│                    🚀 Promotion Queue                        │
├─────────────────────────────────────────────────────────────┤
│ 📋 대기 중인 승격 (3개)                                      │
│                                                             │
│ 1. 상인 토마스 (NPC)                                        │
│    생성일: 2025-10-18 14:30                                │
│    사유: 플레이어가 상호작용한 NPC                          │
│    [승격] [거부] [미리보기]                                 │
│                                                             │
│ 2. 마법 검 (아이템)                                         │
│    생성일: 2025-10-18 14:25                                │
│    사유: 플레이어가 획득한 아이템                          │
│    [승격] [거부] [미리보기]                                 │
│                                                             │
│ 3. 숲의 신전 (지역)                                         │
│    생성일: 2025-10-18 14:20                                │
│    사유: 플레이어가 발견한 지역                              │
│    [승격] [거부] [미리보기]                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 **미리보기 시스템**

### **미리보기 생성**

#### **대화 미리보기**
```python
# 대화 미리보기 생성
dialogue_preview = await dev_mode.generate_preview(
    content_type="dialogue",
    context={
        "npc_personality": "friendly_merchant",
        "dialogue_topic": "shop_items",
        "player_level": 5
    },
    constraints={
        "max_length": 200,
        "tone": "friendly",
        "style": "medieval"
    }
)

# 미리보기 결과
preview_result = {
    "content": "안녕하세요! 오늘은 어떤 물건을 찾고 계신가요?",
    "confidence": 0.85,
    "constraints_met": True,
    "generated_at": "2025-10-18 14:35:00"
}
```

#### **묘사 미리보기**
```python
# 묘사 미리보기 생성
description_preview = await dev_mode.generate_preview(
    content_type="description",
    context={
        "location_type": "temple",
        "atmosphere": "sacred",
        "lighting": "dim"
    },
    constraints={
        "max_length": 150,
        "style": "descriptive",
        "mood": "mysterious"
    }
)

# 미리보기 결과
preview_result = {
    "content": "고대 신전의 제단이 어둠 속에서 은은하게 빛나고 있습니다.",
    "confidence": 0.92,
    "constraints_met": True,
    "generated_at": "2025-10-18 14:35:00"
}
```

### **미리보기 UI**
```
┌─────────────────────────────────────────────────────────────┐
│                    🔍 Preview Generator                      │
├─────────────────────────────────────────────────────────────┤
│ 콘텐츠 타입: [대화 ▼]                                      │
│                                                             │
│ 컨텍스트:                                                   │
│ • NPC 성격: friendly_merchant                              │
│ • 대화 주제: shop_items                                     │
│ • 플레이어 레벨: 5                                          │
│                                                             │
│ 제약 조건:                                                  │
│ • 최대 길이: 200                                            │
│ • 톤: friendly                                              │
│ • 스타일: medieval                                          │
│                                                             │
│ [미리보기 생성]                                             │
│                                                             │
│ 생성된 내용:                                                │
│ "안녕하세요! 오늘은 어떤 물건을 찾고 계신가요?"             │
│                                                             │
│ 신뢰도: 85% | 제약 조건 충족: ✅                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 **버전/감사 시스템**

### **버전 관리**

#### **버전 히스토리**
```python
# 버전 히스토리 조회
version_history = await dev_mode.get_version_history(
    entity_id="ENTITY_TEMPLE_PRIEST_001",
    limit=10
)

# 버전 정보
version_info = {
    "version_id": "v1.2.0",
    "editor": "user_001",
    "created_at": "2025-10-18 14:30:00",
    "reason": "지능 수치 증가",
    "changes": {
        "base_properties": {
            "intelligence": {"old": 15, "new": 16}
        }
    },
    "diff": "+1 intelligence"
}
```

#### **롤백**
```python
# 특정 버전으로 롤백
rollback_result = await dev_mode.rollback_to_version(
    entity_id="ENTITY_TEMPLE_PRIEST_001",
    version_id="v1.1.0",
    reason="이전 버전이 더 적합함"
)

# 롤백 결과
if rollback_result["success"]:
    print("롤백 완료")
else:
    print(f"롤백 실패: {rollback_result['error']}")
```

### **감사 로그**

#### **감사 로그 조회**
```python
# 감사 로그 조회
audit_log = await dev_mode.get_audit_log(
    entity_id="ENTITY_TEMPLE_PRIEST_001",
    action="edit",
    limit=20
)

# 감사 로그 항목
audit_entry = {
    "log_id": "AUDIT_001",
    "entity_id": "ENTITY_TEMPLE_PRIEST_001",
    "action": "edit",
    "editor": "user_001",
    "timestamp": "2025-10-18 14:30:00",
    "changes": {
        "base_properties": {
            "intelligence": {"old": 15, "new": 16}
        }
    },
    "reason": "지능 수치 증가",
    "ip_address": "192.168.1.100"
}
```

### **감사 로그 UI**
```
┌─────────────────────────────────────────────────────────────┐
│                    📊 Audit Log                             │
├─────────────────────────────────────────────────────────────┤
│ 🔍 필터: [엔티티: Temple Priest] [액션: 편집] [기간: 7일]   │
│                                                             │
│ 📋 최근 활동 (20개)                                         │
│                                                             │
│ 2025-10-18 14:30:00 | user_001 | 편집                      │
│ • 지능: 15 → 16                                             │
│ • 사유: 지능 수치 증가                                       │
│                                                             │
│ 2025-10-18 14:25:00 | user_001 | 생성                      │
│ • 새 NPC 생성: Temple Priest                                │
│ • 사유: 플레이어 요청                                        │
│                                                             │
│ 2025-10-18 14:20:00 | user_001 | 승격                      │
│ • Runtime → Game Data                                       │
│ • 사유: 승격 요청                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 **권한 관리**

### **RBAC (Role-Based Access Control)**

#### **권한 확인**
```python
# 권한 확인
can_edit = await dev_mode.check_permission(
    user_id="user_001",
    action="edit",
    resource="game_data"
)

can_promote = await dev_mode.check_promote_permission(
    user_id="user_001",
    target_table="entities"
)

# 권한 결과
if can_edit:
    print("편집 권한 있음")
else:
    print("편집 권한 없음")
```

#### **권한 설정**
```python
# 권한 설정
await dev_mode.set_permission(
    user_id="user_001",
    role="developer",
    permissions={
        "edit": ["game_data", "runtime_data"],
        "promote": ["entities", "items", "locations"],
        "audit": ["read", "export"]
    }
)
```

### **권한 UI**
```
┌─────────────────────────────────────────────────────────────┐
│                    🔐 Permission Management                  │
├─────────────────────────────────────────────────────────────┤
│ 👤 사용자: user_001                                         │
│ 🎭 역할: developer                                          │
│                                                             │
│ 📋 권한 목록:                                               │
│                                                             │
│ ✅ 편집 권한                                                │
│   • game_data                                               │
│   • runtime_data                                            │
│                                                             │
│ ✅ 승격 권한                                                │
│   • entities                                                │
│   • items                                                   │
│   • locations                                               │
│                                                             │
│ ✅ 감사 권한                                                │
│   • read                                                    │
│   • export                                                  │
│                                                             │
│ [권한 수정] [역할 변경] [권한 내보내기]                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 **테스트 및 검증**

### **Dev Mode 테스트**

#### **기능 테스트**
```python
class DevModeTest:
    def __init__(self):
        self.test_results = []
    
    async def test_dev_mode_activation(self):
        """Dev Mode 활성화 테스트"""
        
        # Dev Mode 활성화
        dev_mode = await DevModeManager.activate(session_id="test_session")
        assert dev_mode is not None
        
        # 권한 확인
        has_permission = await dev_mode.check_permission("test_user", "dev_mode", "activate")
        assert has_permission == True
        
        return True
    
    async def test_game_data_editing(self):
        """Game Data 편집 테스트"""
        
        # Region 생성
        region = await dev_mode.create_region(
            region_name="Test Region",
            region_type="forest",
            region_description="테스트 지역"
        )
        assert region["region_name"] == "Test Region"
        
        # Region 편집
        edited_region = await dev_mode.edit_region(
            region_id=region["region_id"],
            changes={"region_description": "수정된 테스트 지역"}
        )
        assert edited_region["region_description"] == "수정된 테스트 지역"
        
        return True
    
    async def test_promote_functionality(self):
        """승격 기능 테스트"""
        
        # Runtime 데이터 생성
        runtime_data = await dev_mode.create_runtime_data(
            data_type="npc",
            data={"name": "Test NPC", "type": "merchant"}
        )
        
        # 승격 실행
        promotion_result = await dev_mode.promote_to_game_data(
            runtime_id=runtime_data["runtime_id"],
            target_table="entities",
            reason="테스트 승격"
        )
        
        assert promotion_result["success"] == True
        assert promotion_result["game_data_id"] is not None
        
        return True
```

---

## 📋 **사용 체크리스트**

### **Dev Mode 활성화**
- [ ] Dev Mode 권한 확인
- [ ] 세션 연결 확인
- [ ] UI 접근 가능

### **Game Data 편집**
- [ ] Region 생성/편집
- [ ] Location 생성/편집
- [ ] Cell 생성/편집
- [ ] Entity 생성/편집
- [ ] Effect Carrier 생성/편집

### **승격 시스템**
- [ ] 승격 대기 목록 확인
- [ ] 승격 실행
- [ ] 승격 결과 확인

### **미리보기 시스템**
- [ ] 대화 미리보기 생성
- [ ] 묘사 미리보기 생성
- [ ] 제약 조건 확인

### **버전/감사**
- [ ] 버전 히스토리 확인
- [ ] 롤백 실행
- [ ] 감사 로그 확인

---

## 🚀 **다음 단계**

1. **Dev Mode UI 구현**: PyQt5 기반 Dev Mode 인터페이스
2. **권한 시스템 구현**: RBAC 기반 권한 관리
3. **승격 시스템 구현**: Runtime → Game Data 승격 로직
4. **미리보기 시스템 구현**: LLM 기반 미리보기 생성
5. **버전 관리 시스템**: Git 기반 버전 관리

---

**문서 작성자**: RPG Engine Development Team  
**최종 검토**: 2025-10-18  
**다음 검토 예정**: 2025-11-18
