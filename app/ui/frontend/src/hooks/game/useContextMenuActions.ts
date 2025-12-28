/**
 * ContextMenu 액션 목록 생성 Hook
 */
import { useMemo } from 'react';
import { WorldObjectInfo, EntityInfo } from '../../types/game';

interface ContextMenuAction {
  id: string;
  label: string;
  icon?: string;
}

export const useContextMenuActions = (
  object?: WorldObjectInfo,
  entity?: EntityInfo
): ContextMenuAction[] => {
  return useMemo(() => {
    const actions: ContextMenuAction[] = [];

    if (object) {
      const interactionType = object.properties?.interaction_type || 
                             (object as any).interaction_type;
      const contents = (object.properties?.contents as string[]) || [];
      
      // 현재 상태 확인
      const currentState = object.properties?.current_state || 
                          object.properties?.state ||
                          (object as any).current_state || 
                          (object as any).state ||
                          'closed';
      
      // 연결된 셀 확인
      const connectedCell = object.properties?.connected_cell || 
                           object.properties?.leads_to || 
                           null;
      
      // 조사하기 (항상 가능)
      actions.push({ id: 'examine', label: '조사', icon: '🔍' });
      
      // 상호작용 타입에 따른 액션
      if (interactionType === 'openable') {
        if (currentState === 'closed' || currentState === 'default') {
          actions.push({ id: 'open', label: '열기', icon: '📦' });
        } else if (currentState === 'open') {
          actions.push({ id: 'close', label: '닫기', icon: '📦' });
          // 열려있고 연결된 셀이 있으면 이동 버튼 표시
          if (connectedCell) {
            actions.push({ id: 'move', label: '이동', icon: '🚪' });
          }
        }
      } else if (interactionType === 'lightable') {
        actions.push({ id: 'light', label: '불', icon: '🕯️' });
      } else if (interactionType === 'sitable') {
        actions.push({ id: 'sit', label: '앉기', icon: '🪑' });
      } else if (interactionType === 'restable') {
        actions.push({ id: 'rest', label: '쉬기', icon: '🛏️' });
      }
      
      // 내용물이 있으면 줍기
      if (contents.length > 0) {
        actions.push({ id: 'pickup', label: '줍기', icon: '📥' });
      }
    } else if (entity) {
      // 조사하기 (항상 가능)
      actions.push({ id: 'examine', label: '조사', icon: '🔍' });
      
      // 대화하기
      if (entity.dialogue_id) {
        actions.push({ id: 'dialogue', label: '대화', icon: '💬' });
      }
      
      // 상호작용하기
      if (entity.can_interact) {
        actions.push({ id: 'interact', label: '상호작용', icon: '🤝' });
      }
    }

    return actions;
  }, [object, entity]);
};


