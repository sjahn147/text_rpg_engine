/**
 * 상태바 컴포넌트
 */
import React from 'react';

interface StatusBarProps {
  status?: 'ready' | 'loading' | 'saving' | 'error';
  statusMessage?: string;
  selectedEntityType?: string;
  selectedEntityId?: string | null;
  selectedCount?: number;
  mouseX?: number;
  mouseY?: number;
  selectedX?: number;
  selectedY?: number;
  zoomLevel?: number;
  fps?: number;
  websocketConnected?: boolean;
  autoSaveEnabled?: boolean;
  autoSaveStatus?: 'saved' | 'saving' | 'pending';
}

export const StatusBar: React.FC<StatusBarProps> = ({
  status = 'ready',
  statusMessage,
  selectedEntityType,
  selectedEntityId,
  selectedCount = 0,
  mouseX,
  mouseY,
  selectedX,
  selectedY,
  zoomLevel = 100,
  fps,
  websocketConnected = false,
  autoSaveEnabled = false,
  autoSaveStatus = 'saved',
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'ready':
        return '#4CAF50';
      case 'loading':
        return '#2196F3';
      case 'saving':
        return '#FF9800';
      case 'error':
        return '#F44336';
      default:
        return '#999';
    }
  };

  const getAutoSaveIcon = () => {
    switch (autoSaveStatus) {
      case 'saved':
        return '✓';
      case 'saving':
        return '⟳';
      case 'pending':
        return '○';
      default:
        return '';
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        height: '24px',
        backgroundColor: '#f5f5f5',
        borderTop: '1px solid #ddd',
        fontSize: '11px',
        padding: '0 8px',
        gap: '16px',
        userSelect: 'none',
      }}
    >
      {/* 상태 표시기 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <div
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: getStatusColor(),
          }}
        />
        <span style={{ color: '#666' }}>
          {statusMessage || status.toUpperCase()}
        </span>
        {websocketConnected && (
          <span style={{ color: '#4CAF50', marginLeft: '4px' }}>●</span>
        )}
        {autoSaveEnabled && (
          <span
            style={{
              color: autoSaveStatus === 'saved' ? '#4CAF50' : '#FF9800',
              marginLeft: '4px',
              fontSize: '10px',
            }}
            title={`Auto-save: ${autoSaveStatus}`}
          >
            {getAutoSaveIcon()}
          </span>
        )}
      </div>

      {/* 선택 정보 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        <span style={{ color: '#999' }}>Selected:</span>
        {selectedCount > 0 ? (
          <span style={{ color: '#333', fontWeight: 'bold' }}>
            {selectedCount} {selectedCount === 1 ? 'item' : 'items'}
          </span>
        ) : selectedEntityType && selectedEntityId ? (
          <span style={{ color: '#333' }}>
            {selectedEntityType} ({selectedEntityId})
          </span>
        ) : (
          <span style={{ color: '#999' }}>None</span>
        )}
      </div>

      {/* 좌표 정보 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        <span style={{ color: '#999' }}>Position:</span>
        {selectedX !== undefined && selectedY !== undefined ? (
          <span style={{ color: '#333' }}>
            ({selectedX}, {selectedY})
          </span>
        ) : mouseX !== undefined && mouseY !== undefined ? (
          <span style={{ color: '#666' }}>
            ({mouseX}, {mouseY})
          </span>
        ) : (
          <span style={{ color: '#999' }}>(-, -)</span>
        )}
      </div>

      {/* 뷰 정보 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginLeft: 'auto' }}>
        <span style={{ color: '#999' }}>Zoom:</span>
        <span style={{ color: '#333' }}>{zoomLevel.toFixed(0)}%</span>
        {fps !== undefined && (
          <>
            <span style={{ color: '#999', marginLeft: '12px' }}>FPS:</span>
            <span
              style={{
                color: fps >= 30 ? '#4CAF50' : fps >= 15 ? '#FF9800' : '#F44336',
                fontWeight: 'bold',
              }}
            >
              {fps}
            </span>
          </>
        )}
      </div>
    </div>
  );
};

