/**
 * 게임 액션 처리 로직 Hook
 */
import { useState, useCallback } from 'react';
import { useGameStore } from '../../store/gameStore';
import { gameApi } from '../../services/gameApi';
import { GameAction } from '../../types/game';

export const useGameActions = () => {
  const {
    gameState,
    currentCell,
    setGameState,
    setCurrentCell,
    setCurrentMessage,
    setLoading,
    setError,
    addHistory,
  } = useGameStore();

  const [availableActions, setAvailableActions] = useState<GameAction[]>([]);
  const [discoveredObjects, setDiscoveredObjects] = useState<Set<string>>(new Set());

  const handleActionSelect = useCallback(async (action: GameAction) => {
    if (!gameState) return;

    try {
      setLoading(true);
      
      switch (action.action_type) {
        case 'move':
          if (action.target_id) {
            const response = await gameApi.movePlayer(gameState.session_id, action.target_id);
            setGameState(response.game_state);
            
            const newCell = await gameApi.getCurrentCell(gameState.session_id);
            setCurrentCell(newCell);
            
            setCurrentMessage({
              text: `${newCell.cell_name}로 이동했습니다.`,
              message_type: 'narration',
              timestamp: Date.now(),
            });
            
            const actions = await gameApi.getAvailableActions(gameState.session_id);
            setAvailableActions(actions);
          }
          break;
          
        case 'dialogue':
          if (action.target_id) {
            const dialogue = await gameApi.startDialogue(gameState.session_id, action.target_id);
            setCurrentMessage({
              text: dialogue.messages[0]?.text || '대화를 시작합니다.',
              character_name: dialogue.npc_name,
              message_type: 'dialogue',
              timestamp: Date.now(),
            });
          }
          break;
          
        case 'interact':
          if (action.target_id) {
            const response = await gameApi.interactWithEntity(gameState.session_id, action.target_id);
            setCurrentMessage({
              text: response.message || `${action.target_name}와 상호작용했습니다.`,
              message_type: 'system',
              timestamp: Date.now(),
            });
          }
          break;
          
        case 'observe':
          if (currentCell && currentCell.objects) {
            const allObjectIds = currentCell.objects.map(obj => 
              obj.object_id || (obj as any).runtime_object_id || (obj as any).game_object_id
            ).filter(id => id);
            setDiscoveredObjects(prev => new Set([...prev, ...allObjectIds]));
            
            const objectNames = currentCell.objects.map(obj => obj.object_name).join(', ');
            setCurrentMessage({
              text: action.description || `주변을 관찰하니 ${objectNames} 등이 보입니다.`,
              message_type: 'narration',
              timestamp: Date.now(),
            });
            
            const actions = await gameApi.getAvailableActions(gameState.session_id);
            setAvailableActions(actions);
          }
          break;
          
        case 'examine':
          if (action.target_id && currentCell) {
            const targetEntity = currentCell.entities.find(e => e.entity_id === action.target_id);
            
            if (targetEntity) {
              try {
                const response = await gameApi.interactWithEntity(
                  gameState.session_id,
                  action.target_id,
                  'examine'
                );
                
                setCurrentMessage({
                  text: response.message,
                  message_type: 'narration',
                  timestamp: Date.now(),
                });
                
                // 엔티티 조사 후 액션 목록 업데이트
                const actions = await gameApi.getAvailableActions(gameState.session_id);
                setAvailableActions(actions);
              } catch (error) {
                setCurrentMessage({
                  text: action.description || `${action.target_name}를 살펴봅니다.`,
                  message_type: 'narration',
                  timestamp: Date.now(),
                });
              }
            } else if (action.target_type === 'object') {
              // 오브젝트 조사
              try {
                const response = await gameApi.interactWithObject(
                  gameState.session_id,
                  action.target_id,
                  'examine'
                );
                
                setCurrentMessage({
                  text: response.message || action.description || `${action.target_name}를 살펴봅니다.`,
                  message_type: 'narration',
                  timestamp: Date.now(),
                });
                
                // 오브젝트 조사 후 액션 목록 업데이트 (해당 오브젝트에 대한 액션들이 나타남)
                const actions = await gameApi.getAvailableActions(gameState.session_id);
                setAvailableActions(actions);
              } catch (error) {
                setCurrentMessage({
                  text: action.description || `${action.target_name}를 살펴봅니다.`,
                  message_type: 'narration',
                  timestamp: Date.now(),
                });
              }
            } else {
              setCurrentMessage({
                text: action.description || `${action.target_name}를 살펴봅니다.`,
                message_type: 'narration',
                timestamp: Date.now(),
              });
            }
          }
          break;
          
        case 'open':
        case 'close':
        case 'light':
        case 'extinguish':
        case 'sit':
        case 'rest':
          if (action.target_id && action.target_type === 'object') {
            try {
              const response = await gameApi.interactWithObject(
                gameState.session_id,
                action.target_id,
                action.action_type
              );
              
              setCurrentMessage({
                text: response.message || `${action.target_name}와 상호작용했습니다.`,
                message_type: 'system',
                timestamp: Date.now(),
              });
              
              if (['open', 'close', 'light', 'extinguish'].includes(action.action_type)) {
                const cell = await gameApi.getCurrentCell(gameState.session_id);
                setCurrentCell(cell);
                const actions = await gameApi.getAvailableActions(gameState.session_id);
                setAvailableActions(actions);
              }
            } catch (error) {
              setError(error instanceof Error ? error.message : '상호작용 실패');
              setCurrentMessage({
                text: `상호작용에 실패했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`,
                message_type: 'system',
                timestamp: Date.now(),
              });
            }
          }
          break;
          
        case 'pickup':
          // pickup 액션은 GameView에서 ObjectInventoryModal을 통해 처리
          // 여기서는 모달을 열기 위한 콜백이 필요하지만, 
          // useGameActions는 hook이므로 모달 상태 관리는 GameView에서 처리
          // 따라서 pickup 액션은 GameView의 handleActionSelect에서 직접 처리됨
          break;
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : '액션을 처리할 수 없습니다.';
      setError(errorMessage);
      console.error('액션 처리 실패:', error);
    } finally {
      setLoading(false);
    }
  }, [gameState, currentCell, setGameState, setCurrentCell, setCurrentMessage, setLoading, setError]);

  const loadAvailableActions = useCallback(async () => {
    if (!gameState) return;
    try {
      const actions = await gameApi.getAvailableActions(gameState.session_id);
      setAvailableActions(actions);
    } catch (error) {
      console.error('액션 로드 실패:', error);
    }
  }, [gameState]);

  return {
    availableActions,
    discoveredObjects,
    setDiscoveredObjects,
    handleActionSelect,
    loadAvailableActions,
    setAvailableActions,
  };
};

