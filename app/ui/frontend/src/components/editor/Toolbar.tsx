/**
 * 도구 모음 컴포넌트
 */
import React from 'react';
import { EditorTool } from '../../types';

interface ToolbarProps {
  currentTool: EditorTool;
  onToolChange: (tool: EditorTool) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onGridToggle: () => void;
  gridEnabled: boolean;
}

export const Toolbar: React.FC<ToolbarProps> = ({
  currentTool,
  onToolChange,
  onZoomIn,
  onZoomOut,
  onGridToggle,
  gridEnabled,
}) => {
  return (
    <div className="toolbar" style={{
      display: 'flex',
      gap: '10px',
      padding: '10px',
      backgroundColor: '#f0f0f0',
      borderBottom: '1px solid #ccc',
    }}>
      <button
        className={`tool-button ${currentTool === 'select' ? 'active' : ''}`}
        onClick={() => onToolChange('select')}
        style={{
          padding: '8px 16px',
          cursor: 'pointer',
          backgroundColor: currentTool === 'select' ? '#4ECDC4' : '#fff',
        }}
      >
        선택
      </button>
      <button
        className={`tool-button ${currentTool === 'pin' ? 'active' : ''}`}
        onClick={() => onToolChange('pin')}
        style={{
          padding: '8px 16px',
          cursor: 'pointer',
          backgroundColor: currentTool === 'pin' ? '#4ECDC4' : '#fff',
        }}
      >
        핀 추가
      </button>
      <button
        className={`tool-button ${currentTool === 'road' ? 'active' : ''}`}
        onClick={() => onToolChange('road')}
        style={{
          padding: '8px 16px',
          cursor: 'pointer',
          backgroundColor: currentTool === 'road' ? '#4ECDC4' : '#fff',
        }}
      >
        도로 그리기
      </button>
      <div style={{ marginLeft: '20px', display: 'flex', gap: '10px' }}>
        <button onClick={onZoomIn} style={{ padding: '8px 16px' }}>
          확대
        </button>
        <button onClick={onZoomOut} style={{ padding: '8px 16px' }}>
          축소
        </button>
        <button
          onClick={onGridToggle}
          style={{
            padding: '8px 16px',
            backgroundColor: gridEnabled ? '#4ECDC4' : '#fff',
          }}
        >
          그리드 {gridEnabled ? 'ON' : 'OFF'}
        </button>
      </div>
    </div>
  );
};

