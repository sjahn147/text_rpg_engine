"""
TimeSystem 모듈 - 시간 기반 시뮬레이션 엔진
게임 내 시간 진행, 이벤트 스케줄링, NPC 행동 패턴 관리
"""
import asyncio
import sys
import os
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.connection import DatabaseConnection
from common.utils.logger import logger
from common.error_handling.error_types import (
    ErrorContext, BusinessLogicError, SystemError
)

class TimeScale(str, Enum):
    """시간 가속 배율"""
    REAL_TIME = "real_time"      # 실시간 (1:1)
    FAST = "fast"                # 빠름 (1:10)
    VERY_FAST = "very_fast"      # 매우 빠름 (1:100)
    INSTANT = "instant"          # 즉시 (무한대)

class TimePeriod(str, Enum):
    """게임 내 시간대 (테스트 호환 최소 정의)"""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"

@dataclass
class GameTime:
    """게임 내 시간"""
    day: int = 1
    hour: int = 6
    minute: int = 0
    second: int = 0
    
    def __str__(self) -> str:
        return f"Day {self.day}, {self.hour:02d}:{self.minute:02d}:{self.second:02d}"
    
    def to_dict(self) -> Dict[str, int]:
        return {
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second
        }
    
    def from_dict(self, data: Dict[str, int]) -> "GameTime":
        return GameTime(
            day=data.get("day", 1),
            hour=data.get("hour", 6),
            minute=data.get("minute", 0),
            second=data.get("second", 0)
        )

@dataclass
class ScheduledEvent:
    """스케줄된 이벤트"""
    event_id: str
    event_name: str
    event_type: str
    trigger_time: GameTime
    event_data: Dict[str, Any]
    handler: Optional[Callable] = None
    is_active: bool = True
    repeat_interval: Optional[int] = None  # 분 단위 반복 간격

