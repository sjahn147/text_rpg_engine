/**
 * 에디터 모달 상태 관리 훅
 */
import { useState, useCallback } from 'react';

export interface EditorModalsState {
  settingsModalOpen: boolean;
  knowledgeManagerOpen: boolean;
  searchResultsModalOpen: boolean;
  keyboardShortcutsModalOpen: boolean;
  aboutModalOpen: boolean;
}

export interface EditorModalsActions {
  openSettings: () => void;
  closeSettings: () => void;
  openKnowledgeManager: () => void;
  closeKnowledgeManager: () => void;
  openSearchResults: () => void;
  closeSearchResults: () => void;
  openKeyboardShortcuts: () => void;
  closeKeyboardShortcuts: () => void;
  openAbout: () => void;
  closeAbout: () => void;
  closeAll: () => void;
}

export const useEditorModals = () => {
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);
  const [knowledgeManagerOpen, setKnowledgeManagerOpen] = useState(false);
  const [searchResultsModalOpen, setSearchResultsModalOpen] = useState(false);
  const [keyboardShortcutsModalOpen, setKeyboardShortcutsModalOpen] = useState(false);
  const [aboutModalOpen, setAboutModalOpen] = useState(false);

  const openSettings = useCallback(() => setSettingsModalOpen(true), []);
  const closeSettings = useCallback(() => setSettingsModalOpen(false), []);
  const openKnowledgeManager = useCallback(() => setKnowledgeManagerOpen(true), []);
  const closeKnowledgeManager = useCallback(() => setKnowledgeManagerOpen(false), []);
  const openSearchResults = useCallback(() => setSearchResultsModalOpen(true), []);
  const closeSearchResults = useCallback(() => setSearchResultsModalOpen(false), []);
  const openKeyboardShortcuts = useCallback(() => setKeyboardShortcutsModalOpen(true), []);
  const closeKeyboardShortcuts = useCallback(() => setKeyboardShortcutsModalOpen(false), []);
  const openAbout = useCallback(() => setAboutModalOpen(true), []);
  const closeAbout = useCallback(() => setAboutModalOpen(false), []);

  const closeAll = useCallback(() => {
    setSettingsModalOpen(false);
    setKnowledgeManagerOpen(false);
    setSearchResultsModalOpen(false);
    setKeyboardShortcutsModalOpen(false);
    setAboutModalOpen(false);
  }, []);

  return {
    // State
    settingsModalOpen,
    knowledgeManagerOpen,
    searchResultsModalOpen,
    keyboardShortcutsModalOpen,
    aboutModalOpen,
    // Actions
    openSettings,
    closeSettings,
    openKnowledgeManager,
    closeKnowledgeManager,
    openSearchResults,
    closeSearchResults,
    openKeyboardShortcuts,
    closeKeyboardShortcuts,
    openAbout,
    closeAbout,
    closeAll,
  };
};

