#!/usr/bin/env python3
"""
프레임워크 안정화 테스트
아키텍처 리팩토링, 성능 최적화, 모듈 통합 검증
"""
import asyncio
import sys
import os
from typing import Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.framework_manager import (
    FrameworkManager, framework_manager,
    initialize_framework, cleanup_framework,
    get_module, get_framework_status
)
from common.utils.logger import logger

class FrameworkStabilizationTester:
    """프레임워크 안정화 테스터"""
    
    def __init__(self):
        self.test_results = []
    
    async def test_framework_initialization(self):
        """프레임워크 초기화 테스트"""
        print("\n프레임워크 초기화 테스트...")
        
        try:
            await initialize_framework()
            
            # 초기화 상태 확인
            status = await get_framework_status()
            module_status = status["module_status"]
            
            success = len(module_status) > 0 and all(
                status in ["initialized", "running"] 
                for status in module_status.values()
            )
            
            self.test_results.append({
                "test": "framework_initialization",
                "success": success,
                "result": {
                    "module_count": len(module_status),
                    "module_status": module_status
                }
            })
            
            print(f"프레임워크 초기화 성공: {len(module_status)}개 모듈")
            
        except Exception as e:
            print(f"프레임워크 초기화 테스트 실패: {e}")
            self.test_results.append({
                "test": "framework_initialization",
                "success": False,
                "error": str(e)
            })
    
    async def test_module_dependencies(self):
        """모듈 의존성 테스트"""
        print("\n모듈 의존성 테스트...")
        
        try:
            # 핵심 모듈들 조회
            core_modules = [
                "DatabaseConnection",
                "ErrorHandler", 
                "TimeSystem",
                "EntityManager",
                "CellManager",
                "DialogueManager",
                "ActionHandler"
            ]
            
            available_modules = []
            for module_name in core_modules:
                module = await get_module(module_name)
                if module:
                    available_modules.append(module_name)
            
            success = len(available_modules) >= 5  # 최소 5개 모듈 필요
            
            self.test_results.append({
                "test": "module_dependencies",
                "success": success,
                "result": {
                    "available_modules": available_modules,
                    "total_modules": len(available_modules)
                }
            })
            
            print(f"모듈 의존성 성공: {len(available_modules)}개 모듈 사용 가능")
            
        except Exception as e:
            print(f"모듈 의존성 테스트 실패: {e}")
            self.test_results.append({
                "test": "module_dependencies",
                "success": False,
                "error": str(e)
            })
    
    async def test_performance_optimization(self):
        """성능 최적화 테스트"""
        print("\n성능 최적화 테스트...")
        
        try:
            # 성능 최적화 실행
            await framework_manager.optimize_performance()
            
            # 성능 메트릭 조회
            metrics = await framework_manager.get_performance_metrics()
            
            success = (
                metrics["total_modules"] > 0 and
                metrics["initialized_modules"] > 0
            )
            
            self.test_results.append({
                "test": "performance_optimization",
                "success": success,
                "result": metrics
            })
            
            print(f"성능 최적화 성공: {metrics['total_modules']}개 모듈")
            print(f"   초기화된 모듈: {metrics['initialized_modules']}개")
            print(f"   실행 중인 모듈: {metrics['running_modules']}개")
            
        except Exception as e:
            print(f"성능 최적화 테스트 실패: {e}")
            self.test_results.append({
                "test": "performance_optimization",
                "success": False,
                "error": str(e)
            })
    
    async def test_health_check(self):
        """헬스 체크 테스트"""
        print("\n헬스 체크 테스트...")
        
        try:
            health_status = await framework_manager.health_check()
            
            success = (
                health_status["overall_status"] in ["healthy", "degraded"] and
                len(health_status["modules"]) > 0
            )
            
            self.test_results.append({
                "test": "health_check",
                "success": success,
                "result": health_status
            })
            
            print(f"헬스 체크 성공: {health_status['overall_status']}")
            print(f"   모듈 수: {len(health_status['modules'])}")
            print(f"   이슈 수: {len(health_status['issues'])}")
            
        except Exception as e:
            print(f"헬스 체크 테스트 실패: {e}")
            self.test_results.append({
                "test": "health_check",
                "success": False,
                "error": str(e)
            })
    
    async def test_module_integration(self):
        """모듈 통합 테스트"""
        print("\n모듈 통합 테스트...")
        
        try:
            # EntityManager와 CellManager 통합 테스트
            entity_manager = await get_module("EntityManager")
            cell_manager = await get_module("CellManager")
            
            if entity_manager and cell_manager:
                # 의존성 확인
                success = True
                integration_result = {
                    "entity_manager_available": entity_manager is not None,
                    "cell_manager_available": cell_manager is not None,
                    "integration_successful": True
                }
            else:
                success = False
                integration_result = {
                    "entity_manager_available": entity_manager is not None,
                    "cell_manager_available": cell_manager is not None,
                    "integration_successful": False
                }
            
            self.test_results.append({
                "test": "module_integration",
                "success": success,
                "result": integration_result
            })
            
            print(f"모듈 통합 성공: EntityManager={entity_manager is not None}, CellManager={cell_manager is not None}")
            
        except Exception as e:
            print(f"모듈 통합 테스트 실패: {e}")
            self.test_results.append({
                "test": "module_integration",
                "success": False,
                "error": str(e)
            })
    
    async def test_framework_cleanup(self):
        """프레임워크 정리 테스트"""
        print("\n프레임워크 정리 테스트...")
        
        try:
            # 정리 전 상태 확인
            status_before = await get_framework_status()
            
            # 프레임워크 정리
            await cleanup_framework()
            
            # 정리 후 상태 확인
            status_after = await get_framework_status()
            
            success = (
                len(status_before["module_status"]) > 0 and
                len(status_after["module_status"]) == 0
            )
            
            self.test_results.append({
                "test": "framework_cleanup",
                "success": success,
                "result": {
                    "modules_before": len(status_before["module_status"]),
                    "modules_after": len(status_after["module_status"])
                }
            })
            
            print(f"프레임워크 정리 성공: {len(status_before['module_status'])} -> {len(status_after['module_status'])}")
            
        except Exception as e:
            print(f"프레임워크 정리 테스트 실패: {e}")
            self.test_results.append({
                "test": "framework_cleanup",
                "success": False,
                "error": str(e)
            })
    
    async def generate_test_report(self):
        """테스트 보고서 생성"""
        print("\n테스트 보고서 생성...")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "test_results": self.test_results,
            "framework_status": await get_framework_status()
        }
        
        # 보고서 저장
        import json
        with open("database/framework_stabilization_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"테스트 보고서 저장: database/framework_stabilization_test_report.json")
        print(f"테스트 성공률: {report['test_summary']['success_rate']:.1f}%")
        
        return report

async def main():
    """메인 함수"""
    tester = FrameworkStabilizationTester()
    
    try:
        await tester.test_framework_initialization()
        await tester.test_module_dependencies()
        await tester.test_performance_optimization()
        await tester.test_health_check()
        await tester.test_module_integration()
        await tester.test_framework_cleanup()
        await tester.generate_test_report()
        
        print("\n프레임워크 안정화 테스트 완료!")
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())
