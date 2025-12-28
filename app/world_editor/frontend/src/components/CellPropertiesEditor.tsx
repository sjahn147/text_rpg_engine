/**
 * Cell Properties JSON 편집기 컴포넌트
 * 게임 디자이너가 Cell Properties를 쉽게 편집할 수 있는 UI 제공
 */
import React, { useState, useEffect } from 'react';
import { cellsApi } from '../services/api';

interface CellPropertiesEditorProps {
  cellId: string;
  onClose?: () => void;
  onSave?: () => void;
}

export const CellPropertiesEditor: React.FC<CellPropertiesEditorProps> = ({
  cellId,
  onClose,
  onSave,
}) => {
  const [properties, setProperties] = useState<any>({});
  const [jsonText, setJsonText] = useState<string>('{}');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'form' | 'json'>('form');

  // Properties 로드
  useEffect(() => {
    const loadProperties = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await cellsApi.getProperties(cellId);
        const props = response.data.properties || {};
        setProperties(props);
        setJsonText(JSON.stringify(props, null, 2));
      } catch (err: any) {
        console.error('Properties 로드 실패:', err);
        setError(`로드 실패: ${err.response?.data?.detail || err.message}`);
        setProperties({});
        setJsonText('{}');
      } finally {
        setLoading(false);
      }
    };

    if (cellId) {
      loadProperties();
    }
  }, [cellId]);

  // JSON 텍스트 파싱 및 검증
  const validateJson = (text: string): { valid: boolean; data?: any; error?: string } => {
    try {
      const parsed = JSON.parse(text);
      return { valid: true, data: parsed };
    } catch (e: any) {
      return { valid: false, error: e.message };
    }
  };

  // Properties 저장
  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);

      let propsToSave: any;
      if (viewMode === 'json') {
        const validation = validateJson(jsonText);
        if (!validation.valid) {
          setError(`JSON 형식 오류: ${validation.error}`);
          return;
        }
        propsToSave = validation.data;
      } else {
        propsToSave = properties;
      }

      await cellsApi.updateProperties(cellId, propsToSave);
      
      // 저장 후 다시 로드
      const response = await cellsApi.getProperties(cellId);
      const updatedProps = response.data.properties || {};
      setProperties(updatedProps);
      setJsonText(JSON.stringify(updatedProps, null, 2));

      if (onSave) {
        onSave();
      }

      alert('Properties가 저장되었습니다.');
    } catch (err: any) {
      console.error('Properties 저장 실패:', err);
      setError(`저장 실패: ${err.response?.data?.detail || err.message}`);
    } finally {
      setSaving(false);
    }
  };

  // Form 모드에서 속성 업데이트
  const updateProperty = (path: string[], value: any) => {
    const newProps = { ...properties };
    let current: any = newProps;

    for (let i = 0; i < path.length - 1; i++) {
      if (!current[path[i]]) {
        current[path[i]] = {};
      }
      current = current[path[i]];
    }

    current[path[path.length - 1]] = value;
    setProperties(newProps);
    setJsonText(JSON.stringify(newProps, null, 2));
  };

  // 중첩된 객체 렌더링
  const renderProperty = (key: string, value: any, path: string[] = []): React.ReactNode => {
    const currentPath = [...path, key];

    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      return (
        <div key={key} style={{ marginLeft: `${path.length * 20}px`, marginBottom: '12px' }}>
          <div style={{ fontWeight: 'bold', marginBottom: '8px', color: '#333' }}>
            {key}:
          </div>
          {Object.entries(value).map(([k, v]) => renderProperty(k, v, currentPath))}
        </div>
      );
    }

    if (Array.isArray(value)) {
      return (
        <div key={key} style={{ marginLeft: `${path.length * 20}px`, marginBottom: '12px' }}>
          <label style={{ display: 'block', marginBottom: '4px', fontSize: '12px', fontWeight: 'bold' }}>
            {key}:
          </label>
          <textarea
            value={JSON.stringify(value, null, 2)}
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value);
                updateProperty(currentPath, parsed);
              } catch {
                // 파싱 실패 시 무시
              }
            }}
            style={{
              width: '100%',
              minHeight: '60px',
              padding: '6px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '11px',
              fontFamily: 'monospace',
            }}
          />
        </div>
      );
    }

    return (
      <div key={key} style={{ marginLeft: `${path.length * 20}px`, marginBottom: '12px' }}>
        <label style={{ display: 'block', marginBottom: '4px', fontSize: '12px', fontWeight: 'bold' }}>
          {key}:
        </label>
        {typeof value === 'boolean' ? (
          <select
            value={value ? 'true' : 'false'}
            onChange={(e) => updateProperty(currentPath, e.target.value === 'true')}
            style={{
              width: '100%',
              padding: '6px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '12px',
            }}
          >
            <option value="true">true</option>
            <option value="false">false</option>
          </select>
        ) : typeof value === 'number' ? (
          <input
            type="number"
            value={value}
            onChange={(e) => updateProperty(currentPath, parseFloat(e.target.value) || 0)}
            style={{
              width: '100%',
              padding: '6px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '12px',
            }}
          />
        ) : (
          <input
            type="text"
            value={String(value)}
            onChange={(e) => updateProperty(currentPath, e.target.value)}
            style={{
              width: '100%',
              padding: '6px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '12px',
            }}
          />
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>로딩 중...</p>
      </div>
    );
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      backgroundColor: '#fff',
    }}>
      {/* Header */}
      <div style={{
        padding: '12px',
        borderBottom: '1px solid #ddd',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 'bold' }}>
          Cell Properties 편집기
        </h3>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setViewMode(viewMode === 'form' ? 'json' : 'form')}
            style={{
              padding: '6px 12px',
              backgroundColor: '#f0f0f0',
              border: '1px solid #ddd',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px',
            }}
          >
            {viewMode === 'form' ? 'JSON 모드' : 'Form 모드'}
          </button>
          {onClose && (
            <button
              onClick={onClose}
              style={{
                padding: '6px 12px',
                backgroundColor: '#f0f0f0',
                border: '1px solid #ddd',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px',
              }}
            >
              닫기
            </button>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div style={{
          padding: '8px 12px',
          backgroundColor: '#fee',
          color: '#c00',
          fontSize: '12px',
          borderBottom: '1px solid #fcc',
        }}>
          {error}
        </div>
      )}

      {/* Content */}
      <div style={{ flex: 1, overflow: 'auto', padding: '12px' }}>
        {viewMode === 'form' ? (
          <div>
            {Object.keys(properties).length === 0 ? (
              <div style={{ textAlign: 'center', color: '#999', padding: '20px' }}>
                Properties가 비어있습니다. JSON 모드에서 추가하세요.
              </div>
            ) : (
              Object.entries(properties).map(([key, value]) => renderProperty(key, value))
            )}
          </div>
        ) : (
          <textarea
            value={jsonText}
            onChange={(e) => {
              setJsonText(e.target.value);
              const validation = validateJson(e.target.value);
              if (validation.valid && validation.data) {
                setProperties(validation.data);
                setError(null);
              } else if (validation.error) {
                setError(`JSON 형식 오류: ${validation.error}`);
              }
            }}
            style={{
              width: '100%',
              height: '100%',
              minHeight: '400px',
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '12px',
              fontFamily: 'monospace',
              resize: 'none',
            }}
          />
        )}
      </div>

      {/* Footer */}
      <div style={{
        padding: '12px',
        borderTop: '1px solid #ddd',
        display: 'flex',
        justifyContent: 'flex-end',
        gap: '8px',
      }}>
        <button
          onClick={handleSave}
          disabled={saving}
          style={{
            padding: '8px 16px',
            backgroundColor: saving ? '#ccc' : '#007bff',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: saving ? 'not-allowed' : 'pointer',
            fontSize: '12px',
            fontWeight: 'bold',
          }}
        >
          {saving ? '저장 중...' : '저장'}
        </button>
      </div>
    </div>
  );
};

