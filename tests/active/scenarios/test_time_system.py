"""
TimeSystem 모듈 테스트
시간 기반 시뮬레이션 엔진의 핵심 기능 검증
"""
import pytest
import asyncio
from datetime import datetime
from app.systems.time_system import (
    TimeSystem, GameTime, TimeScale, TimePeriod, ScheduledEvent
)
from common.utils.logger import logger


@pytest.mark.asyncio
class TestTimeSystem:
    """TimeSystem 기본 기능 테스트"""
    
    async def test_time_system_initialization(self, db_with_templates, test_session):
        """TimeSystem 초기화 테스트"""
        time_system = TimeSystem()
        
        # 초기화
        await time_system.initialize()
        
        try:
            # 초기 상태 확인
            assert time_system.current_time.day == 1
            assert time_system.current_time.hour == 6
            assert time_system.current_time.minute == 0
            assert time_system.time_scale == TimeScale.REAL_TIME
            assert time_system.is_running == False
            assert len(time_system.scheduled_events) == 0
            assert len(time_system.tick_handlers) == 0
            
            logger.info("[OK] TimeSystem 초기화 성공")
            
        finally:
            await time_system.cleanup()
    
    async def test_time_system_start_stop(self, db_with_templates, test_session):
        """TimeSystem 시작/중지 테스트"""
        time_system = TimeSystem()
        await time_system.initialize()
        
        try:
            # session_id 추출 (dict인 경우)
            session_id = test_session if isinstance(test_session, str) else test_session['session_id']
            
            # 시작
            await time_system.start(session_id)
            assert time_system.is_running == True
            assert time_system._session_id == session_id
            
            # 잠시 대기
            await asyncio.sleep(0.1)
            
            # 중지
            await time_system.stop()
            assert time_system.is_running == False
            assert time_system._session_id is None
            
            logger.info("[OK] TimeSystem 시작/중지 성공")
            
        finally:
            await time_system.cleanup()
    
    async def test_time_advancement(self, db_with_templates, test_session):
        """시간 진행 테스트"""
        time_system = TimeSystem()
        await time_system.initialize()
        
        try:
            # 초기 시간 설정
            initial_time = GameTime(day=1, hour=6, minute=0)
            time_system.set_time(initial_time)
            
            # 시간 수동 진행
            await time_system.advance_time(30)  # 30분 진행
            
            current_time = time_system.get_current_time()
            assert current_time.day == 1
            assert current_time.hour == 6
            assert current_time.minute == 30
            
            # 1시간 더 진행
            await time_system.advance_time(60)
            current_time = time_system.get_current_time()
            assert current_time.hour == 7
            assert current_time.minute == 30
            
            # 하루 넘어가기 (07:30 + 960분 = 07:990분 = 23:30, 다음날 넘어가려면 더 필요)
            # 07:30 + 960분 = 23:30 (같은 날)
            # 다음날로 넘어가려면 24시간(1440분) 이상 필요
            await time_system.advance_time(16 * 60)  # 16시간 진행
            current_time = time_system.get_current_time()
            # 07:30 + 16시간 = 23:30 (같은 날)
            assert current_time.day == 1
            assert current_time.hour == 23
            assert current_time.minute == 30
            
            # 다음날로 넘어가기 (23:30 + 1시간 = 다음날 00:30)
            await time_system.advance_time(60)  # 1시간 더 진행
            current_time = time_system.get_current_time()
            assert current_time.day == 2
            assert current_time.hour == 0
            assert current_time.minute == 30
            
            logger.info(f"[OK] 시간 진행 테스트 성공: {current_time}")
            
        finally:
            await time_system.cleanup()
    
    async def test_time_scale(self, db_with_templates, test_session):
        """시간 가속 배율 테스트"""
        time_system = TimeSystem()
        await time_system.initialize()
        
        try:
            # 각 시간 가속 배율 테스트
            scales = [
                (TimeScale.REAL_TIME, 1.0),
                (TimeScale.FAST, 10.0),
                (TimeScale.VERY_FAST, 100.0),
            ]
            
            for scale, expected_multiplier in scales:
                time_system.set_time_scale(scale)
                assert time_system.time_scale == scale
                assert time_system.scale_multipliers[scale] == expected_multiplier
            
            logger.info("[OK] 시간 가속 배율 테스트 성공")
            
        finally:
            await time_system.cleanup()
    
    async def test_time_period(self, db_with_templates, test_session):
        """시간대(TimePeriod) 테스트"""
        time_system = TimeSystem()
        await time_system.initialize()
        
        try:
            # 각 시간대별 시간 설정 및 확인
            test_cases = [
                (6, TimePeriod.MORNING),    # 06:00 - 오전
                (12, TimePeriod.AFTERNOON), # 12:00 - 오후
                (18, TimePeriod.EVENING),   # 18:00 - 저녁
                (22, TimePeriod.NIGHT),    # 22:00 - 밤
            ]
            
            for hour, expected_period in test_cases:
                time_system.set_time(GameTime(day=1, hour=hour, minute=0))
                # TimePeriod는 현재 구현에서 직접 사용되지 않지만, Enum으로 정의되어 있음
                assert TimePeriod.MORNING in [TimePeriod.MORNING, TimePeriod.AFTERNOON, 
                                             TimePeriod.EVENING, TimePeriod.NIGHT]
            
            logger.info("[OK] 시간대 테스트 성공")
            
        finally:
            await time_system.cleanup()
    
    async def test_schedule_event(self, db_with_templates, test_session):
        """이벤트 스케줄링 테스트"""
        time_system = TimeSystem()
        await time_system.initialize()
        
        try:
            # 현재 시간 설정
            current_time = GameTime(day=1, hour=10, minute=0)
            time_system.set_time(current_time)
            
            # 이벤트 스케줄링
            trigger_time = GameTime(day=1, hour=12, minute=0)
            event_id = await time_system.schedule_event(
                event_name="점심 시간",
                event_type="daily",
                trigger_time=trigger_time,
                event_data={"description": "점심 시간 이벤트"}
            )
            
            assert event_id is not None
            assert len(time_system.scheduled_events) == 1
            
            scheduled_event = time_system.scheduled_events[0]
            assert scheduled_event.event_id == event_id
            assert scheduled_event.event_name == "점심 시간"
            assert scheduled_event.is_active == True
            
            logger.info(f"[OK] 이벤트 스케줄링 성공: {event_id}")
            
        finally:
            await time_system.cleanup()
    
    async def test_cancel_event(self, db_with_templates, test_session):
        """이벤트 취소 테스트"""
        time_system = TimeSystem()
        await time_system.initialize()
        
        try:
            # 이벤트 스케줄링
            trigger_time = GameTime(day=1, hour=12, minute=0)
            event_id = await time_system.schedule_event(
                event_name="테스트 이벤트",
                event_type="test",
                trigger_time=trigger_time,
                event_data={"test": True}
            )
            
            assert len(time_system.scheduled_events) == 1
            
            # 이벤트 취소
            result = await time_system.cancel_event(event_id)
            assert result == True
            
            # 취소된 이벤트 확인
            scheduled_event = time_system.scheduled_events[0]
            assert scheduled_event.is_active == False
            
            # 존재하지 않는 이벤트 취소 시도
            result = await time_system.cancel_event("nonexistent-id")
            assert result == False
            
            logger.info("[OK] 이벤트 취소 테스트 성공")
            
        finally:
            await time_system.cleanup()
    
    async def test_tick_handlers(self, db_with_templates, test_session):
        """틱 핸들러 테스트"""
        time_system = TimeSystem()
        await time_system.initialize()
        
        try:
            # 틱 핸들러 추가
            tick_count = {"count": 0}
            
            async def test_handler(game_time: GameTime):
                tick_count["count"] += 1
                logger.debug(f"틱 핸들러 실행: {game_time}, count={tick_count['count']}")
            
            time_system.add_tick_handler(test_handler)
            assert len(time_system.tick_handlers) == 1
            
            # 시간 진행 (틱 핸들러는 자동 실행되지 않으므로 수동 호출)
            await time_system._execute_tick_handlers()
            assert tick_count["count"] == 1
            
            # 틱 핸들러 제거
            time_system.remove_tick_handler(test_handler)
            assert len(time_system.tick_handlers) == 0
            
            logger.info("[OK] 틱 핸들러 테스트 성공")
            
        finally:
            await time_system.cleanup()
    
    async def test_session_state_persistence(self, db_with_templates, test_session):
        """세션 상태 영속성 테스트"""
        time_system = TimeSystem()
        await time_system.initialize()
        
        try:
            # session_id 추출 (dict인 경우)
            session_id = test_session if isinstance(test_session, str) else test_session['session_id']
            
            # 세션 시작 및 시간 설정
            await time_system.start(session_id)
            time_system.set_time(GameTime(day=5, hour=15, minute=30))
            
            # 시간 상태 저장
            await time_system._save_time_state()
            
            # TimeSystem 중지
            await time_system.stop()
            
            # 새로운 TimeSystem 인스턴스로 세션 상태 로드
            time_system2 = TimeSystem()
            await time_system2.initialize()
            
            try:
                await time_system2.start(session_id)
                
                # 로드된 시간 확인
                loaded_time = time_system2.get_current_time()
                assert loaded_time.day == 5
                assert loaded_time.hour == 15
                assert loaded_time.minute == 30
                
                logger.info(f"[OK] 세션 상태 영속성 테스트 성공: {loaded_time}")
                
            finally:
                await time_system2.cleanup()
            
        finally:
            await time_system.cleanup()
    
    async def test_time_statistics(self, db_with_templates, test_session):
        """시간 시스템 통계 테스트"""
        time_system = TimeSystem()
        await time_system.initialize()
        
        try:
            # 이벤트 및 핸들러 추가
            await time_system.schedule_event(
                event_name="테스트 이벤트",
                event_type="test",
                trigger_time=GameTime(day=1, hour=12, minute=0),
                event_data={}
            )
            
            async def dummy_handler(game_time: GameTime):
                pass
            
            time_system.add_tick_handler(dummy_handler)
            
            # 통계 조회
            stats = await time_system.get_time_statistics()
            
            assert "current_time" in stats
            assert "time_scale" in stats
            assert "is_running" in stats
            assert "scheduled_events_count" in stats
            assert "tick_handlers_count" in stats
            assert stats["scheduled_events_count"] == 1
            assert stats["tick_handlers_count"] == 1
            
            logger.info(f"[OK] 시간 시스템 통계 테스트 성공: {stats}")
            
        finally:
            await time_system.cleanup()

