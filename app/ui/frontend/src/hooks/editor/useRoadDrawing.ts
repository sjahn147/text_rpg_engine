/**
 * 도로 그리기 상태 관리 훅
 */
import { useState, useCallback } from 'react';

export interface RoadDrawingState {
  fromPinId: string | null;
  drawing: boolean;
}

export interface RoadDrawingActions {
  startDrawing: (fromPinId: string) => void;
  finishDrawing: () => void;
  cancelDrawing: () => void;
  isDrawing: () => boolean;
}

export const useRoadDrawing = () => {
  const [roadDrawingState, setRoadDrawingState] = useState<RoadDrawingState>({
    fromPinId: null,
    drawing: false,
  });

  const startDrawing = useCallback((fromPinId: string) => {
    setRoadDrawingState({ fromPinId, drawing: true });
  }, []);

  const finishDrawing = useCallback(() => {
    setRoadDrawingState({ fromPinId: null, drawing: false });
  }, []);

  const cancelDrawing = useCallback(() => {
    setRoadDrawingState({ fromPinId: null, drawing: false });
  }, []);

  const isDrawing = useCallback(() => {
    return roadDrawingState.drawing;
  }, [roadDrawingState.drawing]);

  return {
    // State
    roadDrawingState,
    // Actions
    startDrawing,
    finishDrawing,
    cancelDrawing,
    isDrawing,
  };
};

