/**
 * Entity 선택 모달 컴포넌트
 */
import React, { useState, useEffect } from 'react';
import { entitiesApi } from '../../services/api';

interface Entity {
  entity_id: string;
  entity_name: string;
  entity_type: string;
  entity_description?: string;
}

interface EntityPickerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (entityId: string, entityName: string) => void;
  currentEntityId?: string;
}

export const EntityPickerModal: React.FC<EntityPickerModalProps> = ({
  isOpen,
  onClose,
  onSelect,
  currentEntityId,
}) => {
  const [entities, setEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadEntities();
    }
  }, [isOpen]);

  const loadEntities = async () => {
    try {
      setLoading(true);
      const response = await entitiesApi.getAll();
      setEntities(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('엔티티 로드 실패:', error);
      setEntities([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredEntities = entities.filter((entity) => {
    const name = entity.entity_name?.toLowerCase() || '';
    const id = entity.entity_id?.toLowerCase() || '';
    const query = searchQuery.toLowerCase();
    return name.includes(query) || id.includes(query);
  });

  const handleSelect = (entity: Entity) => {
    onSelect(entity.entity_id, entity.entity_name);
    onClose();
  };

  if (!isOpen) return null;

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
      zIndex: 10000,
    }}>
      <div style={{
        backgroundColor: '#fff',
        borderRadius: '8px',
        width: '600px',
        maxHeight: '80vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
      }}>
        {/* Header */}
        <div style={{
          padding: '16px',
          borderBottom: '1px solid #E0E0E0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold' }}>엔티티 선택</h3>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '20px',
              cursor: 'pointer',
              color: '#666',
              padding: '0',
              width: '24px',
              height: '24px',
            }}
          >
            ×
          </button>
        </div>

        {/* Search */}
        <div style={{ padding: '16px', borderBottom: '1px solid #E0E0E0' }}>
          <input
            type="text"
            placeholder="엔티티 이름 또는 ID로 검색..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #E0E0E0',
              borderRadius: '4px',
              fontSize: '14px',
            }}
            autoFocus
          />
        </div>

        {/* Entity List */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '8px',
        }}>
          {loading ? (
            <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
              로딩 중...
            </div>
          ) : filteredEntities.length === 0 ? (
            <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
              {searchQuery ? '검색 결과가 없습니다.' : '엔티티가 없습니다.'}
            </div>
          ) : (
            filteredEntities.map((entity) => (
              <div
                key={entity.entity_id}
                onClick={() => handleSelect(entity)}
                style={{
                  padding: '12px',
                  marginBottom: '4px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  backgroundColor: currentEntityId === entity.entity_id ? '#E3F2FD' : '#fff',
                  border: currentEntityId === entity.entity_id ? '1px solid #2196F3' : '1px solid transparent',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  if (currentEntityId !== entity.entity_id) {
                    e.currentTarget.style.backgroundColor = '#F5F5F5';
                  }
                }}
                onMouseLeave={(e) => {
                  if (currentEntityId !== entity.entity_id) {
                    e.currentTarget.style.backgroundColor = '#fff';
                  }
                }}
              >
                <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '4px' }}>
                  {entity.entity_name}
                </div>
                <div style={{ fontSize: '12px', color: '#666', marginBottom: '2px' }}>
                  ID: {entity.entity_id}
                </div>
                {entity.entity_type && (
                  <div style={{ fontSize: '12px', color: '#999' }}>
                    타입: {entity.entity_type}
                  </div>
                )}
                {entity.entity_description && (
                  <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
                    {entity.entity_description}
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '12px 16px',
          borderTop: '1px solid #E0E0E0',
          display: 'flex',
          justifyContent: 'flex-end',
        }}>
          <button
            onClick={onClose}
            style={{
              padding: '6px 16px',
              border: '1px solid #E0E0E0',
              borderRadius: '4px',
              backgroundColor: '#fff',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            취소
          </button>
        </div>
      </div>
    </div>
  );
};

