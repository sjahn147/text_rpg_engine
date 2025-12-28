/**
 * Effect Carrier 편집 모달
 */
import React, { useState, useEffect } from 'react';
import { effectCarriersApi } from '../services/api';
import { Modal } from './ui/Modal';
import { CollapsibleSection } from './ui/CollapsibleSection';
import { FormField } from './ui/FormField';
import { InputField } from './ui/InputField';
import { JsonFormField } from './ui/JsonFormField';

interface EffectCarrierEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  effectId: string | null;
  onSave: () => Promise<void>;
}

interface EffectCarrierData {
  effect_id: string;
  name: string;
  carrier_type: string;
  effect_json: Record<string, any>;
  constraints_json: Record<string, any>;
  source_entity_id?: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export const EffectCarrierEditorModal: React.FC<EffectCarrierEditorModalProps> = ({
  isOpen,
  onClose,
  effectId,
  onSave,
}) => {
  const [effect, setEffect] = useState<EffectCarrierData | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [newTag, setNewTag] = useState('');

  // Effect Carrier 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      if (!isOpen || !effectId) {
        setEffect(null);
        return;
      }

      setLoading(true);
      try {
        const response = await effectCarriersApi.getById(effectId);
        setEffect({
          ...response.data,
          effect_id: String(response.data.effect_id), // UUID를 문자열로 변환
        });
      } catch (error) {
        console.error('데이터 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [isOpen, effectId]);

  const handleSave = async () => {
    if (!effect) return;

    try {
      setSaving(true);
      await effectCarriersApi.update(effect.effect_id, {
        name: effect.name,
        carrier_type: effect.carrier_type,
        effect_json: effect.effect_json,
        constraints_json: effect.constraints_json,
        source_entity_id: effect.source_entity_id,
        tags: effect.tags,
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

  const handleAddTag = () => {
    if (newTag.trim() && effect) {
      setEffect({
        ...effect,
        tags: [...effect.tags, newTag.trim()],
      });
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    if (effect) {
      setEffect({
        ...effect,
        tags: effect.tags.filter(tag => tag !== tagToRemove),
      });
    }
  };

  if (!effect && !loading) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Effect Carrier 편집" width="700px" height="80vh">
      {loading ? (
        <div style={{ padding: '20px', textAlign: 'center' }}>로딩 중...</div>
      ) : effect ? (
        <>
          <CollapsibleSection title="기본 정보" defaultExpanded={true}>
            <FormField label="ID" labelWidth={120}>
              <InputField
                type="text"
                value={effect.effect_id}
                onChange={() => {}}
                readOnly
                copyButton
              />
            </FormField>
            <FormField label="이름" labelWidth={120}>
              <InputField
                type="text"
                value={effect.name}
                onChange={(value) => setEffect({ ...effect, name: value })}
              />
            </FormField>
            <FormField label="타입" labelWidth={120}>
              <select
                value={effect.carrier_type}
                onChange={(e) => setEffect({ ...effect, carrier_type: e.target.value })}
                style={{
                  width: '100%',
                  padding: '6px 8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '12px',
                }}
              >
                <option value="skill">Skill (스킬)</option>
                <option value="buff">Buff (버프)</option>
                <option value="item">Item (아이템)</option>
                <option value="blessing">Blessing (축복)</option>
                <option value="curse">Curse (저주)</option>
                <option value="ritual">Ritual (의식)</option>
              </select>
            </FormField>
            <FormField label="출처 Entity ID" labelWidth={120}>
              <InputField
                type="text"
                value={effect.source_entity_id || ''}
                onChange={(value) => setEffect({ ...effect, source_entity_id: value || undefined })}
                placeholder="ENTITY_..."
              />
            </FormField>
          </CollapsibleSection>

          <CollapsibleSection title="태그 (Tags)" defaultExpanded={false}>
            <div style={{ padding: '8px' }}>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                <input
                  type="text"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddTag();
                    }
                  }}
                  placeholder="새 태그 입력"
                  style={{
                    flex: 1,
                    fontSize: '12px',
                    padding: '6px 8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                  }}
                />
                <button
                  onClick={handleAddTag}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: '#4CAF50',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '2px',
                    cursor: 'pointer',
                    fontSize: '12px',
                  }}
                >
                  추가
                </button>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                {effect.tags.map((tag, index) => (
                  <span
                    key={index}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      padding: '4px 8px',
                      backgroundColor: '#e3f2fd',
                      borderRadius: '12px',
                      fontSize: '11px',
                      gap: '4px',
                    }}
                  >
                    {tag}
                    <button
                      onClick={() => handleRemoveTag(tag)}
                      style={{
                        marginLeft: '4px',
                        padding: '0',
                        border: 'none',
                        background: 'none',
                        cursor: 'pointer',
                        fontSize: '14px',
                        color: '#666',
                      }}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </CollapsibleSection>

          <CollapsibleSection title="효과 데이터 (Effect JSON)" defaultExpanded={false}>
            <div style={{ padding: '8px' }}>
              <InputField
                type="textarea"
                value={JSON.stringify(effect.effect_json || {}, null, 2)}
                onChange={(value) => {
                  try {
                    const parsed = JSON.parse(value);
                    setEffect({ ...effect, effect_json: parsed });
                  } catch (e) {
                    // JSON 파싱 실패 시 무시
                  }
                }}
                rows={8}
              />
            </div>
          </CollapsibleSection>

          <CollapsibleSection title="제약 조건 (Constraints JSON)" defaultExpanded={false}>
            <div style={{ padding: '8px' }}>
              <InputField
                type="textarea"
                value={JSON.stringify(effect.constraints_json || {}, null, 2)}
                onChange={(value) => {
                  try {
                    const parsed = JSON.parse(value);
                    setEffect({ ...effect, constraints_json: parsed });
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

