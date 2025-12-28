# [deprecated] PostgreSQL 5431 포트 서버 설정 가이드

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 사유**: 이 문서는 초기 설정 메모로, 현재는 더 이상 사용되지 않습니다.

## 1. 데이터 디렉토리 초기화

1. 기존 데이터 디렉토리 삭제 (있는 경우)
```powershell
Remove-Item -Recurse -Force C:\hobby\RPG\data5431
```

2. 새로운 데이터베이스 클러스터 초기화
```powershell
& 'C:\Program Files\PostgreSQL\17\bin\initdb.exe' -D C:\hobby\RPG\data5431 -U postgres
```

## 2. PostgreSQL 설정 파일 수정

1. postgresql.conf 파일 수정 (C:\hobby\RPG\data5431\postgresql.conf)
```conf
# -----------------------------
# PostgreSQL configuration file
# -----------------------------

listen_addresses = '*'
port = 5431

shared_buffers = 128MB
dynamic_shared_memory_type = windows

client_encoding = 'UTF8'
```

2. pg_hba.conf 파일 수정 (C:\hobby\RPG\data5431\pg_hba.conf)
```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust
# IPv4 local connections:
host    all             all             127.0.0.1/32            trust
# IPv6 local connections:
host    all             all             ::1/128                 trust
```

## 3. PostgreSQL 서버 시작
```powershell
& 'C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe' -D C:\hobby\RPG\data5431 start
```

## 4. 사용자 및 데이터베이스 생성

1. rpgmaker 사용자 생성
```powershell
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -p 5431 -U postgres -d postgres -c "CREATE USER rpgmaker WITH PASSWORD '0000' CREATEDB;"
```

2. rpg_engine 데이터베이스 생성
```powershell
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -p 5431 -U postgres -d postgres -c "CREATE DATABASE rpg_engine OWNER rpgmaker;"
```

## 5. pgAdmin에서 서버 등록

1. pgAdmin 실행
2. 왼쪽 브라우저 패널에서 'Servers' 우클릭
3. Register > Server 선택
4. 서버 정보 입력:
   - General 탭:
     - Name: RPG_Server (또는 원하는 이름)
   - Connection 탭:
     - Host name/address: localhost
     - Port: 5431
     - Maintenance database: postgres
     - Username: rpgmaker
     - Password: 0000
     - Save password: 체크 (선택사항)

## 6. 서버 관리 명령어

- 서버 상태 확인:
```powershell
& 'C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe' -D C:\hobby\RPG\data5431 status
```

- 서버 중지:
```powershell
& 'C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe' -D C:\hobby\RPG\data5431 stop
```

- 서버 재시작:
```powershell
& 'C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe' -D C:\hobby\RPG\data5431 restart
```

## 주의사항

1. 모든 명령어는 관리자 권한의 PowerShell에서 실행해야 할 수 있습니다.
2. PostgreSQL이 설치된 경로가 다른 경우 'C:\Program Files\PostgreSQL\17\bin\' 부분을 적절히 수정해야 합니다.
3. 데이터 디렉토리 경로(C:\hobby\RPG\data5431)는 필요에 따라 변경할 수 있습니다.
4. 비밀번호와 포트는 보안을 위해 변경하여 사용할 수 있습니다. 