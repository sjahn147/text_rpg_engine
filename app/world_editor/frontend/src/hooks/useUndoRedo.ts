/**
 * Undo/Redo 시스템 Hook
 */
import { useState, useCallback, useRef } from 'react';

export interface HistoryAction {
  type: string;
  description: string;
  undo: () => void;
  redo: () => void;
  timestamp: number;
}

interface UseUndoRedoOptions {
  maxHistorySize?: number;
}

export const useUndoRedo = (options: UseUndoRedoOptions = {}) => {
  const { maxHistorySize = 50 } = options;
  const [history, setHistory] = useState<HistoryAction[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const isExecutingRef = useRef(false);

  const canUndo = historyIndex >= 0;
  const canRedo = historyIndex < history.length - 1;

  const executeAction = useCallback((action: HistoryAction, isRedo: boolean = false) => {
    if (isRedo) {
      action.redo();
    } else {
      action.undo();
    }
  }, []);

  const addAction = useCallback((action: HistoryAction) => {
    if (isExecutingRef.current) {
      return; // Undo/Redo 실행 중에는 히스토리에 추가하지 않음
    }

    setHistory((prev) => {
      // 현재 인덱스 이후의 히스토리 제거 (새로운 액션 추가 시)
      const newHistory = prev.slice(0, historyIndex + 1);
      
      // 최대 크기 제한
      if (newHistory.length >= maxHistorySize) {
        newHistory.shift();
      } else {
        setHistoryIndex(newHistory.length);
      }

      return [...newHistory, action];
    });
  }, [historyIndex, maxHistorySize]);

  const undo = useCallback(() => {
    if (!canUndo) return;

    isExecutingRef.current = true;
    const action = history[historyIndex];
    executeAction(action, false);
    setHistoryIndex((prev) => prev - 1);
    isExecutingRef.current = false;
  }, [canUndo, history, historyIndex, executeAction]);

  const redo = useCallback(() => {
    if (!canRedo) return;

    isExecutingRef.current = true;
    const action = history[historyIndex + 1];
    executeAction(action, true);
    setHistoryIndex((prev) => prev + 1);
    isExecutingRef.current = false;
  }, [canRedo, history, historyIndex, executeAction]);

  const clearHistory = useCallback(() => {
    setHistory([]);
    setHistoryIndex(-1);
  }, []);

  const getHistoryInfo = useCallback(() => {
    return {
      canUndo,
      canRedo,
      historySize: history.length,
      currentIndex: historyIndex,
      nextUndo: canUndo ? history[historyIndex] : null,
      nextRedo: canRedo ? history[historyIndex + 1] : null,
    };
  }, [canUndo, canRedo, history, historyIndex]);

  return {
    addAction,
    undo,
    redo,
    clearHistory,
    canUndo,
    canRedo,
    getHistoryInfo,
  };
};

