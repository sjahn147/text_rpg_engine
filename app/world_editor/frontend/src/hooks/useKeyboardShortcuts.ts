/**
 * 단축키 시스템 Hook
 */
import { useEffect } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';

interface KeyboardShortcuts {
  // File
  onNewProject?: () => void;
  onOpenProject?: () => void;
  onSaveProject?: () => void;
  onSaveProjectAs?: () => void;

  // Edit
  onUndo?: () => void;
  onRedo?: () => void;
  onCut?: () => void;
  onCopy?: () => void;
  onPaste?: () => void;
  onDuplicate?: () => void;
  onDelete?: () => void;
  onSelectAll?: () => void;
  onDeselectAll?: () => void;
  onFind?: () => void;
  onFindInFiles?: () => void;
  onReplace?: () => void;
  onPreferences?: () => void;

  // View
  onToggleExplorer?: () => void;
  onToggleProperties?: () => void;
  onToggleConsole?: () => void;
  onViewMode?: (mode: 'map' | 'list' | 'tree' | 'split') => void;
  onZoom?: (action: 'in' | 'out' | 'fit' | 'selection') => void;
  onGridToggle?: () => void;
  onFullscreen?: () => void;

  // Entity
  onNewEntity?: (type: string) => void;
  onEntityProperties?: () => void;

  // Help
  onDocumentation?: () => void;
}

export const useKeyboardShortcuts = (shortcuts: KeyboardShortcuts) => {
  // File
  useHotkeys('ctrl+n', (e) => {
    e.preventDefault();
    shortcuts.onNewProject?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+o', (e) => {
    e.preventDefault();
    shortcuts.onOpenProject?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+s', (e) => {
    e.preventDefault();
    shortcuts.onSaveProject?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+shift+s', (e) => {
    e.preventDefault();
    shortcuts.onSaveProjectAs?.();
  }, { enableOnFormTags: false });

  // Edit
  useHotkeys('ctrl+z', (e) => {
    e.preventDefault();
    shortcuts.onUndo?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+y, ctrl+shift+z', (e) => {
    e.preventDefault();
    shortcuts.onRedo?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+x', (e) => {
    e.preventDefault();
    shortcuts.onCut?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+c', (e) => {
    e.preventDefault();
    shortcuts.onCopy?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+v', (e) => {
    e.preventDefault();
    shortcuts.onPaste?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+d', (e) => {
    e.preventDefault();
    shortcuts.onDuplicate?.();
  }, { enableOnFormTags: false });

  useHotkeys('delete', (e) => {
    e.preventDefault();
    shortcuts.onDelete?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+a', (e) => {
    e.preventDefault();
    shortcuts.onSelectAll?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+shift+a', (e) => {
    e.preventDefault();
    shortcuts.onDeselectAll?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+f', (e) => {
    e.preventDefault();
    shortcuts.onFind?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+shift+f', (e) => {
    e.preventDefault();
    shortcuts.onFindInFiles?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+h', (e) => {
    e.preventDefault();
    shortcuts.onReplace?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+,', (e) => {
    e.preventDefault();
    shortcuts.onPreferences?.();
  }, { enableOnFormTags: false });

  // View
  useHotkeys('ctrl+shift+e', (e) => {
    e.preventDefault();
    shortcuts.onToggleExplorer?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+shift+p', (e) => {
    e.preventDefault();
    shortcuts.onToggleProperties?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+shift+c', (e) => {
    e.preventDefault();
    shortcuts.onToggleConsole?.();
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+1', (e) => {
    e.preventDefault();
    shortcuts.onViewMode?.('map');
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+2', (e) => {
    e.preventDefault();
    shortcuts.onViewMode?.('list');
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+3', (e) => {
    e.preventDefault();
    shortcuts.onViewMode?.('tree');
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+4', (e) => {
    e.preventDefault();
    shortcuts.onViewMode?.('split');
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+=, ctrl+plus', (e) => {
    e.preventDefault();
    shortcuts.onZoom?.('in');
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+-', (e) => {
    e.preventDefault();
    shortcuts.onZoom?.('out');
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+0', (e) => {
    e.preventDefault();
    shortcuts.onZoom?.('fit');
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+shift+0', (e) => {
    e.preventDefault();
    shortcuts.onZoom?.('selection');
  }, { enableOnFormTags: false });

  useHotkeys('ctrl+g', (e) => {
    e.preventDefault();
    shortcuts.onGridToggle?.();
  }, { enableOnFormTags: false });

  useHotkeys('f11', (e) => {
    e.preventDefault();
    shortcuts.onFullscreen?.();
  }, { enableOnFormTags: false });

  // Entity
  useHotkeys('enter', (e) => {
    if (document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
      e.preventDefault();
      shortcuts.onEntityProperties?.();
    }
  }, { enableOnFormTags: false });

  // Help
  useHotkeys('f1', (e) => {
    e.preventDefault();
    shortcuts.onDocumentation?.();
  }, { enableOnFormTags: false });
};

