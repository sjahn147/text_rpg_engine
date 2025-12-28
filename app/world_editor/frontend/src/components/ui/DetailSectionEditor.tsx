/**
 * 상세 정보 섹션 편집기
 */
import React, { useState } from 'react';
import { FormField } from './FormField';
import { InputField } from './InputField';

export interface DetailSection {
  id: string;
  type: 'text' | 'list' | 'structured' | 'title';
  title: string;
  content?: string;
  items?: string[];
  fields?: StructuredField[];
  expanded?: boolean;
}

export interface StructuredField {
  id: string;
  label: string;
  type: 'text' | 'longtext' | 'select' | 'list';
  value: string | string[];
  options?: string[];
}

interface DetailSectionEditorProps {
  sections: DetailSection[];
  onChange: (sections: DetailSection[]) => void;
  readOnly?: boolean;
}

// 템플릿 카테고리 정의
const TEMPLATE_CATEGORIES = [
  { id: 'identity', name: '기본 식별 정보', fields: [
    { label: '이름 (공식명)', type: 'text' as const },
    { label: '이름 (통칭)', type: 'text' as const },
    { label: '정착지 유형', type: 'select' as const, options: ['촌락', '마을', '소도시', '대도시', '수도', '요새도시'] },
    { label: '규모 (인구)', type: 'text' as const },
    { label: '물리적 크기', type: 'text' as const },
    { label: '설립 시기', type: 'text' as const },
    { label: '소속', type: 'text' as const },
    { label: '상징', type: 'longtext' as const },
    { label: '슬로건', type: 'text' as const },
    { label: '상세 설명', type: 'longtext' as const },
  ]},
  { id: 'geography', name: '지리 · 환경', fields: [
    { label: '위치', type: 'text' as const },
    { label: '지형', type: 'select' as const, options: ['평야', '산악', '해안', '사막', '숲', '늪지'] },
    { label: '인접 지형 및 랜드마크', type: 'longtext' as const },
    { label: '기후', type: 'text' as const },
    { label: '천연 자원', type: 'longtext' as const },
    { label: '자연적 위협', type: 'longtext' as const },
    { label: '방어적 지형 요소', type: 'longtext' as const },
  ]},
  { id: 'history', name: '역사', fields: [
    { label: '건국 배경', type: 'longtext' as const },
    { label: '주요 역사적 사건', type: 'longtext' as const },
    { label: '전쟁 / 침공 / 재난', type: 'longtext' as const },
    { label: '몰락 또는 재건의 기록', type: 'longtext' as const },
    { label: '전설 및 신화', type: 'longtext' as const },
    { label: '최근 10~20년 내 주요 사건', type: 'longtext' as const },
  ]},
  // 나머지 템플릿은 필요시 추가
];

