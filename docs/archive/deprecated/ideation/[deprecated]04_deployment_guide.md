# [deprecated] RPG Engine 배포 가이드

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: 배포 관련 내용이 구현 완료되었으며, 실제 배포 환경과 다릅니다. 현재는 World Editor 웹 기반 배포가 주로 사용됩니다.

> **문서 버전**: v1.0  
> **작성일**: 2025-10-18  
> **최종 수정**: 2025-10-18

## 🚀 **배포 개요**

RPG Engine은 Python 기반의 크로스 플랫폼 게임 엔진으로, 다양한 환경에서 배포할 수 있습니다.

### **핵심 철학: "이야기 엔진" 배포**
이 시스템은 단순한 게임이 아니라 **"서사 기반 세계의 시뮬레이션 구조체"**이므로, 배포도 이 철학을 반영합니다.

- **지속적 세계**: 플레이어가 없어도 세계는 계속 작동
- **데이터 중심**: PostgreSQL이 세계의 심장 역할
- **AI 통합**: LLM이 세계를 해석하고 서사를 생성
- **개발자 모드**: 게임하면서 세계관을 실시간으로 편집

### **기술 스택**
- **PostgreSQL**: 데이터베이스 (포트 5432)
- **Python**: FASTAPI/asyncio 기반 백엔드
- **UI**: 웹/Tauri/PyQt 중 택1
- **SQLAlchemy**: ORM
- **Alembic**: 마이그레이션
- **EventBus**: in-proc 큐 + 예약 처리
- **캐시**: 셀 컨텐츠/대화 컨텍스트/LLM 응답 캐시

### **지원 플랫폼**
- **Windows**: Windows 10/11
- **macOS**: macOS 10.14+
- **Linux**: Ubuntu 18.04+, CentOS 7+

### **배포 방식**
- **독립 실행**: 단일 실행 파일
- **Docker 컨테이너**: 컨테이너 기반 배포
- **클라우드 배포**: AWS, Azure, GCP
- **로컬 네트워크**: LAN 환경 배포

---

## 📦 **패키지 준비**

### **의존성 관리**

#### **requirements.txt**
```txt
psycopg2-binary==2.9.9
python-dotenv==1.0.0
asyncpg==0.30.0
PyQt5==5.15.10
PyYAML==6.0.1
qasync==0.24.0
pytest==7.4.0
black==23.7.0
mypy==1.5.1
```

#### **패키지 설치**
```bash
# 가상환경 생성
python -m venv rpg_engine_env

# 가상환경 활성화 (Windows)
rpg_engine_env\Scripts\activate

# 가상환경 활성화 (Linux/macOS)
source rpg_engine_env/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

---

## 🗄️ **데이터베이스 설정**

### **PostgreSQL 설치**

#### **Windows**
```bash
# PostgreSQL 17 설치
# https://www.postgresql.org/download/windows/

# 서비스 시작
net start postgresql-x64-17

# 사용자 생성
createuser -U postgres rpg_user
createdb -U postgres rpg_engine
```

#### **Linux (Ubuntu)**
```bash
# PostgreSQL 설치
sudo apt update
sudo apt install postgresql postgresql-contrib

# 서비스 시작
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 사용자 생성
sudo -u postgres createuser rpg_user
sudo -u postgres createdb rpg_engine
```

#### **macOS**
```bash
# Homebrew로 설치
brew install postgresql

# 서비스 시작
brew services start postgresql

# 사용자 생성
createuser -U $(whoami) rpg_user
createdb -U $(whoami) rpg_engine
```

### **데이터베이스 초기화**

#### **스키마 생성**
```bash
# 데이터베이스 스키마 생성
psql -U postgres -d rpg_engine -f database/create_db.sql

