# 월드 에디터 설계 문서

> **문서 번호**: 25  
> **작성일**: 2025-12-27  
> **버전**: 1.0.0  
> **목적**: D&D 타운 스타일의 월드 에디터 설계 및 구현 계획

---

## 📋 목차

1. [개요](#개요)
2. [요구사항](#요구사항)
3. [아키텍처 설계](#아키텍처-설계)
4. [데이터 구조](#데이터-구조)
5. [프론트엔드 설계](#프론트엔드-설계)
6. [백엔드 API 설계](#백엔드-api-설계)
7. [UI 컴포넌트 설계](#ui-컴포넌트-설계)
8. [데이터베이스 호환성](#데이터베이스-호환성)
9. [구현 단계](#구현-단계)

---

## 개요

### 목표

D&D 타운 스타일의 시각적 월드 에디터를 구축하여 게임 개발자가 직관적으로 월드를 생성하고 편집할 수 있도록 합니다.

### 핵심 기능

- **지도 기반 편집**: 캔버스에 지도를 그리고 핀으로 지역 표시
- **D&D 스타일 정보 입력**: 각 지역에 상세 정보를 필드 입력으로 쉽게 추가
- **도로 연결 시스템**: 지역 간 도로를 시각적으로 그려 연결
- **실시간 동기화**: 편집 내용이 즉시 데이터베이스에 반영
- **기존 데이터 호환**: 현재 3-Layer 스키마와 완전 호환

### 기술 스택

- **프론트엔드**: Tauri + React (참조: `_3_frontend_backend_design.md`)
- **렌더링**: Canvas API + Konva.js (2D 그래픽 라이브러리)
- **백엔드**: FastAPI (Python) - 포트 8001 사용 (기존 서버 8000과 분리)
- **데이터베이스**: PostgreSQL (기존 스키마 활용)
- **통신**: WebSocket (실시간 동기화) + HTTP REST API
- **지도 에셋**: `assets/world_editor/worldmap.png` (기본 지도 이미지)

---

## 요구사항

### 기능 요구사항

#### 1. 지도 편집
- [ ] 캔버스에 지도 이미지 업로드 및 배치
- [ ] 지도 확대/축소/이동 (Pan & Zoom)
- [ ] 그리드 표시 옵션
- [ ] 지도 배경색/이미지 설정

#### 2. 핀 시스템
- [ ] 지역 핀 추가/삭제/이동
- [ ] 핀 타입별 아이콘 (도시, 마을, 던전, 상점 등)
- [ ] 핀 클릭 시 상세 정보 패널 표시
- [ ] 핀 드래그 앤 드롭으로 위치 변경

#### 3. D&D 스타일 정보 입력
- [ ] 지역 기본 정보 (이름, 설명, 타입)
- [ ] 지역 특성 (기후, 위험도, 추천 레벨)
- [ ] NPC 목록 및 관계
- [ ] 퀘스트/이벤트 정보
- [ ] 상점/시설 정보
- [ ] 로어/역사 정보

#### 4. 도로 연결 시스템
- [ ] 두 지역 간 도로 그리기
- [ ] 도로 타입 설정 (일반 도로, 숨겨진 길, 강 등)
- [ ] 도로 거리/이동 시간 설정
- [ ] 도로 위험도/조건 설정
- [ ] 도로 삭제/수정

#### 5. 데이터 관리
- [ ] 실시간 DB 동기화
- [ ] 변경사항 미리보기
- [ ] 되돌리기/다시하기 (Undo/Redo)
- [ ] 내보내기/가져오기 (Export/Import)

### 비기능 요구사항

- **성능**: 60fps 유지, 1000개 이상 핀 지원
- **반응성**: 모든 UI 상호작용 < 100ms
- **확장성**: 새로운 핀 타입/도로 타입 쉽게 추가
- **호환성**: 기존 DB 스키마 100% 호환

---

## 아키텍처 설계

### 계층 구조

```
┌─────────────────────────────────────────┐
│      Presentation Layer (Tauri + React) │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │  Map      │  │  Info    │  │  Road  ││
│  │  Canvas   │  │  Panel   │  │  Tool  ││
│  └──────────┘  └──────────┘  └────────┘│
├─────────────────────────────────────────┤
│      Application Layer (React State)    │
│  ┌──────────────────────────┐        │
│  │  World Editor State        │        │
│  │  - Map State               │        │
│  │  - Pin State               │        │
│  │  - Road State              │        │
│  └──────────────────────────┘        │
├─────────────────────────────────────────┤
│      Service Layer (FastAPI)           │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │  Region  │  │ Location │  │  Cell  ││
│  │  Service │  │  Service │  │ Service││
│  └──────────┘  └──────────┘  └────────┘│
├─────────────────────────────────────────┤
│      Data Layer (PostgreSQL)           │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │  Region  │  │ Location │  │  Cell  ││
│  │  Data    │  │   Data   │  │  Data  ││
│  └──────────┘  └──────────┘  └────────┘│
└─────────────────────────────────────────┘
```

### 데이터 흐름

```
User Action → React State → FastAPI → PostgreSQL
                ↓
         WebSocket → Real-time Sync
                ↓
         Other Clients Update
```

### 포트 구성

- **월드 에디터 백엔드**: 포트 8001 사용 (FastAPI)
- **기존 서버**: 포트 8000 유지
- **WebSocket**: ws://localhost:8001/ws
- **참고**: 기존 서버와 충돌하지 않도록 별도 포트 사용

### 에셋 디렉토리 구조

```
rpg_engine/
├── assets/
│   └── world_editor/
│       ├── worldmap.png          # 기본 지도 이미지 ✅ 배치 완료
│       └── README.md             # 에셋 디렉토리 설명
├── app/
│   └── world_editor/             # 월드 에디터 모듈 (구현 예정)
└── ...
```

**지도 이미지 사용 방법**:
- React/Konva 컴포넌트에서: `import worldmapImage from '../../assets/world_editor/worldmap.png'`
- 또는 상대 경로: `/assets/world_editor/worldmap.png`
- Tauri 환경에서는 `@tauri-apps/api/path`를 사용하여 리소스 경로 접근

---

## 데이터 구조

### 1. 지도 메타데이터

```typescript
interface MapMetadata {
  map_id: string;
  map_name: string;
  background_image?: string;  // 지도 배경 이미지 경로 (기본: assets/world_editor/worldmap.png)
  background_color: string;   // 지도 배경색
  width: number;              // 지도 너비 (픽셀)
  height: number;             // 지도 높이 (픽셀)
  grid_enabled: boolean;      // 그리드 표시 여부
  grid_size: number;          // 그리드 크기
  zoom_level: number;         // 현재 확대/축소 레벨
  viewport_x: number;         // 뷰포트 X 좌표
  viewport_y: number;         // 뷰포트 Y 좌표
  created_at: string;
  updated_at: string;
}
```

**기본 지도 이미지**: `assets/world_editor/worldmap.png` ✅ 배치 완료
- 프로젝트 루트의 `worldmap.png`를 `assets/world_editor/` 디렉토리로 이동 완료
- 월드 에디터에서 기본 배경 이미지로 사용
- 지도 이미지 로드 시 상대 경로 또는 절대 경로로 접근 가능
- 지도 특징:
  - 판타지 스타일 월드맵 (에오스트레아 산맥, 니베르두를 해, 마왕성 임구 등)
  - 지역, 도시, 산맥, 바다 등이 표시된 상세 지도
  - 그리드 오버레이 지원
  - 핀 배치 및 도로 그리기 작업의 기준

### 2. 핀 데이터 (Region/Location)

```typescript
interface PinData {
  pin_id: string;
  pin_type: 'region' | 'location' | 'cell';
  
  // 화면 좌표 (픽셀)
  x: number;
  y: number;
  
  // 게임 데이터 ID
  game_data_id: string;  // region_id, location_id, cell_id
  
  // 핀 시각적 속성
  icon_type: string;      // 'city', 'village', 'dungeon', 'shop', etc.
  color: string;         // 핀 색상
  size: number;          // 핀 크기
  
  // 연결된 데이터
  region_data?: RegionData;
  location_data?: LocationData;
  cell_data?: CellData;
}
```

### 3. 도로 데이터

```typescript
interface RoadData {
  road_id: string;
  from_pin_id: string;    // 시작 핀 ID
  to_pin_id: string;     // 종료 핀 ID
  
  // 경로 좌표 (베지어 곡선 지원)
  path: Array<{x: number, y: number}>;
  
  // 도로 속성
  road_type: 'normal' | 'hidden' | 'river' | 'mountain_pass';
  distance: number;      // 거리 (킬로미터 또는 게임 단위)
  travel_time: number;   // 이동 시간 (분)
  danger_level: number;  // 위험도 (1-10)
  
  // 조건
  conditions?: Array<{
    type: 'flag' | 'variable' | 'level';
    target: string;
    operator: string;
    value: any;
  }>;
  
  // 시각적 속성
  color: string;
  width: number;
  dashed: boolean;
}
```

### 4. D&D 스타일 정보 구조

```typescript
interface LocationInfo {
  // 기본 정보
  name: string;
  description: string;
  type: string;
  
  // D&D 스타일 정보
  demographics: {
    population: number;
    races: Record<string, number>;  // 종족별 인구
    classes: Record<string, number>; // 직업별 분포
  };
  
  economy: {
    primary_industry: string;
    trade_goods: string[];
    gold_value: number;
  };
  
  government: {
    type: string;  // 'democracy', 'monarchy', 'theocracy', etc.
    leader: string;
    laws: string[];
  };
  
  culture: {
    religion: string[];
    customs: string[];
    festivals: string[];
  };
  
  // 게임 데이터 연결
  npcs: Array<{
    npc_id: string;
    name: string;
    role: string;
    location: string;
  }>;
  
  quests: Array<{
    quest_id: string;
    name: string;
    type: string;
    status: string;
  }>;
  
  shops: Array<{
    shop_id: string;
    name: string;
    type: string;
    items: string[];
  }>;
  
  // 로어
  lore: {
    history: string;
    legends: string[];
    secrets: string[];
  };
}
```

### 5. 데이터베이스 매핑

#### Region → Pin
```sql
-- game_data.world_regions 테이블과 매핑
-- pin_data.game_data_id = world_regions.region_id
-- pin_data.x, pin_data.y는 지도 좌표
-- world_regions.region_properties에 D&D 정보 저장
```

#### Location → Pin
```sql
-- game_data.world_locations 테이블과 매핑
-- pin_data.game_data_id = world_locations.location_id
-- world_locations.location_properties에 D&D 정보 저장
```

#### Road → 새로운 테이블
```sql
-- 도로 정보를 저장할 새 테이블 필요
CREATE TABLE game_data.world_roads (
    road_id VARCHAR(50) PRIMARY KEY,
    from_region_id VARCHAR(50),
    from_location_id VARCHAR(50),
    to_region_id VARCHAR(50),
    to_location_id VARCHAR(50),
    road_type VARCHAR(50),
    distance DECIMAL(10, 2),
    travel_time INTEGER,
    danger_level INTEGER,
    road_properties JSONB,
    path_coordinates JSONB,  -- 경로 좌표 배열
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_region_id) REFERENCES game_data.world_regions(region_id),
    FOREIGN KEY (to_region_id) REFERENCES game_data.world_regions(region_id),
    FOREIGN KEY (from_location_id) REFERENCES game_data.world_locations(location_id),
    FOREIGN KEY (to_location_id) REFERENCES game_data.world_locations(location_id)
);
```

---

## 프론트엔드 설계

### 1. 메인 레이아웃

```
┌─────────────────────────────────────────────────────────┐
│  Title Bar: World Editor - [Map Name]                   │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│  Toolbar     │         Map Canvas                       │
│  ┌────────┐  │  ┌──────────────────────────────────┐  │
│  │ Select │  │  │                                  │  │
│  │  Pin   │  │  │        [지도 영역]                │  │
│  │  Road  │  │  │                                  │  │
│  │  Zoom  │  │  │    [핀들]  [도로들]              │  │
│  └────────┘  │  │                                  │  │
│              │  └──────────────────────────────────┘  │
│  Info Panel  │                                          │
│  ┌────────┐  │                                          │
│  │ [선택된│  │                                          │
│  │  핀/도로│  │                                          │
│  │  정보] │  │                                          │
│  │        │  │                                          │
│  │ [D&D   │  │                                          │
│  │  정보] │  │                                          │
│  └────────┘  │                                          │
└──────────────┴──────────────────────────────────────────┘
```

### 2. 컴포넌트 구조 (React)

```typescript
// src/ui/world-editor/components/WorldEditor.tsx
import React from 'react';
import { MapCanvas } from './MapCanvas';
import { Toolbar } from './Toolbar';
import { InfoPanel } from './InfoPanel';
import { useWorldEditorState } from '../hooks/useWorldEditorState';

export const WorldEditor: React.FC = () => {
  const {
    mapState,
    pins,
    roads,
    selectedPin,
    selectedRoad,
    updatePin,
    updateRoad,
    addPin,
    addRoad,
    deletePin,
    deleteRoad
  } = useWorldEditorState();

  return (
    <div className="world-editor">
      <Toolbar />
      <div className="editor-content">
        <MapCanvas
          mapState={mapState}
          pins={pins}
          roads={roads}
          selectedPin={selectedPin}
          selectedRoad={selectedRoad}
          onPinClick={(pinId) => selectPin(pinId)}
          onPinDrag={(pinId, x, y) => updatePinPosition(pinId, x, y)}
          onRoadDraw={(fromPinId, toPinId, path) => addRoad(fromPinId, toPinId, path)}
        />
        <InfoPanel
          selectedPin={selectedPin}
          selectedRoad={selectedRoad}
          onUpdate={(data) => updateEntity(data)}
        />
      </div>
    </div>
  );
};
```

### 3. MapCanvas 컴포넌트 (Konva.js)

```typescript
// src/ui/world-editor/components/MapCanvas.tsx
import React, { useRef, useEffect } from 'react';
import { Stage, Layer, Image, Circle, Line, Transformer } from 'react-konva';
import Konva from 'konva';
import useImage from 'use-image';

interface MapCanvasProps {
  mapState: MapMetadata;
  pins: PinData[];
  roads: RoadData[];
  selectedPin?: string;
  selectedRoad?: string;
  onPinClick: (pinId: string) => void;
  onPinDrag: (pinId: string, x: number, y: number) => void;
  onRoadDraw: (fromPinId: string, toPinId: string, path: Array<{x: number, y: number}>) => void;
}

export const MapCanvas: React.FC<MapCanvasProps> = ({
  mapState,
  pins,
  roads,
  selectedPin,
  selectedRoad,
  onPinClick,
  onPinDrag,
  onRoadDraw
}) => {
  const stageRef = useRef<Konva.Stage>(null);
  const [backgroundImage] = useImage(mapState.background_image || '');

  // Pan & Zoom 구현
  const handleWheel = (e: Konva.KonvaEventObject<WheelEvent>) => {
    e.evt.preventDefault();
    const stage = stageRef.current;
    if (!stage) return;

    const oldScale = stage.scaleX();
    const pointer = stage.getPointerPosition();
    if (!pointer) return;

    const mousePointTo = {
      x: (pointer.x - stage.x()) / oldScale,
      y: (pointer.y - stage.y()) / oldScale,
    };

    const newScale = e.evt.deltaY > 0 ? oldScale * 0.95 : oldScale * 1.05;
    const clampedScale = Math.max(0.1, Math.min(5, newScale));

    stage.scale({ x: clampedScale, y: clampedScale });

    const newPos = {
      x: pointer.x - mousePointTo.x * clampedScale,
      y: pointer.y - mousePointTo.y * clampedScale,
    };

    stage.position(newPos);
  };

  return (
    <Stage
      ref={stageRef}
      width={window.innerWidth - 300}
      height={window.innerHeight - 100}
      onWheel={handleWheel}
      draggable
    >
      <Layer>
        {/* 배경 이미지 - 기본 지도 이미지 또는 사용자 지정 이미지 */}
        <MapBackgroundLayer
          backgroundPath={mapState.background_image}
          defaultMapPath="/assets/world_editor/worldmap.png"
          width={mapState.width}
          height={mapState.height}
        />

        {/* 그리드 */}
        {mapState.grid_enabled && (
          <GridLayer
            width={mapState.width}
            height={mapState.height}
            gridSize={mapState.grid_size}
          />
        )}

        {/* 도로 렌더링 */}
        {roads.map(road => (
          <RoadLine
            key={road.road_id}
            road={road}
            pins={pins}
            selected={selectedRoad === road.road_id}
            onClick={() => onRoadClick(road.road_id)}
          />
        ))}

        {/* 핀 렌더링 */}
        {pins.map(pin => (
          <PinMarker
            key={pin.pin_id}
            pin={pin}
            selected={selectedPin === pin.pin_id}
            onClick={() => onPinClick(pin.pin_id)}
            onDragEnd={(e) => {
              const node = e.target;
              onPinDrag(pin.pin_id, node.x(), node.y());
            }}
          />
        ))}
      </Layer>
    </Stage>
  );
};
```

### 4. InfoPanel 컴포넌트 (D&D 스타일 정보 입력)

```typescript
// src/ui/world-editor/components/InfoPanel.tsx
import React, { useState } from 'react';
import { DnDInfoForm } from './DnDInfoForm';

interface InfoPanelProps {
  selectedPin?: PinData;
  selectedRoad?: RoadData;
  onUpdate: (data: any) => void;
}

export const InfoPanel: React.FC<InfoPanelProps> = ({
  selectedPin,
  selectedRoad,
  onUpdate
}) => {
  if (!selectedPin && !selectedRoad) {
    return (
      <div className="info-panel">
        <p>핀이나 도로를 선택하세요</p>
      </div>
    );
  }

  if (selectedPin) {
    return (
      <div className="info-panel">
        <h3>{selectedPin.region_data?.name || selectedPin.location_data?.name}</h3>
        <DnDInfoForm
          pinData={selectedPin}
          onUpdate={(data) => onUpdate({ pinId: selectedPin.pin_id, ...data })}
        />
      </div>
    );
  }

  if (selectedRoad) {
    return (
      <div className="info-panel">
        <h3>도로 정보</h3>
        <RoadInfoForm
          roadData={selectedRoad}
          onUpdate={(data) => onUpdate({ roadId: selectedRoad.road_id, ...data })}
        />
      </div>
    );
  }

  return null;
};
```

### 5. DnDInfoForm 컴포넌트

```typescript
// src/ui/world-editor/components/DnDInfoForm.tsx
import React, { useState } from 'react';

interface DnDInfoFormProps {
  pinData: PinData;
  onUpdate: (data: LocationInfo) => void;
}

export const DnDInfoForm: React.FC<DnDInfoFormProps> = ({ pinData, onUpdate }) => {
  const [formData, setFormData] = useState<LocationInfo>({
    name: pinData.region_data?.region_name || pinData.location_data?.location_name || '',
    description: '',
    type: '',
    demographics: {
      population: 0,
      races: {},
      classes: {}
    },
    economy: {
      primary_industry: '',
      trade_goods: [],
      gold_value: 0
    },
    government: {
      type: '',
      leader: '',
      laws: []
    },
    culture: {
      religion: [],
      customs: [],
      festivals: []
    },
    npcs: [],
    quests: [],
    shops: [],
    lore: {
      history: '',
      legends: [],
      secrets: []
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onUpdate(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="dnd-info-form">
      {/* 기본 정보 섹션 */}
      <section className="form-section">
        <h4>기본 정보</h4>
        <label>
          이름:
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
        </label>
        <label>
          설명:
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={4}
          />
        </label>
      </section>

      {/* 인구 통계 섹션 */}
      <section className="form-section">
        <h4>인구 통계</h4>
        <label>
          총 인구:
          <input
            type="number"
            value={formData.demographics.population}
            onChange={(e) => setFormData({
              ...formData,
              demographics: {
                ...formData.demographics,
                population: parseInt(e.target.value)
              }
            })}
          />
        </label>
        {/* 종족별 인구 입력 필드들 */}
      </section>

      {/* 경제 섹션 */}
      <section className="form-section">
        <h4>경제</h4>
        <label>
          주요 산업:
          <input
            type="text"
            value={formData.economy.primary_industry}
            onChange={(e) => setFormData({
              ...formData,
              economy: {
                ...formData.economy,
                primary_industry: e.target.value
              }
            })}
          />
        </label>
        {/* 기타 경제 필드들 */}
      </section>

      {/* 정부 섹션 */}
      <section className="form-section">
        <h4>정부</h4>
        <label>
          정부 형태:
          <select
            value={formData.government.type}
            onChange={(e) => setFormData({
              ...formData,
              government: {
                ...formData.government,
                type: e.target.value
              }
            })}
          >
            <option value="">선택하세요</option>
            <option value="democracy">민주주의</option>
            <option value="monarchy">군주제</option>
            <option value="theocracy">신정정치</option>
            <option value="oligarchy">과두정치</option>
          </select>
        </label>
      </section>

      {/* 로어 섹션 */}
      <section className="form-section">
        <h4>로어</h4>
        <label>
          역사:
          <textarea
            value={formData.lore.history}
            onChange={(e) => setFormData({
              ...formData,
              lore: {
                ...formData.lore,
                history: e.target.value
              }
            })}
            rows={6}
          />
        </label>
      </section>

      <button type="submit">저장</button>
    </form>
  );
};
```

---

## 백엔드 API 설계

### 1. FastAPI 서버 구조

```python
# app/world_editor/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.world_editor.routes import regions, locations, cells, roads, map_metadata

# 기존 게임 엔진과 통합된 FastAPI 앱
# 포트는 기존 게임 엔진 설정에 따라 결정
app = FastAPI(title="World Editor API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경, 프로덕션에서는 제한 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(regions.router, prefix="/api/regions", tags=["regions"])
app.include_router(locations.router, prefix="/api/locations", tags=["locations"])
app.include_router(cells.router, prefix="/api/cells", tags=["cells"])
app.include_router(roads.router, prefix="/api/roads", tags=["roads"])
app.include_router(map_metadata.router, prefix="/api/map", tags=["map"])

# WebSocket 엔드포인트
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # 실시간 동기화 로직
    pass
```

### 2. Region API

```python
# app/world_editor/routes/regions.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.world_editor.schemas import RegionCreate, RegionUpdate, RegionResponse
from app.world_editor.services.region_service import RegionService

router = APIRouter()
region_service = RegionService()

@router.get("/", response_model=List[RegionResponse])
async def get_regions():
    """모든 지역 조회"""
    return await region_service.get_all_regions()

@router.get("/{region_id}", response_model=RegionResponse)
async def get_region(region_id: str):
    """특정 지역 조회"""
    region = await region_service.get_region(region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region

@router.post("/", response_model=RegionResponse)
async def create_region(region_data: RegionCreate):
    """새 지역 생성"""
    return await region_service.create_region(region_data)

@router.put("/{region_id}", response_model=RegionResponse)
async def update_region(region_id: str, region_data: RegionUpdate):
    """지역 정보 업데이트"""
    return await region_service.update_region(region_id, region_data)

@router.delete("/{region_id}")
async def delete_region(region_id: str):
    """지역 삭제"""
    await region_service.delete_region(region_id)
    return {"message": "Region deleted successfully"}
```

### 3. Road API

```python
# app/world_editor/routes/roads.py
from fastapi import APIRouter, HTTPException
from typing import List
from app.world_editor.schemas import RoadCreate, RoadUpdate, RoadResponse
from app.world_editor.services.road_service import RoadService

router = APIRouter()
road_service = RoadService()

@router.get("/", response_model=List[RoadResponse])
async def get_roads():
    """모든 도로 조회"""
    return await road_service.get_all_roads()

@router.post("/", response_model=RoadResponse)
async def create_road(road_data: RoadCreate):
    """새 도로 생성"""
    return await road_service.create_road(road_data)

@router.put("/{road_id}", response_model=RoadResponse)
async def update_road(road_id: str, road_data: RoadUpdate):
    """도로 정보 업데이트"""
    return await road_service.update_road(road_id, road_data)

@router.delete("/{road_id}")
async def delete_road(road_id: str):
    """도로 삭제"""
    await road_service.delete_road(road_id)
    return {"message": "Road deleted successfully"}
```

### 4. WebSocket 실시간 동기화

```python
# app/world_editor/websocket/connection_manager.py
from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# app/world_editor/main.py
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # 변경사항을 다른 클라이언트에 브로드캐스트
            await manager.broadcast(data)
    except:
        manager.disconnect(websocket)
```

---

## UI 컴포넌트 설계

### 1. Toolbar 컴포넌트

```typescript
// src/ui/world-editor/components/Toolbar.tsx
import React from 'react';

export const Toolbar: React.FC = () => {
  return (
    <div className="toolbar">
      <button className="tool-button" data-tool="select">
        <span>선택</span>
      </button>
      <button className="tool-button" data-tool="pin">
        <span>핀 추가</span>
      </button>
      <button className="tool-button" data-tool="road">
        <span>도로 그리기</span>
      </button>
      <button className="tool-button" data-tool="zoom-in">
        <span>확대</span>
      </button>
      <button className="tool-button" data-tool="zoom-out">
        <span>축소</span>
      </button>
      <button className="tool-button" data-tool="grid-toggle">
        <span>그리드</span>
      </button>
    </div>
  );
};
```

### 2. PinMarker 컴포넌트

```typescript
// src/ui/world-editor/components/PinMarker.tsx
import React from 'react';
import { Circle, Text, Group } from 'react-konva';

interface PinMarkerProps {
  pin: PinData;
  selected: boolean;
  onClick: () => void;
  onDragEnd: (e: Konva.KonvaEventObject<DragEvent>) => void;
}

export const PinMarker: React.FC<PinMarkerProps> = ({
  pin,
  selected,
  onClick,
  onDragEnd
}) => {
  const pinColors = {
    region: '#FF6B9D',
    location: '#4ECDC4',
    cell: '#95E1D3'
  };

  return (
    <Group
      x={pin.x}
      y={pin.y}
      draggable
      onClick={onClick}
      onDragEnd={onDragEnd}
    >
      <Circle
        radius={selected ? 12 : 10}
        fill={pinColors[pin.pin_type]}
        stroke={selected ? '#FFFFFF' : '#000000'}
        strokeWidth={selected ? 3 : 2}
      />
      <Text
        text={pin.region_data?.region_name || pin.location_data?.location_name || ''}
        fontSize={12}
        fill="#000000"
        x={-20}
        y={15}
      />
    </Group>
  );
};
```

### 3. RoadLine 컴포넌트

```typescript
// src/ui/world-editor/components/RoadLine.tsx
import React from 'react';
import { Line, Group } from 'react-konva';

interface RoadLineProps {
  road: RoadData;
  pins: PinData[];
  selected: boolean;
  onClick: () => void;
}

export const RoadLine: React.FC<RoadLineProps> = ({
  road,
  pins,
  selected,
  onClick
}) => {
  const fromPin = pins.find(p => p.pin_id === road.from_pin_id);
  const toPin = pins.find(p => p.pin_id === road.to_pin_id);

  if (!fromPin || !toPin) return null;

  const points = road.path.length > 0
    ? road.path.flatMap(p => [p.x, p.y])
    : [fromPin.x, fromPin.y, toPin.x, toPin.y];

  const roadColors = {
    normal: '#8B4513',
    hidden: '#696969',
    river: '#4169E1',
    mountain_pass: '#A0522D'
  };

  return (
    <Group onClick={onClick}>
      <Line
        points={points}
        stroke={roadColors[road.road_type]}
        strokeWidth={selected ? 4 : road.width}
        dash={road.dashed ? [10, 5] : []}
        tension={0.5}  // 베지어 곡선
      />
    </Group>
  );
};
```

---

## 데이터베이스 호환성

### 1. 기존 스키마 활용

월드 에디터는 기존 3-Layer 스키마를 그대로 활용합니다:

- **game_data.world_regions**: 지역 데이터
- **game_data.world_locations**: 위치 데이터
- **game_data.world_cells**: 셀 데이터

### 2. 확장 스키마

도로 정보를 저장하기 위한 새 테이블 추가:

```sql
-- app/world_editor/database/migrations/001_create_roads_table.sql
CREATE TABLE IF NOT EXISTS game_data.world_roads (
    road_id VARCHAR(50) PRIMARY KEY,
    from_region_id VARCHAR(50),
    from_location_id VARCHAR(50),
    to_region_id VARCHAR(50),
    to_location_id VARCHAR(50),
    road_type VARCHAR(50) NOT NULL DEFAULT 'normal',
    distance DECIMAL(10, 2),
    travel_time INTEGER,
    danger_level INTEGER DEFAULT 1,
    road_properties JSONB DEFAULT '{}',
    path_coordinates JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_region_id) REFERENCES game_data.world_regions(region_id) ON DELETE CASCADE,
    FOREIGN KEY (to_region_id) REFERENCES game_data.world_regions(region_id) ON DELETE CASCADE,
    FOREIGN KEY (from_location_id) REFERENCES game_data.world_locations(location_id) ON DELETE CASCADE,
    FOREIGN KEY (to_location_id) REFERENCES game_data.world_locations(location_id) ON DELETE CASCADE
);

CREATE INDEX idx_roads_from_region ON game_data.world_roads(from_region_id);
CREATE INDEX idx_roads_to_region ON game_data.world_roads(to_region_id);
CREATE INDEX idx_roads_from_location ON game_data.world_roads(from_location_id);
CREATE INDEX idx_roads_to_location ON game_data.world_roads(to_location_id);

COMMENT ON TABLE game_data.world_roads IS '지역 간 도로 연결 정보';
COMMENT ON COLUMN game_data.world_roads.path_coordinates IS 'JSONB 배열: [{"x": 100, "y": 200}, ...]';
COMMENT ON COLUMN game_data.world_roads.road_properties IS 'JSONB 구조: {"conditions": [...], "visual": {...}}';
```

### 3. 지도 메타데이터 테이블

```sql
-- app/world_editor/database/migrations/002_create_map_metadata_table.sql
CREATE TABLE IF NOT EXISTS game_data.map_metadata (
    map_id VARCHAR(50) PRIMARY KEY,
    map_name VARCHAR(100) NOT NULL,
    background_image VARCHAR(255),
    background_color VARCHAR(7) DEFAULT '#FFFFFF',
    width INTEGER NOT NULL DEFAULT 1920,
    height INTEGER NOT NULL DEFAULT 1080,
    grid_enabled BOOLEAN DEFAULT false,
    grid_size INTEGER DEFAULT 50,
    zoom_level DECIMAL(3, 2) DEFAULT 1.0,
    viewport_x INTEGER DEFAULT 0,
    viewport_y INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE game_data.map_metadata IS '월드 에디터 지도 메타데이터';
```

### 4. 핀 위치 정보 테이블

```sql
-- app/world_editor/database/migrations/003_create_pin_positions_table.sql
CREATE TABLE IF NOT EXISTS game_data.pin_positions (
    pin_id VARCHAR(50) PRIMARY KEY,
    game_data_id VARCHAR(50) NOT NULL,
    pin_type VARCHAR(20) NOT NULL,  -- 'region', 'location', 'cell'
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    icon_type VARCHAR(50) DEFAULT 'default',
    color VARCHAR(7) DEFAULT '#FF6B9D',
    size INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game_data_id, pin_type)
);

CREATE INDEX idx_pin_positions_type ON game_data.pin_positions(pin_type);
CREATE INDEX idx_pin_positions_game_data ON game_data.pin_positions(game_data_id);

COMMENT ON TABLE game_data.pin_positions IS '월드 에디터 핀 위치 정보';
```

### 5. JSONB 확장 활용

기존 `region_properties`, `location_properties` JSONB 필드에 D&D 정보 저장:

```json
{
  "editor_data": {
    "pin_position": {"x": 500, "y": 300},
    "icon_type": "city"
  },
  "dnd_info": {
    "demographics": {
      "population": 5000,
      "races": {"human": 3000, "elf": 1500, "dwarf": 500}
    },
    "economy": {
      "primary_industry": "trade",
      "trade_goods": ["spices", "textiles", "metals"]
    },
    "government": {
      "type": "monarchy",
      "leader": "King Aldric"
    },
    "lore": {
      "history": "Founded 200 years ago...",
      "legends": ["The Legend of the First King"],
      "secrets": ["Hidden treasure in the castle"]
    }
  }
}
```

---

## 구현 단계

### Phase 1: 기본 인프라 (1주)

- [x] 지도 이미지 에셋 배치 (`assets/world_editor/worldmap.png`) ✅ 완료
- [ ] FastAPI 서버 설정 (기존 게임 엔진과 통합)
- [ ] Tauri + React 프로젝트 초기화
- [ ] 데이터베이스 마이그레이션 (도로, 지도 메타데이터, 핀 위치 테이블)
- [ ] 기본 API 엔드포인트 구현 (CRUD)
- [ ] WebSocket 연결 설정
- [ ] 지도 이미지 로드 기능 구현
  - `assets/world_editor/worldmap.png`를 기본 배경으로 사용
  - Konva.js Image 컴포넌트로 로드
  - Pan & Zoom 지원

### Phase 2: 지도 캔버스 (1주)

- [ ] Konva.js 통합
- [ ] 지도 이미지 로드 및 표시
- [ ] Pan & Zoom 기능
- [ ] 그리드 표시
- [ ] 배경색/이미지 설정

### Phase 3: 핀 시스템 (1주)

- [ ] 핀 추가/삭제/이동
- [ ] 핀 타입별 아이콘
- [ ] 핀 클릭 이벤트
- [ ] 핀 드래그 앤 드롭
- [ ] 핀 위치 DB 저장

### Phase 4: 도로 시스템 (1주)

- [ ] 도로 그리기 도구
- [ ] 두 핀 간 도로 연결
- [ ] 베지어 곡선 지원
- [ ] 도로 타입 설정
- [ ] 도로 속성 편집

### Phase 5: D&D 정보 입력 (1주)

- [ ] InfoPanel 컴포넌트
- [ ] DnDInfoForm 구현
- [ ] 필드별 입력 폼
- [ ] JSONB 데이터 저장
- [ ] 데이터 검증

### Phase 6: 실시간 동기화 (1주)

- [ ] WebSocket 브로드캐스트
- [ ] 변경사항 실시간 반영
- [ ] 충돌 해결 로직
- [ ] 오프라인 모드 지원

### Phase 7: 고급 기능 (1주)

- [ ] Undo/Redo 기능
- [ ] Export/Import 기능
- [ ] 핀 필터링
- [ ] 검색 기능
- [ ] 미리보기 모드

### Phase 8: 통합 및 테스트 (1주)

- [ ] 전체 시스템 통합
- [ ] 성능 최적화
- [ ] 버그 수정
- [ ] 사용자 테스트
- [ ] 문서화

---

## 참고 사항

### 포트 구성

- **월드 에디터 백엔드**: 기존 게임 엔진과 동일 포트 사용 (FastAPI)
- **월드 에디터 WebSocket**: 기존 게임 엔진 WebSocket 엔드포인트 활용
- **참고**: 다른 프로젝트(novel_game 등)와의 포트 충돌 방지를 위해 이 프로젝트 내에서는 통합 포트 사용

### 에셋 관리

- **지도 이미지**: `assets/world_editor/worldmap.png`
  - 기본 지도 배경 이미지로 사용
  - 월드 에디터 시작 시 자동 로드
  - 사용자가 다른 이미지로 교체 가능

### 데이터 호환성

- 모든 편집 내용은 기존 `game_data` 스키마에 저장
- `region_properties`, `location_properties` JSONB 필드 활용
- 새로운 테이블은 `game_data` 스키마에 추가

### 성능 고려사항

- 대용량 지도 (5000x5000 이상) 지원
- 1000개 이상 핀 렌더링 최적화
- 실시간 동기화 시 변경사항 배치 처리

---

**작성일**: 2025-12-27  
**버전**: 1.0.0  
**작성자**: AI Assistant  
**다음 문서**: 구현 시작 시 `26_world_editor_implementation_log.md` 생성

