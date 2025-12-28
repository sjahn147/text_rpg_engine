#!/usr/bin/env python3
"""
테스트 실행 스크립트
"""
import sys
import subprocess
import os
from pathlib import Path

def run_tests():
    """테스트 실행"""
    print("🧪 RPG Engine 테스트 실행 시작...")
    
    # 프로젝트 루트 디렉토리로 이동
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # pytest 실행
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",  # 상세 출력
        "--tb=short",  # 짧은 traceback
        "--cov=app",  # app 모듈 커버리지
        "--cov=database",  # database 모듈 커버리지
        "--cov=common",  # common 모듈 커버리지
        "--cov-report=term-missing",  # 누락된 라인 표시
        "--cov-fail-under=80"  # 80% 이상 커버리지 요구
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ 모든 테스트 통과!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 테스트 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 테스트 실행 오류: {e}")
        return False

def run_specific_test(test_path: str):
    """특정 테스트 실행"""
    print(f"🧪 특정 테스트 실행: {test_path}")
    
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "-v",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ 테스트 통과!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 특정 테스트 실행
        test_path = sys.argv[1]
        success = run_specific_test(test_path)
    else:
        # 전체 테스트 실행
        success = run_tests()
    
    sys.exit(0 if success else 1)
