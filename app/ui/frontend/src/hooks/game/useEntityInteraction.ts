/**
 * 엔티티 상호작용 처리 Hook
 */
import { useCallback } from 'react';
import { useGameStore } from '../../store/gameStore';
import { gameApi } from '../../services/gameApi';
import { EntityInfo } from '../../types/game';

export const useEntityInteraction = () => {
  const {
    gameState,
    setCurrentMessage,
    setLoading,
    setError,
  } = useGameStore();

  const handleEntityAction = useCallback(async (
    entity: EntityInfo,
    actionId: string
  ) => {
    if (!gameState) return;

    const entityId = entity.entity_id || '';

    try {
      setLoading(true);
      setError(null);

      if (actionId === 'examine') {
        try {
          const response = await gameApi.interactWithEntity(
            gameState.session_id,
            entityId,
            'examine'
          );
          
          setCurrentMessage({
            text: response.message || `${entity.entity_name}를 살펴봅니다.`,
            message_type: 'narration',
            timestamp: Date.now(),
          });
        } catch (error) {
          console.error('엔티티 조사 실패:', error);
          setCurrentMessage({
            text: `${entity.entity_name}를 살펴봅니다.`,
            message_type: 'narration',
            timestamp: Date.now(),
          });
        }
      } else if (actionId === 'dialogue' && entity.dialogue_id) {
        const dialogue = await gameApi.startDialogue(gameState.session_id, entityId);
        setCurrentMessage({
          text: dialogue.messages[0]?.text || '대화를 시작합니다.',
          character_name: dialogue.npc_name,
          message_type: 'dialogue',
          timestamp: Date.now(),
        });
      } else if (actionId === 'interact') {
        const response = await gameApi.interactWithEntity(
          gameState.session_id,
          entityId
        );
        setCurrentMessage({
          text: response.message || `${entity.entity_name}와 상호작용했습니다.`,
          message_type: 'system',
          timestamp: Date.now(),
        });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '상호작용 실패';
      setError(errorMessage);
      console.error('엔티티 상호작용 실패:', error);
    } finally {
      setLoading(false);
    }
  }, [gameState, setCurrentMessage, setLoading, setError]);

  return {
    handleEntityAction,
  };
};

