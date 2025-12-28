/**
 * Behavior Schedule 편집 모달
 */
import React, { useState, useEffect } from 'react';
import { behaviorSchedulesApi } from '../../services/api';
import { Modal } from '../common/ui/Modal';
import { FormField } from '../common/ui/FormField';
import { InputField } from '../common/ui/InputField';
import { JsonFormField } from '../common/ui/JsonFormField';

interface BehaviorScheduleData {
  schedule_id: string;
  entity_id: string;
  time_period: string;
  action_type: string;
  action_priority: number;
  conditions: Record<string, any>;
  action_data: Record<string, any>;
  created_at: string;
  updated_at: string;
}

interface BehaviorScheduleEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  scheduleId: string | null;
  entityId: string | null;
  onSave: () => Promise<void>;
}

export const BehaviorScheduleEditorModal: React.FC<BehaviorScheduleEditorModalProps> = ({
  isOpen,
  onClose,
  scheduleId,
  entityId,
  onSave,
}) => {
  const [schedule, setSchedule] = useState<BehaviorScheduleData | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // Schedule 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      if (!isOpen) {
        setSchedule(null);
        return;
      }

      if (scheduleId) {
        // 기존 스케줄 편집
        setLoading(true);
        try {
          const response = await behaviorSchedulesApi.getById(scheduleId);
          setSchedule(response.data);
        } catch (error) {
          console.error('스케줄 로드 실패:', error);
        } finally {
          setLoading(false);
        }
      } else if (entityId) {
        // 새 스케줄 생성
        setSchedule({
          schedule_id: '',
          entity_id: entityId,
          time_period: 'morning',
          action_type: 'work',
          action_priority: 1,
          conditions: {},
          action_data: {},
          created_at: '',
          updated_at: '',
        });
      }
    };

    loadData();
  }, [isOpen, scheduleId, entityId]);

  const handleSave = async () => {
    if (!schedule) return;

    try {
      setSaving(true);
      if (scheduleId) {
        // 업데이트
        await behaviorSchedulesApi.update(scheduleId, {
          time_period: schedule.time_period,
          action_type: schedule.action_type,
          action_priority: schedule.action_priority,
          conditions: schedule.conditions,
          action_data: schedule.action_data,
        });
      } else {
        // 생성
        await behaviorSchedulesApi.create({
          entity_id: schedule.entity_id,
          time_period: schedule.time_period,
          action_type: schedule.action_type,
          action_priority: schedule.action_priority,
          conditions: schedule.conditions,
          action_data: schedule.action_data,
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

  if (!schedule && !loading) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="행동 스케줄 편집" width="600px" height="80vh">
      {loading ? (
        <div style={{ padding: '20px', textAlign: 'center' }}>로딩 중...</div>
      ) : schedule ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', minHeight: '100%' }}>
          <FormField label="시간대 (Time Period)" labelWidth={150}>
            <InputField
              type="select"
              value={schedule.time_period}
              onChange={(value) => setSchedule({ ...schedule, time_period: value })}
              options={['morning', 'afternoon', 'evening', 'night']}
            />
          </FormField>

          <FormField label="행동 타입 (Action Type)" labelWidth={150}>
            <InputField
              type="select"
              value={schedule.action_type}
              onChange={(value) => setSchedule({ ...schedule, action_type: value })}
              options={['work', 'rest', 'socialize', 'patrol', 'sleep', 'move', 'investigate', 'wait']}
            />
          </FormField>

          <FormField label="우선순위 (Priority)" labelWidth={150}>
            <InputField
              type="number"
              value={schedule.action_priority}
              onChange={(value) => setSchedule({ ...schedule, action_priority: parseInt(value, 10) || 1 })}
              min={1}
              max={10}
            />
          </FormField>

          <div style={{ marginTop: '12px' }}>
            <JsonFormField
              label="조건 (Conditions)"
              value={schedule.conditions || {}}
              onChange={(value) => setSchedule({ ...schedule, conditions: value })}
              fields={[
                { key: 'min_energy', label: '최소 에너지', type: 'number', default: 0 },
                { key: 'max_energy', label: '최대 에너지', type: 'number', default: 100 },
                { key: 'weather', label: '날씨', type: 'text', placeholder: 'clear, rain, snow' },
                { key: 'mood', label: '기분', type: 'text', placeholder: 'happy, neutral, sad' },
                { key: 'day_of_week', label: '요일', type: 'text', placeholder: 'monday, tuesday, ...' },
              ]}
            />
          </div>

          <div style={{ marginTop: '12px' }}>
            <JsonFormField
              label="행동 데이터 (Action Data)"
              value={schedule.action_data || {}}
              onChange={(value) => setSchedule({ ...schedule, action_data: value })}
              fields={[
                { key: 'duration', label: '지속 시간 (시간)', type: 'number', default: 1 },
                { key: 'location', label: '위치', type: 'text', placeholder: 'shop, tavern, home' },
                { key: 'target_entity', label: '대상 엔티티', type: 'text', placeholder: 'ENTITY_ID' },
                { key: 'target_cell', label: '대상 셀', type: 'text', placeholder: 'CELL_ID' },
                { key: 'description', label: '설명', type: 'textarea', placeholder: '행동에 대한 설명' },
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
      ) : null}
    </Modal>
  );
};

