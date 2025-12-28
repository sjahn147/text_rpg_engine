# 월드 에디터 프론트엔드

Vite + React + Konva.js 기반 월드 에디터 프론트엔드

## 프로젝트 구조

```
frontend/
├── src/
│   ├── components/          # React 컴포넌트
│   │   ├── MapCanvas.tsx   # 지도 캔버스 (Konva.js)
│   │   ├── Toolbar.tsx     # 도구 모음
│   │   ├── InfoPanel.tsx   # 정보 패널
│   │   └── DnDInfoForm.tsx # D&D 정보 입력 폼
│   ├── hooks/              # React Hooks
│   │   ├── useWorldEditor.ts
│   │   └── useWebSocket.ts
│   ├── services/           # API 서비스
│   │   └── api.ts
│   ├── types/              # TypeScript 타입
│   │   └── index.ts
│   ├── App.tsx             # 메인 앱
│   ├── main.tsx            # 진입점
│   └── index.css           # 전역 스타일
├── public/
│   └── assets/
│       └── world_editor/
│           └── worldmap.png  # 지도 이미지
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 설치 및 실행

### 1. 의존성 설치

```bash
npm install
```

### 2. 개발 서버 실행

```bash
npm run dev
```

프론트엔드가 http://localhost:3000 에서 실행됩니다.

### 3. 빌드

```bash
npm run build
```

## 백엔드 연결

프론트엔드는 자동으로 백엔드 API (http://localhost:8000)로 프록시됩니다.

- API 요청: `/api/*` → `http://localhost:8000/api/*`
- WebSocket: `/ws` → `ws://localhost:8000/ws`

## 주요 기능

- ✅ 지도 이미지 배경 표시
- ✅ 핀 추가/수정/삭제/드래그
- ✅ 도로 그리기 및 연결
- ✅ D&D 스타일 정보 입력
- ✅ 실시간 동기화 (WebSocket)
- ✅ 그리드 표시/숨김
- ✅ 확대/축소/이동 (Pan & Zoom)

## API 엔드포인트

- Regions: `/api/regions`
- Locations: `/api/locations`
- Cells: `/api/cells`
- Roads: `/api/roads`
- Pins: `/api/pins`
- Map: `/api/map`
- WebSocket: `/ws`
