/**
 * 폼 필드 컴포넌트 (라벨 + 입력)
 */
import React from 'react';

interface FormFieldProps {
  label: string;
  labelWidth?: number;
  required?: boolean;
  error?: string;
  children: React.ReactNode;
}

export const FormField: React.FC<FormFieldProps> = ({
  label,
  labelWidth = 80,
  required = false,
  error,
  children,
}) => {
  return (
    <div style={{ marginBottom: '6px' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: `${labelWidth}px 1fr`,
        gap: '8px',
        alignItems: 'center',
      }}>
        <label style={{
          fontSize: '9px',
          fontWeight: 'medium',
          color: '#999',
          textAlign: 'right',
        }}>
          {label}
          {required && <span style={{ color: '#F44336' }}> *</span>}
        </label>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {children}
          {error && (
            <div style={{
              fontSize: '9px',
              color: '#F44336',
            }}>
              ⚠ {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