export const DetailSectionEditor: React.FC<DetailSectionEditorProps> = ({
  sections,
  onChange,
  readOnly = false,
}) => {
  const [newSectionType, setNewSectionType] = useState<'text' | 'list' | 'structured' | 'title'>('text');
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');

  const addSection = () => {
    const newSection: DetailSection = {
      id: `section_${Date.now()}`,
      type: newSectionType,
      title: '',
      expanded: true,
    };

    if (newSectionType === 'text') {
      newSection.content = '';
    } else if (newSectionType === 'list') {
      newSection.items = [];
    } else if (newSectionType === 'structured') {
      const template = TEMPLATE_CATEGORIES.find(t => t.id === selectedTemplate);
      if (template) {
        newSection.title = template.name;
        newSection.fields = template.fields.map((f, idx) => ({
          id: `field_${Date.now()}_${idx}`,
          label: f.label,
          type: f.type,
          value: (f.type as any) === 'list' ? [] : '',
          options: f.options,
        }));
      }
    }

    onChange([...sections, newSection]);
    setNewSectionType('text');
    setSelectedTemplate('');
  };

  const deleteSection = (id: string) => {
    onChange(sections.filter(s => s.id !== id));
  };

  const updateSection = (id: string, updates: Partial<DetailSection>) => {
    onChange(sections.map(s => s.id === id ? { ...s, ...updates } : s));
  };

  const toggleSection = (id: string) => {
    updateSection(id, { expanded: !sections.find(s => s.id === id)?.expanded });
  };

  return (
    <div>
      {/* 섹션 추가 버튼 */}
      {!readOnly && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
            <select
              value={newSectionType}
              onChange={(e) => setNewSectionType(e.target.value as any)}
              style={{
                fontSize: '10px',
                padding: '4px 8px',
                border: '1px solid #E0E0E0',
                borderRadius: '2px',
                height: '24px',
              }}
            >
              <option value="text">텍스트 섹션</option>
              <option value="list">리스트 섹션</option>
              <option value="structured">구조화된 섹션 (템플릿)</option>
              <option value="title">제목 섹션</option>
            </select>
            {newSectionType === 'structured' && (
              <select
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                style={{
                  fontSize: '10px',
                  padding: '4px 8px',
                  border: '1px solid #E0E0E0',
                  borderRadius: '2px',
                  height: '24px',
                  flex: 1,
                }}
              >
                <option value="">템플릿 선택</option>
                {TEMPLATE_CATEGORIES.map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            )}
            <button
              onClick={addSection}
              disabled={newSectionType === 'structured' && !selectedTemplate}
              style={{
                fontSize: '9px',
                padding: '4px 12px',
                backgroundColor: newSectionType === 'structured' && !selectedTemplate ? '#ccc' : '#4CAF50',
                color: '#fff',
                border: 'none',
                borderRadius: '2px',
                cursor: newSectionType === 'structured' && !selectedTemplate ? 'not-allowed' : 'pointer',
              }}
            >
              섹션 추가
            </button>
          </div>
        </div>
      )}

      {/* 섹션 목록 */}
      {sections.map((section) => (
        <div key={section.id} style={{ marginBottom: '12px' }}>
          <div style={{
            backgroundColor: '#F8F9FA',
            border: '1px solid #E0E0E0',
            borderRadius: '2px',
            padding: '8px',
          }}>
            {/* 섹션 헤더 */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: section.expanded ? '8px' : '0',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
                <span
                  onClick={() => toggleSection(section.id)}
                  style={{
                    fontSize: '10px',
                    color: '#666',
                    cursor: 'pointer',
                  }}
                >
                  {section.expanded ? '▼' : '▶'}
                </span>
                {section.type === 'title' ? (
                  <input
                    type="text"
                    value={section.title}
                    onChange={(e) => updateSection(section.id, { title: e.target.value })}
                    placeholder="섹션 제목"
                    readOnly={readOnly}
                    style={{
                      fontSize: '10px',
                      fontWeight: 'bold',
                      padding: '4px 8px',
                      border: '1px solid #E0E0E0',
                      borderRadius: '2px',
                      flex: 1,
                    }}
                  />
                ) : (
                  <input
                    type="text"
                    value={section.title}
                    onChange={(e) => updateSection(section.id, { title: e.target.value })}
                    placeholder="섹션 제목"
                    readOnly={readOnly}
                    style={{
                      fontSize: '10px',
                      fontWeight: 'bold',
                      padding: '4px 8px',
                      border: '1px solid #E0E0E0',
                      borderRadius: '2px',
                      flex: 1,
                    }}
                  />
                )}
              </div>
              {!readOnly && (
                <button
                  onClick={() => deleteSection(section.id)}
                  style={{
                    fontSize: '9px',
                    padding: '4px 8px',
                    backgroundColor: '#F44336',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '2px',
                    cursor: 'pointer',
                  }}
                >
                  ×
                </button>
              )}
            </div>

            {/* 섹션 콘텐츠 */}
            {section.expanded && (
              <div>
                {section.type === 'text' && (
                  <InputField
                    type="textarea"
                    value={section.content || ''}
                    onChange={(value) => updateSection(section.id, { content: value })}
                    rows={5}
                    readOnly={readOnly}
                  />
                )}

                {section.type === 'list' && (
                  <div>
                    {(section.items || []).map((item, idx) => (
                      <div key={idx} style={{ display: 'flex', gap: '4px', marginBottom: '4px' }}>
                        <span style={{ fontSize: '10px', marginTop: '4px' }}>•</span>
                        <InputField
                          type="textarea"
                          value={item}
                          onChange={(value) => {
                            const newItems = [...(section.items || [])];
                            newItems[idx] = value;
                            updateSection(section.id, { items: newItems });
                          }}
                          rows={2}
                          readOnly={readOnly}
                        />
                        {!readOnly && (
                          <button
                            onClick={() => {
                              const newItems = (section.items || []).filter((_, i) => i !== idx);
                              updateSection(section.id, { items: newItems });
                            }}
                            style={{
                              fontSize: '9px',
                              padding: '4px 8px',
                              backgroundColor: '#F44336',
                              color: '#fff',
                              border: 'none',
                              borderRadius: '2px',
                              cursor: 'pointer',
                            }}
                          >
                            삭제
                          </button>
                        )}
                      </div>
                    ))}
                    {!readOnly && (
                      <button
                        onClick={() => {
                          const newItems = [...(section.items || []), ''];
                          updateSection(section.id, { items: newItems });
                        }}
                        style={{
                          fontSize: '9px',
                          padding: '4px 12px',
                          backgroundColor: '#2196F3',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '2px',
                          cursor: 'pointer',
                          marginTop: '4px',
                        }}
                      >
                        + 항목 추가
                      </button>
                    )}
                  </div>
                )}

                {section.type === 'structured' && section.fields && (
                  <div>
                    {section.fields.map((field) => (
                      <FormField key={field.id} label={field.label} labelWidth={120}>
                        {field.type === 'longtext' ? (
                          <InputField
                            type="textarea"
                            value={typeof field.value === 'string' ? field.value : ''}
                            onChange={(value) => {
                              const newFields = section.fields!.map(f =>
                                f.id === field.id ? { ...f, value } : f
                              );
                              updateSection(section.id, { fields: newFields });
                            }}
                            rows={5}
                            readOnly={readOnly}
                          />
                        ) : field.type === 'select' ? (
                          <InputField
                            type="select"
                            value={typeof field.value === 'string' ? field.value : ''}
                            onChange={(value) => {
                              const newFields = section.fields!.map(f =>
                                f.id === field.id ? { ...f, value } : f
                              );
                              updateSection(section.id, { fields: newFields });
                            }}
                            options={field.options || []}
                            readOnly={readOnly}
                          />
                        ) : field.type === 'list' ? (
                          <div>
                            {(Array.isArray(field.value) ? field.value : []).map((item, idx) => (
                              <div key={idx} style={{ display: 'flex', gap: '4px', marginBottom: '4px' }}>
                                <InputField
                                  type="text"
                                  value={item}
                                  onChange={(value) => {
                                    const newItems = [...(Array.isArray(field.value) ? field.value : [])];
                                    newItems[idx] = value;
                                    const newFields = section.fields!.map(f =>
                                      f.id === field.id ? { ...f, value: newItems } : f
                                    );
                                    updateSection(section.id, { fields: newFields });
                                  }}
                                  readOnly={readOnly}
                                />
                                {!readOnly && (
                                  <button
                                    onClick={() => {
                                      const newItems = (Array.isArray(field.value) ? field.value : []).filter((_, i) => i !== idx);
                                      const newFields = section.fields!.map(f =>
                                        f.id === field.id ? { ...f, value: newItems } : f
                                      );
                                      updateSection(section.id, { fields: newFields });
                                    }}
                                    style={{
                                      fontSize: '9px',
                                      padding: '4px 8px',
                                      backgroundColor: '#F44336',
                                      color: '#fff',
                                      border: 'none',
                                      borderRadius: '2px',
                                      cursor: 'pointer',
                                    }}
                                  >
                                    삭제
                                  </button>
                                )}
                              </div>
                            ))}
                            {!readOnly && (
                              <button
                                onClick={() => {
                                  const newItems = [...(Array.isArray(field.value) ? field.value : []), ''];
                                  const newFields = section.fields!.map(f =>
                                    f.id === field.id ? { ...f, value: newItems } : f
                                  );
                                  updateSection(section.id, { fields: newFields });
                                }}
                                style={{
                                  fontSize: '9px',
                                  padding: '4px 12px',
                                  backgroundColor: '#2196F3',
                                  color: '#fff',
                                  border: 'none',
                                  borderRadius: '2px',
                                  cursor: 'pointer',
                                  marginTop: '4px',
                                }}
                              >
                                + 항목 추가
                              </button>
                            )}
                          </div>
                        ) : (
                          <InputField
                            type="text"
                            value={typeof field.value === 'string' ? field.value : ''}
                            onChange={(value) => {
                              const newFields = section.fields!.map(f =>
                                f.id === field.id ? { ...f, value } : f
                              );
                              updateSection(section.id, { fields: newFields });
                            }}
                            readOnly={readOnly}
                          />
                        )}
                      </FormField>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

