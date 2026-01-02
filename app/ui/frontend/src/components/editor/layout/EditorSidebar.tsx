/**
 * 에디터 사이드바 컴포넌트
 */
import React from 'react';
import { EntityExplorer, EntityType } from '../EntityExplorer';
import { PinTreeView } from '../PinTreeView';

export interface EditorSidebarProps {
  explorerMode: 'map' | 'explorer';
  onExplorerModeChange: (mode: 'map' | 'explorer') => void;
  onEntitySelect: (entityType: EntityType, entityId: string) => void;
  onAddPinToMap?: (entityType: EntityType, entityId: string, entityName: string) => Promise<void>;
  pins: any[];
  regions: any[];
  locations: any[];
  cells: any[];
  selectedPin: string | null;
  onPinSelect: (pinId: string | null) => void;
  searchQuery?: string;
  onSearchQueryChange?: (query: string) => void;
}

export const EditorSidebar: React.FC<EditorSidebarProps> = ({
  explorerMode,
  onExplorerModeChange,
  onEntitySelect,
  onAddPinToMap,
  pins,
  regions,
  locations,
  cells,
  selectedPin,
  onPinSelect,
  searchQuery,
  onSearchQueryChange,
}) => {
  return (
    <div style={{ 
      width: '250px', 
      backgroundColor: '#f5f5f5', 
      borderRight: '1px solid #ddd', 
      display: 'flex', 
      flexDirection: 'column', 
      overflow: 'hidden' 
    }}>
      <div style={{ 
        display: 'flex', 
        borderBottom: '1px solid #ddd',
        backgroundColor: '#fff',
      }}>
        <button
          onClick={() => onExplorerModeChange('map')}
          style={{
            flex: 1,
            padding: '8px',
            border: 'none',
            borderRight: '1px solid #ddd',
            backgroundColor: explorerMode === 'map' ? '#e3f2fd' : '#fff',
            cursor: 'pointer',
            fontSize: '12px',
          }}
        >
          지도
        </button>
        <button
          onClick={() => onExplorerModeChange('explorer')}
          style={{
            flex: 1,
            padding: '8px',
            border: 'none',
            backgroundColor: explorerMode === 'explorer' ? '#e3f2fd' : '#fff',
            cursor: 'pointer',
            fontSize: '12px',
          }}
        >
          탐색기
        </button>
      </div>
      {explorerMode === 'explorer' ? (
        <EntityExplorer
          onEntitySelect={onEntitySelect}
          onAddPinToMap={onAddPinToMap}
          searchQuery={searchQuery}
          onSearchQueryChange={onSearchQueryChange}
          selectedEntityType={undefined}
          selectedEntityId={null}
        />
      ) : (
        <PinTreeView
          pins={pins}
          selectedPin={selectedPin}
          onPinSelect={onPinSelect}
        />
      )}
    </div>
  );
};

