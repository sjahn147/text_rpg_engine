---
id: TODO-003-rest-timesystem-integration
type: todo
status: development
sub_status: implement_green
task_id: TASK-004-timesystem-integration
file: app/handlers/object_interactions/recovery.py
line: 12
code_snippet: |
  async def handle_rest(
      self,
      entity_id: str,
      target_id: Optional[str] = None,
      parameters: Optional[Dict[str, Any]] = None
  ) -> ActionResult:
keyword: rest-timesystem-integration
created_at: 2026-01-01T17:15:00Z
updated_at: 2026-01-01T17:15:00Z
author: agent
---

# rest 액션에 TimeSystem 연동 추가

## 설명

`recovery.py`의 `handle_rest` 메서드에 TimeSystem 연동을 추가합니다.

## 작업 내용

### 현재 상태
- `handle_sleep`에는 TimeSystem 연동이 있음 (132-140줄)
- `handle_rest`에는 TimeSystem 연동이 없음

### 구현 계획
1. `rest_config`에서 `time_cost` 확인 (기본값: 30분)
2. TimeSystem을 통해 시간 진행
3. 에러 처리 및 로깅

## 구현 코드

```python
# TimeSystem 연동 (30분)
time_cost = rest_config.get('time_cost', 30)
if time_cost > 0:
    from app.systems.time_system import TimeSystem
    time_system = TimeSystem()
    try:
        await time_system.advance_time(minutes=time_cost)
    except Exception as e:
        self.logger.warning(f"TimeSystem 연동 실패: {str(e)}")
```

## 관련 파일

- `app/handlers/object_interactions/recovery.py` (12-74줄)

## 관련 Task

- [TASK-004-timesystem-integration](../06-task/TASK-004-timesystem-integration.md)

## 테스트 파일

- `tests/active/integration/test_recovery_handler_timesystem.py`

## 구현 상태

- [x] 요구사항 분석 완료 ✅
- [x] 구현 (implement_green) ✅
- [x] 테스트 작성 ✅
- [ ] 품질 게이트 통과 (quality_gate)

