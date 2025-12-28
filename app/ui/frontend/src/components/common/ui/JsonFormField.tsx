/**
 * JSON 필드를 GUI로 입력할 수 있는 컴포넌트
 */
import React from 'react';

interface JsonFormFieldProps {
  label: string;
  value: any;
  onChange: (value: any) => void;
  fields: Array<{
    key: string;
    label: string;
    type: 'number' | 'text' | 'textarea' | 'boolean' | 'array' | 'object';
    placeholder?: string;
    default?: any;
  }>;
}

export const JsonFormField: React.FC<JsonFormFieldProps> = ({
  label,
  value,
  onChange,
  fields,
}) => {
  const handleFieldChange = (key: string, fieldValue: any) => {
    const newValue = { ...(value || {}) };
    newValue[key] = fieldValue;
    onChange(newValue);
  };

  const handleArrayAdd = (key: string) => {
    const newValue = { ...(value || {}) };
    if (!Array.isArray(newValue[key])) {
      newValue[key] = [];
    }
    newValue[key] = [...newValue[key], ''];
    onChange(newValue);
  };

  const handleArrayRemove = (key: string, index: number) => {
    const newValue = { ...(value || {}) };
    if (Array.isArray(newValue[key])) {
      newValue[key] = newValue[key].filter((_: any, i: number) => i !== index);
      onChange(newValue);
    }
  };

  const handleArrayItemChange = (key: string, index: number, itemValue: string) => {
    const newValue = { ...(value || {}) };
    if (Array.isArray(newValue[key])) {
      newValue[key] = newValue[key].map((item: any, i: number) =>
        i === index ? itemValue : item
      );
      onChange(newValue);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {fields.map((field) => {
        const fieldValue = value?.[field.key] ?? field.default;

        if (field.type === 'number') {
          return (
            <div key={field.key} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <label style={{ minWidth: '120px', fontSize: '12px' }}>{field.label}:</label>
              <input
                type="number"
                value={fieldValue || 0}
                onChange={(e) => handleFieldChange(field.key, Number(e.target.value))}
                placeholder={field.placeholder}
                style={{
                  flex: 1,
                  padding: '4px 8px',
                  border: '1px solid #ddd',
                  borderRadius: '2px',
                  fontSize: '12px',
                }}
              />
            </div>
          );
        }

        if (field.type === 'text') {
          return (
            <div key={field.key} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <label style={{ minWidth: '120px', fontSize: '12px' }}>{field.label}:</label>
              <input
                type="text"
                value={fieldValue || ''}
                onChange={(e) => handleFieldChange(field.key, e.target.value)}
                placeholder={field.placeholder}
                style={{
                  flex: 1,
                  padding: '4px 8px',
                  border: '1px solid #ddd',
                  borderRadius: '2px',
                  fontSize: '12px',
                }}
              />
            </div>
          );
        }

        if (field.type === 'textarea') {
          return (
            <div key={field.key} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '12px' }}>{field.label}:</label>
              <textarea
                value={fieldValue || ''}
                onChange={(e) => handleFieldChange(field.key, e.target.value)}
                placeholder={field.placeholder}
                rows={3}
                style={{
                  width: '100%',
                  padding: '4px 8px',
                  border: '1px solid #ddd',
                  borderRadius: '2px',
                  fontSize: '12px',
                  resize: 'vertical',
                }}
              />
            </div>
          );
        }

        if (field.type === 'boolean') {
          return (
            <div key={field.key} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <label style={{ minWidth: '120px', fontSize: '12px' }}>{field.label}:</label>
              <input
                type="checkbox"
                checked={fieldValue || false}
                onChange={(e) => handleFieldChange(field.key, e.target.checked)}
                style={{ cursor: 'pointer' }}
              />
            </div>
          );
        }

        if (field.type === 'array') {
          const arrayValue = Array.isArray(fieldValue) ? fieldValue : [];
          return (
            <div key={field.key} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <label style={{ minWidth: '120px', fontSize: '12px' }}>{field.label}:</label>
                <button
                  onClick={() => handleArrayAdd(field.key)}
                  style={{
                    fontSize: '10px',
                    padding: '2px 8px',
                    backgroundColor: '#4CAF50',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '2px',
                    cursor: 'pointer',
                  }}
                >
                  + 추가
                </button>
              </div>
              {arrayValue.map((item: any, index: number) => (
                <div
                  key={index}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    marginLeft: '120px',
                  }}
                >
                  <input
                    type="text"
                    value={item || ''}
                    onChange={(e) => handleArrayItemChange(field.key, index, e.target.value)}
                    placeholder={field.placeholder}
                    style={{
                      flex: 1,
                      padding: '4px 8px',
                      border: '1px solid #ddd',
                      borderRadius: '2px',
                      fontSize: '12px',
                    }}
                  />
                  <button
                    onClick={() => handleArrayRemove(field.key, index)}
                    style={{
                      fontSize: '10px',
                      padding: '2px 6px',
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
              {arrayValue.length === 0 && (
                <div
                  style={{
                    marginLeft: '120px',
                    fontSize: '11px',
                    color: '#999',
                    fontStyle: 'italic',
                  }}
                >
                  항목이 없습니다. + 추가 버튼을 클릭하여 추가하세요.
                </div>
              )}
            </div>
          );
        }

        return null;
      })}
    </div>
  );
};

