/**
 * 핀 트리뷰 컴포넌트
 */
import React, { useState } from 'react';
import { PinData } from '../../types';

interface PinTreeViewProps {
  pins: PinData[];
  selectedPin: string | null;
  onPinSelect: (pinId: string) => void;
  onPinDelete?: (pinId: string) => void;
}

export const PinTreeView: React.FC<PinTreeViewProps> = ({
  pins,
  selectedPin,
  onPinSelect,
  onPinDelete,
}) => {
  const [expandedTypes, setExpandedTypes] = useState<Set<string>>(new Set(['region', 'location', 'cell']));

  const toggleType = (type: string) => {
    const newExpanded = new Set(expandedTypes);
    if (newExpanded.has(type)) {
      newExpanded.delete(type);
    } else {
      newExpanded.add(type);
    }
    setExpandedTypes(newExpanded);
  };

  // 핀을 타입별로 그룹화
  const pinsByType = pins.reduce((acc, pin) => {
    if (!acc[pin.pin_type]) {
      acc[pin.pin_type] = [];
    }
    acc[pin.pin_type].push(pin);
    return acc;
  }, {} as Record<string, PinData[]>);

  const typeLabels: Record<string, string> = {
    region: '지역',
    location: '위치',
    cell: '셀',
  };

  const typeColors: Record<string, string> = {
    region: '#FF6B9D',
    location: '#4ECDC4',
    cell: '#95E1D3',
  };

  return (
    <div style={{
      padding: '10px',
      height: '100%',
      overflowY: 'auto',
      backgroundColor: '#f9f9f9',
    }}>
      <h3 style={{ margin: '0 0 10px 0', fontSize: '16px', fontWeight: 'bold' }}>
        핀 목록 ({pins.length})
      </h3>
      
      {Object.entries(pinsByType).map(([type, typePins]) => (
        <div key={type} style={{ marginBottom: '5px' }}>
          <div
            onClick={() => toggleType(type)}
            style={{
              padding: '5px 10px',
              backgroundColor: typeColors[type] || '#ccc',
              color: '#fff',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              borderRadius: '3px',
              fontWeight: 'bold',
            }}
          >
            <span>
              {expandedTypes.has(type) ? '▼' : '▶'} {typeLabels[type] || type} ({typePins.length})
            </span>
          </div>
          
          {expandedTypes.has(type) && (
            <div style={{ marginLeft: '10px', marginTop: '5px' }}>
              {typePins.map((pin) => (
                <div
                  key={pin.pin_id}
                  onClick={() => onPinSelect(pin.pin_id)}
                  style={{
                    padding: '5px 10px',
                    marginBottom: '2px',
                    backgroundColor: selectedPin === pin.pin_id ? '#e3f2fd' : '#fff',
                    border: selectedPin === pin.pin_id ? '2px solid #2196f3' : '1px solid #ddd',
                    borderRadius: '3px',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 'bold', fontSize: '12px' }}>
                      {pin.pin_name || `새 핀 ${pin.pin_id.slice(-4)}`}
                    </div>
                    <div style={{ fontSize: '10px', color: '#666' }}>
                      ({pin.x}, {pin.y})
                    </div>
                  </div>
                  {onPinDelete && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm(`핀 "${pin.pin_name || pin.pin_id}"를 삭제하시겠습니까?`)) {
                          onPinDelete(pin.pin_id);
                        }
                      }}
                      style={{
                        padding: '2px 6px',
                        fontSize: '10px',
                        backgroundColor: '#f44336',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '3px',
                        cursor: 'pointer',
                      }}
                    >
                      삭제
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
      
      {pins.length === 0 && (
        <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
          핀이 없습니다.<br />
          '핀 추가' 버튼을 클릭하고 맵을 클릭하여 핀을 추가하세요.
        </div>
      )}
    </div>
  );
};

