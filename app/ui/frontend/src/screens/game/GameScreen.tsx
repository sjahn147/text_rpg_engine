/**
 * 게임 화면 라우터 - 화면 전환 관리
 */
import React, { useState } from 'react';
import { IntroScreen } from '../../components/game/IntroScreen';
import { MainGameScreen } from './MainGameScreen';
import { InventoryScreen } from './InventoryScreen';
import { CharacterScreen } from './CharacterScreen';
import { SaveLoadScreen } from './SaveLoadScreen';
import { JournalScreen } from './JournalScreen';
import { MapScreen } from './MapScreen';
import { SettingsScreen } from './SettingsScreen';
import { GameOverScreen } from './GameOverScreen';
import { useGameNavigation } from '../../hooks/game/useGameNavigation';
import type { GameScreenType } from '../../hooks/game/useGameNavigation';
import { useGameKeyboard } from '../../hooks/game/useGameKeyboard';
import { useGameStore } from '../../store/gameStore';

export const GameScreen: React.FC = () => {
  const { currentScreen, navigate } = useGameNavigation('intro');
  const [saveLoadMode, setSaveLoadMode] = useState<'save' | 'load'>('save');
  
  // 키보드 단축키 설정
  useGameKeyboard({ currentScreen, onNavigate: navigate });

  const handleIntroComplete = () => {
    navigate('main');
  };

  return (
    <>
      {currentScreen === 'intro' && (
        <IntroScreen onComplete={handleIntroComplete} />
      )}
      {currentScreen === 'main' && (
        <MainGameScreen onNavigate={navigate} />
      )}
      {currentScreen === 'inventory' && (
        <InventoryScreen onClose={() => navigate('main')} />
      )}
      {currentScreen === 'character' && (
        <CharacterScreen onClose={() => navigate('main')} />
      )}
      {currentScreen === 'journal' && (
        <JournalScreen onClose={() => navigate('main')} />
      )}
      {currentScreen === 'map' && (
        <MapScreen onClose={() => navigate('main')} />
      )}
      {currentScreen === 'saveLoad' && (
        <SaveLoadScreen onClose={() => navigate('main')} mode={saveLoadMode} />
      )}
      {currentScreen === 'settings' && (
        <SettingsScreen onClose={() => navigate('main')} />
      )}
      {currentScreen === 'gameOver' && (
        <GameOverScreen
          onRestart={() => {
            // 게임 상태 초기화
            const { reset } = useGameStore.getState();
            reset();
            // 인트로 화면으로 이동
            navigate('intro');
          }}
          onLoadSave={() => {
            setSaveLoadMode('load');
            navigate('saveLoad');
          }}
          onMainMenu={() => {
            // 게임 상태 초기화
            const { reset } = useGameStore.getState();
            reset();
            navigate('intro');
          }}
        />
      )}
    </>
  );
};
