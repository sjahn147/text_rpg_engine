/**
 * 게임 상태 관리 (Zustand) - RPG 엔진용
 */

import { create } from 'zustand';
import { GameState, CellInfo, GameMessage, DialogueInfo } from '../types/game';

export interface HistoryEntry {
  cellId: string;
  characterName?: string;
  text: string;
  timestamp: number;
}

interface GameStore {
  gameState: GameState | null;
  currentCell: CellInfo | null;
  currentDialogue: DialogueInfo | null;
  currentMessage: GameMessage | null;
  isLoading: boolean;
  error: string | null;
  textSpeed: number; // 타이핑 속도 (ms)
  isAutoMode: boolean; // 자동 진행 모드
  isSkipMode: boolean; // 스킵 모드
  history: HistoryEntry[]; // 대화/액션 기록
  isInfoPanelOpen: boolean; // 정보 패널 (인벤토리, 시간, 저널)
  discoveredObjects: Set<string>; // 발견된 오브젝트 ID 목록
  
  setGameState: (state: GameState) => void;
  setCurrentCell: (cell: CellInfo) => void;
  setCurrentDialogue: (dialogue: DialogueInfo | null) => void;
  setCurrentMessage: (message: GameMessage | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setTextSpeed: (speed: number) => void;
  setAutoMode: (enabled: boolean) => void;
  setSkipMode: (enabled: boolean) => void;
  addHistory: (entry: HistoryEntry) => void;
  clearHistory: () => void;
  toggleInfoPanel: () => void;
  setDiscoveredObjects: (objects: Set<string>) => void;
  reset: () => void;
}

export const useGameStore = create<GameStore>((set) => ({
  gameState: null,
  currentCell: null,
  currentDialogue: null,
  currentMessage: null,
  isLoading: false,
  error: null,
  textSpeed: 30,
  isAutoMode: false,
  isSkipMode: false,
  history: [],
  isInfoPanelOpen: false,
  discoveredObjects: new Set<string>(),

  setGameState: (state) => set({ gameState: state }),
  setCurrentCell: (cell) => set({ currentCell: cell }),
  setCurrentDialogue: (dialogue) => set({ currentDialogue: dialogue }),
  setCurrentMessage: (message) => set({ currentMessage: message }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setTextSpeed: (speed) => set({ textSpeed: speed }),
  setAutoMode: (enabled) => set({ isAutoMode: enabled }),
  setSkipMode: (enabled) => set({ isSkipMode: enabled }),
  addHistory: (entry) => set((state) => ({ 
    history: [...state.history, entry].slice(-1000) // 최대 1000개 유지
  })),
  clearHistory: () => set({ history: [] }),
  toggleInfoPanel: () => set((state) => ({ isInfoPanelOpen: !state.isInfoPanelOpen })),
  setDiscoveredObjects: (objects) => set({ discoveredObjects: objects }),
  reset: () => set({
    gameState: null,
    currentCell: null,
    currentDialogue: null,
    currentMessage: null,
    isLoading: false,
    error: null,
    textSpeed: 30,
    isAutoMode: false,
    isSkipMode: false,
    history: [],
    isInfoPanelOpen: false,
    discoveredObjects: new Set<string>(),
  }),
}));

