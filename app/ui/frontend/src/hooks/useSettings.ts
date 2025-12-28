/**
 * 설정 시스템 Hook
 */
import { useState, useEffect, useCallback } from 'react';

export interface EditorSettings {
  // General
  language: string;
  theme: 'light' | 'dark' | 'high-contrast';
  autoSaveInterval: number; // seconds
  recentProjectsCount: number;

  // Editing
  defaultEntityType: string;
  autoCompleteEnabled: boolean;
  gridSnapDefault: boolean;
  undoRedoStackSize: number;

  // View
  defaultZoomLevel: number;
  gridShowDefault: boolean;
  defaultLayout: string;
  fontSize: number;

  // Performance
  virtualScrollThreshold: number;
  cacheSize: number;
  autoOptimizeEnabled: boolean;

  // Advanced
  debugMode: boolean;
  logLevel: 'error' | 'warning' | 'info' | 'debug';
  apiEndpoint: string;
}

const DEFAULT_SETTINGS: EditorSettings = {
  // General
  language: 'ko',
  theme: 'light',
  autoSaveInterval: 30,
  recentProjectsCount: 10,

  // Editing
  defaultEntityType: 'region',
  autoCompleteEnabled: true,
  gridSnapDefault: false,
  undoRedoStackSize: 50,

  // View
  defaultZoomLevel: 1.0,
  gridShowDefault: true,
  defaultLayout: 'default',
  fontSize: 13,

  // Performance
  virtualScrollThreshold: 100,
  cacheSize: 100,
  autoOptimizeEnabled: true,

  // Advanced
  debugMode: false,
  logLevel: 'info',
  apiEndpoint: 'http://localhost:8000',
};

const SETTINGS_STORAGE_KEY = 'world_editor_settings';

export const useSettings = () => {
  const [settings, setSettings] = useState<EditorSettings>(() => {
    // 로컬 스토리지에서 설정 로드
    try {
      const stored = localStorage.getItem(SETTINGS_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        return { ...DEFAULT_SETTINGS, ...parsed };
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
    return DEFAULT_SETTINGS;
  });

  // 설정 저장
  const saveSettings = useCallback((newSettings: Partial<EditorSettings>) => {
    const updated = { ...settings, ...newSettings };
    setSettings(updated);
    try {
      localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(updated));
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  }, [settings]);

  // 설정 초기화
  const resetSettings = useCallback(() => {
    setSettings(DEFAULT_SETTINGS);
    try {
      localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(DEFAULT_SETTINGS));
    } catch (error) {
      console.error('Failed to reset settings:', error);
    }
  }, []);

  // 특정 설정 업데이트
  const updateSetting = useCallback(<K extends keyof EditorSettings>(
    key: K,
    value: EditorSettings[K]
  ) => {
    saveSettings({ [key]: value });
  }, [saveSettings]);

  // 설정 가져오기
  const getSetting = useCallback(<K extends keyof EditorSettings>(
    key: K
  ): EditorSettings[K] => {
    return settings[key];
  }, [settings]);

  return {
    settings,
    saveSettings,
    resetSettings,
    updateSetting,
    getSetting,
  };
};

