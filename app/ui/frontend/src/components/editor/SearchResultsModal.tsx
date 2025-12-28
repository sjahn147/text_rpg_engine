/**
 * 검색 결과 모달 컴포넌트
 */
import React from 'react';
import { Modal } from '../common/ui/Modal';

interface SearchResult {
  entity_type: string;
  entity_id: string;
  name: string;
  description?: string;
  metadata?: Record<string, any>;
}

interface SearchResultsModalProps {
  isOpen: boolean;
  onClose: () => void;
  results: SearchResult[];
  onResultClick: (entityType: string, entityId: string) => void;
}

export const SearchResultsModal: React.FC<SearchResultsModalProps> = ({
  isOpen,
  onClose,
  results,
  onResultClick,
}) => {
  const getEntityTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      region: '지역',
      location: '위치',
      cell: '셀',
      entity: '인물',
      world_object: '오브젝트',
      effect_carrier: '효과',
      item: '아이템',
    };
    return labels[type] || type;
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="검색 결과" width="600px" height="70vh">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: 'calc(70vh - 100px)', overflowY: 'auto' }}>
        {results.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
            검색 결과가 없습니다.
          </div>
        ) : (
          results.map((result, index) => (
            <div
              key={`${result.entity_type}-${result.entity_id}-${index}`}
              onClick={() => {
                onResultClick(result.entity_type, result.entity_id);
                onClose();
              }}
              style={{
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                cursor: 'pointer',
                backgroundColor: '#fff',
                transition: 'background-color 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f5f5f5';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#fff';
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: '12px' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span style={{
                      fontSize: '10px',
                      padding: '2px 6px',
                      backgroundColor: '#e3f2fd',
                      color: '#1976d2',
                      borderRadius: '2px',
                      fontWeight: 'bold',
                    }}>
                      {getEntityTypeLabel(result.entity_type)}
                    </span>
                    <span style={{ fontSize: '14px', fontWeight: 'bold' }}>{result.name}</span>
                  </div>
                  {result.description && (
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                      {result.description.length > 100
                        ? `${result.description.substring(0, 100)}...`
                        : result.description}
                    </div>
                  )}
                  <div style={{ fontSize: '10px', color: '#999', marginTop: '4px', fontFamily: 'monospace' }}>
                    ID: {result.entity_id}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </Modal>
  );
};

