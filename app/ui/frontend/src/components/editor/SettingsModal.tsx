/**
 * 설정 모달 컴포넌트
 */
import React, { useState } from 'react';
import { Modal } from '../common/ui/Modal';
import { CollapsibleSection } from '../common/ui/CollapsibleSection';
import { FormField } from '../common/ui/FormField';
import { InputField } from '../common/ui/InputField';
import { EditorSettings, useSettings } from '../../hooks/useSettings';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const { settings, saveSettings, resetSettings, updateSetting } = useSettings();
  const [localSettings, setLocalSettings] = useState<EditorSettings>(settings);
  const [activeTab, setActiveTab] = useState<'general' | 'editing' | 'view' | 'performance' | 'advanced'>('general');

  React.useEffect(() => {
    if (isOpen) {
      setLocalSettings(settings);
    }
  }, [isOpen, settings]);

  const handleSave = () => {
    saveSettings(localSettings);
    onClose();
  };

  const handleReset = () => {
    if (confirm('모든 설정을 기본값으로 초기화하시겠습니까?')) {
      resetSettings();
      setLocalSettings(settings);
    }
  };

  const tabs = [
    { id: 'general', label: '일반' },
    { id: 'editing', label: '편집' },
    { id: 'view', label: '뷰' },
    { id: 'performance', label: '성능' },
    { id: 'advanced', label: '고급' },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="설정" width="700px" height="80vh">
      <div style={{ display: 'flex', height: '100%' }}>
        {/* 탭 네비게이션 */}
        <div style={{ width: '150px', borderRight: '1px solid #ddd', padding: '8px 0' }}>
          {tabs.map((tab) => (
            <div
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              style={{
                padding: '8px 16px',
                cursor: 'pointer',
                backgroundColor: activeTab === tab.id ? '#e3f2fd' : 'transparent',
                fontSize: '13px',
              }}
            >
              {tab.label}
            </div>
          ))}
        </div>

        {/* 설정 내용 */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
          {activeTab === 'general' && (
            <>
              <CollapsibleSection title="일반 설정" defaultExpanded={true}>
                <FormField label="언어" labelWidth={150}>
                  <select
                    value={localSettings.language}
                    onChange={(e) => setLocalSettings({ ...localSettings, language: e.target.value })}
                    style={{ width: '100%', padding: '6px 8px', border: '1px solid #ddd', borderRadius: '4px' }}
                  >
                    <option value="ko">한국어</option>
                    <option value="en">English</option>
                  </select>
                </FormField>
                <FormField label="테마" labelWidth={150}>
                  <select
                    value={localSettings.theme}
                    onChange={(e) => setLocalSettings({ ...localSettings, theme: e.target.value as any })}
                    style={{ width: '100%', padding: '6px 8px', border: '1px solid #ddd', borderRadius: '4px' }}
                  >
                    <option value="light">밝은 테마</option>
                    <option value="dark">어두운 테마</option>
                    <option value="high-contrast">고대비</option>
                  </select>
                </FormField>
                <FormField label="자동 저장 간격 (초)" labelWidth={150}>
                  <InputField
                    type="number"
                    value={localSettings.autoSaveInterval}
                    onChange={(value) => setLocalSettings({ ...localSettings, autoSaveInterval: parseInt(value) || 30 })}
                    min={10}
                  />
                </FormField>
                <FormField label="최근 프로젝트 개수" labelWidth={150}>
                  <InputField
                    type="number"
                    value={localSettings.recentProjectsCount}
                    onChange={(value) => setLocalSettings({ ...localSettings, recentProjectsCount: parseInt(value) || 10 })}
                    min={1}
                    max={50}
                  />
                </FormField>
              </CollapsibleSection>
            </>
          )}

          {activeTab === 'editing' && (
            <>
              <CollapsibleSection title="편집 설정" defaultExpanded={true}>
                <FormField label="기본 엔티티 타입" labelWidth={150}>
                  <select
                    value={localSettings.defaultEntityType}
                    onChange={(e) => setLocalSettings({ ...localSettings, defaultEntityType: e.target.value })}
                    style={{ width: '100%', padding: '6px 8px', border: '1px solid #ddd', borderRadius: '4px' }}
                  >
                    <option value="region">Region</option>
                    <option value="location">Location</option>
                    <option value="cell">Cell</option>
                    <option value="entity">Entity</option>
                  </select>
                </FormField>
                <FormField label="자동 완성" labelWidth={150}>
                  <input
                    type="checkbox"
                    checked={localSettings.autoCompleteEnabled}
                    onChange={(e) => setLocalSettings({ ...localSettings, autoCompleteEnabled: e.target.checked })}
                  />
                </FormField>
                <FormField label="그리드 스냅 기본값" labelWidth={150}>
                  <input
                    type="checkbox"
                    checked={localSettings.gridSnapDefault}
                    onChange={(e) => setLocalSettings({ ...localSettings, gridSnapDefault: e.target.checked })}
                  />
                </FormField>
                <FormField label="Undo/Redo 스택 크기" labelWidth={150}>
                  <InputField
                    type="number"
                    value={localSettings.undoRedoStackSize}
                    onChange={(value) => setLocalSettings({ ...localSettings, undoRedoStackSize: parseInt(value) || 50 })}
                    min={10}
                    max={200}
                  />
                </FormField>
              </CollapsibleSection>
            </>
          )}

          {activeTab === 'view' && (
            <>
              <CollapsibleSection title="뷰 설정" defaultExpanded={true}>
                <FormField label="기본 줌 레벨" labelWidth={150}>
                  <InputField
                    type="number"
                    value={localSettings.defaultZoomLevel}
                    onChange={(value) => setLocalSettings({ ...localSettings, defaultZoomLevel: parseFloat(value) || 1.0 })}
                    min={0.1}
                    max={5.0}
                    step={0.1}
                  />
                </FormField>
                <FormField label="그리드 표시 기본값" labelWidth={150}>
                  <input
                    type="checkbox"
                    checked={localSettings.gridShowDefault}
                    onChange={(e) => setLocalSettings({ ...localSettings, gridShowDefault: e.target.checked })}
                  />
                </FormField>
                <FormField label="기본 레이아웃" labelWidth={150}>
                  <select
                    value={localSettings.defaultLayout}
                    onChange={(e) => setLocalSettings({ ...localSettings, defaultLayout: e.target.value })}
                    style={{ width: '100%', padding: '6px 8px', border: '1px solid #ddd', borderRadius: '4px' }}
                  >
                    <option value="default">기본</option>
                    <option value="compact">컴팩트</option>
                    <option value="wide">와이드</option>
                  </select>
                </FormField>
                <FormField label="폰트 크기" labelWidth={150}>
                  <InputField
                    type="number"
                    value={localSettings.fontSize}
                    onChange={(value) => setLocalSettings({ ...localSettings, fontSize: parseInt(value) || 13 })}
                    min={10}
                    max={20}
                  />
                </FormField>
              </CollapsibleSection>
            </>
          )}

          {activeTab === 'performance' && (
            <>
              <CollapsibleSection title="성능 설정" defaultExpanded={true}>
                <FormField label="가상 스크롤 임계값" labelWidth={150}>
                  <InputField
                    type="number"
                    value={localSettings.virtualScrollThreshold}
                    onChange={(value) => setLocalSettings({ ...localSettings, virtualScrollThreshold: parseInt(value) || 100 })}
                    min={50}
                    max={1000}
                  />
                </FormField>
                <FormField label="캐시 크기" labelWidth={150}>
                  <InputField
                    type="number"
                    value={localSettings.cacheSize}
                    onChange={(value) => setLocalSettings({ ...localSettings, cacheSize: parseInt(value) || 100 })}
                    min={10}
                    max={1000}
                  />
                </FormField>
                <FormField label="자동 최적화" labelWidth={150}>
                  <input
                    type="checkbox"
                    checked={localSettings.autoOptimizeEnabled}
                    onChange={(e) => setLocalSettings({ ...localSettings, autoOptimizeEnabled: e.target.checked })}
                  />
                </FormField>
              </CollapsibleSection>
            </>
          )}

          {activeTab === 'advanced' && (
            <>
              <CollapsibleSection title="고급 설정" defaultExpanded={true}>
                <FormField label="디버그 모드" labelWidth={150}>
                  <input
                    type="checkbox"
                    checked={localSettings.debugMode}
                    onChange={(e) => setLocalSettings({ ...localSettings, debugMode: e.target.checked })}
                  />
                </FormField>
                <FormField label="로그 레벨" labelWidth={150}>
                  <select
                    value={localSettings.logLevel}
                    onChange={(e) => setLocalSettings({ ...localSettings, logLevel: e.target.value as any })}
                    style={{ width: '100%', padding: '6px 8px', border: '1px solid #ddd', borderRadius: '4px' }}
                  >
                    <option value="error">Error</option>
                    <option value="warning">Warning</option>
                    <option value="info">Info</option>
                    <option value="debug">Debug</option>
                  </select>
                </FormField>
                <FormField label="API 엔드포인트" labelWidth={150}>
                  <InputField
                    type="text"
                    value={localSettings.apiEndpoint}
                    onChange={(value) => setLocalSettings({ ...localSettings, apiEndpoint: value })}
                  />
                </FormField>
              </CollapsibleSection>
            </>
          )}

          <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', gap: '8px' }}>
            <button
              onClick={handleReset}
              style={{
                padding: '8px 16px',
                backgroundColor: '#999',
                color: '#fff',
                border: 'none',
                borderRadius: '2px',
                cursor: 'pointer',
              }}
            >
              기본값으로 초기화
            </button>
            <div style={{ display: 'flex', gap: '8px' }}>
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
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#4CAF50',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '2px',
                  cursor: 'pointer',
                }}
              >
                저장
              </button>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  );
};

