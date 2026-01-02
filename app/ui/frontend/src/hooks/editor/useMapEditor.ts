/**
 * 지도 편집 상태 관리 훅
 */
import { useState, useCallback } from 'react';
import { MapLevel } from '../../components/editor/HierarchicalMapView';

export interface MapEditorState {
  mapViewMode: 'world' | 'hierarchical' | 'cell';
  currentMapLevel: MapLevel;
  currentMapEntityId: string | null;
  selectedCellId: string | null;
  previousLocationId: string | null;
}

export interface MapEditorActions {
  setMapViewMode: (mode: 'world' | 'hierarchical' | 'cell') => void;
  setCurrentMapLevel: (level: MapLevel) => void;
  setCurrentMapEntityId: (id: string | null) => void;
  setSelectedCellId: (id: string | null) => void;
  setPreviousLocationId: (id: string | null) => void;
  navigateToWorld: () => void;
  navigateToRegion: (regionId: string) => void;
  navigateToLocation: (locationId: string) => void;
  navigateToCell: (cellId: string, previousLocationId?: string | null) => void;
  navigateBack: () => void;
}

export const useMapEditor = () => {
  const [mapViewMode, setMapViewMode] = useState<'world' | 'hierarchical' | 'cell'>('world');
  const [currentMapLevel, setCurrentMapLevel] = useState<MapLevel>('world');
  const [currentMapEntityId, setCurrentMapEntityId] = useState<string | null>(null);
  const [selectedCellId, setSelectedCellId] = useState<string | null>(null);
  const [previousLocationId, setPreviousLocationId] = useState<string | null>(null);

  const navigateToWorld = useCallback(() => {
    setMapViewMode('world');
    setCurrentMapLevel('world');
    setCurrentMapEntityId(null);
    setSelectedCellId(null);
    setPreviousLocationId(null);
  }, []);

  const navigateToRegion = useCallback((regionId: string) => {
    setMapViewMode('hierarchical');
    setCurrentMapLevel('region');
    setCurrentMapEntityId(regionId);
    setSelectedCellId(null);
  }, []);

  const navigateToLocation = useCallback((locationId: string) => {
    setMapViewMode('hierarchical');
    setCurrentMapLevel('location');
    setCurrentMapEntityId(locationId);
    setSelectedCellId(null);
  }, []);

  const navigateToCell = useCallback((cellId: string, prevLocationId?: string | null) => {
    setMapViewMode('cell');
    setCurrentMapLevel('cell');
    setSelectedCellId(cellId);
    if (prevLocationId !== undefined) {
      setPreviousLocationId(prevLocationId);
    }
  }, []);

  const navigateBack = useCallback(() => {
    if (currentMapLevel === 'cell' && previousLocationId) {
      // Cell → Location
      navigateToLocation(previousLocationId);
      setPreviousLocationId(null);
    } else if (currentMapLevel === 'location') {
      // Location → Region (현재는 World로 이동)
      navigateToWorld();
    } else if (currentMapLevel === 'region') {
      // Region → World
      navigateToWorld();
    }
  }, [currentMapLevel, previousLocationId, navigateToLocation, navigateToWorld]);

  return {
    // State
    mapViewMode,
    currentMapLevel,
    currentMapEntityId,
    selectedCellId,
    previousLocationId,
    // Actions
    setMapViewMode,
    setCurrentMapLevel,
    setCurrentMapEntityId,
    setSelectedCellId,
    setPreviousLocationId,
    navigateToWorld,
    navigateToRegion,
    navigateToLocation,
    navigateToCell,
    navigateBack,
  };
};

