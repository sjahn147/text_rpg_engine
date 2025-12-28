/**
 * Game 모드 - 텍스트 어드벤처 게임 UI
 */
import React from 'react';
import { GameView } from '../components/game/GameView';

export const GameMode: React.FC = () => {
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100vh',
      width: '100vw',
      position: 'relative',
      overflow: 'hidden',
      margin: 0,
      padding: 0
    }}>
      <GameView />
    </div>
  );
};

