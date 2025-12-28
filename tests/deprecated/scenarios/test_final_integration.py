#!/usr/bin/env python3
"""
최종 통합 테스트
모든 시나리오와 시뮬레이션을 순차적으로 실행하여 전체 시스템 통합성 검증
"""

import sys
import os
import asyncio
import subprocess
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from common.utils.logger import get_logger

logger = get_logger(__name__)

class FinalIntegrationTest:
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    async def run_all_tests(self):
        """모든 테스트 실행"""
        logger.info("=== 최종 통합 테스트 시작 ===")
        self.start_time = datetime.now()
        
        # 테스트 시나리오 목록
        test_scenarios = [
            {
                "name": "DB 연결 시나리오",
                "file": "tests/scenarios/test_direct_db_scenarios.py",
                "description": "실제 DB 연결을 통한 Manager 테스트"
            },
            {
                "name": "행동 실행 시나리오", 
                "file": "tests/scenarios/test_action_execution_scenario.py",
                "description": "플레이어 행동 및 결과 테스트"
            },
            {
                "name": "마을 시뮬레이션 DB 통합",
                "file": "tests/scenarios/test_village_simulation_db.py", 
                "description": "실제 DB를 통한 100일 시뮬레이션"
            }
        ]
        
        # 각 시나리오 실행
        for i, scenario in enumerate(test_scenarios, 1):
            logger.info(f"--- 테스트 {i}/{len(test_scenarios)}: {scenario['name']} ---")
            result = await self._run_scenario(scenario)
            self.test_results[scenario['name']] = result
            
            if result['success']:
                logger.info(f"[SUCCESS] {scenario['name']} 통과")
            else:
                logger.error(f"[FAILED] {scenario['name']} 실패: {result['error']}")
        
        self.end_time = datetime.now()
        await self._analyze_results()
        
        logger.info("=== 최종 통합 테스트 완료 ===")
    
    async def _run_scenario(self, scenario):
        """개별 시나리오 실행"""
        try:
            # Python 스크립트 실행
            result = subprocess.run(
                [sys.executable, scenario['file']],
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'error': None if result.returncode == 0 else f"Exit code: {result.returncode}"
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': '',
                'returncode': -1,
                'error': 'Timeout (5분 초과)'
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': '',
                'returncode': -1,
                'error': str(e)
            }
    
    async def _analyze_results(self):
        """테스트 결과 분석"""
        logger.info("=== 테스트 결과 분석 ===")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        failed_tests = total_tests - passed_tests
        
        # 전체 통계
        logger.info(f"총 테스트: {total_tests}")
        logger.info(f"통과: {passed_tests}")
        logger.info(f"실패: {failed_tests}")
        logger.info(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        # 실행 시간
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            logger.info(f"총 실행 시간: {duration:.2f}초")
        
        # 개별 결과
        logger.info("=== 개별 테스트 결과 ===")
        for name, result in self.test_results.items():
            status = "[SUCCESS]" if result['success'] else "[FAILED]"
            logger.info(f"{status} {name}")
            
            if not result['success'] and result['error']:
                logger.error(f"  오류: {result['error']}")
        
        # 최종 평가
        if failed_tests == 0:
            logger.info("=== 최종 평가: 모든 테스트 통과 ===")
            return True
        else:
            logger.error(f"=== 최종 평가: {failed_tests}개 테스트 실패 ===")
            return False

async def run_final_integration_test():
    """최종 통합 테스트 실행"""
    test = FinalIntegrationTest()
    
    try:
        success = await test.run_all_tests()
        return success
        
    except Exception as e:
        logger.error(f"최종 통합 테스트 실행 중 오류: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(run_final_integration_test())
    if result:
        print("최종 통합 테스트 성공!")
        sys.exit(0)
    else:
        print("최종 통합 테스트 실패!")
        sys.exit(1)
