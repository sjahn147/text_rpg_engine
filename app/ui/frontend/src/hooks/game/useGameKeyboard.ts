/**
 * 게임 키보드 단축키 로직 Hook
 */
import { useEffect } from 'react';
import { useGameStore } from '../../store/gameStore';
import { GameScreenType } from './useGameNavigation';

interface UseGameKeyboardProps {
  currentScreen: GameScreenType;
  onNavigate: (screen: GameScreenType) => void;
}

export const useGameKeyboard = ({ currentScreen, onNavigate }: UseGameKeyboardProps) => {
  const { isAutoMode, setAutoMode, isSkipMode, setSkipMode } = useGameStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // 메인 게임 화면에서만 화면 전환 단축키 활성화
      if (currentScreen === 'main') {
        // I: 인벤토리
        if (e.key === 'i' || e.key === 'I') {
          e.preventDefault();
          onNavigate('inventory');
          return;
        }
        // C: 캐릭터 정보
        if (e.key === 'c' || e.key === 'C') {
          e.preventDefault();
          onNavigate('character');
          return;
        }
        // J: 저널
        if (e.key === 'j' || e.key === 'J') {
          e.preventDefault();
          onNavigate('journal');
          return;
        }
        // M: 지도
        if (e.key === 'm' || e.key === 'M') {
          e.preventDefault();
          onNavigate('map');
          return;
        }
        // Ctrl+S: 저장/로드
        if ((e.key === 's' || e.key === 'S') && e.ctrlKey) {
          e.preventDefault();
          onNavigate('saveLoad');
          return;
        }
      }

      // 모든 화면에서 공통 단축키
      // ESC: 현재 화면 닫기 또는 설정 열기
      if (e.key === 'Escape') {
        e.preventDefault();
        if (currentScreen === 'main') {
          onNavigate('settings');
        } else {
          onNavigate('main');
        }
        return;
      }

      // A: 자동 모드 토글 (메인 화면에서만)
      if (currentScreen === 'main' && (e.key === 'a' || e.key === 'A')) {
        e.preventDefault();
        setAutoMode(!isAutoMode);
        return;
      }

      // Ctrl: 스킵 모드
      if (e.key === 'Control') {
        setSkipMode(true);
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.key === 'Control') {
        setSkipMode(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [currentScreen, onNavigate, isAutoMode, setAutoMode, setSkipMode]);
};

