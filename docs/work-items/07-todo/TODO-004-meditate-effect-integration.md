---
id: TODO-004-meditate-effect-integration
type: todo
status: development
sub_status: implement_green
task_id: TASK-005-effect-system-integration
file: app/handlers/object_interactions/recovery.py
line: 158
code_snippet: |
  async def handle_meditate(
      self,
      entity_id: str,
      target_id: Optional[str] = None,
      parameters: Optional[Dict[str, Any]] = None
  ) -> ActionResult:
keyword: meditate-effect-integration
created_at: 2026-01-01T17:20:00Z
updated_at: 2026-01-01T17:20:00Z
author: agent
---

# meditate 액션에 EffectCarrierManager 연동 추가

## 설명

`recovery.py`의 `handle_meditate` 메서드에 EffectCarrierManager 연동을 추가합니다.

## 작업 내용

### 현재 상태
- `handle_meditate`에는 EffectCarrierManager 연동이 없음
- MP 회복만 처리하고 있음

### 구현 계획
1. `meditate_config`에서 `effect_carrier_id` 확인
2. EffectCarrierManager를 통해 효과 적용
3. 에러 처리 및 로깅

## 구현 코드

```python
# EffectCarrier 적용
effect_carrier_id = meditate_config.get('effect_carrier_id')
if effect_carrier_id and self.effect_carrier_manager:
    session_id = parameters.get("session_id") if parameters else None
    if session_id:
        effect_result = await self.effect_carrier_manager.grant_effect_to_entity(
            session_id=session_id,
            entity_id=entity_id,
            effect_id=effect_carrier_id,
            source=f"meditate_object:{game_object_id}"
        )
        if not effect_result.success:
            self.logger.warning(f"Effect Carrier 적용 실패: {effect_result.message}")
```

## 관련 파일

- `app/handlers/object_interactions/recovery.py` (158-210줄)

## 관련 Task

- [TASK-005-effect-system-integration](../06-task/TASK-005-effect-system-integration.md)

## 테스트 파일

- `tests/active/integration/test_recovery_handler_timesystem.py`

## 구현 상태

- [x] 요구사항 분석 완료 ✅
- [x] 구현 (implement_green) ✅
- [x] 테스트 작성 ✅
- [ ] 품질 게이트 통과 (quality_gate)

