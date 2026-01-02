/**
 * 오브젝트 상호작용 처리 Hook
 */
import { useCallback } from 'react';
import { useGameStore } from '../../store/gameStore';
import { gameApi } from '../../services/gameApi';
import { WorldObjectInfo } from '../../types/game';

interface UseObjectInteractionCallbacks {
  onPickupRequest?: (objectId: string, objectName: string) => void;
  onCellChange?: () => void;
}

export const useObjectInteraction = (callbacks?: UseObjectInteractionCallbacks) => {
  const {
    gameState,
    setGameState,
    setCurrentCell,
    setCurrentMessage,
    setLoading,
    setError,
    setDiscoveredObjects,
  } = useGameStore();

  const handleObjectAction = useCallback(async (
    object: WorldObjectInfo,
    actionId: string
  ) => {
    if (!gameState) return;

    const objId = object.object_id || 
                  (object as any).runtime_object_id || 
                  (object as any).game_object_id || 
                  '';
    
    if (!objId) {
      console.error('오브젝트 ID가 없습니다:', object);
      setError('오브젝트 ID를 찾을 수 없습니다.');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      if (actionId === 'pickup') {
        // 오브젝트 인벤토리 모달 표시
        if (callbacks?.onPickupRequest) {
          callbacks.onPickupRequest(objId, object.object_name || '오브젝트');
        }
        return;
      }

      if (actionId === 'move') {
        // 이동 액션: 오브젝트의 연결된 셀로 이동
        const connectedCell = object.properties?.connected_cell || 
                             object.properties?.leads_to || 
                             null;
        
        if (!connectedCell) {
          setError('이동할 수 있는 곳이 없습니다.');
          return;
        }
        
        try {
          // game_cell_id를 전달 (백엔드에서 runtime_cell_id로 변환)
          const response = await gameApi.movePlayer(
            gameState.session_id,
            connectedCell
          );
          
          if (response.success) {
            setGameState(response.game_state);
            
            // 새로운 셀 정보 로드
            const cell = await gameApi.getCurrentCell(gameState.session_id);
            setCurrentCell(cell);
            
            // 새로운 액션 조회 및 발견된 오브젝트 초기화는 콜백으로 처리
            if (callbacks?.onCellChange) {
              await callbacks.onCellChange();
            }
            
            setCurrentMessage({
              text: response.message || '이동했습니다.',
              message_type: 'narration',
              timestamp: Date.now(),
            });
          }
        } catch (error) {
          console.error('이동 실패:', error);
          setError('이동에 실패했습니다.');
        }
        return;
      }

      // 일반 오브젝트 상호작용
      console.log('오브젝트 상호작용 요청:', {
        sessionId: gameState.session_id,
        objectId: objId,
        actionId: actionId,
        object: object
      });
      
      const response = await gameApi.interactWithObject(
        gameState.session_id,
        objId,
        actionId
      );
      
      if (response && response.message) {
        setCurrentMessage({
          text: response.message,
          message_type: actionId === 'examine' ? 'narration' : 'system',
          timestamp: Date.now(),
        });
      } else {
        setCurrentMessage({
          text: `${object.object_name || '오브젝트'}와 상호작용했습니다.`,
          message_type: 'system',
          timestamp: Date.now(),
        });
      }
      
      // 열기/닫기 액션의 경우 상태가 변경되므로 셀 정보 새로고침
      if (actionId === 'open' || actionId === 'close') {
        const cell = await gameApi.getCurrentCell(gameState.session_id);
        setCurrentCell(cell);
        if (callbacks?.onCellChange) {
          callbacks.onCellChange();
        }
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '상호작용 실패';
      setError(errorMessage);
      console.error('오브젝트 상호작용 실패:', error);
    } finally {
      setLoading(false);
    }
  }, [gameState, setGameState, setCurrentCell, setCurrentMessage, setLoading, setError, callbacks]);

  return {
    handleObjectAction,
  };
};

