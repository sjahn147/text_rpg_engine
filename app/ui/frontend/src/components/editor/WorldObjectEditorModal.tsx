/**
 * World Object 편집 모달
 */
import React, { useState, useEffect } from 'react';
import { worldObjectsApi } from '../../services/api';
import { Modal } from '../common/ui/Modal';
import { CollapsibleSection } from '../common/ui/CollapsibleSection';
import { FormField } from '../common/ui/FormField';
import { InputField } from '../common/ui/InputField';
import { JsonFormField } from '../common/ui/JsonFormField';

interface WorldObjectEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  objectId: string | null;
  onSave: () => Promise<void>;
}

interface WorldObjectData {
  object_id: string;
  object_type: string;
  object_name: string;
  object_description?: string;
  default_cell_id?: string;
  default_position: Record<string, any>;
  interaction_type?: string;
  possible_states: Record<string, any>;
  properties: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export const WorldObjectEditorModal: React.FC<WorldObjectEditorModalProps> = ({
  isOpen,
  onClose,
  objectId,
  onSave,
}) => {
  const [object, setObject] = useState<WorldObjectData | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // World Object 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      if (!isOpen || !objectId) {
        setObject(null);
        return;
      }

      setLoading(true);
      try {
        const response = await worldObjectsApi.getById(objectId);
        setObject(response.data);
      } catch (error) {
        console.error('데이터 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [isOpen, objectId]);

  const handleSave = async () => {
    if (!object) return;

    try {
      setSaving(true);
      await worldObjectsApi.update(object.object_id, {
        object_type: object.object_type,
        object_name: object.object_name,
        object_description: object.object_description,
        default_cell_id: object.default_cell_id,
        default_position: object.default_position,
        interaction_type: object.interaction_type,
        possible_states: object.possible_states,
        properties: object.properties,
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

  if (!object && !loading) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="World Object 편집" width="700px" height="80vh">
      {loading ? (
        <div style={{ padding: '20px', textAlign: 'center' }}>로딩 중...</div>
      ) : object ? (
        <>
          <CollapsibleSection title="기본 정보" defaultExpanded={true}>
            <FormField label="ID" labelWidth={120}>
              <InputField
                type="text"
                value={object.object_id}
                onChange={() => {}}
                readOnly
                copyButton
              />
            </FormField>
            <FormField label="타입" labelWidth={120}>
              <select
                value={object.object_type}
                onChange={(e) => setObject({ ...object, object_type: e.target.value })}
                style={{
                  width: '100%',
                  padding: '6px 8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '12px',
                }}
              >
                <option value="static">Static (정적)</option>
                <option value="interactive">Interactive (상호작용 가능)</option>
                <option value="trigger">Trigger (트리거)</option>
              </select>
            </FormField>
            <FormField label="이름" labelWidth={120}>
              <InputField
                type="text"
                value={object.object_name}
                onChange={(value) => setObject({ ...object, object_name: value })}
              />
            </FormField>
            <FormField label="설명" labelWidth={120}>
              <InputField
                type="textarea"
                value={object.object_description || ''}
                onChange={(value) => setObject({ ...object, object_description: value })}
                rows={4}
              />
            </FormField>
            <FormField label="Cell ID" labelWidth={120}>
              <InputField
                type="text"
                value={object.default_cell_id || ''}
                onChange={(value) => setObject({ ...object, default_cell_id: value || undefined })}
                placeholder="CELL_..."
              />
            </FormField>
            <FormField label="상호작용 타입" labelWidth={120}>
              <select
                value={object.interaction_type || 'none'}
                onChange={(e) => setObject({ ...object, interaction_type: e.target.value || undefined })}
                style={{
                  width: '100%',
                  padding: '6px 8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '12px',
                }}
              >
                <option value="none">None (없음)</option>
                <option value="openable">Openable (열 수 있음)</option>
                <option value="triggerable">Triggerable (트리거 가능)</option>
              </select>
            </FormField>
          </CollapsibleSection>

          <CollapsibleSection title="기본 위치 (Default Position)" defaultExpanded={false}>
            <div style={{ padding: '8px' }}>
              <JsonFormField
                label="위치"
                value={object.default_position || {}}
                onChange={(value) => setObject({ ...object, default_position: value })}
                fields={[
                  { key: 'x', label: 'X', type: 'number', default: 0 },
                  { key: 'y', label: 'Y', type: 'number', default: 0 },
                  { key: 'z', label: 'Z', type: 'number', default: 0 },
                ]}
              />
            </div>
          </CollapsibleSection>

          <CollapsibleSection title="가능한 상태 (Possible States)" defaultExpanded={false}>
            <div style={{ padding: '8px' }}>
              <InputField
                type="textarea"
                value={JSON.stringify(object.possible_states || {}, null, 2)}
                onChange={(value) => {
                  try {
                    const parsed = JSON.parse(value);
                    setObject({ ...object, possible_states: parsed });
                  } catch (e) {
                    // JSON 파싱 실패 시 무시
                  }
                }}
                rows={6}
              />
            </div>
          </CollapsibleSection>

          <CollapsibleSection title="추가 속성 (Properties)" defaultExpanded={false}>
            <div style={{ padding: '8px' }}>
              <InputField
                type="textarea"
                value={JSON.stringify(object.properties || {}, null, 2)}
                onChange={(value) => {
                  try {
                    const parsed = JSON.parse(value);
                    setObject({ ...object, properties: parsed });
                  } catch (e) {
                    // JSON 파싱 실패 시 무시
                  }
                }}
                rows={6}
              />
            </div>
          </CollapsibleSection>

          <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
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
        </>
      ) : null}
    </Modal>
  );
};