# 테스트 데이터 생성
python setup_test_data.py
```

#### **환경 변수 설정**
```bash
# .env 파일 생성
cat > .env << EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rpg_engine
DB_USER=postgres
DB_PASSWORD=your_password
EOF
```

---

## 🏗️ **빌드 및 패키징**

### **PyInstaller를 사용한 독립 실행 파일**

#### **PyInstaller 설치**
```bash
pip install pyinstaller
```

#### **빌드 설정**
```python
# build.spec 파일 생성
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('database/', 'database/'),
        ('docs/', 'docs/'),
        ('tests/', 'tests/'),
    ],
    hiddenimports=[
        'asyncpg',
        'PyQt5',
        'qasync',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RPG_Engine',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)
```

#### **빌드 실행**
```bash
# Windows
pyinstaller build.spec

# Linux/macOS
pyinstaller build.spec
```

---

## 🔄 **CI/CD 파이프라인**

### **자동화 파이프라인**
```yaml
# .github/workflows/deploy.yml
name: Deploy RPG Engine

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python -m pytest tests/
      - name: Run database tests
        run: |
          python tests/database_test.py
          python tests/database_integrity_test.py

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # 배포 스크립트 실행
          ./deploy.sh
```

### **스키마 마이그레이션**
```bash
# Alembic 마이그레이션
alembic upgrade head

# 스키마 검증
python -c "from database.connection import DatabaseConnection; print('Schema OK')"

# 시나리오 회귀 테스트
python tests/scenarios/scenario_test.py
```

### **스냅샷 검증**
```python
# 스냅샷 생성
pg_dump -h localhost -U postgres -d rpg_engine > snapshot.sql

# 스냅샷 검증
python -c "
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
# 스냅샷 무결성 검증
"
```

---

## 🐳 **Docker 배포**

### **Dockerfile**
```dockerfile
FROM python:3.12-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_NAME=rpg_engine
ENV DB_USER=rpg_user
ENV DB_PASSWORD=rpg_password

# 포트 노출
EXPOSE 8000

# 실행 명령
CMD ["python", "run_gui.py"]
```

### **docker-compose.yml**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_DB: rpg_engine
      POSTGRES_USER: rpg_user
      POSTGRES_PASSWORD: rpg_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/create_db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  rpg_engine:
    build: .
    depends_on:
      - postgres
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=rpg_engine
      - DB_USER=rpg_user
      - DB_PASSWORD=rpg_password

volumes:
  postgres_data:
```

### **Docker 배포 실행**
```bash
# 이미지 빌드
docker-compose build

# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f rpg_engine

# 서비스 중지
docker-compose down
```

---

## ☁️ **클라우드 배포**

### **AWS 배포**

#### **EC2 인스턴스 설정**
```bash
# Ubuntu 20.04 LTS 인스턴스 생성
# t3.medium 이상 권장

# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Python 3.12 설치
sudo apt install python3.12 python3.12-venv python3.12-dev

# PostgreSQL 설치
sudo apt install postgresql postgresql-contrib

# Git 설치
sudo apt install git

# 애플리케이션 클론
git clone https://github.com/your-repo/rpg_engine.git
cd rpg_engine

# 가상환경 설정
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### **RDS 데이터베이스 설정**
```bash
# RDS PostgreSQL 인스턴스 생성
# db.t3.micro 이상 권장

# 보안 그룹 설정
# - 인바운드: PostgreSQL (5432) from EC2 security group
# - 아웃바운드: All traffic
```

#### **시스템 서비스 설정**
```bash
# systemd 서비스 파일 생성
sudo nano /etc/systemd/system/rpg-engine.service

[Unit]
Description=RPG Engine Game Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/rpg_engine
Environment=PATH=/home/ubuntu/rpg_engine/venv/bin
ExecStart=/home/ubuntu/rpg_engine/venv/bin/python run_gui.py
Restart=always

[Install]
WantedBy=multi-user.target

# 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable rpg-engine
sudo systemctl start rpg-engine
```

### **Azure 배포**

#### **App Service 배포**
```bash
# Azure CLI 설치
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# 로그인
az login

# 리소스 그룹 생성
az group create --name rpg-engine-rg --location eastus

# App Service 계획 생성
az appservice plan create --name rpg-engine-plan --resource-group rpg-engine-rg --sku B1 --is-linux

# 웹 앱 생성
az webapp create --resource-group rpg-engine-rg --plan rpg-engine-plan --name rpg-engine-app --runtime "PYTHON|3.12"

# 배포 설정
az webapp config appsettings set --resource-group rpg-engine-rg --name rpg-engine-app --settings @appsettings.json
```

### **GCP 배포**

#### **Cloud Run 배포**
```bash
# Google Cloud SDK 설치
curl https://sdk.cloud.google.com | bash

# 프로젝트 설정
gcloud config set project your-project-id

# Cloud Run 배포
gcloud run deploy rpg-engine --source . --platform managed --region us-central1 --allow-unauthenticated
```

---

## ⚡ **성능 최적화**

### **캐시 + 페이징**
```python
# 셀 컨텐츠 캐시 설정
CACHE_CONFIG = {
    "cell_content_ttl": 3600,  # 1시간
    "dialogue_context_ttl": 1800,  # 30분
    "llm_response_ttl": 7200,  # 2시간
    "max_cache_size": "1GB"
}

# 페이징 설정
PAGINATION_CONFIG = {
    "default_page_size": 50,
    "max_page_size": 200,
    "lazy_loading": True
}
```

### **레이지 로딩**
```python
# 동적 셀 로딩
async def load_cell_on_demand(cell_id: str):
    if not cache.exists(f"cell:{cell_id}"):
        cell_data = await database.load_cell(cell_id)
        await cache.set(f"cell:{cell_id}", cell_data, ttl=3600)
    return await cache.get(f"cell:{cell_id}")
```

### **배치 컴팩션**
```python
# 오래된 runtime 정리
async def cleanup_old_runtime_data():
    cutoff_date = datetime.now() - timedelta(days=30)
    await database.cleanup_old_sessions(cutoff_date)
    await database.cleanup_old_events(cutoff_date)
```

### **인덱스 최적화**
```sql
-- JSONB 필드 GIN 인덱스
CREATE INDEX CONCURRENTLY idx_entities_properties_gin 
ON runtime_data.entity_states USING GIN (properties);

-- FK B-Tree 인덱스
CREATE INDEX CONCURRENTLY idx_entity_refs_session 
ON reference_layer.entity_references (session_id);

-- 이벤트 시간 인덱스
CREATE INDEX CONCURRENTLY idx_events_triggered 
ON runtime_data.triggered_events (triggered_at);
```

---

## 📊 **모니터링 & 로깅**

### **게임 이벤트 로그**
```python
# 행동/결과/조건 실패/비용 로그
async def log_game_event(session_id: str, event_type: str, data: dict):
    await database.insert_event_log({
        "session_id": session_id,
        "event_type": event_type,
        "data": data,
        "timestamp": datetime.now()
    })
```

### **세계 이벤트 로그**
```python
# 비가시 진행, 틱 결과 로그
async def log_world_event(event_type: str, parameters: dict):
    await database.insert_world_log({
        "event_type": event_type,
        "parameters": parameters,
        "timestamp": datetime.now()
    })
```

### **Dev 행동 로그**
```python
# 편집/승격/롤백 로그
async def log_dev_action(user_id: str, action: str, target: str):
    await database.insert_dev_log({
        "user_id": user_id,
        "action": action,
        "target": target,
        "timestamp": datetime.now()
    })
```

### **대시보드 메트릭**
- **세션당 행동 수**: 플레이어 활동도 측정
- **생성된 로어 수**: 콘텐츠 생성량 측정
- **실패 규칙 TOP N**: 문제점 식별
- **캐시 적중률**: 성능 최적화 지표

---

## 💾 **백업/복구**

### **주기 스냅샷**
```bash
# 일일 백업 스크립트
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/rpg_engine"
mkdir -p $BACKUP_DIR

# PostgreSQL 백업
pg_dump -h localhost -U postgres -d rpg_engine > $BACKUP_DIR/rpg_engine_$DATE.sql

# 압축
gzip $BACKUP_DIR/rpg_engine_$DATE.sql

# 30일 이상 된 백업 삭제
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### **WAL (Write-Ahead Log) 백업**
```bash
# WAL 아카이브 설정
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'

# 복구 설정
# recovery.conf
restore_command = 'cp /backup/wal/%f %p'
```

### **포인트-인-타임 복구**
```bash
# 특정 시점으로 복구
pg_restore -h localhost -U postgres -d rpg_engine_new \
  --clean --if-exists \
  /backup/rpg_engine/rpg_engine_20241018_120000.sql.gz

# WAL을 이용한 정확한 시점 복구
pg_basebackup -h localhost -U postgres -D /backup/base \
  -Ft -z -P -W

# 특정 시점까지 복구
pg_receivewal -h localhost -U postgres -D /backup/wal
```

### **자동 백업 설정**
```bash
# crontab 설정
# 매일 새벽 2시 백업
0 2 * * * /home/ubuntu/rpg_engine/scripts/backup.sh

# 매주 일요일 새벽 3시 전체 백업
0 3 * * 0 /home/ubuntu/rpg_engine/scripts/full_backup.sh
```

---

## 🔧 **환경별 설정**

### **개발 환경**
```bash
# .env.development
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rpg_engine_dev
DB_USER=postgres
DB_PASSWORD=dev_password
LOG_LEVEL=DEBUG
```

### **스테이징 환경**
```bash
# .env.staging
DB_HOST=staging-db.example.com
DB_PORT=5432
DB_NAME=rpg_engine_staging
DB_USER=rpg_user
DB_PASSWORD=staging_password
LOG_LEVEL=INFO
```

### **프로덕션 환경**
```bash
# .env.production
DB_HOST=prod-db.example.com
DB_PORT=5432
DB_NAME=rpg_engine_prod
DB_USER=rpg_user
DB_PASSWORD=prod_password
LOG_LEVEL=WARNING
```

---

## 📊 **모니터링 및 로깅**

### **로깅 설정**
```python
# logging.conf
[loggers]
keys=root,rpg_engine

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter,detailedFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_rpg_engine]
level=DEBUG
handlers=consoleHandler,fileHandler
qualname=rpg_engine
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=detailedFormatter
args=('logs/rpg_engine.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[formatter_detailedFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s
```

### **성능 모니터링**
```python
# monitoring.py
import psutil
import time
from datetime import datetime

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
    
    def log_performance(self):
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # 시스템 리소스 모니터링
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        logger.info(f"성능 지표 - Uptime: {uptime:.2f}s, CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%")
        logger.info(f"요청 수: {self.request_count}, 에러 수: {self.error_count}")
```

---

## 🔒 **보안 설정**

### **데이터베이스 보안**
```sql
-- 사용자 권한 설정
GRANT CONNECT ON DATABASE rpg_engine TO rpg_user;
GRANT USAGE ON SCHEMA game_data TO rpg_user;
GRANT USAGE ON SCHEMA reference_layer TO rpg_user;
GRANT USAGE ON SCHEMA runtime_data TO rpg_user;

-- 테이블 권한 설정
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA game_data TO rpg_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA reference_layer TO rpg_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA runtime_data TO rpg_user;

-- 시퀀스 권한 설정
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA game_data TO rpg_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA reference_layer TO rpg_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA runtime_data TO rpg_user;
```

### **네트워크 보안**
```bash
# 방화벽 설정 (Ubuntu)
sudo ufw allow 5432/tcp  # PostgreSQL
sudo ufw allow 8000/tcp  # 애플리케이션
sudo ufw enable

# SSL 인증서 설정
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

---

## 🧪 **배포 테스트**

### **배포 전 체크리스트**
- [ ] 데이터베이스 연결 테스트
- [ ] 애플리케이션 시작 테스트
- [ ] 기본 게임플레이 테스트
- [ ] 성능 테스트
- [ ] 보안 테스트

### **자동화된 배포 테스트**
```bash
#!/bin/bash
# deploy_test.sh

echo "배포 테스트 시작..."

# 1. 데이터베이스 연결 테스트
python tests/database_test.py
if [ $? -ne 0 ]; then
    echo "데이터베이스 연결 실패"
    exit 1
fi

# 2. 애플리케이션 시작 테스트
timeout 30s python run_gui.py &
APP_PID=$!
sleep 10

if ! kill -0 $APP_PID 2>/dev/null; then
    echo "애플리케이션 시작 실패"
    exit 1
fi

kill $APP_PID

# 3. 시나리오 테스트
python tests/scenarios/scenario_test.py
if [ $? -ne 0 ]; then
    echo "시나리오 테스트 실패"
    exit 1
fi

echo "배포 테스트 완료!"
```

---

## 📚 **문제 해결**

### **일반적인 문제들**

#### **데이터베이스 연결 실패**
```bash
# 연결 테스트
psql -h localhost -p 5432 -U postgres -d rpg_engine -c "SELECT 1;"

# 방화벽 확인
sudo ufw status

# PostgreSQL 서비스 확인
sudo systemctl status postgresql
```

#### **메모리 부족**
```bash
# 메모리 사용량 확인
free -h
ps aux --sort=-%mem | head

# 스왑 파일 생성
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### **포트 충돌**
```bash
# 포트 사용 확인
netstat -tulpn | grep :5432
netstat -tulpn | grep :8000

# 프로세스 종료
sudo kill -9 <PID>
```

---

## 📈 **성능 최적화**

### **데이터베이스 최적화**
```sql
-- 인덱스 최적화
CREATE INDEX CONCURRENTLY idx_entity_states_entity ON runtime_data.entity_states(runtime_entity_id);
CREATE INDEX CONCURRENTLY idx_entity_states_cell ON runtime_data.entity_states(runtime_cell_id);
CREATE INDEX CONCURRENTLY idx_sessions_active ON runtime_data.active_sessions(session_state);

-- 통계 업데이트
ANALYZE;
```

### **애플리케이션 최적화**
```python
# 연결 풀 크기 조정
DATABASE_CONFIG = {
    "min_size": 10,
    "max_size": 50,
    "command_timeout": 60
}

# 캐싱 설정
import functools
import time

@functools.lru_cache(maxsize=128)
def cached_query(query_hash):
    # 캐시된 쿼리 결과 반환
    pass
```

---

## 📚 **참고 자료**

### **배포 관련**
- **Docker 문서**: https://docs.docker.com/
- **Kubernetes 문서**: https://kubernetes.io/docs/
- **AWS 문서**: https://docs.aws.amazon.com/
- **Azure 문서**: https://docs.microsoft.com/azure/

### **모니터링**
- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/
- **ELK Stack**: https://www.elastic.co/guide/

### **보안**
- **OWASP**: https://owasp.org/
- **PostgreSQL 보안**: https://www.postgresql.org/docs/current/security.html
- **SSL/TLS**: https://www.ssl.com/guide/

---

**문서 작성자**: RPG Engine Development Team  
**최종 검토**: 2025-10-18  
**다음 검토 예정**: 2025-11-18
