/**
 * 지도 편집 컴포넌트
 */
import React from 'react';
import { MapCanvas } from '../MapCanvas';
import { HierarchicalMapView, MapLevel } from '../HierarchicalMapView';
import { EditorTool } from '../../../types';

export interface MapEditorProps {
  mapViewMode: 'world' | 'hierarchical' | 'cell';
  currentMapLevel: MapLevel;
  currentMapEntityId: string | null;
  selectedCellId: string | null;
  mapState: any;
  pins: any[];
  roads: any[];
  selectedPin: string | null;
  selectedRoad: string | null;
  currentTool: EditorTool;
  onPinClick: (pinId: string) => void;
  onPinDoubleClick: (pinId: string) => void;
  onPinDrag: (pinId: string, x: number, y: number) => Promise<void>;
  onRoadClick: (roadId: string) => void;
  onMapClick: (x: number, y: number) => Promise<void>;
  onMouseMove: (x: number, y: number) => void;
  onNavigateToCell?: (cellId: string, previousLocationId?: string | null) => void;
  onNavigateToLocation?: (locationId: string) => void;
  onNavigateToRegion?: (regionId: string) => void;
  onNavigateBack?: () => void;
}

export const MapEditor: React.FC<MapEditorProps> = ({
  mapViewMode,
  currentMapLevel,
  currentMapEntityId,
  selectedCellId,
  mapState,
  pins,
  roads,
  selectedPin,
  selectedRoad,
  currentTool,
  onPinClick,
  onPinDoubleClick,
  onPinDrag,
  onRoadClick,
  onMapClick,
  onMouseMove,
  onNavigateToCell,
  onNavigateToLocation,
  onNavigateToRegion,
  onNavigateBack,
}) => {
  if (mapViewMode === 'cell' && selectedCellId) {
    return (
      <HierarchicalMapView
        currentLevel="cell"
        currentEntityId={selectedCellId}
        onLevelChange={(level, entityId) => {
          if (level === 'world' && onNavigateBack) {
            onNavigateBack();
          }
        }}
        onEntitySelect={(entityId: string, entityType: string) => {
          if (entityType === 'cell' && onNavigateToCell) {
            onNavigateToCell(entityId);
          } else if (entityType === 'location' && onNavigateToLocation) {
            onNavigateToLocation(entityId);
          } else if (entityType === 'region' && onNavigateToRegion) {
            onNavigateToRegion(entityId);
          }
        }}
      />
    );
  }

  if (mapViewMode === 'hierarchical' && currentMapEntityId) {
    return (
      <HierarchicalMapView
        currentLevel={currentMapLevel}
        currentEntityId={currentMapEntityId}
        onLevelChange={(level, entityId) => {
          if (level === 'world' && onNavigateBack) {
            onNavigateBack();
          }
        }}
        onEntitySelect={(entityId: string, entityType: string) => {
          if (entityType === 'cell' && onNavigateToCell) {
            onNavigateToCell(entityId);
          } else if (entityType === 'location' && onNavigateToLocation) {
            onNavigateToLocation(entityId);
          } else if (entityType === 'region' && onNavigateToRegion) {
            onNavigateToRegion(entityId);
          }
        }}
      />
    );
  }

  return (
    <MapCanvas
      mapState={mapState}
      pins={pins}
      roads={roads}
      selectedPin={selectedPin}
      selectedRoad={selectedRoad}
      currentTool={currentTool}
      onPinClick={onPinClick}
      onPinDoubleClick={onPinDoubleClick}
      onPinDrag={onPinDrag}
      onRoadClick={onRoadClick}
      onMapClick={onMapClick}
      onMouseMove={onMouseMove}
      currentMapLevel={mapViewMode === 'world' ? 'world' : undefined}
    />
  );
};

