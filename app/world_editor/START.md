# 월드 에디터 실행 가이드

## 빠른 시작

### 1. 백엔드 서버 실행

```bash
# 프로젝트 루트에서
python app/world_editor/run_server.py
```

또는:

```bash
uvicorn app.world_editor.main:app --host 0.0.0.0 --port 8001 --reload
```

서버가 실행되면:
- API 문서: http://localhost:8001/docs
- API 엔드포인트: http://localhost:8001/api/*
- 포트: 8001 (기존 서버 8000과 분리)

### 2. 프론트엔드 개발 서버 실행

```bash
cd app/world_editor/frontend
npm install  # 최초 1회만
npm run dev
```

프론트엔드가 실행되면:
- 개발 서버: http://localhost:3000
- 자동으로 백엔드 API로 프록시 설정됨

## 접속 정보

- **프론트엔드**: http://localhost:3000
- **월드 에디터 백엔드 API**: http://localhost:8001 (포트 8001 사용)
- **API 문서**: http://localhost:8001/docs
- **WebSocket**: ws://localhost:8001/ws
- **기존 서버**: http://localhost:8000 (유지)

## 문제 해결

### 백엔드 서버가 시작되지 않는 경우

1. 데이터베이스 연결 확인:
   ```bash
   python scripts/apply_world_editor_migrations.py
   ```

2. 포트 충돌 확인:
   ```bash
   netstat -ano | findstr ":8001"
   ```
   
   **참고**: 월드 에디터는 포트 8001을 사용합니다. 기존 서버(8000)와 충돌하지 않습니다.

### 프론트엔드가 시작되지 않는 경우

1. 의존성 재설치:
   ```bash
   cd app/world_editor/frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

2. 포트 충돌 확인:
   ```bash
   netstat -ano | findstr ":3000"
   ```

### 이미지가 표시되지 않는 경우

지도 이미지가 `app/world_editor/frontend/public/assets/world_editor/worldmap.png`에 있는지 확인하세요.