class TimeSystem:
    """시간 기반 시뮬레이션 엔진"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.current_time = GameTime()
        self.time_scale = TimeScale.REAL_TIME
        self.is_running = False
        self.scheduled_events: List[ScheduledEvent] = []
        self.tick_handlers: List[Callable] = []
        self.tick_interval = 1.0  # 초 단위
        self._tick_task: Optional[asyncio.Task] = None
        self._session_id: Optional[str] = None  # 현재 세션 ID 저장
        
        # 시간 가속 배율 매핑
        self.scale_multipliers = {
            TimeScale.REAL_TIME: 1.0,
            TimeScale.FAST: 10.0,
            TimeScale.VERY_FAST: 100.0,
            TimeScale.INSTANT: float('inf')
        }
    
    async def initialize(self):
        """TimeSystem 초기화"""
        try:
            await self.db.initialize()
            logger.info("TimeSystem 초기화 완료")
        except Exception as e:
            logger.error(f"TimeSystem 초기화 실패: {e}")
            raise
    
    async def cleanup(self):
        """TimeSystem 정리"""
        try:
            await self.stop()
            await self.db.close()
            logger.info("TimeSystem 정리 완료")
        except Exception as e:
            logger.error(f"TimeSystem 정리 실패: {e}")
    
    async def start(self, session_id: str):
        """시간 시스템 시작"""
        if self.is_running:
            logger.warning("TimeSystem이 이미 실행 중입니다")
            return
        
        try:
            # 세션 ID 저장
            self._session_id = session_id
            
            # 세션 상태 로드
            await self._load_session_state(session_id)
            
            # 시간 시스템 시작
            self.is_running = True
            self._tick_task = asyncio.create_task(self._tick_loop())
            
            logger.info(f"TimeSystem 시작: {self.current_time} (Session: {session_id})")
            
        except Exception as e:
            logger.error(f"TimeSystem 시작 실패: {e}")
            raise SystemError(
                message=f"TimeSystem 시작 실패: {str(e)}",
                error_code="TIMESYSTEM_START_FAILED",
                context=ErrorContext(session_id=session_id)
            )
    
    async def stop(self):
        """시간 시스템 중지"""
        if not self.is_running:
            return
        
        try:
            # 마지막 시간 상태 저장
            if self._session_id:
                await self._save_time_state()
            
            self.is_running = False
            
            if self._tick_task:
                self._tick_task.cancel()
                try:
                    await self._tick_task
                except asyncio.CancelledError:
                    pass
            
            logger.info(f"TimeSystem 중지 (Session: {self._session_id})")
            self._session_id = None
            
        except Exception as e:
            logger.error(f"TimeSystem 중지 실패: {e}")
    
    async def _tick_loop(self):
        """시간 틱 루프"""
        while self.is_running:
            try:
                # 시간 진행
                await self._advance_time()
                
                # 스케줄된 이벤트 확인
                await self._check_scheduled_events()
                
                # 틱 핸들러 실행
                await self._execute_tick_handlers()
                
                # DB에 시간 상태 저장
                await self._save_time_state()
                
                # 다음 틱까지 대기
                await asyncio.sleep(self.tick_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"틱 루프 오류: {e}")
                await asyncio.sleep(1.0)  # 오류 시 1초 대기
    
    async def _advance_time(self):
        """시간 진행"""
        # 시간 가속 배율 적용
        multiplier = self.scale_multipliers[self.time_scale]
        
        if multiplier == float('inf'):
            # 즉시 모드: 시간을 즉시 진행
            self.current_time.second += 60
        else:
            # 일반 모드: 가속 배율 적용
            self.current_time.second += int(1 * multiplier)
        
        # 시간 정규화
        self._normalize_time()
    
    def _normalize_time(self):
        """시간 정규화 (초 -> 분 -> 시간 -> 일)"""
        while self.current_time.second >= 60:
            self.current_time.second -= 60
            self.current_time.minute += 1
        
        while self.current_time.minute >= 60:
            self.current_time.minute -= 60
            self.current_time.hour += 1
        
        while self.current_time.hour >= 24:
            self.current_time.hour -= 24
            self.current_time.day += 1
    
    async def _check_scheduled_events(self):
        """스케줄된 이벤트 확인"""
        current_time = self.current_time
        
        for event in self.scheduled_events:
            if not event.is_active:
                continue
            
            # 이벤트 트리거 시간 확인
            if (event.trigger_time.day == current_time.day and
                event.trigger_time.hour == current_time.hour and
                event.trigger_time.minute == current_time.minute):
                
                try:
                    # 이벤트 실행
                    await self._execute_event(event)
                    
                    # 반복 이벤트 처리
                    if event.repeat_interval:
                        event.trigger_time.minute += event.repeat_interval
                        self._normalize_time()
                    
                except Exception as e:
                    logger.error(f"이벤트 실행 실패: {event.event_name} - {e}")
    
    async def _execute_event(self, event: ScheduledEvent):
        """이벤트 실행"""
        logger.info(f"🎯 이벤트 실행: {event.event_name} at {self.current_time}")
        
        # 이벤트 핸들러 실행
        if event.handler:
            await event.handler(event.event_data)
        
        # DB에 이벤트 기록
        await self._log_event(event)
    
    async def _log_event(self, event: ScheduledEvent):
        """이벤트 로깅"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO runtime_data.triggered_events 
                    (session_id, event_type, event_data, triggered_at)
                    VALUES ($1, $2, $3, $4)
                """, 
                event.event_data.get("session_id"),
                event.event_type,
                json.dumps(event.event_data),
                datetime.now()
                )
        except Exception as e:
            logger.error(f"이벤트 로깅 실패: {e}")
    
    async def _execute_tick_handlers(self):
        """틱 핸들러 실행"""
        for handler in self.tick_handlers:
            try:
                await handler(self.current_time)
            except Exception as e:
                logger.error(f"틱 핸들러 실행 실패: {e}")
    
    async def _load_session_state(self, session_id: str):
        """세션 상태 로드"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # UUID 타입 변환 (필요시)
                result = await conn.fetchrow("""
                    SELECT current_day, current_hour, current_minute, last_tick
                    FROM runtime_data.session_states
                    WHERE session_id = $1::uuid
                """, session_id)
                
                if result:
                    self.current_time = GameTime(
                        day=result['current_day'] or 1,
                        hour=result['current_hour'] or 6,
                        minute=result['current_minute'] or 0
                    )
                    logger.info(f"📅 세션 상태 로드: {self.current_time}")
                else:
                    # 새 세션 상태 생성
                    await self._create_session_state(session_id)
                    
        except Exception as e:
            logger.error(f"세션 상태 로드 실패: {e}")
            raise
    
    async def _create_session_state(self, session_id: str):
        """새 세션 상태 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO runtime_data.session_states 
                    (session_id, current_day, current_hour, current_minute, last_tick)
                    VALUES ($1::uuid, $2, $3, $4, $5)
                    ON CONFLICT (session_id) DO UPDATE
                    SET current_day = EXCLUDED.current_day,
                        current_hour = EXCLUDED.current_hour,
                        current_minute = EXCLUDED.current_minute,
                        last_tick = EXCLUDED.last_tick,
                        updated_at = CURRENT_TIMESTAMP
                """, 
                session_id,
                self.current_time.day,
                self.current_time.hour,
                self.current_time.minute,
                datetime.now()
                )
            logger.info(f"📅 새 세션 상태 생성: {self.current_time}")
        except Exception as e:
            logger.error(f"세션 상태 생성 실패: {e}")
            raise
    
    async def _save_time_state(self):
        """시간 상태 저장"""
        if not self._session_id:
            logger.warning("세션 ID가 없어 시간 상태를 저장할 수 없습니다")
            return
            
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                await conn.execute("""
                    UPDATE runtime_data.session_states
                    SET current_day = $1, current_hour = $2, current_minute = $3, 
                        last_tick = $4, updated_at = $5
                    WHERE session_id = $6::uuid
                """, 
                self.current_time.day,
                self.current_time.hour,
                self.current_time.minute,
                datetime.now(),
                datetime.now(),
                self._session_id
                )
        except Exception as e:
            logger.error(f"시간 상태 저장 실패: {e}")
    
    async def schedule_event(
        self,
        event_name: str,
        event_type: str,
        trigger_time: GameTime,
        event_data: Dict[str, Any],
        handler: Optional[Callable] = None,
        repeat_interval: Optional[int] = None
    ) -> str:
        """이벤트 스케줄링"""
        event_id = str(uuid.uuid4())
        
        event = ScheduledEvent(
            event_id=event_id,
            event_name=event_name,
            event_type=event_type,
            trigger_time=trigger_time,
            event_data=event_data,
            handler=handler,
            repeat_interval=repeat_interval
        )
        
        self.scheduled_events.append(event)
        logger.info(f"📅 이벤트 스케줄링: {event_name} at {trigger_time}")
        
        return event_id
    
    async def cancel_event(self, event_id: str) -> bool:
        """이벤트 취소"""
        for event in self.scheduled_events:
            if event.event_id == event_id:
                event.is_active = False
                logger.info(f"이벤트 취소: {event.event_name}")
                return True
        return False
    
    def add_tick_handler(self, handler: Callable):
        """틱 핸들러 추가"""
        self.tick_handlers.append(handler)
        logger.info(f"➕ 틱 핸들러 추가: {handler.__name__}")
    
    def remove_tick_handler(self, handler: Callable):
        """틱 핸들러 제거"""
        if handler in self.tick_handlers:
            self.tick_handlers.remove(handler)
            logger.info(f"➖ 틱 핸들러 제거: {handler.__name__}")
    
    def set_time_scale(self, scale: TimeScale):
        """시간 가속 배율 설정"""
        self.time_scale = scale
        logger.info(f"⏰ 시간 가속 배율 변경: {scale.value}")
    
    def get_current_time(self) -> GameTime:
        """현재 시간 조회"""
        return self.current_time
    
    def set_time(self, time: GameTime):
        """시간 설정"""
        self.current_time = time
        logger.info(f"시간 설정: {time}")
    
    async def advance_time(self, minutes: int):
        """시간 수동 진행"""
        self.current_time.minute += minutes
        self._normalize_time()
        # 이모지 제거하여 Windows 인코딩 문제 해결
        logger.info(f"시간 수동 진행: +{minutes}분 -> {self.current_time}")
    
    def get_scheduled_events(self) -> List[ScheduledEvent]:
        """스케줄된 이벤트 조회"""
        return [event for event in self.scheduled_events if event.is_active]
    
    async def get_time_statistics(self) -> Dict[str, Any]:
        """시간 시스템 통계"""
        return {
            "current_time": self.current_time.to_dict(),
            "time_scale": self.time_scale.value,
            "is_running": self.is_running,
            "scheduled_events_count": len(self.get_scheduled_events()),
            "tick_handlers_count": len(self.tick_handlers),
            "tick_interval": self.tick_interval
        }

# 전역 TimeSystem 인스턴스
time_system = TimeSystem()

# 편의 함수들
async def start_time_system(session_id: str):
    """시간 시스템 시작 편의 함수"""
    await time_system.start(session_id)

async def stop_time_system():
    """시간 시스템 중지 편의 함수"""
    await time_system.stop()

async def schedule_event(
    event_name: str,
    event_type: str,
    trigger_time: GameTime,
    event_data: Dict[str, Any],
    handler: Optional[Callable] = None,
    repeat_interval: Optional[int] = None
) -> str:
    """이벤트 스케줄링 편의 함수"""
    return await time_system.schedule_event(
        event_name, event_type, trigger_time, event_data, handler, repeat_interval
    )

def get_current_time() -> GameTime:
    """현재 시간 조회 편의 함수"""
    return time_system.get_current_time()

def set_time_scale(scale: TimeScale):
    """시간 가속 배율 설정 편의 함수"""
    time_system.set_time_scale(scale)