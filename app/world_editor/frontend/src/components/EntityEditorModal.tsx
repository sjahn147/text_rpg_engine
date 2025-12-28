/**
 * Entity (인물) 편집 모달
 */
import React, { useState, useEffect } from 'react';
import { entitiesApi, cellsApi, locationsApi, effectCarriersApi, dialogueApi, behaviorSchedulesApi } from '../services/api';
import { Modal } from './ui/Modal';
import { CollapsibleSection } from './ui/CollapsibleSection';
import { FormField } from './ui/FormField';
import { InputField } from './ui/InputField';
import { JsonFormField } from './ui/JsonFormField';
import { EffectCarrierEditorModal } from './EffectCarrierEditorModal';
import { BehaviorScheduleEditorModal } from './BehaviorScheduleEditorModal';
import { DialogueContextEditorModal } from './DialogueContextEditorModal';

interface EntityData {
  entity_id: string;
  entity_type: string;
  entity_name: string;
  entity_description?: string;
  entity_status?: string;
  base_stats: Record<string, any>;
  default_equipment: Record<string, any>;
  default_abilities: Record<string, any>;
  default_inventory: Record<string, any>;
  entity_properties: Record<string, any>;
  dialogue_context_id?: string;
  created_at: string;
  updated_at: string;
}

interface CellData {
  cell_id: string;
  location_id: string;
  cell_name?: string;
}

interface LocationData {
  location_id: string;
  location_name: string;
}

interface EntityEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  entityId: string | null;
  onSave: () => Promise<void>;
  embedded?: boolean; // 사이드바에 임베드된 경우 true
}

