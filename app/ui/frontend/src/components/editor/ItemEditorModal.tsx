/**
 * Item 편집 모달
 */
import React, { useState, useEffect } from 'react';
import { itemsApi } from '../../services/api';
import { Modal } from '../common/ui/Modal';
import { CollapsibleSection } from '../common/ui/CollapsibleSection';
import { FormField } from '../common/ui/FormField';
import { InputField } from '../common/ui/InputField';
import { JsonFormField } from '../common/ui/JsonFormField';

interface ItemEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  itemId: string | null;
  onSave: () => Promise<void>;
}

interface ItemData {
  item_id: string;
  base_property_id: string;
  item_type?: string;
  stack_size: number;
  consumable: boolean;
  item_properties: Record<string, any>;
  base_property_name?: string;
  base_property_description?: string;
  created_at: string;
  updated_at: string;
}

export const ItemEditorModal: React.FC<ItemEditorModalProps> = ({
  isOpen,
  onClose,
  itemId,
  onSave,
}) => {
  const [item, setItem] = useState<ItemData | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // Item 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      if (!isOpen || !itemId) {
        setItem(null);
        return;
      }

      setLoading(true);
      try {
        const response = await itemsApi.getById(itemId);
        setItem(response.data);
      } catch (error) {
        console.error('데이터 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [isOpen, itemId]);

  const handleSave = async () => {
    if (!item) return;

    try {
      setSaving(true);
      await itemsApi.update(item.item_id, {
        base_property_id: item.base_property_id,
        item_type: item.item_type,
        stack_size: item.stack_size,
        consumable: item.consumable,
        item_properties: item.item_properties,
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

  if (!item && !loading) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Item 편집" width="700px" height="80vh">
      {loading ? (
        <div style={{ padding: '20px', textAlign: 'center' }}>로딩 중...</div>
      ) : item ? (
        <>
          <CollapsibleSection title="기본 정보" defaultExpanded={true}>
            <FormField label="ID" labelWidth={120}>
              <InputField
                type="text"
                value={item.item_id}
                onChange={() => {}}
                readOnly
                copyButton
              />
            </FormField>
            <FormField label="기본 속성 ID" labelWidth={120}>
              <InputField
                type="text"
                value={item.base_property_id}
                onChange={(value) => setItem({ ...item, base_property_id: value })}
                placeholder="PROP_..."
              />
            </FormField>
            {item.base_property_name && (
              <FormField label="기본 속성 이름" labelWidth={120}>
                <InputField
                  type="text"
                  value={item.base_property_name}
                  onChange={() => {}}
                  readOnly
                />
              </FormField>
            )}
            {item.base_property_description && (
              <FormField label="기본 속성 설명" labelWidth={120}>
                <InputField
                  type="textarea"
                  value={item.base_property_description}
                  onChange={() => {}}
                  readOnly
                  rows={3}
                />
              </FormField>
            )}
            <FormField label="아이템 타입" labelWidth={120}>
              <InputField
                type="text"
                value={item.item_type || ''}
                onChange={(value) => setItem({ ...item, item_type: value || undefined })}
                placeholder="weapon, armor, consumable, etc."
              />
            </FormField>
            <FormField label="스택 크기" labelWidth={120}>
              <InputField
                type="number"
                value={item.stack_size}
                onChange={(value) => setItem({ ...item, stack_size: parseInt(value) || 1 })}
                min="1"
              />
            </FormField>
            <FormField label="소비 가능" labelWidth={120}>
              <input
                type="checkbox"
                checked={item.consumable}
                onChange={(e) => setItem({ ...item, consumable: e.target.checked })}
                style={{ marginRight: '8px' }}
              />
              <span style={{ fontSize: '12px' }}>이 아이템은 소비 가능합니다</span>
            </FormField>
          </CollapsibleSection>

          <CollapsibleSection title="아이템 속성 (Item Properties)" defaultExpanded={false}>
            <div style={{ padding: '8px' }}>
              <InputField
                type="textarea"
                value={JSON.stringify(item.item_properties || {}, null, 2)}
                onChange={(value) => {
                  try {
                    const parsed = JSON.parse(value);
                    setItem({ ...item, item_properties: parsed });
                  } catch (e) {
                    // JSON 파싱 실패 시 무시
                  }
                }}
                rows={8}
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

