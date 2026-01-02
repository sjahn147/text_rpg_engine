/**
 * 에디터 전역 상태 관리 훅
 */
import { useState, useCallback } from 'react';
import { EntityType } from '../../components/editor/EntityExplorer';

export interface EditorState {
  explorerMode: 'map' | 'explorer';
  selectedEntityType: EntityType | undefined;
  selectedEntityId: string | null;
  selectedPins: Set<string>;
  status: 'ready' | 'loading' | 'saving' | 'error';
  statusMessage: string;
}

export interface EditorStateActions {
  setExplorerMode: (mode: 'map' | 'explorer') => void;
  setSelectedEntityType: (type: EntityType | undefined) => void;
  setSelectedEntityId: (id: string | null) => void;
  setSelectedPins: (pins: Set<string>) => void;
  setStatus: (status: 'ready' | 'loading' | 'saving' | 'error') => void;
  setStatusMessage: (message: string) => void;
  clearSelection: () => void;
}

export const useEditorState = () => {
  const [explorerMode, setExplorerMode] = useState<'map' | 'explorer'>('map');
  const [selectedEntityType, setSelectedEntityType] = useState<EntityType | undefined>();
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const [selectedPins, setSelectedPins] = useState<Set<string>>(new Set());
  const [status, setStatus] = useState<'ready' | 'loading' | 'saving' | 'error'>('ready');
  const [statusMessage, setStatusMessage] = useState<string>('');

  const clearSelection = useCallback(() => {
    setSelectedEntityType(undefined);
    setSelectedEntityId(null);
    setSelectedPins(new Set());
  }, []);

  return {
    // State
    explorerMode,
    selectedEntityType,
    selectedEntityId,
    selectedPins,
    status,
    statusMessage,
    // Actions
    setExplorerMode,
    setSelectedEntityType,
    setSelectedEntityId,
    setSelectedPins,
    setStatus,
    setStatusMessage,
    clearSelection,
  };
};

