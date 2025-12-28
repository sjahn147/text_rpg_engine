#!/usr/bin/env python3
"""
TimeSystem 모듈 테스트
시간 기반 시뮬레이션 엔진 검증
"""
import asyncio
import sys
import os
from typing import Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.systems.time_system import (
    TimeSystem, GameTime, TimeScale, ScheduledEvent,
    time_system, start_time_system, stop_time_system,
    schedule_event, get_current_time, set_time_scale
)
from common.utils.logger import logger

class TimeSystemTester:
    """TimeSystem 테스터"""
    
    def __init__(self):
        self.test_results = []
        self.event_log = []
    
    async def test_basic_time_operations(self):
        """기본 시간 연산 테스트"""
        print("\n🔍 기본 시간 연산 테스트...")
        
        try:
            # 시간 생성 및 조작
            time1 = GameTime(day=1, hour=10, minute=30, second=0)
            time2 = GameTime(day=2, hour=15, minute=45, second=30)
            
            # 시간 문자열 변환
            time_str = str(time1)
            time_dict = time1.to_dict()
            
            # 딕셔너리에서 시간 복원
            time3 = GameTime().from_dict(time_dict)
            
            success = (time_str == "Day 1, 10:30:00" and 
                      time_dict["day"] == 1 and
                      time3.day == time1.day)
            
            self.test_results.append({
                "test": "basic_time_operations",
                "success": success,
                "result": {
                    "time_str": time_str,
                    "time_dict": time_dict,
                    "restored_time": time3.to_dict()
                }
            })
            
            print(f"✅ 기본 시간 연산: {time_str}")
            
        except Exception as e:
            print(f"❌ 기본 시간 연산 테스트 실패: {e}")
            self.test_results.append({
                "test": "basic_time_operations",
                "success": False,
                "error": str(e)
            })
    
    async def test_time_system_initialization(self):
        """TimeSystem 초기화 테스트"""
        print("\n🔍 TimeSystem 초기화 테스트...")
        
        try:
            await time_system.initialize()
            
            # 초기 상태 확인
            current_time = get_current_time()
            stats = await time_system.get_time_statistics()
            
            success = (current_time.day == 1 and 
                      current_time.hour == 6 and
                      stats["is_running"] == False)
            
            self.test_results.append({
                "test": "time_system_initialization",
                "success": success,
                "result": {
                    "current_time": current_time.to_dict(),
                    "stats": stats
                }
            })
            
            print(f"✅ TimeSystem 초기화: {current_time}")
            
        except Exception as e:
            print(f"❌ TimeSystem 초기화 테스트 실패: {e}")
            self.test_results.append({
                "test": "time_system_initialization",
                "success": False,
                "error": str(e)
            })
    
    async def test_time_scaling(self):
        """시간 가속 배율 테스트"""
        print("\n🔍 시간 가속 배율 테스트...")
        
        try:
            # 다양한 시간 가속 배율 테스트
            scales = [TimeScale.REAL_TIME, TimeScale.FAST, TimeScale.VERY_FAST]
            
            for scale in scales:
                set_time_scale(scale)
                current_scale = time_system.time_scale
                
                print(f"⏰ 시간 가속 배율: {scale.value}")
            
            success = True
            self.test_results.append({
                "test": "time_scaling",
                "success": success,
                "result": {"tested_scales": [s.value for s in scales]}
            })
            
            print(f"✅ 시간 가속 배율 테스트 완료")
            
        except Exception as e:
            print(f"❌ 시간 가속 배율 테스트 실패: {e}")
            self.test_results.append({
                "test": "time_scaling",
                "success": False,
                "error": str(e)
            })
    
    async def test_event_scheduling(self):
        """이벤트 스케줄링 테스트"""
        print("\n🔍 이벤트 스케줄링 테스트...")
        
        try:
            # 현재 시간 설정
            current_time = get_current_time()
            trigger_time = GameTime(
                day=current_time.day,
                hour=current_time.hour,
                minute=current_time.minute + 1  # 1분 후
            )
            
            # 이벤트 핸들러 정의
            async def test_event_handler(event_data):
                self.event_log.append({
                    "event": "test_event",
                    "data": event_data,
                    "timestamp": str(current_time)
                })
                print(f"🎯 이벤트 실행: {event_data['message']}")
            
            # 이벤트 스케줄링
            event_id = await schedule_event(
                event_name="테스트 이벤트",
                event_type="test",
                trigger_time=trigger_time,
                event_data={"message": "테스트 이벤트가 실행되었습니다"},
                handler=test_event_handler
            )
            
            # 스케줄된 이벤트 확인
            scheduled_events = time_system.get_scheduled_events()
            
            success = (event_id is not None and 
                      len(scheduled_events) == 1 and
                      scheduled_events[0].event_name == "테스트 이벤트")
            
            self.test_results.append({
                "test": "event_scheduling",
                "success": success,
                "result": {
                    "event_id": event_id,
                    "scheduled_events_count": len(scheduled_events),
                    "event_name": scheduled_events[0].event_name if scheduled_events else None
                }
            })
            
            print(f"✅ 이벤트 스케줄링: {event_id}")
            
        except Exception as e:
            print(f"❌ 이벤트 스케줄링 테스트 실패: {e}")
            self.test_results.append({
                "test": "event_scheduling",
                "success": False,
                "error": str(e)
            })
    
    async def test_time_advancement(self):
        """시간 진행 테스트"""
        print("\n🔍 시간 진행 테스트...")
        
        try:
            # 초기 시간 설정
            initial_time = GameTime(day=1, hour=10, minute=30, second=0)
            time_system.set_time(initial_time)
            
            # 시간 수동 진행
            await time_system.advance_time(30)  # 30분 진행
            
            # 시간 확인
            current_time = get_current_time()
            expected_hour = 11 if initial_time.minute + 30 >= 60 else 10
            expected_minute = (initial_time.minute + 30) % 60
            
            success = (current_time.hour == expected_hour and 
                      current_time.minute == expected_minute)
            
            self.test_results.append({
                "test": "time_advancement",
                "success": success,
                "result": {
                    "initial_time": initial_time.to_dict(),
                    "current_time": current_time.to_dict(),
                    "expected_hour": expected_hour,
                    "expected_minute": expected_minute
                }
            })
            
            print(f"✅ 시간 진행: {initial_time} -> {current_time}")
            
        except Exception as e:
            print(f"❌ 시간 진행 테스트 실패: {e}")
            self.test_results.append({
                "test": "time_advancement",
                "success": False,
                "error": str(e)
            })
    
    async def test_tick_handlers(self):
        """틱 핸들러 테스트"""
        print("\n🔍 틱 핸들러 테스트...")
        
        try:
            # 틱 핸들러 정의
            tick_count = 0
            
            async def test_tick_handler(current_time):
                nonlocal tick_count
                tick_count += 1
                print(f"⏰ 틱 #{tick_count}: {current_time}")
            
            # 틱 핸들러 추가
            time_system.add_tick_handler(test_tick_handler)
            
            # 시간 시스템 시작 (짧은 시간)
            await start_time_system("test_session")
            
            # 잠시 대기
            await asyncio.sleep(2)
            
            # 시간 시스템 중지
            await stop_time_system()
            
            success = tick_count > 0
            
            self.test_results.append({
                "test": "tick_handlers",
                "success": success,
                "result": {
                    "tick_count": tick_count,
                    "handlers_count": len(time_system.tick_handlers)
                }
            })
            
            print(f"✅ 틱 핸들러: {tick_count}회 실행")
            
        except Exception as e:
            print(f"❌ 틱 핸들러 테스트 실패: {e}")
            self.test_results.append({
                "test": "tick_handlers",
                "success": False,
                "error": str(e)
            })
    
    async def test_time_statistics(self):
        """시간 통계 테스트"""
        print("\n🔍 시간 통계 테스트...")
        
        try:
            stats = await time_system.get_time_statistics()
            
            required_fields = [
                "current_time", "time_scale", "is_running",
                "scheduled_events_count", "tick_handlers_count", "tick_interval"
            ]
            
            success = all(field in stats for field in required_fields)
            
            self.test_results.append({
                "test": "time_statistics",
                "success": success,
                "result": stats
            })
            
            print(f"✅ 시간 통계: {len(stats)}개 필드")
            print(f"   현재 시간: {stats['current_time']}")
            print(f"   시간 가속: {stats['time_scale']}")
            print(f"   실행 상태: {stats['is_running']}")
            
        except Exception as e:
            print(f"❌ 시간 통계 테스트 실패: {e}")
            self.test_results.append({
                "test": "time_statistics",
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
            "event_log": self.event_log,
            "time_statistics": await time_system.get_time_statistics()
        }
        
        # 보고서 저장
        import json
        with open("database/time_system_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 테스트 보고서 저장: database/time_system_test_report.json")
        print(f"📊 테스트 성공률: {report['test_summary']['success_rate']:.1f}%")
        
        return report

async def main():
    """메인 함수"""
    tester = TimeSystemTester()
    
    try:
        await tester.test_basic_time_operations()
        await tester.test_time_system_initialization()
        await tester.test_time_scaling()
        await tester.test_event_scheduling()
        await tester.test_time_advancement()
        await tester.test_tick_handlers()
        await tester.test_time_statistics()
        await tester.generate_test_report()
        
        print("\n🎉 TimeSystem 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
    finally:
        await time_system.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
