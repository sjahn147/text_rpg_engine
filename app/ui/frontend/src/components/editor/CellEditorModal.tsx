/**
 * Cell 편집 모달
 */
import React, { useState, useEffect } from 'react';
import { CellData, LocationData } from '../types';
import { cellsApi, locationsApi, entitiesApi, managementApi, worldObjectsApi } from '../../services/api';
import { Modal } from '../common/ui/Modal';
import { CollapsibleSection } from '../common/ui/CollapsibleSection';
import { FormField } from '../common/ui/FormField';
import { InputField } from '../common/ui/InputField';
import { EntityEditorModal } from './EntityEditorModal';
import { WorldObjectEditorModal } from './WorldObjectEditorModal';
import { CellPropertiesEditor } from './CellPropertiesEditor';

interface CellEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  cellId: string | null;
  onSave: () => Promise<void>;
  embedded?: boolean;
}

export const CellEditorModal: React.FC<CellEditorModalProps> = ({
  isOpen,
  onClose,
  cellId,
  onSave,
  embedded = false,
}) => {
  const [cell, setCell] = useState<CellData | null>(null);
  const [location, setLocation] = useState<LocationData | null>(null);
  const [entities, setEntities] = useState<any[]>([]);
  const [worldObjects, setWorldObjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingEntityId, setEditingEntityId] = useState<string | null>(null);
  const [editingObjectId, setEditingObjectId] = useState<string | null>(null);
  const [showPropertiesEditor, setShowPropertiesEditor] = useState(false);

  // Cell 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      // embedded 모드에서는 isOpen 체크를 건너뛰고 cellId만 확인
      if ((!embedded && !isOpen) || !cellId) {
        setCell(null);
        setLocation(null);
        return;
      }

      setLoading(true);
      try {
        // Cell 조회
        const cellResponse = await cellsApi.getById(cellId);
        setCell(cellResponse.data);

        // Location 조회
        if (cellResponse.data.location_id) {
          const locationResponse = await locationsApi.getById(cellResponse.data.location_id);
          setLocation(locationResponse.data);
        }

        // Entities 조회
        try {
          const entitiesResponse = await entitiesApi.getByCell(cellId);
          setEntities(entitiesResponse.data);
        } catch (error) {
          console.error('인물 조회 실패:', error);
          setEntities([]);
        }

        // World Objects 조회
        try {
          const objectsResponse = await worldObjectsApi.getByCell(cellId);
          setWorldObjects(objectsResponse.data || []);
        } catch (error) {
          console.error('오브젝트 조회 실패:', error);
          setWorldObjects([]);
        }
      } catch (error) {
        console.error('데이터 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [isOpen, cellId, embedded]);

  const handleSave = async () => {
    if (!cell) return;

    try {
      setSaving(true);
      await cellsApi.update(cell.cell_id, {
        cell_name: cell.cell_name,
        cell_description: cell.cell_description,
        matrix_width: cell.matrix_width,
        matrix_height: cell.matrix_height,
        cell_status: cell.cell_status,
        cell_type: cell.cell_type,
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

  if (!cell && !loading) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Cell 편집" width="600px" height="70vh">
      {loading ? (
        <div style={{ padding: '20px', textAlign: 'center' }}>로딩 중...</div>
      ) : cell ? (
        <>
          <CollapsibleSection title="Cell 정보" defaultExpanded={true}>
            <FormField label="ID" labelWidth={100}>
              <InputField
                type="text"
                value={cell.cell_id}
                onChange={() => {}}
                readOnly
                copyButton
              />
            </FormField>
            {location && (
              <FormField label="Location" labelWidth={100}>
                <InputField
                  type="text"
                  value={`${location.location_id} - ${location.location_name}`}
                  onChange={() => {}}
                  readOnly
                />
              </FormField>
            )}
            <FormField label="이름" labelWidth={100}>
              <InputField
                type="text"
                value={cell.cell_name || ''}
                onChange={(value) => setCell({ ...cell, cell_name: value })}
              />
            </FormField>
            <FormField label="크기" labelWidth={100}>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ fontSize: '10px' }}>Width:</span>
                <InputField
                  type="number"
                  value={cell.matrix_width}
                  onChange={(value) => setCell({ ...cell, matrix_width: parseInt(value) || 10 })}
                />
                <span style={{ fontSize: '10px' }}>Height:</span>
                <InputField
                  type="number"
                  value={cell.matrix_height}
                  onChange={(value) => setCell({ ...cell, matrix_height: parseInt(value) || 10 })}
                />
              </div>
            </FormField>
            <FormField label="설명" labelWidth={100}>
              <InputField
                type="textarea"
                value={cell.cell_description || ''}
                onChange={(value) => setCell({ ...cell, cell_description: value })}
                rows={5}
              />
            </FormField>
            <FormField label="상태 (Status)" labelWidth={100}>
              <InputField
                type="select"
                value={cell.cell_status || 'active'}
                onChange={(value) => setCell({ ...cell, cell_status: value })}
                options={['active', 'inactive', 'locked', 'dangerous']}
              />
            </FormField>
            <FormField label="타입 (Type)" labelWidth={100}>
              <InputField
                type="select"
                value={cell.cell_type || 'indoor'}
                onChange={(value) => setCell({ ...cell, cell_type: value })}
                options={['indoor', 'outdoor', 'dungeon', 'shop', 'tavern', 'temple']}
              />
            </FormField>
          </CollapsibleSection>

          <CollapsibleSection 
            title="인물 (NPCs)" 
            count={entities.length}
            defaultExpanded={true}
            actionButton={
              <button
                onClick={async (e) => {
                  e.stopPropagation();
                  const entityName = prompt('인물 이름을 입력하세요:');
                  if (entityName && cell) {
                    try {
                      await managementApi.createEntity({
                        cell_id: cell.cell_id,
                        entity_name: entityName,
                        entity_type: 'npc',
                      });
                      // 인물 목록 새로고침 (로컬 상태만 업데이트, 전체 새로고침 방지)
                      const entitiesResponse = await entitiesApi.getByCell(cell.cell_id);
                      setEntities(entitiesResponse.data);
                      // onSave() 호출하지 않음 - 전체 새로고침 방지
                    } catch (error) {
                      console.error('인물 생성 실패:', error);
                      alert('인물 생성에 실패했습니다.');
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
            {entities.length === 0 ? (
              <div style={{ padding: '8px', fontSize: '12px', color: '#999' }}>
                인물이 없습니다.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {entities.map((entity) => (
                  <div
                    key={entity.entity_id}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '6px 8px',
                      backgroundColor: '#f5f5f5',
                      borderRadius: '2px',
                      gap: '8px',
                    }}
                  >
                    <div
                      style={{
                        flex: 1,
                        cursor: 'pointer',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                      onClick={() => setEditingEntityId(entity.entity_id)}
                    >
                      <span style={{ fontSize: '12px' }}>{entity.entity_name}</span>
                      <span style={{ fontSize: '10px', color: '#999' }}>{entity.entity_type}</span>
                    </div>
                    <button
                      onClick={async (e) => {
                        e.stopPropagation();
                        if (confirm(`정말로 "${entity.entity_name}"을(를) 삭제하시겠습니까?`)) {
                          try {
                            await entitiesApi.delete(entity.entity_id);
                            // 인물 목록 새로고침
                            const entitiesResponse = await entitiesApi.getByCell(cell!.cell_id);
                            setEntities(entitiesResponse.data);
                          } catch (error) {
                            console.error('인물 삭제 실패:', error);
                            alert('인물 삭제에 실패했습니다.');
                          }
                        }
                      }}
                      style={{
                        fontSize: '10px',
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
                ))}
              </div>
            )}
          </CollapsibleSection>

          <CollapsibleSection 
            title="오브젝트 (World Objects)" 
            count={worldObjects.length}
            defaultExpanded={true}
            actionButton={
              <button
                onClick={async (e) => {
                  e.stopPropagation();
                  const objectName = prompt('오브젝트 이름을 입력하세요:');
                  if (objectName && cell) {
                    const objectId = prompt('오브젝트 ID를 입력하세요 (예: OBJ_STATIC_CHEST_001):');
                    if (objectId) {
                      try {
                        await worldObjectsApi.create({
                          object_id: objectId,
                          object_type: 'static',
                          object_name: objectName,
                          default_cell_id: cell.cell_id,
                        });
                        // 오브젝트 목록 새로고침
                        const objectsResponse = await worldObjectsApi.getByCell(cell.cell_id);
                        setWorldObjects(objectsResponse.data || []);
                      } catch (error) {
                        console.error('오브젝트 생성 실패:', error);
                        alert('오브젝트 생성에 실패했습니다.');
                      }
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
            {worldObjects.length === 0 ? (
              <div style={{ padding: '8px', fontSize: '12px', color: '#999' }}>
                오브젝트가 없습니다.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {worldObjects.map((obj) => (
                  <div
                    key={obj.object_id}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '6px 8px',
                      backgroundColor: '#f5f5f5',
                      borderRadius: '2px',
                      gap: '8px',
                    }}
                  >
                    <div
                      style={{
                        flex: 1,
                        cursor: 'pointer',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                      onClick={() => setEditingObjectId(obj.object_id)}
                    >
                      <span style={{ fontSize: '12px' }}>{obj.object_name}</span>
                      <span style={{ fontSize: '10px', color: '#999' }}>{obj.object_type}</span>
                    </div>
                    <button
                      onClick={async (e) => {
                        e.stopPropagation();
                        if (confirm(`정말로 "${obj.object_name}"을(를) 삭제하시겠습니까?`)) {
                          try {
                            await worldObjectsApi.delete(obj.object_id);
                            // 오브젝트 목록 새로고침
                            const objectsResponse = await worldObjectsApi.getByCell(cell!.cell_id);
                            setWorldObjects(objectsResponse.data || []);
                          } catch (error) {
                            console.error('오브젝트 삭제 실패:', error);
                            alert('오브젝트 삭제에 실패했습니다.');
                          }
                        }
                      }}
                      style={{
                        fontSize: '10px',
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
                ))}
              </div>
            )}
          </CollapsibleSection>

          <CollapsibleSection 
            title="Properties" 
            defaultExpanded={false}
            actionButton={
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowPropertiesEditor(true);
                }}
                style={{
                  fontSize: '9px',
                  padding: '2px 8px',
                  backgroundColor: '#2196F3',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '2px',
                  cursor: 'pointer',
                }}
              >
                편집
              </button>
            }
          >
            <div style={{ padding: '8px', fontSize: '12px', color: '#666' }}>
              {cell.cell_properties && Object.keys(cell.cell_properties).length > 0 ? (
                <pre style={{ 
                  fontSize: '10px', 
                  backgroundColor: '#f5f5f5', 
                  padding: '8px', 
                  borderRadius: '4px',
                  overflow: 'auto',
                  maxHeight: '200px',
                }}>
                  {JSON.stringify(cell.cell_properties, null, 2)}
                </pre>
              ) : (
                <div style={{ color: '#999' }}>Properties가 설정되지 않았습니다.</div>
              )}
            </div>
          </CollapsibleSection>

          <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', gap: '8px' }}>
            <button
              onClick={async () => {
                if (confirm(`정말로 "${cell.cell_name || cell.cell_id}"을(를) 삭제하시겠습니까?\n\n주의: 이 Cell에 속한 모든 인물도 함께 삭제됩니다.`)) {
                  try {
                    await cellsApi.delete(cell.cell_id);
                    await onSave();
                    onClose();
                  } catch (error) {
                    console.error('Cell 삭제 실패:', error);
                    alert('Cell 삭제에 실패했습니다.');
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
      <EntityEditorModal
        isOpen={editingEntityId !== null}
        onClose={() => {
          setEditingEntityId(null);
        }}
        entityId={editingEntityId}
        onSave={async () => {
          // 인물 목록 새로고침 (로컬 상태만 업데이트)
          if (cell) {
            const entitiesResponse = await entitiesApi.getByCell(cell.cell_id);
            setEntities(entitiesResponse.data);
          }
          // onSave() 호출하지 않음 - 전체 새로고침 방지
        }}
      />
      <WorldObjectEditorModal
        isOpen={editingObjectId !== null}
        onClose={() => {
          setEditingObjectId(null);
        }}
        objectId={editingObjectId}
        onSave={async () => {
          // 오브젝트 목록 새로고침 (로컬 상태만 업데이트)
          if (cell) {
            const objectsResponse = await worldObjectsApi.getByCell(cell.cell_id);
            setWorldObjects(objectsResponse.data || []);
          }
          // onSave() 호출하지 않음 - 전체 새로고침 방지
        }}
      />
      {showPropertiesEditor && cell && (
        <Modal 
          isOpen={showPropertiesEditor} 
          onClose={() => setShowPropertiesEditor(false)} 
          title="Cell Properties 편집" 
          width="800px" 
          height="80vh"
        >
          <CellPropertiesEditor
            cellId={cell.cell_id}
            onClose={async () => {
              setShowPropertiesEditor(false);
              // Cell 데이터 새로고침
              if (cell) {
                const response = await cellsApi.getById(cell.cell_id);
                setCell(response.data);
              }
            }}
            onSave={async () => {
              // Cell 데이터 새로고침
              if (cell) {
                const response = await cellsApi.getById(cell.cell_id);
                setCell(response.data);
              }
            }}
          />
        </Modal>
      )}
    </Modal>
  );
};

