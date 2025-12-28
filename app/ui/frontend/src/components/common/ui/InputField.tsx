/**
 * 입력 필드 컴포넌트
 */
import React from 'react';

interface InputFieldProps {
  value: string | number;
  onChange: (value: string) => void;
  placeholder?: string;
  readOnly?: boolean;
  copyButton?: boolean;
  type?: 'text' | 'number' | 'select' | 'color' | 'textarea';
  options?: string[];
  min?: number;
  max?: number;
  rows?: number;
}

export const InputField: React.FC<InputFieldProps> = ({
  value,
  onChange,
  placeholder,
  readOnly = false,
  copyButton = false,
  type = 'text',
  options = [],
  min,
  max,
  rows = 3,
}) => {
  const handleCopy = () => {
    navigator.clipboard.writeText(String(value));
  };

  if (type === 'textarea') {
    return (
      <div style={{ display: 'flex', gap: '4px', alignItems: 'flex-start' }}>
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          readOnly={readOnly}
          rows={rows}
          style={{
            flex: 1,
            fontSize: '10px',
            padding: '4px 8px',
            border: '1px solid #E0E0E0',
            borderRadius: '2px',
            fontFamily: 'inherit',
            resize: 'vertical',
            minHeight: '100px',
          }}
        />
        {copyButton && (
          <button
            onClick={handleCopy}
            style={{
              fontSize: '9px',
              padding: '4px 8px',
              backgroundColor: '#2196F3',
              color: '#fff',
              border: 'none',
              borderRadius: '2px',
              cursor: 'pointer',
            }}
          >
            Copy
          </button>
        )}
      </div>
    );
  }

  if (type === 'select') {
    return (
      <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={readOnly}
          style={{
            flex: 1,
            fontSize: '10px',
            padding: '4px 8px',
            border: '1px solid #E0E0E0',
            borderRadius: '2px',
            height: '24px',
            fontFamily: 'inherit',
          }}
        >
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
        {copyButton && (
          <button
            onClick={handleCopy}
            style={{
              fontSize: '9px',
              padding: '4px 8px',
              backgroundColor: '#2196F3',
              color: '#fff',
              border: 'none',
              borderRadius: '2px',
              cursor: 'pointer',
            }}
          >
            Copy
          </button>
        )}
      </div>
    );
  }

  if (type === 'color') {
    return (
      <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={readOnly}
          style={{
            width: '40px',
            height: '24px',
            border: '1px solid #E0E0E0',
            borderRadius: '2px',
            cursor: readOnly ? 'not-allowed' : 'pointer',
          }}
        />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          readOnly={readOnly}
          style={{
            flex: 1,
            fontSize: '10px',
            padding: '4px 8px',
            border: '1px solid #E0E0E0',
            borderRadius: '2px',
            height: '24px',
            fontFamily: 'inherit',
          }}
        />
        {copyButton && (
          <button
            onClick={handleCopy}
            style={{
              fontSize: '9px',
              padding: '4px 8px',
              backgroundColor: '#2196F3',
              color: '#fff',
              border: 'none',
              borderRadius: '2px',
              cursor: 'pointer',
            }}
          >
            Copy
          </button>
        )}
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        readOnly={readOnly}
        min={min}
        max={max}
        style={{
          flex: 1,
          fontSize: '10px',
          padding: '4px 8px',
          border: '1px solid #E0E0E0',
          borderRadius: '2px',
          height: '24px',
          fontFamily: 'inherit',
        }}
      />
      {copyButton && (
        <button
          onClick={handleCopy}
          style={{
            fontSize: '9px',
            padding: '4px 8px',
            backgroundColor: '#2196F3',
            color: '#fff',
            border: 'none',
            borderRadius: '2px',
            cursor: 'pointer',
          }}
        >
          Copy
        </button>
      )}
    </div>
  );
};

