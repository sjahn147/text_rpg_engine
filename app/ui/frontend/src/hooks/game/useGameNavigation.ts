/**
 * 게임 화면 전환 로직 Hook
 */
import { useState, useCallback } from 'react';

export type GameScreenType = 
  | 'intro'
  | 'main'
  | 'inventory'
  | 'character'
  | 'journal'
  | 'map'
  | 'saveLoad'
  | 'settings'
  | 'gameOver';

export const useGameNavigation = (initialScreen: GameScreenType = 'intro') => {
  const [currentScreen, setCurrentScreen] = useState<GameScreenType>(initialScreen);

  const navigate = useCallback((screen: GameScreenType) => {
    setCurrentScreen(screen);
  }, []);

  const goBack = useCallback(() => {
    setCurrentScreen('main');
  }, []);

  return {
    currentScreen,
    navigate,
    goBack,
  };
};
