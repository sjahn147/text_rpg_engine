/**
 * 설정 화면 - 게임 설정, 사운드, 디스플레이
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface SettingsScreenProps {
  onClose: () => void;
}

interface GameSettings {
  textSpeed: number;
  autoPlaySpeed: number;
  soundVolume: number;
  musicVolume: number;
  effectVolume: number;
  fontSize: 'small' | 'medium' | 'large';
  theme: 'light' | 'dark' | 'sepia';
  animations: boolean;
  autoSave: boolean;
  confirmActions: boolean;
  language: 'ko' | 'en' | 'ja';
}

type TabType = 'gameplay' | 'audio' | 'display' | 'system';

export const SettingsScreen: React.FC<SettingsScreenProps> = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState<TabType>('gameplay');
  const [settings, setSettings] = useState<GameSettings>({
    textSpeed: 50,
    autoPlaySpeed: 3000,
    soundVolume: 80,
    musicVolume: 60,
    effectVolume: 70,
    fontSize: 'medium',
    theme: 'light',
    animations: true,
    autoSave: true,
    confirmActions: true,
    language: 'ko',
  });
  const [hasChanges, setHasChanges] = useState(false);

  const updateSetting = <K extends keyof GameSettings>(key: K, value: GameSettings[K]) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSave = () => {
    // TODO: 설정 저장 API 호출 또는 localStorage 저장
    localStorage.setItem('gameSettings', JSON.stringify(settings));
    setHasChanges(false);
    alert('설정이 저장되었습니다.');
  };

  const handleReset = () => {
    if (confirm('설정을 기본값으로 초기화하시겠습니까?')) {
      setSettings({
        textSpeed: 50,
        autoPlaySpeed: 3000,
        soundVolume: 80,
        musicVolume: 60,
        effectVolume: 70,
        fontSize: 'medium',
        theme: 'light',
        animations: true,
        autoSave: true,
        confirmActions: true,
        language: 'ko',
      });
      setHasChanges(true);
    }
  };

  const renderSlider = (
    label: string,
    value: number,
    onChange: (value: number) => void,
    min: number = 0,
    max: number = 100,
    step: number = 1,
    unit: string = ''
  ) => (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-black/70">{label}</span>
        <span className="text-sm text-black/50">{value}{unit}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-2 bg-black/10 rounded-lg appearance-none cursor-pointer accent-blue-600"
      />
    </div>
  );

  const renderToggle = (
    label: string,
    value: boolean,
    onChange: (value: boolean) => void,
    description?: string
  ) => (
    <div className="flex items-center justify-between py-3 border-b border-black/5">
      <div>
        <span className="text-sm text-black/80">{label}</span>
        {description && (
          <p className="text-xs text-black/50 mt-1">{description}</p>
        )}
      </div>
      <button
        onClick={() => onChange(!value)}
        className={`w-12 h-6 rounded-full transition-colors ${
          value ? 'bg-blue-600' : 'bg-black/20'
        }`}
      >
        <div
          className={`w-5 h-5 bg-white rounded-full shadow transition-transform ${
            value ? 'translate-x-6' : 'translate-x-0.5'
          }`}
        />
      </button>
    </div>
  );

  const renderSelect = (
    label: string,
    value: string,
    options: { value: string; label: string }[],
    onChange: (value: string) => void
  ) => (
    <div className="mb-4">
      <label className="text-sm text-black/70 block mb-2">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 border border-black/10 rounded bg-white text-black/80 text-sm focus:outline-none focus:border-black/30"
      >
        {options.map(opt => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="bg-white p-8 rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 50, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* 헤더 */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-light text-black/90">설정</h2>
            <button
              onClick={onClose}
              className="text-black/60 hover:text-black/90 transition-colors text-2xl"
            >
              ✕
            </button>
          </div>

          {/* 탭 */}
          <div className="flex gap-2 mb-6">
            {(['gameplay', 'audio', 'display', 'system'] as TabType[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-sm font-light transition-colors rounded ${
                  activeTab === tab
                    ? 'bg-black/10 text-black/90'
                    : 'text-black/60 hover:text-black/80 hover:bg-black/5'
                }`}
              >
                {tab === 'gameplay' ? '게임플레이' :
                 tab === 'audio' ? '오디오' :
                 tab === 'display' ? '디스플레이' : '시스템'}
              </button>
            ))}
          </div>

          {/* 컨텐츠 */}
          <div className="flex-1 overflow-y-auto">
            <AnimatePresence mode="wait">
              {activeTab === 'gameplay' && (
                <motion.div
                  key="gameplay"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                >
                  {renderSlider(
                    '텍스트 속도',
                    settings.textSpeed,
                    (v) => updateSetting('textSpeed', v),
                    0, 100, 10, '%'
                  )}
                  {renderSlider(
                    '자동 진행 속도 (밀리초)',
                    settings.autoPlaySpeed,
                    (v) => updateSetting('autoPlaySpeed', v),
                    1000, 10000, 500, 'ms'
                  )}
                  {renderToggle(
                    '행동 확인',
                    settings.confirmActions,
                    (v) => updateSetting('confirmActions', v),
                    '중요한 행동 전에 확인 대화상자를 표시합니다.'
                  )}
                </motion.div>
              )}

              {activeTab === 'audio' && (
                <motion.div
                  key="audio"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                >
                  {renderSlider(
                    '전체 볼륨',
                    settings.soundVolume,
                    (v) => updateSetting('soundVolume', v),
                    0, 100, 5, '%'
                  )}
                  {renderSlider(
                    '음악 볼륨',
                    settings.musicVolume,
                    (v) => updateSetting('musicVolume', v),
                    0, 100, 5, '%'
                  )}
                  {renderSlider(
                    '효과음 볼륨',
                    settings.effectVolume,
                    (v) => updateSetting('effectVolume', v),
                    0, 100, 5, '%'
                  )}
                </motion.div>
              )}

              {activeTab === 'display' && (
                <motion.div
                  key="display"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                >
                  {renderSelect(
                    '글꼴 크기',
                    settings.fontSize,
                    [
                      { value: 'small', label: '작게' },
                      { value: 'medium', label: '보통' },
                      { value: 'large', label: '크게' },
                    ],
                    (v) => updateSetting('fontSize', v as GameSettings['fontSize'])
                  )}
                  {renderSelect(
                    '테마',
                    settings.theme,
                    [
                      { value: 'light', label: '라이트' },
                      { value: 'dark', label: '다크' },
                      { value: 'sepia', label: '세피아' },
                    ],
                    (v) => updateSetting('theme', v as GameSettings['theme'])
                  )}
                  {renderToggle(
                    '애니메이션',
                    settings.animations,
                    (v) => updateSetting('animations', v),
                    '화면 전환 및 UI 애니메이션을 활성화합니다.'
                  )}
                </motion.div>
              )}

              {activeTab === 'system' && (
                <motion.div
                  key="system"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                >
                  {renderSelect(
                    '언어',
                    settings.language,
                    [
                      { value: 'ko', label: '한국어' },
                      { value: 'en', label: 'English' },
                      { value: 'ja', label: '日本語' },
                    ],
                    (v) => updateSetting('language', v as GameSettings['language'])
                  )}
                  {renderToggle(
                    '자동 저장',
                    settings.autoSave,
                    (v) => updateSetting('autoSave', v),
                    '게임 진행 상황을 자동으로 저장합니다.'
                  )}
                  <div className="mt-6">
                    <button
                      onClick={handleReset}
                      className="text-sm text-red-600 hover:text-red-700 transition-colors"
                    >
                      설정 초기화
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* 하단 버튼 */}
          <div className="mt-6 flex justify-end gap-3">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded transition-colors"
            >
              닫기
            </button>
            <button
              onClick={handleSave}
              disabled={!hasChanges}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors disabled:opacity-50"
            >
              저장
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

