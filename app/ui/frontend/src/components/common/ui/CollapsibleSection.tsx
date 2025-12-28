/**
 * 접기/펼치기 가능한 섹션 컴포넌트
 */
import React, { useState } from 'react';

interface CollapsibleSectionProps {
  title: string;
  count?: number;
  defaultExpanded?: boolean;
  actionButton?: React.ReactNode;
  children: React.ReactNode;
}

export const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({
  title,
  count,
  defaultExpanded = true,
  actionButton,
  children,
}) => {
  const [expanded, setExpanded] = useState(defaultExpanded);

  return (
    <div style={{
      marginBottom: '12px',
      backgroundColor: '#F8F9FA',
      border: '1px solid #E0E0E0',
      borderRadius: '2px',
      overflow: 'hidden',
    }}>
      {/* 헤더 */}
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          padding: '8px 12px',
          backgroundColor: '#F8F9FA',
          borderBottom: expanded ? '1px solid #E0E0E0' : 'none',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
          userSelect: 'none',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '10px', color: '#666' }}>
            {expanded ? '▼' : '▶'}
          </span>
          <span style={{ fontSize: '11px', fontWeight: 'bold', color: '#333' }}>
            {title}
            {count !== undefined && ` (${count})`}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {actionButton}
          <button
            onClick={(e) => {
              e.stopPropagation();
              setExpanded(!expanded);
            }}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '10px',
              color: '#666',
              padding: '2px 4px',
            }}
          >
            {expanded ? '접기' : '펼치기'}
          </button>
        </div>
      </div>

      {/* 콘텐츠 */}
      {expanded && (
        <div style={{ padding: '8px' }}>
          {children}
        </div>
      )}
    </div>
  );
};

