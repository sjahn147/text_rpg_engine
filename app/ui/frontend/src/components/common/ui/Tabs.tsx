/**
 * 탭 컴포넌트
 */
import React from 'react';

interface TabsProps {
  tabs: Array<{ id: string; label: string }>;
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

export const Tabs: React.FC<TabsProps> = ({ tabs, activeTab, onTabChange }) => {
  return (
    <div style={{
      display: 'flex',
      borderBottom: '1px solid #E0E0E0',
      backgroundColor: '#FFFFFF',
    }}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          style={{
            padding: '8px 16px',
            fontSize: '10px',
            fontWeight: activeTab === tab.id ? 'bold' : 'normal',
            color: activeTab === tab.id ? '#2196F3' : '#666',
            backgroundColor: 'transparent',
            border: 'none',
            borderBottom: activeTab === tab.id ? '2px solid #2196F3' : '2px solid transparent',
            cursor: 'pointer',
            transition: 'all 0.2s',
          }}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
};

