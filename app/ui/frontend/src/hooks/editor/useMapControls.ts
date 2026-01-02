/**
 * 지도 컨트롤 (줌, 그리드 등) 훅
 */
import { useCallback } from 'react';

export interface MapControlsActions {
  zoomIn: () => void;
  zoomOut: () => void;
  zoomToFit: () => void;
  zoomToSelection: () => void;
  toggleGrid: () => void;
  setGridSize: (size: number) => void;
}

export const useMapControls = (
  mapState: any,
  updateMap: (updates: any) => void,
  selectedPin: string | null,
  pins: any[],
  onStatusMessage?: (message: string) => void
) => {
  const zoomIn = useCallback(() => {
    if (mapState) {
      const newZoom = Math.min(3, (mapState.zoom_level || 1.0) + 0.1);
      updateMap({ zoom_level: newZoom });
    }
  }, [mapState, updateMap]);

  const zoomOut = useCallback(() => {
    if (mapState) {
      const newZoom = Math.max(0.5, (mapState.zoom_level || 1.0) - 0.1);
      updateMap({ zoom_level: newZoom });
    }
  }, [mapState, updateMap]);

  const zoomToFit = useCallback(() => {
    if (mapState) {
      const canvasWidth = window.innerWidth - 600;
      const canvasHeight = window.innerHeight - 100;
      const scaleX = canvasWidth / mapState.width;
      const scaleY = canvasHeight / mapState.height;
      const newZoom = Math.min(scaleX, scaleY, 3) * 0.9;
      updateMap({ zoom_level: Math.max(0.5, newZoom) });
      onStatusMessage?.('맵에 맞춤');
    }
  }, [mapState, updateMap, onStatusMessage]);

  const zoomToSelection = useCallback(() => {
    if (selectedPin && mapState) {
      const pin = pins.find(p => p.pin_id === selectedPin);
      if (pin) {
        const newZoom = Math.min(2, (mapState.zoom_level || 1.0) * 1.5);
        updateMap({ zoom_level: newZoom });
        onStatusMessage?.('선택된 핀에 맞춤');
      }
    } else {
      alert('줌할 대상을 선택하세요.');
    }
  }, [selectedPin, mapState, pins, updateMap, onStatusMessage]);

  const toggleGrid = useCallback(() => {
    if (mapState) {
      updateMap({ grid_enabled: !mapState.grid_enabled });
    }
  }, [mapState, updateMap]);

  const setGridSize = useCallback((size: number) => {
    if (mapState && size > 0) {
      updateMap({ grid_size: size });
      onStatusMessage?.(`그리드 크기가 ${size}로 설정되었습니다.`);
    }
  }, [mapState, updateMap, onStatusMessage]);

  return {
    zoomIn,
    zoomOut,
    zoomToFit,
    zoomToSelection,
    toggleGrid,
    setGridSize,
  };
};

