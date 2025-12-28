/**
 * 메인 게임 화면 - 실제 게임 플레이
 */
import React, { useEffect } from 'react';
import { GameView } from '../../components/game/GameView';
import { useGameInitialization } from '../../hooks/game/useGameInitialization';
import type { GameScreenType } from '../../hooks/game/useGameNavigation';

interface MainGameScreenProps {
  onNavigate?: (screen: GameScreenType) => void;
}

export const MainGameScreen: React.FC<MainGameScreenProps> = ({ onNavigate }) => {
  const { isInitialized, initializeGame } = useGameInitialization();

  useEffect(() => {
    if (!isInitialized) {
      initializeGame();
    }
  }, [isInitialized, initializeGame]);

  return <GameView onNavigate={onNavigate} />;
};
