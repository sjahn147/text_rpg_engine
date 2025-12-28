# 월드 에디터 모듈

D&D 타운 스타일의 시각적 월드 에디터

## 구조

```
app/world_editor/
├── __init__.py
├── main.py                    # FastAPI 메인 앱
├── schemas.py                 # Pydantic 스키마
├── services/                  # 비즈니스 로직
│   ├── region_service.py
│   ├── location_service.py
│   ├── cell_service.py
│   ├── road_service.py
│   ├── pin_service.py
│   └── map_service.py
├── routes/                    # API 라우터
│   ├── regions.py
│   ├── locations.py
│   ├── cells.py
│   ├── roads.py
│   ├── pins.py
│   └── map_metadata.py
├── frontend/                  # 프론트엔드 (Tauri + React)
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       └── types/
└── run_server.py              # 서버 실행 스크립트
```

## 설치

### 백엔드 의존성

```bash
pip install fastapi uvicorn websockets
```

### 프론트엔드 의존성

```bash
cd app/world_editor/frontend
npm install react react-dom konva react-konva axios use-image
```

## 실행

### 1. 데이터베이스 마이그레이션

```bash
psql -U postgres -d rpg_engine -f database/setup/world_editor_migrations.sql
```

### 2. 백엔드 서버 실행

```bash
python app/world_editor/run_server.py
```

또는:

```bash
uvicorn app.world_editor.main:app --host 0.0.0.0 --port 8001 --reload
```

**참고**: 월드 에디터는 포트 8001을 사용합니다 (기존 서버 8000과 분리).

### 3. 프론트엔드 실행 (Tauri)

```bash
cd app/world_editor/frontend
npm run tauri dev
```

## API 엔드포인트

- **Regions**: `GET/POST/PUT/DELETE /api/regions`
- **Locations**: `GET/POST/PUT/DELETE /api/locations`
- **Cells**: `GET/POST/PUT/DELETE /api/cells`
- **Roads**: `GET/POST/PUT/DELETE /api/roads`
- **Pins**: `GET/POST/PUT/DELETE /api/pins`
- **Map Metadata**: `GET/POST/PUT /api/map/{map_id}`
- **WebSocket**: `WS /ws`

## 기능

- ✅ 지도 이미지 배경 표시
- ✅ 핀 추가/수정/삭제
- ✅ 도로 그리기 및 연결
- ✅ D&D 스타일 정보 입력
- ✅ 실시간 동기화 (WebSocket)
- ✅ 그리드 표시
- ✅ 확대/축소/이동

## 참고

- 기본 지도 이미지: `assets/world_editor/worldmap.png`
- API 문서: `http://localhost:8000/docs` (FastAPI 자동 생성)

