/**
 * Dialogue Knowledge 관리 컴포넌트
 */
import React, { useState, useEffect } from 'react';
import { dialogueApi } from '../services/api';
import { Modal } from './ui/Modal';
import { FormField } from './ui/FormField';
import { InputField } from './ui/InputField';
import { JsonFormField } from './ui/JsonFormField';

interface DialogueKnowledgeData {
  knowledge_id: string;
  title: string;
  content: string;
  knowledge_type: string;
  related_entities?: Record<string, any>;
  related_topics?: Record<string, any>;
  knowledge_properties?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

interface DialogueKnowledgeManagerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DialogueKnowledgeManager: React.FC<DialogueKnowledgeManagerProps> = ({
  isOpen,
  onClose,
}) => {
  const [knowledgeList, setKnowledgeList] = useState<DialogueKnowledgeData[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedKnowledge, setSelectedKnowledge] = useState<DialogueKnowledgeData | null>(null);
  const [editingKnowledge, setEditingKnowledge] = useState<DialogueKnowledgeData | null>(null);
  const [filterType, setFilterType] = useState<string>('');

  // Knowledge 목록 로드
  useEffect(() => {
    if (!isOpen) return;

    const loadKnowledge = async () => {
      setLoading(true);
      try {
        const response = await dialogueApi.getAllKnowledge();
        setKnowledgeList(response.data || []);
      } catch (error) {
        console.error('Knowledge 로드 실패:', error);
        setKnowledgeList([]);
      } finally {
        setLoading(false);
      }
    };

    loadKnowledge();
  }, [isOpen]);

  const handleCreate = () => {
    setEditingKnowledge({
      knowledge_id: `KNOWLEDGE_${Date.now()}`,
      title: '',
      content: '',
      knowledge_type: 'lore',
      related_entities: {},
      related_topics: {},
      knowledge_properties: {},
    });
  };

  const handleEdit = (knowledge: DialogueKnowledgeData) => {
    setEditingKnowledge({ ...knowledge });
  };

  const handleSave = async () => {
    if (!editingKnowledge) return;

    try {
      if (selectedKnowledge && selectedKnowledge.knowledge_id === editingKnowledge.knowledge_id) {
        // 업데이트
        await dialogueApi.updateKnowledge(editingKnowledge.knowledge_id, {
          title: editingKnowledge.title,
          content: editingKnowledge.content,
          knowledge_type: editingKnowledge.knowledge_type,
          related_entities: editingKnowledge.related_entities,
          related_topics: editingKnowledge.related_topics,
          knowledge_properties: editingKnowledge.knowledge_properties,
        });
      } else {
        // 생성
        await dialogueApi.createKnowledge({
          knowledge_id: editingKnowledge.knowledge_id,
          title: editingKnowledge.title,
          content: editingKnowledge.content,
          knowledge_type: editingKnowledge.knowledge_type,
          related_entities: editingKnowledge.related_entities,
          related_topics: editingKnowledge.related_topics,
          knowledge_properties: editingKnowledge.knowledge_properties,
        });
      }

      // 목록 새로고침
      const response = await dialogueApi.getAllKnowledge();
      setKnowledgeList(response.data || []);
      setEditingKnowledge(null);
      setSelectedKnowledge(null);
    } catch (error) {
      console.error('저장 실패:', error);
      alert('저장에 실패했습니다.');
    }
  };

  const handleDelete = async (knowledgeId: string) => {
    if (!confirm('정말로 이 지식을 삭제하시겠습니까?')) return;

    try {
      await dialogueApi.deleteKnowledge(knowledgeId);
      // 목록 새로고침
      const response = await dialogueApi.getAllKnowledge();
      setKnowledgeList(response.data || []);
      if (selectedKnowledge?.knowledge_id === knowledgeId) {
        setSelectedKnowledge(null);
      }
    } catch (error) {
      console.error('삭제 실패:', error);
      alert('삭제에 실패했습니다.');
    }
  };

  const filteredKnowledge = filterType
    ? knowledgeList.filter((k) => k.knowledge_type === filterType)
    : knowledgeList;

  const knowledgeTypes = Array.from(new Set(knowledgeList.map((k) => k.knowledge_type)));

  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose} title="대화 지식 관리" width="900px" height="85vh">
        <div style={{ display: 'flex', height: '100%', gap: '12px' }}>
          {/* 왼쪽: 목록 */}
          <div style={{ flex: '0 0 300px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <InputField
                type="select"
                value={filterType}
                onChange={(value) => setFilterType(value)}
                options={['', ...knowledgeTypes]}
                placeholder="타입 필터"
              />
              <button
                onClick={handleCreate}
                style={{
                  padding: '6px 12px',
                  backgroundColor: '#4CAF50',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '2px',
                  cursor: 'pointer',
                  fontSize: '11px',
                }}
              >
                + 새 지식
              </button>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', border: '1px solid #ddd', borderRadius: '4px', padding: '4px' }}>
              {loading ? (
                <div style={{ padding: '20px', textAlign: 'center' }}>로딩 중...</div>
              ) : filteredKnowledge.length === 0 ? (
                <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                  지식이 없습니다.
                </div>
              ) : (
                filteredKnowledge.map((knowledge) => (
                  <div
                    key={knowledge.knowledge_id}
                    onClick={() => setSelectedKnowledge(knowledge)}
                    style={{
                      padding: '8px',
                      marginBottom: '4px',
                      backgroundColor: selectedKnowledge?.knowledge_id === knowledge.knowledge_id ? '#e3f2fd' : '#fff',
                      border: selectedKnowledge?.knowledge_id === knowledge.knowledge_id ? '1px solid #2196F3' : '1px solid #ddd',
                      borderRadius: '2px',
                      cursor: 'pointer',
                    }}
                  >
                    <div style={{ fontWeight: 'bold', fontSize: '12px' }}>{knowledge.title}</div>
                    <div style={{ fontSize: '10px', color: '#666', marginTop: '2px' }}>
                      [{knowledge.knowledge_type}] {knowledge.content.substring(0, 50)}
                      {knowledge.content.length > 50 ? '...' : ''}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* 오른쪽: 상세 정보 */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '12px', overflowY: 'auto' }}>
            {selectedKnowledge ? (
              <div style={{ padding: '12px', backgroundColor: '#f9f9f9', borderRadius: '4px', border: '1px solid #ddd' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{selectedKnowledge.title}</div>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <button
                      onClick={() => handleEdit(selectedKnowledge)}
                      style={{
                        padding: '4px 8px',
                        backgroundColor: '#2196F3',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '2px',
                        cursor: 'pointer',
                        fontSize: '11px',
                      }}
                    >
                      편집
                    </button>
                    <button
                      onClick={() => handleDelete(selectedKnowledge.knowledge_id)}
                      style={{
                        padding: '4px 8px',
                        backgroundColor: '#f44336',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '2px',
                        cursor: 'pointer',
                        fontSize: '11px',
                      }}
                    >
                      삭제
                    </button>
                  </div>
                </div>
                <div style={{ fontSize: '11px', color: '#666', marginBottom: '8px' }}>
                  ID: {selectedKnowledge.knowledge_id} | 타입: {selectedKnowledge.knowledge_type}
                </div>
                <div style={{ fontSize: '12px', marginBottom: '12px', whiteSpace: 'pre-wrap' }}>
                  {selectedKnowledge.content}
                </div>
                {selectedKnowledge.related_entities && Object.keys(selectedKnowledge.related_entities).length > 0 && (
                  <div style={{ marginBottom: '8px' }}>
                    <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '4px' }}>관련 엔티티:</div>
                    <div style={{ fontSize: '10px', color: '#666' }}>
                      {JSON.stringify(selectedKnowledge.related_entities, null, 2)}
                    </div>
                  </div>
                )}
                {selectedKnowledge.related_topics && Object.keys(selectedKnowledge.related_topics).length > 0 && (
                  <div style={{ marginBottom: '8px' }}>
                    <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '4px' }}>관련 주제:</div>
                    <div style={{ fontSize: '10px', color: '#666' }}>
                      {JSON.stringify(selectedKnowledge.related_topics, null, 2)}
                    </div>
                  </div>
                )}
                {selectedKnowledge.knowledge_properties && Object.keys(selectedKnowledge.knowledge_properties).length > 0 && (
                  <div>
                    <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '4px' }}>속성:</div>
                    <div style={{ fontSize: '10px', color: '#666' }}>
                      {JSON.stringify(selectedKnowledge.knowledge_properties, null, 2)}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
                왼쪽에서 지식을 선택하거나 새로 생성하세요.
              </div>
            )}
          </div>
        </div>
      </Modal>

      {/* 편집 모달 */}
      {editingKnowledge && (
        <Modal
          isOpen={!!editingKnowledge}
          onClose={() => setEditingKnowledge(null)}
          title={selectedKnowledge ? '지식 편집' : '새 지식 생성'}
          width="700px"
          height="85vh"
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', minHeight: '100%' }}>
            <FormField label="Knowledge ID" labelWidth={150}>
              <InputField
                type="text"
                value={editingKnowledge.knowledge_id}
                onChange={(value) => setEditingKnowledge({ ...editingKnowledge, knowledge_id: value })}
                readOnly={!!selectedKnowledge}
              />
            </FormField>

            <FormField label="제목 (Title)" labelWidth={150}>
              <InputField
                type="text"
                value={editingKnowledge.title}
                onChange={(value) => setEditingKnowledge({ ...editingKnowledge, title: value })}
              />
            </FormField>

            <FormField label="내용 (Content)" labelWidth={150}>
              <InputField
                type="textarea"
                value={editingKnowledge.content}
                onChange={(value) => setEditingKnowledge({ ...editingKnowledge, content: value })}
                rows={6}
              />
            </FormField>

            <FormField label="지식 타입 (Type)" labelWidth={150}>
              <InputField
                type="select"
                value={editingKnowledge.knowledge_type}
                onChange={(value) => setEditingKnowledge({ ...editingKnowledge, knowledge_type: value })}
                options={['lore', 'quest', 'location', 'character', 'item', 'event', 'history', 'other']}
              />
            </FormField>

            <div style={{ marginTop: '12px' }}>
              <JsonFormField
                label="관련 엔티티 (Related Entities)"
                value={editingKnowledge.related_entities || {}}
                onChange={(value) => setEditingKnowledge({ ...editingKnowledge, related_entities: value })}
                fields={[
                  { key: 'npcs', label: 'NPC 목록', type: 'text', placeholder: 'NPC_001, NPC_002 (쉼표로 구분)' },
                  { key: 'locations', label: '위치 목록', type: 'text', placeholder: 'LOCATION_001, LOCATION_002 (쉼표로 구분)' },
                ]}
              />
            </div>

            <div style={{ marginTop: '12px' }}>
              <JsonFormField
                label="관련 주제 (Related Topics)"
                value={editingKnowledge.related_topics || {}}
                onChange={(value) => setEditingKnowledge({ ...editingKnowledge, related_topics: value })}
                fields={[
                  { key: 'main_topics', label: '주요 주제', type: 'text', placeholder: 'topic1, topic2 (쉼표로 구분)' },
                  { key: 'sub_topics', label: '하위 주제', type: 'text', placeholder: 'sub1, sub2 (쉼표로 구분)' },
                ]}
              />
            </div>

            <div style={{ marginTop: '12px' }}>
              <JsonFormField
                label="지식 속성 (Properties)"
                value={editingKnowledge.knowledge_properties || {}}
                onChange={(value) => setEditingKnowledge({ ...editingKnowledge, knowledge_properties: value })}
                fields={[
                  { key: 'importance', label: '중요도', type: 'number', default: 1 },
                  { key: 'reveal_conditions', label: '공개 조건', type: 'text', placeholder: 'quest_stage: 2' },
                ]}
              />
            </div>

            <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end', gap: '8px', paddingTop: '12px', borderTop: '1px solid #ddd' }}>
              <button
                onClick={() => setEditingKnowledge(null)}
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
                disabled={!editingKnowledge.title || !editingKnowledge.content}
                style={{
                  padding: '8px 16px',
                  backgroundColor: !editingKnowledge.title || !editingKnowledge.content ? '#ccc' : '#4CAF50',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '2px',
                  cursor: !editingKnowledge.title || !editingKnowledge.content ? 'not-allowed' : 'pointer',
                }}
              >
                저장
              </button>
            </div>
          </div>
        </Modal>
      )}
    </>
  );
};

