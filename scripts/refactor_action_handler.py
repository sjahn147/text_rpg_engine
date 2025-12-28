"""
ActionHandler의 오브젝트 상호작용 핸들러 메서드를 분리된 핸들러로 위임하도록 변경하는 스크립트
"""
import re
from pathlib import Path

# 매핑: ActionHandler 메서드 -> 분리된 핸들러 메서드
HANDLER_MAPPINGS = {
    # 정보 확인
    'handle_inspect_object': ('info_handler', 'handle_inspect'),
    'handle_search_object': ('info_handler', 'handle_search'),
    
    # 상태 변경
    'handle_extinguish_object': ('state_handler', 'handle_extinguish'),
    'handle_activate_object': ('state_handler', 'handle_activate'),
    'handle_deactivate_object': ('state_handler', 'handle_deactivate'),
    'handle_lock_object': ('state_handler', 'handle_lock'),
    'handle_unlock_object': ('state_handler', 'handle_unlock'),
    
    # 위치 변경
    'handle_stand_from_object': ('position_handler', 'handle_stand'),
    'handle_lie_on_object': ('position_handler', 'handle_lie'),
    'handle_get_up_from_object': ('position_handler', 'handle_get_up'),
    'handle_climb_object': ('position_handler', 'handle_climb'),
    'handle_descend_from_object': ('position_handler', 'handle_descend'),
    
    # 회복
    'handle_sleep_at_object': ('recovery_handler', 'handle_sleep'),
    'handle_meditate_at_object': ('recovery_handler', 'handle_meditate'),
    
    # 소비
    'handle_eat_from_object': ('consumption_handler', 'handle_eat'),
    'handle_drink_from_object': ('consumption_handler', 'handle_drink'),
    'handle_consume_object': ('consumption_handler', 'handle_consume'),
    
    # 학습
    'handle_read_object': ('learning_handler', 'handle_read'),
    'handle_study_object': ('learning_handler', 'handle_study'),
    'handle_write_object': ('learning_handler', 'handle_write'),
    
    # 아이템 조작
    'handle_place_in_object': ('item_handler', 'handle_place'),
    'handle_take_from_object': ('item_handler', 'handle_take'),
    'handle_put_in_object': ('item_handler', 'handle_put'),
    
    # 조합/제작
    'handle_combine_with_object': ('crafting_handler', 'handle_combine'),
    'handle_craft_at_object': ('crafting_handler', 'handle_craft'),
    'handle_cook_at_object': ('crafting_handler', 'handle_cook'),
    'handle_repair_object': ('crafting_handler', 'handle_repair'),
    
    # 파괴/변형
    'handle_destroy_object': ('destruction_handler', 'handle_destroy'),
    'handle_break_object': ('destruction_handler', 'handle_break'),
    'handle_dismantle_object': ('destruction_handler', 'handle_dismantle'),
    
    # 기타
    'handle_use_object': None,  # TODO: 별도 핸들러 필요
}

def refactor_handler_method(file_path: Path, method_name: str, handler_attr: str, handler_method: str):
    """특정 핸들러 메서드를 분리된 핸들러로 위임하도록 변경"""
    content = file_path.read_text(encoding='utf-8')
    
    # 메서드 시그니처 찾기
    pattern = rf'(async def {method_name}\s*\([^)]*\)\s*->\s*ActionResult:.*?""".*?""".*?)(?=async def |def |\Z)'
    
    def replace_method(match):
        method_body = match.group(1)
        
        # 간단한 위임 코드로 교체
        new_body = f'''async def {method_name}(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """{method_name.replace('handle_', '').replace('_', ' ')}"""
        if not hasattr(self, '{handler_attr}'):
            return ActionResult.failure_result("{handler_attr} 핸들러가 초기화되지 않았습니다.")
        return await self.{handler_attr}.{handler_method}(entity_id, target_id, parameters)
    
'''
        return new_body
    
    new_content = re.sub(pattern, replace_method, content, flags=re.DOTALL)
    
    if new_content != content:
        file_path.write_text(new_content, encoding='utf-8')
        print(f"✅ {method_name} 리팩토링 완료")
        return True
    else:
        print(f"⚠️ {method_name} 변경 없음 (이미 위임되었거나 패턴 불일치)")
        return False

if __name__ == '__main__':
    file_path = Path('app/handlers/action_handler.py')
    
    if not file_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        exit(1)
    
    print("ActionHandler 리팩토링 시작...")
    print("=" * 60)
    
    refactored_count = 0
    for method_name, mapping in HANDLER_MAPPINGS.items():
        if mapping is None:
            print(f"⏭️ {method_name} - 스킵 (별도 처리 필요)")
            continue
        
        handler_attr, handler_method = mapping
        if refactor_handler_method(file_path, method_name, handler_attr, handler_method):
            refactored_count += 1
    
    print("=" * 60)
    print(f"✅ 총 {refactored_count}개 메서드 리팩토링 완료")

