/**
 * 통합 UI 메인 앱 - Editor/Game 모드 전환
 */
import React, { useState } from 'react';
import { EditorMode } from './modes/EditorMode';
import { GameMode } from './modes/GameMode';

function App() {
  // URL 파라미터로 모드 확인
  const urlParams = new URLSearchParams(window.location.search);
  const urlMode = urlParams.get('mode') as 'editor' | 'game' | null;
  
  const [mode, setMode] = useState<'editor' | 'game'>(urlMode || 'editor');
  
  return (
    <div className="app-container" style={{ width: '100vw', height: '100vh', overflow: 'hidden' }}>
      {/* 모드 전환 버튼 (개발용) */}
      <div className="fixed top-4 left-4 z-50">
        <button
          onClick={() => setMode(mode === 'editor' ? 'game' : 'editor')}
          className="px-4 py-2 bg-white/20 text-black rounded-lg hover:bg-white/30 transition-colors"
          style={{
            padding: '0.5rem 1rem',
            background: 'rgba(255, 255, 255, 0.2)',
            color: '#000000',
            borderRadius: '0.5rem',
            border: 'none',
            cursor: 'pointer',
            backdropFilter: 'blur(10px)',
            WebkitBackdropFilter: 'blur(10px)',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
            fontSize: '14px',
            fontWeight: 400,
          }}
        >
          {mode === 'editor' ? '게임 모드' : '에디터 모드'}
        </button>
      </div>
      
      {mode === 'editor' ? <EditorMode /> : <GameMode />}
    </div>
  );
}

export default App;