export const EntityEditorModal: React.FC<EntityEditorModalProps> = ({
  isOpen,
  onClose,
  entityId,
  onSave,
  embedded = false,
}) => {
  const [entity, setEntity] = useState<EntityData | null>(null);
  const [cell, setCell] = useState<CellData | null>(null);
  const [location, setLocation] = useState<LocationData | null>(null);
  const [effectCarriers, setEffectCarriers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingEffectId, setEditingEffectId] = useState<string | null>(null);
  const [dialogueContexts, setDialogueContexts] = useState<any[]>([]);
  const [selectedDialogueContext, setSelectedDialogueContext] = useState<any | null>(null);
  const [dialogueTopics, setDialogueTopics] = useState<any[]>([]);
  const [showDialogueManager, setShowDialogueManager] = useState(false);
  const [behaviorSchedules, setBehaviorSchedules] = useState<any[]>([]);
  const [editingScheduleId, setEditingScheduleId] = useState<string | null>(null);
  const [editingDialogueContextId, setEditingDialogueContextId] = useState<string | null>(null);

  // Entity 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      // embedded 모드에서는 isOpen 체크를 건너뛰고 entityId만 확인
      if ((!embedded && !isOpen) || !entityId) {
        setEntity(null);
        setCell(null);
        setLocation(null);
        return;
      }

      setLoading(true);
      try {
        // Entity 조회
        const entityResponse = await entitiesApi.getById(entityId);
        const entityData = entityResponse.data;
        setEntity(entityData);

        // Cell 조회 (entity_properties에서 cell_id 가져오기)
        const cellId = entityData.entity_properties?.cell_id;
        if (cellId) {
          try {
            const cellResponse = await cellsApi.getById(cellId);
            setCell(cellResponse.data);

            // Location 조회
            if (cellResponse.data.location_id) {
              const locationResponse = await locationsApi.getById(cellResponse.data.location_id);
              setLocation(locationResponse.data);
            }
          } catch (error) {
            console.error('Cell/Location 조회 실패:', error);
          }
        }

        // Effect Carriers 조회
        try {
          const effectsResponse = await effectCarriersApi.getByEntity(entityId);
          setEffectCarriers(effectsResponse.data || []);
        } catch (error) {
          console.error('Effect Carriers 조회 실패:', error);
          setEffectCarriers([]);
        }

        // Dialogue Contexts 조회
        try {
          const contextsResponse = await dialogueApi.getContextsByEntity(entityId);
          const contexts = contextsResponse.data || [];
          setDialogueContexts(contexts);
          
          // Entity의 dialogue_context_id와 일치하는 Context 찾기
          if (entityData.dialogue_context_id) {
            const matchingContext = contexts.find((ctx: any) => ctx.dialogue_id === entityData.dialogue_context_id);
            if (matchingContext) {
              setSelectedDialogueContext(matchingContext);
              // Topics 로드
              const topicsResponse = await dialogueApi.getTopics(matchingContext.dialogue_id);
              setDialogueTopics(topicsResponse.data || []);
            }
          }
        } catch (error) {
          console.error('Dialogue Contexts 조회 실패:', error);
          setDialogueContexts([]);
        }

        // Behavior Schedules 조회
        try {
          const schedulesResponse = await behaviorSchedulesApi.getByEntity(entityId);
          setBehaviorSchedules(schedulesResponse.data || []);
        } catch (error) {
          console.error('Behavior Schedules 조회 실패:', error);
          setBehaviorSchedules([]);
        }
      } catch (error) {
        console.error('데이터 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [isOpen, entityId, embedded]); // entityId가 변경될 때마다 데이터 다시 로드

  const handleSave = async () => {
    if (!entity) return;

    try {
      setSaving(true);
      await entitiesApi.update(entity.entity_id, {
        entity_type: entity.entity_type,
        entity_name: entity.entity_name,
        entity_description: entity.entity_description,
        entity_status: entity.entity_status,
        base_stats: entity.base_stats,
        default_equipment: entity.default_equipment,
        default_abilities: entity.default_abilities,
        default_inventory: entity.default_inventory,
        entity_properties: entity.entity_properties,
        dialogue_context_id: entity.dialogue_context_id,
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

  if (!isOpen) return null;
  
  if (loading) {
    return embedded ? (
      <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>로딩 중...</div>
    ) : (
      <Modal isOpen={isOpen} onClose={onClose} title="인물 편집" width="700px" height="85vh">
        <div style={{ padding: '20px', textAlign: 'center' }}>로딩 중...</div>
      </Modal>
    );
  }

  if (!entity) {
    return embedded ? (
      <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
        엔티티를 선택하세요
      </div>
    ) : null;
  }

  const content = (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', minHeight: embedded ? '100%' : 'auto', height: embedded ? '100%' : 'auto', overflow: embedded ? 'auto' : 'visible' }}>
      <CollapsibleSection title="기본 정보" defaultExpanded={true}>
        <FormField label="ID" labelWidth={120}>
              <InputField
                type="text"
                value={entity.entity_id}
                onChange={() => {}}
                readOnly
                copyButton
              />
        </FormField>
        <FormField label="타입" labelWidth={120}>
              <InputField
                type="text"
                value={entity.entity_type}
                onChange={(value) => setEntity({ ...entity, entity_type: value })}
              />
        </FormField>
        <FormField label="이름" labelWidth={120}>
              <InputField
                type="text"
                value={entity.entity_name}
                onChange={(value) => setEntity({ ...entity, entity_name: value })}
              />
            </FormField>
            <FormField label="설명" labelWidth={120}>
              <InputField
                type="textarea"
                value={entity.entity_description || ''}
                onChange={(value) => setEntity({ ...entity, entity_description: value })}
                rows={4}
              />
        </FormField>
        <FormField label="상태 (Status)" labelWidth={120}>
              <InputField
                type="select"
                value={entity.entity_status || 'active'}
                onChange={(value) => setEntity({ ...entity, entity_status: value })}
                options={['active', 'inactive', 'dead', 'hidden']}
              />
        </FormField>
      </CollapsibleSection>

      <CollapsibleSection title="셀 정보" defaultExpanded={true}>
            {cell ? (
              <>
                <FormField label="Cell" labelWidth={120}>
                  <InputField
                    type="text"
                    value={`${cell.cell_id}${cell.cell_name ? ` - ${cell.cell_name}` : ''}`}
                    onChange={() => {}}
                    readOnly
                  />
                </FormField>
                {location && (
                  <FormField label="Location" labelWidth={120}>
                    <InputField
                      type="text"
                      value={`${location.location_id} - ${location.location_name}`}
                      onChange={() => {}}
                      readOnly
                    />
                  </FormField>
                )}
              </>
            ) : (
              <div style={{ padding: '8px', fontSize: '12px', color: '#999' }}>
                셀 정보가 없습니다.
              </div>
            )}
      </CollapsibleSection>

      <CollapsibleSection title="능력치 (Base Stats)" defaultExpanded={false}>
            <div style={{ padding: '8px' }}>
              <JsonFormField
                label="능력치"
                value={entity.base_stats || {}}
                onChange={(value) => setEntity({ ...entity, base_stats: value })}
                fields={[
                  { key: 'hp', label: 'HP', type: 'number', default: 0 },
                  { key: 'mp', label: 'MP', type: 'number', default: 0 },
                  { key: 'strength', label: '힘 (Strength)', type: 'number', default: 0 },
                  { key: 'intelligence', label: '지능 (Intelligence)', type: 'number', default: 0 },
                  { key: 'charisma', label: '매력 (Charisma)', type: 'number', default: 0 },
                  { key: 'dexterity', label: '민첩 (Dexterity)', type: 'number', default: 0 },
                  { key: 'constitution', label: '체력 (Constitution)', type: 'number', default: 0 },
                  { key: 'wisdom', label: '지혜 (Wisdom)', type: 'number', default: 0 },
                ]}
              />
              <div style={{ marginTop: '12px', padding: '8px', backgroundColor: '#f9f9f9', borderRadius: '2px' }}>
                <div style={{ fontSize: '10px', color: '#666', marginBottom: '4px' }}>고급 편집 (JSON):</div>
                <InputField
                  type="textarea"
                  value={JSON.stringify(entity.base_stats || {}, null, 2)}
                  onChange={(value) => {
                    try {
                      const parsed = JSON.parse(value);
                      setEntity({ ...entity, base_stats: parsed });
                    } catch (e) {
                      // JSON 파싱 실패 시 무시
                    }
                  }}
                  rows={4}
                />
              </div>
            </div>
      </CollapsibleSection>

      <CollapsibleSection title="기본 장비 (Default Equipment)" defaultExpanded={false}>
            <div style={{ padding: '8px' }}>
              <JsonFormField
                label="장비"
                value={entity.default_equipment || {}}
                onChange={(value) => setEntity({ ...entity, default_equipment: value })}
                fields={[
                  { key: 'weapon', label: '무기 (Weapon)', type: 'text', placeholder: 'WEAPON_SWORD_NORMAL_001' },
                  { key: 'armor', label: '방어구 (Armor)', type: 'text', placeholder: 'ARMOR_PLATE_NORMAL_001' },
                  { key: 'shield', label: '방패 (Shield)', type: 'text', placeholder: 'SHIELD_WOOD_001' },
                  { key: 'accessory', label: '액세서리 (Accessory)', type: 'text', placeholder: 'ACCESSORY_RING_001' },
                ]}
              />
              <div style={{ marginTop: '12px', padding: '8px', backgroundColor: '#f9f9f9', borderRadius: '2px' }}>
                <div style={{ fontSize: '10px', color: '#666', marginBottom: '4px' }}>고급 편집 (JSON):</div>
                <InputField
                  type="textarea"
                  value={JSON.stringify(entity.default_equipment || {}, null, 2)}
                  onChange={(value) => {
                    try {
                      const parsed = JSON.parse(value);
                      setEntity({ ...entity, default_equipment: parsed });
                    } catch (e) {
                      // JSON 파싱 실패 시 무시
                    }
                  }}
                  rows={4}
                />
              </div>
            </div>
      </CollapsibleSection>

      <CollapsibleSection title="기본 능력 (Default Abilities)" defaultExpanded={false}>
            <div style={{ padding: '8px' }}>
              <JsonFormField
                label="능력"
                value={entity.default_abilities || {}}
                onChange={(value) => setEntity({ ...entity, default_abilities: value })}
                fields={[
                  { key: 'skills', label: '스킬 (Skills)', type: 'array', placeholder: 'SKILL_WARRIOR_SLASH_001' },
                  { key: 'magic', label: '마법 (Magic)', type: 'array', placeholder: 'MAGIC_FIRE_BALL_001' },
                ]}
              />
              <div style={{ marginTop: '12px', padding: '8px', backgroundColor: '#f9f9f9', borderRadius: '2px' }}>
                <div style={{ fontSize: '10px', color: '#666', marginBottom: '4px' }}>고급 편집 (JSON):</div>
                <InputField
                  type="textarea"
                  value={JSON.stringify(entity.default_abilities || {}, null, 2)}
                  onChange={(value) => {
                    try {
                      const parsed = JSON.parse(value);
                      setEntity({ ...entity, default_abilities: parsed });
                    } catch (e) {
                      // JSON 파싱 실패 시 무시
                    }
                  }}
                  rows={4}
                />
              </div>
            </div>
      </CollapsibleSection>

      <CollapsibleSection title="기본 인벤토리 (Default Inventory)" defaultExpanded={false}>
            <div style={{ padding: '8px' }}>
              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '8px' }}>아이템 목록:</div>
                <JsonFormField
                  label="아이템"
                  value={entity.default_inventory || {}}
                  onChange={(value) => setEntity({ ...entity, default_inventory: value })}
                  fields={[
                    { key: 'items', label: '아이템 ID 목록', type: 'array', placeholder: 'ITEM_POTION_HEAL_001' },
                  ]}
                />
              </div>
              <div style={{ marginTop: '12px' }}>
                <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '8px' }}>아이템 수량:</div>
                <div style={{ fontSize: '11px', color: '#666', marginBottom: '8px' }}>
                  각 아이템의 수량을 입력하세요. (예: ITEM_POTION_HEAL_001: 10)
                </div>
                {entity.default_inventory?.items && Array.isArray(entity.default_inventory.items) && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {entity.default_inventory.items.map((itemId, index) => (
                      <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <label style={{ minWidth: '200px', fontSize: '11px' }}>{itemId}:</label>
                        <input
                          type="number"
                          value={entity.default_inventory?.quantities?.[itemId] || 0}
                          onChange={(e) => {
                            const newInventory = { ...(entity.default_inventory || {}) };
                            if (!newInventory.quantities) {
                              newInventory.quantities = {};
                            }
                            newInventory.quantities[itemId] = Number(e.target.value);
                            setEntity({ ...entity, default_inventory: newInventory });
                          }}
                          min="0"
                          style={{
                            width: '80px',
                            padding: '4px 8px',
                            border: '1px solid #ddd',
                            borderRadius: '2px',
                            fontSize: '12px',
                          }}
                        />
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <div style={{ marginTop: '12px', padding: '8px', backgroundColor: '#f9f9f9', borderRadius: '2px' }}>
                <div style={{ fontSize: '10px', color: '#666', marginBottom: '4px' }}>고급 편집 (JSON):</div>
                <InputField
                  type="textarea"
                  value={JSON.stringify(entity.default_inventory || {}, null, 2)}
                  onChange={(value) => {
                    try {
                      const parsed = JSON.parse(value);
                      setEntity({ ...entity, default_inventory: parsed });
                    } catch (e) {
                      // JSON 파싱 실패 시 무시
                    }
                  }}
                  rows={4}
                />
              </div>
            </div>
      </CollapsibleSection>

      <CollapsibleSection title="엔티티 속성 (Entity Properties)" defaultExpanded={false}>
            <div style={{ padding: '8px' }}>
              <JsonFormField
                label="속성"
                value={entity.entity_properties || {}}
                onChange={(value) => setEntity({ ...entity, entity_properties: value })}
                fields={[
                  { key: 'cell_id', label: '셀 ID (Cell ID)', type: 'text', placeholder: 'CELL_...' },
                  { key: 'occupation', label: '직업 (Occupation)', type: 'text', placeholder: 'merchant, guard, npc' },
                  { key: 'personality', label: '성격 (Personality)', type: 'text', placeholder: 'friendly, neutral, hostile' },
                  { key: 'dialogue', label: '대사 (Dialogue)', type: 'textarea', placeholder: 'NPC의 기본 대사' },
                  { key: 'faction', label: '팩션 (Faction)', type: 'text', placeholder: '제국군, 조르가즈 갱' },
                  { key: 'template_type', label: '템플릿 타입', type: 'text', placeholder: 'merchant, quest_giver, npc' },
                  { key: 'ai_type', label: 'AI 타입', type: 'text', placeholder: 'merchant, stationary, aggressive' },
                  { key: 'shop_inventory', label: '상점 인벤토리', type: 'array', placeholder: '["item1", "item2"]' },
                  { key: 'available_quests', label: '제공 가능 퀘스트', type: 'array', placeholder: '["quest1", "quest2"]' },
                  { key: 'gold', label: '골드 (Gold)', type: 'number', default: 0 },
                  { key: 'is_hostile', label: '적대적 (Is Hostile)', type: 'boolean', default: false },
                  { key: 'interaction_flags', label: '상호작용 플래그', type: 'array', placeholder: 'can_trade, can_talk' },
                  { key: 'knowledge', label: '지식 (Knowledge)', type: 'array', placeholder: 'local_news, village_history' },
                ]}
              />
              <div style={{ marginTop: '12px', padding: '8px', backgroundColor: '#f9f9f9', borderRadius: '2px' }}>
                <div style={{ fontSize: '10px', color: '#666', marginBottom: '4px' }}>고급 편집 (JSON):</div>
                <InputField
                  type="textarea"
                  value={JSON.stringify(entity.entity_properties || {}, null, 2)}
                  onChange={(value) => {
                    try {
                      const parsed = JSON.parse(value);
                      setEntity({ ...entity, entity_properties: parsed });
                    } catch (e) {
                      // JSON 파싱 실패 시 무시
                    }
                  }}
                  rows={4}
                />
              </div>
            </div>
      </CollapsibleSection>

      <CollapsibleSection title="대화 시스템 (Dialogue System)" defaultExpanded={false}>
            <div style={{ padding: '8px' }}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ fontSize: '12px', display: 'block', marginBottom: '4px' }}>
                  대화 컨텍스트 ID (Dialogue Context ID):
                </label>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <div style={{ flex: 1 }}>
                    <InputField
                      type="text"
                      value={entity.dialogue_context_id || ''}
                      onChange={(value) => setEntity({ ...entity, dialogue_context_id: value || undefined })}
                      placeholder="DIALOGUE_..."
                    />
                  </div>
                  <button
                    onClick={() => setShowDialogueManager(!showDialogueManager)}
                    style={{
                      fontSize: '11px',
                      padding: '4px 12px',
                      backgroundColor: showDialogueManager ? '#4CAF50' : '#2196F3',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '2px',
                      cursor: 'pointer',
                    }}
                  >
                    {showDialogueManager ? '닫기' : '대화 관리'}
                  </button>
                </div>
              </div>

              {showDialogueManager && (
                <div style={{ marginTop: '12px', padding: '12px', backgroundColor: '#f5f5f5', borderRadius: '4px', border: '1px solid #ddd' }}>
                  <div style={{ fontSize: '13px', fontWeight: 'bold', marginBottom: '12px' }}>
                    대화 컨텍스트 관리
                  </div>
                  
                  {/* Dialogue Contexts 목록 */}
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ fontSize: '12px', marginBottom: '8px', fontWeight: 'bold' }}>
                      대화 컨텍스트 목록 ({dialogueContexts.length}개)
                    </div>
                    {dialogueContexts.length === 0 ? (
                      <div style={{ fontSize: '11px', color: '#999', fontStyle: 'italic', marginBottom: '8px' }}>
                        대화 컨텍스트가 없습니다.
                      </div>
                    ) : (
                      <div style={{ maxHeight: '150px', overflowY: 'auto', border: '1px solid #ddd', borderRadius: '2px', padding: '4px' }}>
                        {dialogueContexts.map((ctx: any) => (
                          <div
                            key={ctx.dialogue_id}
                            onClick={async () => {
                              setSelectedDialogueContext(ctx);
                              setEntity({ ...entity, dialogue_context_id: ctx.dialogue_id });
                              try {
                                const topicsResponse = await dialogueApi.getTopics(ctx.dialogue_id);
                                setDialogueTopics(topicsResponse.data || []);
                              } catch (error) {
                                console.error('Topics 로드 실패:', error);
                                setDialogueTopics([]);
                              }
                            }}
                            style={{
                              padding: '6px 8px',
                              marginBottom: '4px',
                              backgroundColor: selectedDialogueContext?.dialogue_id === ctx.dialogue_id ? '#e3f2fd' : '#fff',
                              border: selectedDialogueContext?.dialogue_id === ctx.dialogue_id ? '1px solid #2196F3' : '1px solid #ddd',
                              borderRadius: '2px',
                              cursor: 'pointer',
                              fontSize: '11px',
                            }}
                          >
                            <div style={{ fontWeight: 'bold' }}>{ctx.title}</div>
                            <div style={{ fontSize: '10px', color: '#666', marginTop: '2px' }}>
                              ID: {ctx.dialogue_id} | 우선순위: {ctx.priority}
                              {ctx.cell_id && ` | Cell: ${ctx.cell_id}`}
                              {ctx.time_category && ` | 시간: ${ctx.time_category}`}
                              {ctx.event_id && ` | 이벤트: ${ctx.event_id}`}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    <div style={{ display: 'flex', gap: '4px', marginTop: '8px' }}>
                      <button
                        onClick={() => {
                          setEditingDialogueContextId(null);
                        }}
                        style={{
                          fontSize: '11px',
                          padding: '4px 12px',
                          backgroundColor: '#4CAF50',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '2px',
                          cursor: 'pointer',
                        }}
                      >
                        + 새 Context 생성
                      </button>
                      {selectedDialogueContext && (
                        <button
                          onClick={() => {
                            setEditingDialogueContextId(selectedDialogueContext.dialogue_id);
                          }}
                          style={{
                            fontSize: '11px',
                            padding: '4px 12px',
                            backgroundColor: '#2196F3',
                            color: '#fff',
                            border: 'none',
                            borderRadius: '2px',
                            cursor: 'pointer',
                          }}
                        >
                          편집
                        </button>
                      )}
                    </div>
                  </div>

                  {/* 선택된 Dialogue Context의 Topics 표시 */}
                  {selectedDialogueContext && (
                    <div style={{ marginTop: '12px', padding: '8px', backgroundColor: '#fff', borderRadius: '2px', border: '1px solid #ddd' }}>
                      <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '8px' }}>
                        대화 주제 (Topics) - {selectedDialogueContext.title}
                      </div>
                      {dialogueTopics.length === 0 ? (
                        <div style={{ fontSize: '11px', color: '#999', fontStyle: 'italic', marginBottom: '8px' }}>
                          주제가 없습니다.
                        </div>
                      ) : (
                        <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                          {dialogueTopics.map((topic: any) => (
                            <div
                              key={topic.topic_id}
                              style={{
                                padding: '6px 8px',
                                marginBottom: '4px',
                                backgroundColor: '#f9f9f9',
                                border: '1px solid #ddd',
                                borderRadius: '2px',
                                fontSize: '11px',
                              }}
                            >
                              <div style={{ fontWeight: 'bold', color: '#2196F3' }}>
                                [{topic.topic_type}] {topic.content?.substring(0, 50)}{topic.content?.length > 50 ? '...' : ''}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      <button
                        onClick={async () => {
                          const topicType = prompt('주제 타입을 선택하세요 (greeting, trade, lore, quest, farewell):', 'greeting');
                          if (topicType && ['greeting', 'trade', 'lore', 'quest', 'farewell'].includes(topicType)) {
                            const content = prompt('주제 내용을 입력하세요:');
                            if (content) {
                              const topicId = `TOPIC_${selectedDialogueContext.dialogue_id}_${topicType}_${Date.now()}`;
                              try {
                                await dialogueApi.createTopic({
                                  topic_id: topicId,
                                  dialogue_id: selectedDialogueContext.dialogue_id,
                                  topic_type: topicType,
                                  content: content,
                                  conditions: {}
                                });
                                const topicsResponse = await dialogueApi.getTopics(selectedDialogueContext.dialogue_id);
                                setDialogueTopics(topicsResponse.data || []);
                                alert('대화 주제가 추가되었습니다.');
                              } catch (error) {
                                console.error('Dialogue Topic 생성 실패:', error);
                                alert('대화 주제 추가에 실패했습니다.');
                              }
                            }
                          } else {
                            alert('올바른 주제 타입을 입력하세요: greeting, trade, lore, quest, farewell');
                          }
                        }}
                        style={{
                          fontSize: '11px',
                          padding: '4px 12px',
                          backgroundColor: '#FF9800',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '2px',
                          cursor: 'pointer',
                          marginTop: '8px',
                        }}
                      >
                        + 주제 추가
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
      </CollapsibleSection>

      <CollapsibleSection 
            title="행동 스케줄 (Behavior Schedules)" 
            count={behaviorSchedules.length}
            defaultExpanded={false}
            actionButton={
              <button
                onClick={async (e) => {
                  e.stopPropagation();
                  if (!entity) return;
                  
                  const timePeriod = prompt('시간대를 선택하세요 (morning, afternoon, evening, night):', 'morning');
                  if (timePeriod && ['morning', 'afternoon', 'evening', 'night'].includes(timePeriod)) {
                    const actionType = prompt('행동 타입을 입력하세요 (work, rest, socialize, patrol, sleep):', 'work');
                    if (actionType) {
                      const priorityStr = prompt('우선순위를 입력하세요 (1-10, 기본값: 1):', '1');
                      const priority = parseInt(priorityStr || '1', 10) || 1;
                      
                      try {
                        await behaviorSchedulesApi.create({
                          entity_id: entity.entity_id,
                          time_period: timePeriod,
                          action_type: actionType,
                          action_priority: priority,
                          conditions: {},
                          action_data: {}
                        });
                        // 스케줄 목록 새로고침
                        const schedulesResponse = await behaviorSchedulesApi.getByEntity(entity.entity_id);
                        setBehaviorSchedules(schedulesResponse.data || []);
                      } catch (error) {
                        console.error('행동 스케줄 생성 실패:', error);
                        alert('행동 스케줄 생성에 실패했습니다.');
                      }
                    }
                  } else {
                    alert('올바른 시간대를 입력하세요: morning, afternoon, evening, night');
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
            {behaviorSchedules.length === 0 ? (
              <div style={{ padding: '8px', fontSize: '12px', color: '#999' }}>
                행동 스케줄이 없습니다.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {behaviorSchedules.map((schedule) => (
                  <div
                    key={schedule.schedule_id}
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
                      onClick={() => {
                        setEditingScheduleId(schedule.schedule_id);
                      }}
                    >
                      <div>
                        <span style={{ fontSize: '12px', fontWeight: 'bold' }}>
                          [{schedule.time_period}] {schedule.action_type}
                        </span>
                        <div style={{ fontSize: '10px', color: '#666', marginTop: '2px' }}>
                          우선순위: {schedule.action_priority}
                          {Object.keys(schedule.conditions || {}).length > 0 && ' | 조건 있음'}
                          {Object.keys(schedule.action_data || {}).length > 0 && ' | 데이터 있음'}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={async (e) => {
                        e.stopPropagation();
                        if (confirm(`정말로 이 행동 스케줄을 삭제하시겠습니까?`)) {
                          try {
                            await behaviorSchedulesApi.delete(schedule.schedule_id);
                            // 스케줄 목록 새로고침
                            if (entity) {
                              const schedulesResponse = await behaviorSchedulesApi.getByEntity(entity.entity_id);
                              setBehaviorSchedules(schedulesResponse.data || []);
                            }
                          } catch (error) {
                            console.error('행동 스케줄 삭제 실패:', error);
                            alert('행동 스케줄 삭제에 실패했습니다.');
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
            title="이펙트 캐리어 (Effect Carriers)" 
            count={effectCarriers.length}
            defaultExpanded={false}
            actionButton={
              <button
                onClick={async (e) => {
                  e.stopPropagation();
                  const effectName = prompt('이펙트 이름을 입력하세요:');
                  if (effectName && entity) {
                    const carrierType = prompt('타입을 입력하세요 (skill, buff, item, blessing, curse, ritual):');
                    if (carrierType) {
                      try {
                        await effectCarriersApi.create({
                          name: effectName,
                          carrier_type: carrierType,
                          effect_json: {},
                          constraints_json: {},
                          source_entity_id: entity.entity_id,
                          tags: [],
                        });
                        // 이펙트 목록 새로고침
                        const effectsResponse = await effectCarriersApi.getByEntity(entity.entity_id);
                        setEffectCarriers(effectsResponse.data || []);
                      } catch (error) {
                        console.error('이펙트 생성 실패:', error);
                        alert('이펙트 생성에 실패했습니다.');
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
            {effectCarriers.length === 0 ? (
              <div style={{ padding: '8px', fontSize: '12px', color: '#999' }}>
                이펙트 캐리어가 없습니다.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {effectCarriers.map((effect) => (
                  <div
                    key={effect.effect_id}
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
                      onClick={() => setEditingEffectId(effect.effect_id)}
                    >
                      <span style={{ fontSize: '12px' }}>{effect.name}</span>
                      <span style={{ fontSize: '10px', color: '#999' }}>{effect.carrier_type}</span>
                    </div>
                    <button
                      onClick={async (e) => {
                        e.stopPropagation();
                        if (confirm(`정말로 "${effect.name}"을(를) 삭제하시겠습니까?`)) {
                          try {
                            await effectCarriersApi.delete(effect.effect_id);
                            // 이펙트 목록 새로고침
                            const effectsResponse = await effectCarriersApi.getByEntity(entity!.entity_id);
                            setEffectCarriers(effectsResponse.data || []);
                          } catch (error) {
                            console.error('이펙트 삭제 실패:', error);
                            alert('이펙트 삭제에 실패했습니다.');
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
  );

  if (embedded) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div style={{ padding: '12px', borderBottom: '1px solid #ddd', backgroundColor: '#f5f5f5', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
          <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 'bold' }}>인물 편집: {entity.entity_name}</h3>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '18px',
              cursor: 'pointer',
              color: '#666',
              padding: '0',
              width: '24px',
              height: '24px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            ×
          </button>
        </div>
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px', minHeight: 0 }}>
          {content}
        </div>
        <EffectCarrierEditorModal
          isOpen={editingEffectId !== null}
          onClose={() => {
            setEditingEffectId(null);
          }}
          effectId={editingEffectId}
          onSave={async () => {
            if (entity) {
              const effectsResponse = await effectCarriersApi.getByEntity(entity.entity_id);
              setEffectCarriers(effectsResponse.data || []);
            }
          }}
        />
        <BehaviorScheduleEditorModal
          isOpen={editingScheduleId !== null}
          onClose={() => {
            setEditingScheduleId(null);
          }}
          scheduleId={editingScheduleId}
          entityId={entity?.entity_id || null}
          onSave={async () => {
            if (entity) {
              const schedulesResponse = await behaviorSchedulesApi.getByEntity(entity.entity_id);
              setBehaviorSchedules(schedulesResponse.data || []);
            }
          }}
        />
        <DialogueContextEditorModal
          isOpen={editingDialogueContextId !== null}
          onClose={() => {
            setEditingDialogueContextId(null);
          }}
          dialogueId={editingDialogueContextId}
          entityId={entity?.entity_id || null}
          onSave={async () => {
            if (entity) {
              const contextsResponse = await dialogueApi.getContextsByEntity(entity.entity_id);
              setDialogueContexts(contextsResponse.data || []);
              if (editingDialogueContextId) {
                try {
                  const updatedContext = await dialogueApi.getContext(editingDialogueContextId);
                  setSelectedDialogueContext(updatedContext.data);
                  setEntity({ ...entity, dialogue_context_id: updatedContext.data.dialogue_id });
                  const topicsResponse = await dialogueApi.getTopics(updatedContext.data.dialogue_id);
                  setDialogueTopics(topicsResponse.data || []);
                } catch (error) {
                  console.error('Context 로드 실패:', error);
                }
              }
            }
          }}
        />
      </div>
    );
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="인물 편집" width="700px" height="85vh">
      {content}
      <EffectCarrierEditorModal
        isOpen={editingEffectId !== null}
        onClose={() => {
          setEditingEffectId(null);
        }}
        effectId={editingEffectId}
        onSave={async () => {
          // 이펙트 목록 새로고침 (로컬 상태만 업데이트)
          if (entity) {
            const effectsResponse = await effectCarriersApi.getByEntity(entity.entity_id);
            setEffectCarriers(effectsResponse.data || []);
          }
          // onSave() 호출하지 않음 - 전체 새로고침 방지
        }}
      />
      <BehaviorScheduleEditorModal
        isOpen={editingScheduleId !== null}
        onClose={() => {
          setEditingScheduleId(null);
        }}
        scheduleId={editingScheduleId}
        entityId={entity?.entity_id || null}
        onSave={async () => {
          // 스케줄 목록 새로고침 (로컬 상태만 업데이트)
          if (entity) {
            const schedulesResponse = await behaviorSchedulesApi.getByEntity(entity.entity_id);
            setBehaviorSchedules(schedulesResponse.data || []);
          }
          // onSave() 호출하지 않음 - 전체 새로고침 방지
        }}
      />
      <DialogueContextEditorModal
        isOpen={editingDialogueContextId !== null}
        onClose={() => {
          setEditingDialogueContextId(null);
        }}
        dialogueId={editingDialogueContextId}
        entityId={entity?.entity_id || null}
        onSave={async () => {
          // Dialogue Context 목록 새로고침
          if (entity) {
            const contextsResponse = await dialogueApi.getContextsByEntity(entity.entity_id);
            setDialogueContexts(contextsResponse.data || []);
            // 선택된 Context가 업데이트되었으면 다시 로드
            if (editingDialogueContextId) {
              try {
                const updatedContext = await dialogueApi.getContext(editingDialogueContextId);
                setSelectedDialogueContext(updatedContext.data);
                setEntity({ ...entity, dialogue_context_id: updatedContext.data.dialogue_id });
                const topicsResponse = await dialogueApi.getTopics(updatedContext.data.dialogue_id);
                setDialogueTopics(topicsResponse.data || []);
              } catch (error) {
                console.error('Context 로드 실패:', error);
              }
            }
          }
          // onSave() 호출하지 않음 - 전체 새로고침 방지
        }}
      />
    </Modal>
  );
};

