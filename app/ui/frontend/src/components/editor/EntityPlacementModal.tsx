/**
 * Entity 배치 모달 컴포넌트
 * Location 또는 Cell을 선택하여 맵에 배치
 */
import React, { useState, useEffect } from 'react';
import { locationsApi, cellsApi } from '../../services/api';

interface EntityPlacementModalProps {
  isOpen: boolean;
  level: 'region' | 'location';
  parentId: string;
  position: { x: number; y: number } | null;
  onClose: () => void;
  onSelect: (entityId: string, position: { x: number; y: number }) => void;
}

export const EntityPlacementModal: React.FC<EntityPlacementModalProps> = ({
  isOpen,
  level,
  parentId,
  position,
  onClose,
  onSelect,
}) => {
  const [entities, setEntities] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (isOpen && parentId) {
      loadEntities();
    }
  }, [isOpen, parentId, level]);

  const loadEntities = async () => {
    try {
      setLoading(true);
      if (level === 'region') {
        const response = await locationsApi.getByRegion(parentId);
        setEntities(response.data);
      } else if (level === 'location') {
        const response = await cellsApi.getByLocation(parentId);
        setEntities(response.data);
      }
    } catch (error) {
      console.error('엔티티 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredEntities = entities.filter((entity) => {
    const name = level === 'region' ? entity.location_name : entity.cell_name;
    return name?.toLowerCase().includes(searchQuery.toLowerCase());
  });

  if (!isOpen || !position) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        backgroundColor: '#fff',
        borderRadius: '8px',
        padding: '20px',
        width: '500px',
        maxHeight: '600px',
        display: 'flex',
        flexDirection: 'column',
      }}>
        <h3 style={{ marginTop: 0 }}>
          {level === 'region' ? 'Location 배치' : 'Cell 배치'}
        </h3>
        <p style={{ fontSize: '12px', color: '#666', marginBottom: '15px' }}>
          위치: ({position.x.toFixed(1)}, {position.y.toFixed(1)})
        </p>

        {/* 검색 */}
        <input
          type="text"
          placeholder={`${level === 'region' ? 'Location' : 'Cell'} 검색...`}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            padding: '8px',
            marginBottom: '15px',
            border: '1px solid #ddd',
            borderRadius: '4px',
          }}
        />

        {/* 엔티티 목록 */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          border: '1px solid #ddd',
          borderRadius: '4px',
          padding: '10px',
        }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>로딩 중...</div>
          ) : filteredEntities.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
              {searchQuery ? '검색 결과가 없습니다' : `${level === 'region' ? 'Location' : 'Cell'}이 없습니다`}
            </div>
          ) : (
            filteredEntities.map((entity) => {
              const id = level === 'region' ? entity.location_id : entity.cell_id;
              const name = level === 'region' ? entity.location_name : entity.cell_name;
              const description = level === 'region' ? entity.location_description : entity.cell_description;

              return (
                <div
                  key={id}
                  onClick={() => {
                    onSelect(id, position);
                    onClose();
                  }}
                  style={{
                    padding: '10px',
                    marginBottom: '5px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    backgroundColor: '#f9f9f9',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#e3f2fd';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#f9f9f9';
                  }}
                >
                  <div style={{ fontWeight: 'bold' }}>{name}</div>
                  {description && (
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                      {description}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* 버튼 */}
        <div style={{
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '10px',
          marginTop: '15px',
        }}>
          <button
            onClick={onClose}
            style={{
              padding: '8px 16px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              cursor: 'pointer',
              backgroundColor: '#fff',
            }}
          >
            취소
          </button>
        </div>
      </div>
    </div>
  );
};

