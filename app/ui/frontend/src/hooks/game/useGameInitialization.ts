/**
 * 게임 초기화 로직 Hook
 */
import { useState, useCallback } from 'react';
import { useGameStore } from '../../store/gameStore';
import { gameApi } from '../../services/gameApi';

export const useGameInitialization = () => {
  const {
    setGameState,
    setCurrentCell,
    setCurrentMessage,
    setLoading,
    setError,
  } = useGameStore();

  const [isInitialized, setIsInitialized] = useState(false);

  const initializeGame = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // 헬스 체크 (옵션)
      try {
        await gameApi.healthCheck();
      } catch (error) {
        console.warn('헬스 체크 실패, 게임 시작 계속 진행:', error);
      }

      // 새 게임 시작
      const playerTemplateId = 'e655a931-d989-4ca6-b3ce-737f6b426978'; // 임시: DB에서 확인한 플레이어 엔티티 ID
      const startCellId = 'CELL_INN_ROOM_001'; // 여관 내 방
      const response = await gameApi.startNewGame(playerTemplateId, startCellId);
      setGameState(response.game_state);

      // 현재 셀 정보 로드
      const cell = await gameApi.getCurrentCell(response.game_state.session_id);
      setCurrentCell(cell);

      // 초기 메시지 설정
      setCurrentMessage({
        text: cell.description || `${cell.cell_name}에 도착했습니다.`,
        message_type: 'narration',
        timestamp: Date.now(),
      });

      // 사용 가능한 액션 조회
      const actions = await gameApi.getAvailableActions(response.game_state.session_id);
      
      setIsInitialized(true);
      return { success: true, actions };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : '게임을 시작할 수 없습니다.';
      setError(errorMessage);
      console.error('게임 초기화 실패:', error);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [setGameState, setCurrentCell, setCurrentMessage, setLoading, setError]);

  return {
    isInitialized,
    initializeGame,
    setIsInitialized,
  };
};


