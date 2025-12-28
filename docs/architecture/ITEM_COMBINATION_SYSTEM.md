# 아이템 조합 시스템 설계 문서

**작성일**: 2025-12-28  
**최종 수정**: 2025-12-28  
**목적**: Effect Carrier 기반 자유 조합 시스템 설계 및 구현 가이드

---

## 📋 목차

1. [시스템 개요](#시스템-개요)
2. [핵심 원칙](#핵심-원칙)
3. [데이터 구조](#데이터-구조)
4. [조합 로직](#조합-로직)
5. [Effect Carrier 동시 작용](#effect-carrier-동시-작용)
6. [아이템 생성 및 사용](#아이템-생성-및-사용)
7. [게임 기획 세부사항](#게임-기획-세부사항)
8. [UI/UX 고려사항](#uiux-고려사항)
9. [확장 가능성](#확장-가능성)
10. [구현 체크리스트](#구현-체크리스트)

---

## 시스템 개요

### 1.1 기본 개념

**아이템 조합 시스템**은 플레이어가 2개 이상의 아이템을 자유롭게 조합하여 새로운 아이템을 생성할 수 있는 시스템입니다.

- **모든 아이템 조합 가능**: 아이템 타입, Effect Carrier 유무와 관계없이 모든 아이템을 조합할 수 있습니다.
- **Effect Carrier 동시 작용**: 조합된 아이템은 입력 아이템들의 모든 Effect Carrier를 동시에 작용시킵니다.
- **성공/실패 시스템**: 조합 시도는 성공률에 따라 성공하거나 실패할 수 있으며, 실패 시 일부 재료만 소모됩니다.

### 1.2 예시 시나리오

```
시나리오 1: 부유풀 + 가속열매
- 부유풀: Effect Carrier "levitation" 보유
- 가속열매: Effect Carrier "speed_boost" 보유
- 조합 성공 → 새 아이템 생성 (두 Effect Carrier 모두 포함)
- 아이템 사용 시: "levitation" + "speed_boost" 동시 작용 → "빠르게 난다"

시나리오 2: 들풀 + 검
- 들풀: Effect Carrier 없음
- 검: Effect Carrier "sharpness" 보유
- 조합 시도 → 성공률 낮음 (호환성 낮음)
- 실패 시: 들풀만 소모, 검은 유지
- 성공 시: "sharpness" Effect Carrier만 가진 새 아이템 생성

시나리오 3: 5개 아이템 조합
- 입력: 아이템 A, B, C, D, E
- 개수 페널티 적용 → 성공률 감소
- 성공 시: 모든 Effect Carrier를 가진 새 아이템 생성
```

---

## 핵심 원칙

### 2.1 설계 원칙

1. **최소 복잡성**: Socket, 마법 아이템 구분 등 복잡한 개념 제거
2. **기존 구조 활용**: DB 마이그레이션 최소화, 기존 테이블 활용
3. **유연성**: 모든 아이템 조합 가능, Effect Carrier 유무와 무관
4. **확장 가능성**: 향후 정교한 크래프트 시스템으로 확장 가능한 구조

### 2.2 Effect Carrier 처리 원칙

- **새로운 Effect Carrier 객체 생성 안 함**: 기존 Effect Carrier ID를 참조만 함
- **동시 작용**: 조합된 아이템 사용 시 모든 Effect Carrier가 동시에 작용
- **선택적 보유**: 아이템은 Effect Carrier를 가질 수도 있고 없을 수도 있음 (NULL 허용)

---

## 데이터 구조

### 3.1 기존 테이블 활용

#### `game_data.items`

```sql
CREATE TABLE game_data.items (
    item_id VARCHAR(50) PRIMARY KEY,
    base_property_id VARCHAR(50) NOT NULL,
    item_type VARCHAR(50),
    stack_size INTEGER DEFAULT 1,
    consumable BOOLEAN DEFAULT false,
    effect_carrier_id UUID,  -- 단일 Effect Carrier (기존)
    item_properties JSONB,   -- 조합 정보 저장
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (effect_carrier_id) REFERENCES game_data.effect_carriers(effect_id) ON DELETE SET NULL
);
```

**`item_properties` JSONB 구조 (조합 아이템)**:

```json
{
    "combined_from": ["ITEM_HERB_001", "ITEM_BERRY_002"],  // 원본 아이템 ID 목록
    "effect_carrier_ids": [  // 여러 Effect Carrier ID (동시 작용)
        "550e8400-e29b-41d4-a716-446655440000",
        "660e8400-e29b-41d4-a716-446655440001"
    ],
    "base_name": "Combined Item",  // 기본 이름 (유저가 변경 가능)
    "custom_name": null,  // 유저가 지정한 이름 (선택적)
    "combination_date": "2025-12-28T10:30:00Z"  // 조합 일시
}
```

#### `game_data.effect_carriers`

```sql
CREATE TABLE game_data.effect_carriers (
    effect_id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    carrier_type VARCHAR(20) NOT NULL,
    effect_json JSONB NOT NULL,
    constraints_json JSONB DEFAULT '{}'::jsonb,
    tags TEXT[],
    ...
);
```

### 3.2 데이터 관계

```
game_data.items
├── effect_carrier_id (단일 Effect Carrier, Optional)
└── item_properties.effect_carrier_ids (여러 Effect Carrier, 조합 아이템용)

game_data.effect_carriers
└── effect_id (UUID, 참조 대상)
```

**중요**: 
- `effect_carrier_id`: 단일 Effect Carrier (기존 아이템)
- `item_properties.effect_carrier_ids`: 여러 Effect Carrier (조합 아이템)

---

## 조합 로직

### 4.1 조합 프로세스

```
1. 입력 아이템 수집
   ↓
2. 각 아이템의 Effect Carrier 수집
   ↓
3. 성공률 계산 (개수 페널티 적용)
   ↓
4. 성공/실패 판정
   ↓
5a. 성공 → 새 아이템 생성 (모든 Effect Carrier 포함)
5b. 실패 → 일부 재료만 소모
```

### 4.2 성공률 계산

#### 기본 공식

```python
base_success_rate = 0.5  # 기본 50%

# 개수 페널티
item_count = len(input_items)
penalty_per_item = 0.08  # 아이템당 8% 페널티
total_penalty = item_count * penalty_per_item

# Effect Carrier 보너스
carrier_count = len(effect_carriers)
bonus_per_carrier = 0.03  # Effect Carrier당 3% 보너스
total_bonus = carrier_count * bonus_per_carrier

# 최종 성공률
success_rate = base_success_rate - total_penalty + total_bonus
success_rate = max(0.1, min(0.9, success_rate))  # 10%~90% 범위
```

#### 성공률 테이블 (참고)

| 입력 아이템 개수 | Effect Carrier 개수 | 성공률 | 비고 |
|-----------------|-------------------|--------|------|
| 2개 | 0개 | 34% | 기본 - 페널티 |
| 2개 | 1개 | 37% | + 보너스 |
| 2개 | 2개 | 40% | + 보너스 |
| 3개 | 0개 | 26% | 페널티 증가 |
| 3개 | 2개 | 32% | 보너스로 완화 |
| 4개 | 0개 | 18% | 높은 페널티 |
| 4개 | 3개 | 27% | 보너스로 완화 |
| 5개 | 0개 | 10% | 최소 성공률 |
| 5개 | 4개 | 22% | 보너스로 완화 |

### 4.3 실패 처리

#### 실패 시 재료 소모 규칙

```python
def determine_consumed_items(input_items, effect_carriers):
    """
    실패 시 소모될 재료 결정
    
    규칙:
    1. Effect Carrier가 없는 아이템 우선 소모
    2. 가치가 낮은 아이템 우선 소모
    3. 최소 1개, 최대 입력 개수의 50% 소모
    """
    # Effect Carrier가 없는 아이템 우선
    items_without_carrier = [item for item in input_items 
                            if not has_effect_carrier(item)]
    
    if items_without_carrier:
        # Effect Carrier 없는 아이템 중 1개 랜덤 선택
        return [random.choice(items_without_carrier)]
    else:
        # 모두 Effect Carrier가 있으면 가치가 낮은 것 우선
        sorted_items = sort_by_value(input_items)
        consume_count = max(1, len(input_items) // 2)
        return sorted_items[:consume_count]
```

### 4.4 조합 제약사항

#### 최소/최대 개수

- **최소 개수**: 2개 (1개는 조합 불가)
- **최대 개수**: 5개 (초기값, 향후 조정 가능)

#### 제약 조건

```python
constraints = {
    "min_items": 2,
    "max_items": 5,
    "allow_same_item": True,  # 같은 아이템 중복 조합 가능
    "allow_equipment": True,  # 장비도 조합 가능 (소모됨)
    "require_workbench": False  # 향후 확장: 작업대 필요 여부
}
```

---

## Effect Carrier 동시 작용

### 5.1 동시 작용 원리

조합된 아이템 사용 시, `item_properties.effect_carrier_ids`에 저장된 모든 Effect Carrier를 엔티티에 부여합니다.

```python
async def use_combined_item(entity_id, item_id, session_id):
    """
    조합된 아이템 사용
    
    1. item_properties.effect_carrier_ids에서 모든 Effect Carrier ID 가져오기
    2. 각 Effect Carrier를 엔티티에 부여
    3. 동시에 작용 (Effect Carrier Manager가 처리)
    """
    item_template = await get_item_template(item_id)
    effect_carrier_ids = item_template.get('item_properties', {}).get(
        'effect_carrier_ids', []
    )
    
    # 모든 Effect Carrier를 엔티티에 부여
    for effect_id in effect_carrier_ids:
        await effect_carrier_manager.grant_effect_to_entity(
            session_id=session_id,
            entity_id=entity_id,
            effect_id=effect_id,
            source=f"combined_item:{item_id}"
        )
```

### 5.2 Effect Carrier 충돌 처리

Effect Carrier 간 충돌이 발생할 수 있습니다 (예: "strength_boost" + "weakness").

**현재 단계**: 충돌 감지만 하고, Effect Carrier Manager의 기본 동작에 맡김

**향후 확장**: `constraints_json.conflicts_with`를 활용한 충돌 해결 로직

---

## 아이템 생성 및 사용

### 6.1 조합된 아이템 생성

```python
async def create_combined_item(input_items, item_carriers):
    """
    조합된 아이템 생성
    
    Args:
        input_items: 입력 아이템 ID 목록
        item_carriers: Effect Carrier 정보 목록
    
    Returns:
        새로 생성된 아이템 ID
    """
    # 1. 기본 이름 생성
    base_name = "Combined Item"
    
    # 2. Effect Carrier ID 수집
    effect_carrier_ids = [ic["carrier"].effect_id for ic in item_carriers]
    
    # 3. 첫 번째 아이템의 속성 상속
    first_item = await get_item_template(input_items[0])
    item_type = first_item.get('item_type', 'consumable')
    stack_size = first_item.get('stack_size', 1)
    consumable = first_item.get('consumable', True)
    
    # 4. 새 아이템 ID 생성
    new_item_id = f"ITEM_COMBINED_{generate_short_uuid()}"
    
    # 5. 아이템 템플릿 생성
    await create_item_template(
        item_id=new_item_id,
        item_name=base_name,  # 기본 이름 (유저가 변경 가능)
        item_type=item_type,
        stack_size=stack_size,
        consumable=consumable,
        effect_carrier_id=None,  # 단일 Effect Carrier 없음
        item_properties={
            "combined_from": input_items,
            "effect_carrier_ids": effect_carrier_ids,
            "base_name": base_name,
            "custom_name": None,  # 유저가 지정한 이름
            "combination_date": datetime.now().isoformat()
        }
    )
    
    return new_item_id
```

### 6.2 아이템 이름 변경

```python
async def rename_combined_item(item_id, custom_name):
    """
    조합된 아이템 이름 변경 (유저 커스터마이징)
    
    Args:
        item_id: 아이템 ID
        custom_name: 유저가 지정한 이름
    """
    item_template = await get_item_template(item_id)
    item_properties = item_template.get('item_properties', {})
    
    # custom_name 업데이트
    item_properties['custom_name'] = custom_name
    
    # 아이템 이름도 업데이트 (표시용)
    await update_item_template(
        item_id=item_id,
        item_name=custom_name or item_properties.get('base_name', 'Combined Item'),
        item_properties=item_properties
    )
```

### 6.3 아이템 사용

```python
async def use_combined_item(entity_id, item_id, session_id):
    """
    조합된 아이템 사용
    
    1. item_properties.effect_carrier_ids 확인
    2. 모든 Effect Carrier를 엔티티에 부여
    3. 소비 가능 아이템이면 인벤토리에서 제거
    """
    item_template = await get_item_template(item_id)
    effect_carrier_ids = item_template.get('item_properties', {}).get(
        'effect_carrier_ids', []
    )
    
    # 모든 Effect Carrier 부여
    for effect_id in effect_carrier_ids:
        await effect_carrier_manager.grant_effect_to_entity(
            session_id=session_id,
            entity_id=entity_id,
            effect_id=effect_id,
            source=f"combined_item:{item_id}"
        )
    
    # 소비 처리
    if item_template.get('consumable', True):
        await inventory_manager.remove_item_from_inventory(
            entity_id,
            item_id,
            quantity=1
        )
```

---

## 게임 기획 세부사항

### 7.1 조합 정책

#### 7.1.1 개수 페널티

- **2개 조합**: 기본 성공률 50%, 페널티 16% → **34%**
- **3개 조합**: 기본 성공률 50%, 페널티 24% → **26%**
- **4개 조합**: 기본 성공률 50%, 페널티 32% → **18%**
- **5개 조합**: 기본 성공률 50%, 페널티 40% → **10%** (최소)

**설계 의도**: 아이템이 많을수록 조합이 어려워지도록 하여 밸런싱

#### 7.1.2 Effect Carrier 보너스

- **Effect Carrier 1개**: +3% 보너스
- **Effect Carrier 2개**: +6% 보너스
- **Effect Carrier 3개**: +9% 보너스
- **Effect Carrier 4개**: +12% 보너스

**설계 의도**: Effect Carrier가 있는 아이템 조합을 장려

#### 7.1.3 실패 시 재료 소모

- **최소 소모**: 1개
- **최대 소모**: 입력 개수의 50%
- **우선순위**: Effect Carrier 없는 아이템 > 가치 낮은 아이템

**설계 의도**: 실패해도 큰 손실을 방지, Effect Carrier 있는 아이템 보호

### 7.2 아이템 속성 상속

조합된 아이템은 첫 번째 입력 아이템의 속성을 상속합니다:

- `item_type`: 첫 번째 아이템의 타입
- `stack_size`: 첫 번째 아이템의 스택 크기
- `consumable`: 첫 번째 아이템의 소비 가능 여부

**예외**: `effect_carrier_id`는 상속하지 않음 (대신 `item_properties.effect_carrier_ids` 사용)

### 7.3 아이템 이름 정책

- **기본 이름**: "Combined Item"
- **유저 커스터마이징**: 유저가 직접 이름 변경 가능
- **표시 우선순위**: `custom_name` > `base_name` > "Combined Item"

### 7.4 조합 가능 아이템 범위

- ✅ **일반 아이템**: 조합 가능
- ✅ **소비품**: 조합 가능 (소모됨)
- ✅ **장비**: 조합 가능 (소모됨)
- ✅ **재료**: 조합 가능
- ✅ **같은 아이템 중복**: 조합 가능 (예: 풀 + 풀 + 풀)

---

## UI/UX 고려사항

### 8.1 조합 UI

#### 필수 요소

1. **아이템 선택 슬롯**: 2~5개 아이템 선택
2. **성공률 표시**: 실시간 성공률 계산 및 표시
3. **Effect Carrier 미리보기**: 조합 시 포함될 Effect Carrier 목록
4. **확인 다이얼로그**: 조합 시도 전 확인

#### 선택 요소

1. **이름 입력 필드**: 조합 성공 시 이름 지정
2. **재료 소모 예상**: 실패 시 소모될 재료 미리보기
3. **조합 히스토리**: 이전 조합 기록

### 8.2 조합 결과 표시

#### 성공 시

- 새 아이템 생성 알림
- Effect Carrier 목록 표시
- 이름 변경 옵션 제공

#### 실패 시

- 실패 메시지
- 소모된 재료 표시
- 재시도 옵션

### 8.3 아이템 표시

조합된 아이템은 특별한 표시가 필요합니다:

- **아이콘**: 조합 아이템 전용 아이콘 또는 배지
- **툴팁**: "Combined Item" 표시, 원본 아이템 목록
- **이름**: 유저가 지정한 이름 또는 기본 이름

---

## 확장 가능성

### 9.1 Phase 2: 정교한 크래프트 시스템

#### 스킬 기반 성공률

```python
# 향후 확장
skill_level = get_crafting_skill_level(entity_id)
skill_bonus = skill_level * 0.02  # 스킬 레벨당 2% 보너스
success_rate += skill_bonus
```

#### 원소 상성 시스템

```python
# 향후 확장
elemental_affinity = calculate_elemental_affinity(item_carriers)
if elemental_affinity > 0:
    success_rate += elemental_affinity * 0.1
```

#### 품질 시스템

```python
# 향후 확장
quality = calculate_quality(input_items, skill_level)
result_item_properties['quality'] = quality
```

### 9.2 Phase 3: 고급 기능

- **작업대 필요**: 특정 조합은 작업대 오브젝트 필요
- **레시피 시스템**: 성공한 조합을 레시피로 저장
- **조합 트리**: 조합 가능한 아이템 트리 표시
- **실험 모드**: 재료 소모 없이 조합 시뮬레이션

---

## 구현 체크리스트

### 10.1 데이터 구조

- [ ] `item_properties.effect_carrier_ids` 배열 지원 확인
- [ ] 조합된 아이템 저장 로직 구현
- [ ] 아이템 이름 변경 기능 구현

### 10.2 조합 로직

- [ ] 입력 아이템 수집 로직
- [ ] Effect Carrier 수집 로직
- [ ] 성공률 계산 로직 (개수 페널티 적용)
- [ ] 실패 시 재료 소모 결정 로직
- [ ] 조합된 아이템 생성 로직

### 10.3 Effect Carrier 동시 작용

- [ ] `item_properties.effect_carrier_ids`에서 Effect Carrier ID 추출
- [ ] 모든 Effect Carrier를 엔티티에 부여하는 로직
- [ ] 아이템 사용 시 Effect Carrier 적용 로직

### 10.4 API 엔드포인트

- [ ] `POST /api/gameplay/combine` - 아이템 조합
- [ ] `POST /api/gameplay/rename-item` - 아이템 이름 변경
- [ ] `GET /api/gameplay/combination-preview` - 조합 미리보기 (성공률, Effect Carrier)

### 10.5 프론트엔드

- [ ] 조합 UI 구현
- [ ] 아이템 선택 슬롯 (2~5개)
- [ ] 성공률 표시
- [ ] Effect Carrier 미리보기
- [ ] 이름 입력 필드
- [ ] 조합 결과 표시

### 10.6 테스트

- [ ] 단위 테스트: 성공률 계산
- [ ] 단위 테스트: Effect Carrier 수집
- [ ] 단위 테스트: 조합된 아이템 생성
- [ ] 통합 테스트: 조합 프로세스 전체
- [ ] 통합 테스트: Effect Carrier 동시 작용

---

## 참고 사항

### 11.1 성능 고려사항

- **Effect Carrier 조회**: 조합 시 여러 Effect Carrier를 조회하므로 캐싱 고려
- **아이템 템플릿 조회**: 입력 아이템 템플릿 조회 최적화
- **조합 히스토리**: 대량 조합 시 히스토리 저장 최적화

### 11.2 보안 고려사항

- **아이템 ID 검증**: 조합 시도 전 입력 아이템 ID 검증
- **인벤토리 소유권 확인**: 조합 시도 전 아이템 소유권 확인
- **Effect Carrier 접근 권한**: Effect Carrier 조회 권한 확인

### 11.3 밸런싱 고려사항

- **성공률 조정**: 게임 테스트 후 성공률 조정 필요
- **재료 소모 비율**: 실패 시 재료 소모 비율 조정 가능
- **최대 조합 개수**: 게임 밸런스에 따라 5개에서 조정 가능

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2025-12-28 | 1.0 | 초기 문서 작성 |

---

## 관련 문서

- [OBJECT_INTERACTION_COMPLETE_GUIDE.md](./OBJECT_INTERACTION_COMPLETE_GUIDE.md)
- [ITEM_EQUIPMENT_EFFECT_CARRIER_ARCHITECTURE_PROPOSAL.md](./ITEM_EQUIPMENT_EFFECT_CARRIER_ARCHITECTURE_PROPOSAL.md)
- [ACTION_HANDLER_REFACTORING_PLAN.md](./ACTION_HANDLER_REFACTORING_PLAN.md)

