#!/usr/bin/env python3
"""
에러 처리 시스템 테스트
계층별 에러 타입, 구조화된 로깅, 복구 메커니즘 검증
"""
import asyncio
import sys
import os
from typing import Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from common.error_handling.error_types import (
    DatabaseError, ValidationError, BusinessLogicError,
    EntityNotFoundError, CellNotFoundError, SessionNotFoundError,
    ErrorContext, ErrorCategory, ErrorSeverity
)
from common.error_handling.error_handler import (
    error_handler, handle_error, register_recovery_action,
    get_error_statistics, get_recent_errors
)
from database.connection import DatabaseConnection

class ErrorHandlingTester:
    """에러 처리 시스템 테스터"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.test_results = []
    
    async def initialize(self):
        """초기화"""
        try:
            await self.db.initialize()
            print("✅ 에러 처리 시스템 테스터 초기화 완료")
        except Exception as e:
            print(f"❌ 초기화 실패: {e}")
            raise
    
    async def cleanup(self):
        """정리"""
        try:
            await self.db.close()
            print("✅ 에러 처리 시스템 테스터 정리 완료")
        except Exception as e:
            print(f"❌ 정리 실패: {e}")
    
    async def test_database_errors(self):
        """데이터베이스 에러 테스트"""
        print("\n🔍 데이터베이스 에러 테스트...")
        
        # 연결 에러 시뮬레이션
        try:
            context = ErrorContext(session_id="test_session_001")
            error = DatabaseError(
                message="데이터베이스 연결 실패",
                error_code="CONNECTION_ERROR",
                context=context
            )
            
            result = await handle_error(error)
            self.test_results.append({
                "test": "database_connection_error",
                "success": result["error_id"] == "CONNECTION_ERROR",
                "result": result
            })
            print(f"✅ 연결 에러 처리: {result['error_id']}")
            
        except Exception as e:
            print(f"❌ 연결 에러 테스트 실패: {e}")
            self.test_results.append({
                "test": "database_connection_error",
                "success": False,
                "error": str(e)
            })
    
    async def test_validation_errors(self):
        """검증 에러 테스트"""
        print("\n🔍 검증 에러 테스트...")
        
        try:
            context = ErrorContext(
                user_id="test_user_001",
                session_id="test_session_001",
                action="create_entity"
            )
            
            error = ValidationError(
                message="엔티티 ID 형식이 올바르지 않습니다",
                field="entity_id",
                value="invalid_id",
                context=context
            )
            
            result = await handle_error(error)
            self.test_results.append({
                "test": "validation_error",
                "success": result["error_id"] == "VALIDATION_ERROR",
                "result": result
            })
            print(f"✅ 검증 에러 처리: {result['error_id']}")
            
        except Exception as e:
            print(f"❌ 검증 에러 테스트 실패: {e}")
            self.test_results.append({
                "test": "validation_error",
                "success": False,
                "error": str(e)
            })
    
    async def test_business_logic_errors(self):
        """비즈니스 로직 에러 테스트"""
        print("\n🔍 비즈니스 로직 에러 테스트...")
        
        try:
            # 엔티티 없음 에러
            context = ErrorContext(
                session_id="test_session_001",
                entity_id="nonexistent_entity"
            )
            
            error = EntityNotFoundError(
                entity_id="nonexistent_entity",
                entity_type="NPC",
                context=context
            )
            
            result = await handle_error(error)
            self.test_results.append({
                "test": "entity_not_found",
                "success": result["error_id"] == "ENTITY_NOT_FOUND",
                "result": result
            })
            print(f"✅ 엔티티 없음 에러 처리: {result['error_id']}")
            
            # 셀 없음 에러
            context = ErrorContext(
                session_id="test_session_001",
                cell_id="nonexistent_cell"
            )
            
            error = CellNotFoundError(
                cell_id="nonexistent_cell",
                context=context
            )
            
            result = await handle_error(error)
            self.test_results.append({
                "test": "cell_not_found",
                "success": result["error_id"] == "CELL_NOT_FOUND",
                "result": result
            })
            print(f"✅ 셀 없음 에러 처리: {result['error_id']}")
            
        except Exception as e:
            print(f"❌ 비즈니스 로직 에러 테스트 실패: {e}")
            self.test_results.append({
                "test": "business_logic_error",
                "success": False,
                "error": str(e)
            })
    
    async def test_recovery_mechanisms(self):
        """복구 메커니즘 테스트"""
        print("\n🔍 복구 메커니즘 테스트...")
        
        # 복구 액션 등록
        async def database_recovery_handler(error):
            """데이터베이스 복구 핸들러"""
            print(f"🔄 데이터베이스 복구 시도: {error.message}")
            # 실제로는 재연결 시도 등
            return {"status": "recovered", "action": "reconnect"}
        
        register_recovery_action(
            error_category=ErrorCategory.DATABASE,
            error_code="CONNECTION_ERROR",
            action_type="reconnect",
            description="데이터베이스 재연결",
            handler=database_recovery_handler,
            max_retries=3
        )
        
        try:
            context = ErrorContext(session_id="test_session_001")
            error = DatabaseError(
                message="데이터베이스 연결 실패",
                error_code="CONNECTION_ERROR",
                context=context
            )
            
            result = await handle_error(error, auto_recovery=True)
            self.test_results.append({
                "test": "recovery_mechanism",
                "success": result["recovery_attempted"] and result["recovery_result"],
                "result": result
            })
            print(f"✅ 복구 메커니즘 테스트: {result['recovery_result']}")
            
        except Exception as e:
            print(f"❌ 복구 메커니즘 테스트 실패: {e}")
            self.test_results.append({
                "test": "recovery_mechanism",
                "success": False,
                "error": str(e)
            })
    
    async def test_error_statistics(self):
        """에러 통계 테스트"""
        print("\n🔍 에러 통계 테스트...")
        
        try:
            stats = get_error_statistics()
            recent_errors = get_recent_errors(10)
            
            print(f"📊 총 에러 수: {stats['total_errors']}")
            print(f"📊 카테고리별 통계: {stats['category_stats']}")
            print(f"📊 심각도별 통계: {stats['severity_stats']}")
            print(f"📊 최근 에러 수: {len(recent_errors)}")
            
            self.test_results.append({
                "test": "error_statistics",
                "success": stats['total_errors'] > 0,
                "result": {
                    "total_errors": stats['total_errors'],
                    "recent_errors_count": len(recent_errors)
                }
            })
            
        except Exception as e:
            print(f"❌ 에러 통계 테스트 실패: {e}")
            self.test_results.append({
                "test": "error_statistics",
                "success": False,
                "error": str(e)
            })
    
    async def generate_test_report(self):
        """테스트 보고서 생성"""
        print("\n📊 테스트 보고서 생성...")
        
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
            "error_statistics": get_error_statistics()
        }
        
        # 보고서 저장
        import json
        with open("database/error_handling_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 테스트 보고서 저장: database/error_handling_test_report.json")
        print(f"📊 테스트 성공률: {report['test_summary']['success_rate']:.1f}%")
        
        return report

async def main():
    """메인 함수"""
    tester = ErrorHandlingTester()
    
    try:
        await tester.initialize()
        await tester.test_database_errors()
        await tester.test_validation_errors()
        await tester.test_business_logic_errors()
        await tester.test_recovery_mechanisms()
        await tester.test_error_statistics()
        await tester.generate_test_report()
        
        print("\n🎉 에러 처리 시스템 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
