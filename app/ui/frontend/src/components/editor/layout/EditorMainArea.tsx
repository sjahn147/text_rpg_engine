/**
 * 에디터 메인 영역 컴포넌트
 */
import React from 'react';
import { MapEditor } from '../map/MapEditor';
import { EntityEditor } from '../EntityEditor';
import { EntityType } from '../EntityExplorer';
import { PinEditorNew as PinEditor } from '../PinEditorNew';
import { InfoPanel } from '../InfoPanel';
import { CellEntityManager } from '../CellEntityManager';
import { MapLevel } from '../HierarchicalMapView';

export interface EditorMainAreaProps {
  // Map Editor Props
  mapViewMode: 'world' | 'hierarchical' | 'cell';
  currentMapLevel: MapLevel;
  currentMapEntityId: string | null;
  selectedCellId: string | null;
  mapState: any;
  pins: any[];
  roads: any[];
  selectedPin: string | null;
  selectedRoad: string | null;
  currentTool: string;
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

  // Entity Editor Props
  explorerMode: 'map' | 'explorer';
  selectedEntityType: EntityType | undefined;
  selectedEntityId: string | null;
  onEntitySave: (entityType: EntityType, entityId: string, data: any) => Promise<void>;
  onEntityDelete: (entityType: EntityType, entityId: string) => Promise<void>;
  onEntityClose: () => void;
  onRefresh: () => Promise<void>;

  // Pin Editor Props
  regions: any[];
  locations: any[];
  cells: any[];
  onPinUpdate: (pinId: string, updates: any) => Promise<void>;
  onPinDelete: (pinId: string) => Promise<void>;
  onPinClose: () => void;
  sendMessage?: (message: any) => void;

  // Cell Manager Props
  showCellManager?: boolean;
}

export const EditorMainArea: React.FC<EditorMainAreaProps> = ({
  // Map Editor
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
  // Entity Editor
  explorerMode,
  selectedEntityType,
  selectedEntityId,
  onEntitySave,
  onEntityDelete,
  onEntityClose,
  onRefresh,
  // Pin Editor
  regions,
  locations,
  cells,
  onPinUpdate,
  onPinDelete,
  onPinClose,
  sendMessage,
  // Cell Manager
  showCellManager,
}) => {
  return (
    <div style={{ display: 'flex', flex: 1, minHeight: 0, overflow: 'hidden' }}>
      {/* 메인 편집 영역 */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {showCellManager && selectedCellId ? (
          <CellEntityManager 
            cellId={selectedCellId}
            onBack={onNavigateBack || (() => {})}
          />
        ) : (
          <MapEditor
            mapViewMode={mapViewMode}
            currentMapLevel={currentMapLevel}
            currentMapEntityId={currentMapEntityId}
            selectedCellId={selectedCellId}
            mapState={mapState}
            pins={pins}
            roads={roads}
            selectedPin={selectedPin}
            selectedRoad={selectedRoad}
            currentTool={currentTool as any}
            onPinClick={onPinClick}
            onPinDoubleClick={onPinDoubleClick}
            onPinDrag={onPinDrag}
            onRoadClick={onRoadClick}
            onMapClick={onMapClick}
            onMouseMove={onMouseMove}
            onNavigateToCell={onNavigateToCell}
            onNavigateToLocation={onNavigateToLocation}
            onNavigateToRegion={onNavigateToRegion}
            onNavigateBack={onNavigateBack}
          />
        )}
      </div>

      {/* 오른쪽 사이드바: 편집기 */}
      <div style={{ 
        width: '350px', 
        backgroundColor: '#f5f5f5', 
        borderLeft: '1px solid #ddd', 
        display: 'flex', 
        flexDirection: 'column', 
        overflow: 'hidden', 
        minHeight: 0 
      }}>
        {explorerMode === 'explorer' && selectedEntityType && selectedEntityId ? (
          <EntityEditor
            entityType={selectedEntityType}
            entityId={selectedEntityId}
            onSave={onEntitySave}
            onDelete={onEntityDelete}
            onClose={onEntityClose}
          />
        ) : selectedPin ? (
          <PinEditor
            pin={pins.find(p => p.pin_id === selectedPin) || null}
            regions={regions}
            locations={locations}
            cells={cells}
            onPinUpdate={onPinUpdate}
            onPinDelete={onPinDelete}
            onClose={onPinClose}
            onRefresh={onRefresh}
          />
        ) : (
          <InfoPanel
            selectedPin={null}
            selectedRoad={roads.find(r => r.road_id === selectedRoad) || null}
            regions={regions}
            locations={locations}
            cells={cells}
            onUpdate={(data) => {
              console.log('업데이트:', data);
            }}
          />
        )}
      </div>
    </div>
  );
};

