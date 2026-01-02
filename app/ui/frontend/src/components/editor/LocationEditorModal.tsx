/**
 * Location 편집 모달
 */
import React, { useState, useEffect } from 'react';
import { LocationData, CellData } from '../../types';
import { locationsApi, cellsApi, managementApi } from '../../services/api';
import { Modal } from '../common/ui/Modal';
import { CollapsibleSection } from '../common/ui/CollapsibleSection';
import { FormField } from '../common/ui/FormField';
import { InputField } from '../common/ui/InputField';
import { CellEditorModal } from './CellEditorModal';

interface LocationEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  locationId: string | null;
  regionId: string;
  onSave: () => Promise<void>;
  embedded?: boolean;
}

export const LocationEditorModal: React.FC<LocationEditorModalProps> = ({
  isOpen,
  onClose,
  locationId,
  regionId,
  onSave,
  embedded = false,
}) => {
  const [location, setLocation] = useState<LocationData | null>(null);
  const [cells, setCells] = useState<CellData[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingCellId, setEditingCellId] = useState<string | null>(null);

  // Location 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      // embedded 모드에서는 isOpen 체크를 건너뛰고 locationId만 확인
      if ((!embedded && !isOpen) || !locationId) {
        setLocation(null);
        setCells([]);
        return;
      }

      setLoading(true);
      try {
        // Location 조회
        const locationResponse = await locationsApi.getById(locationId);
        setLocation(locationResponse.data);

        // Cells 조회
        const cellsResponse = await cellsApi.getByLocation(locationId);
        setCells(cellsResponse.data || []);
      } catch (error) {
        console.error('데이터 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [isOpen, locationId, embedded]);

  const handleSave = async () => {
    if (!location) return;

    try {
      setSaving(true);
      await locationsApi.update(location.location_id, {
        location_name: location.location_name,
        location_description: location.location_description,
        location_type: location.location_type,
      });
      await onSave();
      onClose();
    } catch (error) {
      console.error('저장 실패:', error);
      alert('저장에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  if (!location && !loading) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Location 편집" width="700px" height="80vh">
      {loading ? (
        <div style={{ padding: '20px', textAlign: 'center' }}>로딩 중...</div>
      ) : location ? (
        <>
          <CollapsibleSection title="Location 정보" defaultExpanded={true}>
            <FormField label="ID" labelWidth={100}>
              <InputField
                type="text"
                value={location.location_id}
                onChange={() => {}}
                readOnly
                copyButton
              />
            </FormField>
            <FormField label="이름" labelWidth={100}>
              <InputField
                type="text"
                value={location.location_name}
                onChange={(value) => setLocation({ ...location, location_name: value })}
              />
            </FormField>
            <FormField label="타입" labelWidth={100}>
              <InputField
                type="text"
                value={location.location_type || ''}
                onChange={(value) => setLocation({ ...location, location_type: value })}
              />
            </FormField>
            <FormField label="설명" labelWidth={100}>
              <InputField
                type="textarea"
                value={location.location_description || ''}
                onChange={(value) => setLocation({ ...location, location_description: value })}
                rows={5}
              />
            </FormField>
          </CollapsibleSection>

          <CollapsibleSection 
            title="Cells" 
            count={cells.length} 
            defaultExpanded={true}
            actionButton={
              <button
                onClick={async (e) => {
                  e.stopPropagation();
                  const cellName = prompt('Cell 이름을 입력하세요:');
                  if (cellName && location) {
                    try {
                      await managementApi.createCell({
                        location_id: location.location_id,
                        cell_name: cellName,
                      });
                      // Cell 목록 새로고침
                      const cellsResponse = await cellsApi.getByLocation(location.location_id);
                      setCells(cellsResponse.data || []);
                    } catch (error) {
                      console.error('Cell 생성 실패:', error);
                      alert('Cell 생성에 실패했습니다.');
                    }
                  }
                }}
                style={{
                  fontSize: '9px',
                  padding: '2px 8px',
                  backgroundColor: '#4CAF50',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '2px',
                  cursor: 'pointer',
                }}
              >
                + Add
              </button>
            }
          >
            {cells.length === 0 ? (
              <div style={{ padding: '8px', fontSize: '12px', color: '#999' }}>
                Cell이 없습니다.
              </div>
            ) : (
              cells.map((cell) => (
                <div
                  key={cell.cell_id}
                  style={{
                    marginBottom: '8px',
                    padding: '8px',
                    backgroundColor: '#f9f9f9',
                    border: '1px solid #E0E0E0',
                    borderRadius: '2px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '8px',
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '10px', fontWeight: 'bold' }}>{cell.cell_id}</div>
                    <div style={{ fontSize: '10px', color: '#666' }}>
                      {cell.cell_name || 'Unnamed'} ({cell.matrix_width}x{cell.matrix_height})
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingCellId(cell.cell_id);
                      }}
                      style={{
                        fontSize: '9px',
                        padding: '4px 8px',
                        backgroundColor: '#2196F3',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '2px',
                        cursor: 'pointer',
                      }}
                    >
                      편집
                    </button>
                    <button
                      onClick={async (e) => {
                        e.stopPropagation();
                        if (confirm(`정말로 "${cell.cell_name || cell.cell_id}"을(를) 삭제하시겠습니까?`)) {
                          try {
                            await cellsApi.delete(cell.cell_id);
                            // Cell 목록 새로고침 (로컬 상태만 업데이트)
                            const cellsResponse = await cellsApi.getByLocation(location!.location_id);
                            setCells(cellsResponse.data || []);
                            // onSave() 호출하지 않음 - 전체 새로고침 방지
                          } catch (error) {
                            console.error('Cell 삭제 실패:', error);
                            alert('Cell 삭제에 실패했습니다.');
                          }
                        }
                      }}
                      style={{
                        fontSize: '9px',
                        padding: '4px 8px',
                        backgroundColor: '#f44336',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '2px',
                        cursor: 'pointer',
                      }}
                    >
                      삭제
                    </button>
                  </div>
                </div>
              ))
            )}
          </CollapsibleSection>

          <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', gap: '8px' }}>
            <button
              onClick={async () => {
                if (confirm(`정말로 "${location.location_name}"을(를) 삭제하시겠습니까?\n\n주의: 이 Location에 속한 모든 Cell도 함께 삭제됩니다.`)) {
                  try {
                    await locationsApi.delete(location.location_id);
                    await onSave();
                    onClose();
                  } catch (error) {
                    console.error('Location 삭제 실패:', error);
                    alert('Location 삭제에 실패했습니다.');
                  }
                }
              }}
              style={{
                padding: '8px 16px',
                backgroundColor: '#f44336',
                color: '#fff',
                border: 'none',
                borderRadius: '2px',
                cursor: 'pointer',
              }}
            >
              삭제
            </button>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={onClose}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#999',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '2px',
                  cursor: 'pointer',
                }}
              >
                취소
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                style={{
                  padding: '8px 16px',
                  backgroundColor: saving ? '#ccc' : '#4CAF50',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '2px',
                  cursor: saving ? 'not-allowed' : 'pointer',
                }}
              >
                {saving ? '저장 중...' : '저장'}
              </button>
            </div>
          </div>
        </>
      ) : null}
      <CellEditorModal
        isOpen={editingCellId !== null}
        onClose={() => {
          setEditingCellId(null);
        }}
        cellId={editingCellId}
        onSave={async () => {
          // Cell 목록 새로고침 (로컬 상태만 업데이트)
          if (location) {
            const cellsResponse = await cellsApi.getByLocation(location.location_id);
            setCells(cellsResponse.data || []);
          }
          // onSave() 호출하지 않음 - 전체 새로고침 방지
        }}
      />
    </Modal>
  );
};

