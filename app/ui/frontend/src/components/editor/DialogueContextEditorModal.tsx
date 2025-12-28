/**
 * Dialogue Context 편집 모달
 */
import React, { useState, useEffect } from 'react';
import { dialogueApi, cellsApi } from '../../services/api';
import { Modal } from '../common/ui/Modal';
import { FormField } from '../common/ui/FormField';
import { InputField } from '../common/ui/InputField';
import { JsonFormField } from '../common/ui/JsonFormField';

interface DialogueContextData {
  dialogue_id: string;
  title: string;
  content: string;
  entity_id?: string;
  cell_id?: string;
  time_category?: string;
  event_id?: string;
  priority: number;
  available_topics?: Record<string, any>;
  entity_personality?: string;
  constraints?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

interface DialogueContextEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  dialogueId: string | null;
  entityId: string | null;
  onSave: () => Promise<void>;
}

export const DialogueContextEditorModal: React.FC<DialogueContextEditorModalProps> = ({
  isOpen,
  onClose,
  dialogueId,
  entityId,
  onSave,
}) => {
  const [context, setContext] = useState<DialogueContextData | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [availableCells, setAvailableCells] = useState<any[]>([]);

  // Context 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      if (!isOpen) {
        setContext(null);
        return;
      }

      if (dialogueId) {
        // 기존 Context 편집
        setLoading(true);
        try {
          const response = await dialogueApi.getContext(dialogueId);
          setContext(response.data);
          
          // Cell 목록 로드 (cell_id 선택용)
          if (response.data.entity_id) {
            try {
              // Entity의 cell_id를 찾아서 해당 Location의 Cells를 로드
              // 간단하게 모든 Cells를 로드 (나중에 최적화 가능)
              const cellsResponse = await cellsApi.getAll();
              setAvailableCells(cellsResponse.data || []);
            } catch (error) {
              console.error('Cells 로드 실패:', error);
              setAvailableCells([]);
            }
          }
        } catch (error) {
          console.error('Context 로드 실패:', error);
        } finally {
          setLoading(false);
        }
      } else if (entityId) {
        // 새 Context 생성
        setContext({
          dialogue_id: `DIALOGUE_${entityId}_${Date.now()}`,
          title: '',
          content: '',
          entity_id: entityId,
          cell_id: undefined,
          time_category: undefined,
          event_id: undefined,
          priority: 0,
          available_topics: { topics: ['greeting', 'farewell'], default_topic: 'greeting' },
          entity_personality: 'friendly',
          constraints: { max_response_length: 200, tone: 'friendly' },
        });
        
        // Cell 목록 로드
        try {
          const cellsResponse = await cellsApi.getAll();
          setAvailableCells(cellsResponse.data || []);
        } catch (error) {
          console.error('Cells 로드 실패:', error);
          setAvailableCells([]);
        }
      }
    };

    loadData();
  }, [isOpen, dialogueId, entityId]);

  const handleSave = async () => {
    if (!context) return;

    try {
      setSaving(true);
      if (dialogueId) {
        // 업데이트
        await dialogueApi.updateContext(dialogueId, {
          title: context.title,
          content: context.content,
          entity_id: context.entity_id,
          cell_id: context.cell_id || null,
          time_category: context.time_category || null,
          event_id: context.event_id || null,
          priority: context.priority,
          available_topics: context.available_topics,
          entity_personality: context.entity_personality,
          constraints: context.constraints,
        });
      } else {
        // 생성
        await dialogueApi.createContext({
          dialogue_id: context.dialogue_id,
          title: context.title,
          content: context.content,
          entity_id: context.entity_id,
          cell_id: context.cell_id || null,
          time_category: context.time_category || null,
          event_id: context.event_id || null,
          priority: context.priority,
          available_topics: context.available_topics,
          entity_personality: context.entity_personality,
          constraints: context.constraints,
        });
      }
      await onSave();
      onClose();
    } catch (error) {
      console.error('저장 실패:', error);
      alert('저장에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  if (!context && !loading) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="대화 컨텍스트 편집" width="700px" height="85vh">
      {loading ? (
        <div style={{ padding: '20px', textAlign: 'center' }}>로딩 중...</div>
      ) : context ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', minHeight: '100%' }}>
          <FormField label="Dialogue ID" labelWidth={150}>
            <InputField
              type="text"
              value={context.dialogue_id}
              onChange={(value) => setContext({ ...context, dialogue_id: value })}
              readOnly={!!dialogueId}
            />
          </FormField>

          <FormField label="제목 (Title)" labelWidth={150}>
            <InputField
              type="text"
              value={context.title}
              onChange={(value) => setContext({ ...context, title: value })}
            />
          </FormField>

          <FormField label="내용 (Content)" labelWidth={150}>
            <InputField
              type="textarea"
              value={context.content}
              onChange={(value) => setContext({ ...context, content: value })}
              rows={4}
            />
          </FormField>

          <div style={{ marginTop: '8px', padding: '12px', backgroundColor: '#f0f8ff', borderRadius: '4px', border: '1px solid #b0d4f1' }}>
            <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '12px' }}>
              조건 필드 (Conditional Fields)
            </div>

            <FormField label="Cell ID" labelWidth={120}>
              <InputField
                type="select"
                value={context.cell_id || ''}
                onChange={(value) => setContext({ ...context, cell_id: value === '' ? undefined : value })}
                options={['', ...availableCells.map((c: any) => c.cell_id)]}
                placeholder="선택 안함 (모든 Cell에서 사용 가능)"
              />
              <div style={{ fontSize: '10px', color: '#666', marginTop: '4px' }}>
                특정 Cell에서만 사용 가능한 대화를 설정합니다. 비워두면 모든 Cell에서 사용 가능합니다.
              </div>
            </FormField>

            <FormField label="시간 카테고리 (Time Category)" labelWidth={120}>
              <InputField
                type="select"
                value={context.time_category || ''}
                onChange={(value) => setContext({ ...context, time_category: value === '' ? undefined : value })}
                options={['', 'morning', 'afternoon', 'evening', 'night']}
                placeholder="선택 안함 (모든 시간대)"
              />
              <div style={{ fontSize: '10px', color: '#666', marginTop: '4px' }}>
                특정 시간대에만 사용 가능한 대화를 설정합니다.
              </div>
            </FormField>

            <FormField label="이벤트 ID (Event ID)" labelWidth={120}>
              <InputField
                type="text"
                value={context.event_id || ''}
                onChange={(value) => setContext({ ...context, event_id: value || undefined })}
                placeholder="특정 이벤트 발생 시 대화"
              />
              <div style={{ fontSize: '10px', color: '#666', marginTop: '4px' }}>
                특정 이벤트 발생 시에만 사용 가능한 대화를 설정합니다.
              </div>
            </FormField>
          </div>

          <FormField label="우선순위 (Priority)" labelWidth={150}>
            <InputField
              type="number"
              value={context.priority}
              onChange={(value) => setContext({ ...context, priority: parseInt(value, 10) || 0 })}
              min={0}
              max={100}
            />
          </FormField>

          <FormField label="Entity 성격 (Personality)" labelWidth={150}>
            <InputField
              type="text"
              value={context.entity_personality || ''}
              onChange={(value) => setContext({ ...context, entity_personality: value || undefined })}
              placeholder="friendly, neutral, hostile, etc."
            />
          </FormField>

          <div style={{ marginTop: '12px' }}>
            <JsonFormField
              label="사용 가능한 주제 (Available Topics)"
              value={context.available_topics || {}}
              onChange={(value) => setContext({ ...context, available_topics: value })}
              fields={[
                { key: 'topics', label: '주제 목록', type: 'text', placeholder: 'greeting, trade, lore, quest, farewell (쉼표로 구분)' },
                { key: 'default_topic', label: '기본 주제', type: 'text', placeholder: 'greeting' },
              ]}
            />
          </div>

          <div style={{ marginTop: '12px' }}>
            <JsonFormField
              label="제약 조건 (Constraints)"
              value={context.constraints || {}}
              onChange={(value) => setContext({ ...context, constraints: value })}
              fields={[
                { key: 'max_response_length', label: '최대 응답 길이', type: 'number', default: 200 },
                { key: 'tone', label: '톤', type: 'text', placeholder: 'friendly, formal, casual' },
              ]}
            />
          </div>

          <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end', gap: '8px', paddingTop: '12px', borderTop: '1px solid #ddd' }}>
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
              disabled={saving || !context.title || !context.content}
              style={{
                padding: '8px 16px',
                backgroundColor: saving || !context.title || !context.content ? '#ccc' : '#4CAF50',
                color: '#fff',
                border: 'none',
                borderRadius: '2px',
                cursor: saving || !context.title || !context.content ? 'not-allowed' : 'pointer',
              }}
            >
              {saving ? '저장 중...' : '저장'}
            </button>
          </div>
        </div>
      ) : null}
    </Modal>
  );
};

