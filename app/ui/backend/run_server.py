"""
UI 백엔드 FastAPI 서버 실행 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
# app/ui/backend/run_server.py -> app/ui/backend -> app/ui -> app -> 프로젝트 루트
project_root = Path(__file__).parent.parent.parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 작업 디렉토리를 프로젝트 루트로 변경
os.chdir(project_root)

import uvicorn

if __name__ == "__main__":
    # reload를 사용하려면 import string을 사용해야 함
    # 프로젝트 루트에서 실행되므로 app.ui.backend.main:app 경로 사용
    uvicorn.run(
        "app.ui.backend.main:app",  # import string 형식
        host="0.0.0.0",
        port=8001,  # UI 백엔드 전용 포트 (기존 서버와 분리)
        log_level="info",
        reload=True  # 개발 환경에서 자동 리로드
    )

