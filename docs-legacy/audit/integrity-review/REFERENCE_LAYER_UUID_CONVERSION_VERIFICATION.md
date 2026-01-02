# 레퍼런스 레이어 UUID 변환 검증

## 검증 결과

### ✅ 올바르게 구현된 부분

#### 1. `interact_with_object` (gameplay.py:590-722)
- **위치**: `app/ui/backend/routes/gameplay.py`
- **로직**:
  1. `cell_contents`에서 `request.object_id`와 일치하는 오브젝트 찾기 (UUID 또는 `game_object_id` 모두 지원)
  2. `target_object['game_object_id']`를 사용하여 레퍼런스 레이어에서 UUID 조회
  3. 레퍼런스 레이어에 없으면 새 UUID 생성 및 등록
  4. `runtime_data.runtime_objects`에도 생성
- **상태**: ✅ 올바름

#### 2. `pickup_from_object` (gameplay.py:1086-1432)
- **위치**: `app/ui/backend/routes/gameplay.py`
- **로직**:
  1. `cell_contents`에서 `request.object_id`와 일치하는 오브젝트 찾기 (UUID 또는 `game_object_id` 모두 지원)
  2. `target_object['game_object_id']`를 사용하여 레퍼런스 레이어에서 UUID 조회
  3. 레퍼런스 레이어에 없으면 새 UUID 생성 및 등록
  4. `runtime_data.runtime_objects`에도 생성
- **상태**: ✅ 올바름

#### 3. `CellManager._load_cell_content_from_db` (cell_manager.py:608-682)
- **위치**: `app/managers/cell_manager.py`
- **로직**:
  1. `game_data.world_objects`에서 셀의 오브젝트 조회
  2. 각 `game_object_id`에 대해 레퍼런스 레이어에서 UUID 조회
  3. 레퍼런스 레이어에 없으면 새 UUID 생성 및 등록
  4. `runtime_data.runtime_objects`에도 생성
  5. 결과에 `runtime_object_id`와 `game_object_id` 둘 다 포함
- **상태**: ✅ 올바름

## 데이터 흐름

```
1. Frontend → Backend
   request.object_id (UUID 또는 game_object_id)

2. Backend: cell_contents 조회
   - CellManager.get_cell_contents() 호출
   - 레퍼런스 레이어를 통해 모든 오브젝트의 UUID 확보
   - 결과: [{runtime_object_id: UUID, game_object_id: VARCHAR, ...}, ...]

3. Backend: target_object 찾기
   - cell_contents에서 request.object_id와 일치하는 오브젝트 찾기
   - runtime_object_id 또는 game_object_id 모두 비교

4. Backend: 레퍼런스 레이어 조회
   - target_object['game_object_id'] 사용
   - reference_layer.object_references에서 UUID 조회
   - 없으면 새 UUID 생성 및 등록

5. Backend: 런타임 데이터 조회/수정
   - runtime_object_id (UUID) 사용
   - runtime_data.object_states 조회/수정
```

## 검증 포인트

### ✅ 모든 엔드포인트에서 레퍼런스 레이어 사용
- `interact_with_object`: ✅
- `pickup_from_object`: ✅
- `CellManager.get_cell_contents`: ✅

### ✅ UUID 생성 및 등록
- 레퍼런스 레이어에 없을 때 새 UUID 생성: ✅
- `reference_layer.object_references`에 등록: ✅
- `runtime_data.runtime_objects`에도 생성: ✅

### ✅ 일관된 데이터 구조
- `cell_contents`의 오브젝트는 항상 `runtime_object_id` (UUID) 포함: ✅
- `game_object_id`도 함께 포함하여 역방향 조회 가능: ✅

## 결론

**모든 코드가 레퍼런스 레이어를 통해 올바르게 UUID 변환을 수행하고 있습니다.**

- ✅ `game_object_id` (VARCHAR) → `runtime_object_id` (UUID) 변환
- ✅ 레퍼런스 레이어를 통한 일관된 변환
- ✅ 런타임 데이터는 항상 UUID 사용
- ✅ 정적 데이터는 변경하지 않음

