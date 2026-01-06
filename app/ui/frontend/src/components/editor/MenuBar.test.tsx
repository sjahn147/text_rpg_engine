/**
 * MenuBar 컴포넌트 테스트
 * 모든 메뉴 항목이 올바르게 작동하는지 확인
 */
import React from 'react';
import { vi, describe, test, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MenuBar } from './MenuBar';

// Mock 함수들
const mockHandlers = {
  onToolChange: vi.fn(),
  onNewProject: vi.fn(),
  onOpenProject: vi.fn(),
  onSaveProject: vi.fn(),
  onSaveProjectAs: vi.fn(),
  onImport: vi.fn(),
  onExport: vi.fn(),
  onUndo: vi.fn(),
  onRedo: vi.fn(),
  onCut: vi.fn(),
  onCopy: vi.fn(),
  onPaste: vi.fn(),
  onDuplicate: vi.fn(),
  onDelete: vi.fn(),
  onSelectAll: vi.fn(),
  onDeselectAll: vi.fn(),
  onFind: vi.fn(),
  onFindInFiles: vi.fn(),
  onReplace: vi.fn(),
  onPreferences: vi.fn(),
  onTogglePanel: vi.fn(),
  onViewMode: vi.fn(),
  onZoom: vi.fn(),
  onGridToggle: vi.fn(),
  onGridSettings: vi.fn(),
  onFullscreen: vi.fn(),
  onNewEntity: vi.fn(),
  onEntityProperties: vi.fn(),
  onEntityRelationships: vi.fn(),
  onBatchOperations: vi.fn(),
  onValidate: vi.fn(),
  onLayout: vi.fn(),
  onDocumentation: vi.fn(),
  onKeyboardShortcuts: vi.fn(),
  onAbout: vi.fn(),
  onKnowledgeManager: vi.fn(),
};

describe('MenuBar 컴포넌트 테스트', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderMenuBar = (props = {}) => {
    return render(
      <MenuBar
        currentTool="select"
        canUndo={true}
        canRedo={true}
        canPaste={true}
        hasSelection={true}
        gridEnabled={false}
        {...mockHandlers}
        {...props}
      />
    );
  };

  describe('도구 버튼 테스트', () => {
    test('선택 도구 버튼 클릭 시 onToolChange 호출', () => {
      renderMenuBar();
      const selectButton = screen.getByTitle('선택 (V)');
      fireEvent.click(selectButton);
      expect(mockHandlers.onToolChange).toHaveBeenCalledWith('select');
    });

    test('핀 도구 버튼 클릭 시 onToolChange 호출', () => {
      renderMenuBar();
      const pinButton = screen.getByTitle('핀 추가 (P)');
      fireEvent.click(pinButton);
      expect(mockHandlers.onToolChange).toHaveBeenCalledWith('pin');
    });

    test('도로 도구 버튼 클릭 시 onToolChange 호출', () => {
      renderMenuBar();
      const roadButton = screen.getByTitle('도로 그리기 (R)');
      fireEvent.click(roadButton);
      expect(mockHandlers.onToolChange).toHaveBeenCalledWith('road');
    });
  });

  describe('File 메뉴 테스트', () => {
    test('File 메뉴 열기', async () => {
      renderMenuBar();
      const fileMenu = screen.getByText('File');
      fireEvent.click(fileMenu);
      
      await waitFor(() => {
        expect(screen.getByText('백업 저장...')).toBeInTheDocument();
      });
    });

    test('프로젝트 저장 클릭 시 onSaveProject 호출', async () => {
      renderMenuBar();
      const fileMenu = screen.getByText('File');
      fireEvent.click(fileMenu);
      
      await waitFor(() => {
        const saveButton = screen.getByText('백업 저장...');
        fireEvent.click(saveButton);
        expect(mockHandlers.onSaveProject).toHaveBeenCalled();
      });
    });

    test('프로젝트 복원 클릭 시 onOpenProject 호출', async () => {
      renderMenuBar();
      const fileMenu = screen.getByText('File');
      fireEvent.click(fileMenu);
      
      await waitFor(() => {
        const restoreButton = screen.getByText('백업 복원...');
        fireEvent.click(restoreButton);
        expect(mockHandlers.onOpenProject).toHaveBeenCalled();
      });
    });

    test('Import Map Image 클릭 시 onImport 호출', async () => {
      renderMenuBar();
      const fileMenu = screen.getByText('File');
      fireEvent.click(fileMenu);
      
      await waitFor(() => {
        const importButton = screen.getByText('Import Map Image...');
        fireEvent.click(importButton);
        expect(mockHandlers.onImport).toHaveBeenCalledWith('map');
      });
    });

    test('Import Entities 클릭 시 onImport 호출', async () => {
      renderMenuBar();
      const fileMenu = screen.getByText('File');
      fireEvent.click(fileMenu);
      
      await waitFor(() => {
        const importButton = screen.getByText('Import Entities (JSON)...');
        fireEvent.click(importButton);
        expect(mockHandlers.onImport).toHaveBeenCalledWith('entities');
      });
    });

    test('Import Regions 클릭 시 onImport 호출', async () => {
      renderMenuBar();
      const fileMenu = screen.getByText('File');
      fireEvent.click(fileMenu);
      
      await waitFor(() => {
        const importButton = screen.getByText('Import Regions (CSV)...');
        fireEvent.click(importButton);
        expect(mockHandlers.onImport).toHaveBeenCalledWith('regions');
      });
    });

    test('Export Map Image 클릭 시 onExport 호출', async () => {
      renderMenuBar();
      const fileMenu = screen.getByText('File');
      fireEvent.click(fileMenu);
      
      await waitFor(() => {
        const exportButton = screen.getByText('Export Map Image...');
        fireEvent.click(exportButton);
        expect(mockHandlers.onExport).toHaveBeenCalledWith('map');
      });
    });

    test('Export Entities 클릭 시 onExport 호출', async () => {
      renderMenuBar();
      const fileMenu = screen.getByText('File');
      fireEvent.click(fileMenu);
      
      await waitFor(() => {
        const exportButton = screen.getByText('Export Entities (JSON)...');
        fireEvent.click(exportButton);
        expect(mockHandlers.onExport).toHaveBeenCalledWith('entities');
      });
    });

    test('Export Regions 클릭 시 onExport 호출', async () => {
      renderMenuBar();
      const fileMenu = screen.getByText('File');
      fireEvent.click(fileMenu);
      
      await waitFor(() => {
        const exportButton = screen.getByText('Export Regions (CSV)...');
        fireEvent.click(exportButton);
        expect(mockHandlers.onExport).toHaveBeenCalledWith('regions');
      });
    });

    test('Export Full World Data 클릭 시 onExport 호출', async () => {
      renderMenuBar();
      const fileMenu = screen.getByText('File');
      fireEvent.click(fileMenu);
      
      await waitFor(() => {
        const exportButton = screen.getByText('Export Full World Data...');
        fireEvent.click(exportButton);
        expect(mockHandlers.onExport).toHaveBeenCalledWith('full');
      });
    });
  });

  describe('Edit 메뉴 테스트', () => {
    test('Edit 메뉴 열기', async () => {
      renderMenuBar();
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        expect(screen.getByText('Undo')).toBeInTheDocument();
      });
    });

    test('Undo 클릭 시 onUndo 호출', async () => {
      renderMenuBar({ canUndo: true });
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const undoButton = screen.getByText('Undo');
        fireEvent.click(undoButton);
        expect(mockHandlers.onUndo).toHaveBeenCalled();
      });
    });

    test('Redo 클릭 시 onRedo 호출', async () => {
      renderMenuBar({ canRedo: true });
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const redoButton = screen.getByText('Redo');
        fireEvent.click(redoButton);
        expect(mockHandlers.onRedo).toHaveBeenCalled();
      });
    });

    test('Cut 클릭 시 onCut 호출', async () => {
      renderMenuBar({ hasSelection: true });
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const cutButton = screen.getByText('Cut');
        fireEvent.click(cutButton);
        expect(mockHandlers.onCut).toHaveBeenCalled();
      });
    });

    test('Copy 클릭 시 onCopy 호출', async () => {
      renderMenuBar({ hasSelection: true });
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const copyButton = screen.getByText('Copy');
        fireEvent.click(copyButton);
        expect(mockHandlers.onCopy).toHaveBeenCalled();
      });
    });

    test('Paste 클릭 시 onPaste 호출', async () => {
      renderMenuBar({ canPaste: true });
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const pasteButton = screen.getByText('Paste');
        fireEvent.click(pasteButton);
        expect(mockHandlers.onPaste).toHaveBeenCalled();
      });
    });

    test('Duplicate 클릭 시 onDuplicate 호출', async () => {
      renderMenuBar({ hasSelection: true });
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const duplicateButton = screen.getByText('Duplicate');
        fireEvent.click(duplicateButton);
        expect(mockHandlers.onDuplicate).toHaveBeenCalled();
      });
    });

    test('Delete 클릭 시 onDelete 호출', async () => {
      renderMenuBar({ hasSelection: true });
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const deleteButton = screen.getByText('Delete');
        fireEvent.click(deleteButton);
        expect(mockHandlers.onDelete).toHaveBeenCalled();
      });
    });

    test('Select All 클릭 시 onSelectAll 호출', async () => {
      renderMenuBar();
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const selectAllButton = screen.getByText('Select All');
        fireEvent.click(selectAllButton);
        expect(mockHandlers.onSelectAll).toHaveBeenCalled();
      });
    });

    test('Deselect All 클릭 시 onDeselectAll 호출', async () => {
      renderMenuBar();
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const deselectAllButton = screen.getByText('Deselect All');
        fireEvent.click(deselectAllButton);
        expect(mockHandlers.onDeselectAll).toHaveBeenCalled();
      });
    });

    test('Find 클릭 시 onFind 호출', async () => {
      renderMenuBar();
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const findButton = screen.getByText('Find...');
        fireEvent.click(findButton);
        expect(mockHandlers.onFind).toHaveBeenCalled();
      });
    });

    test('Find in Files 클릭 시 onFindInFiles 호출', async () => {
      renderMenuBar();
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const findInFilesButton = screen.getByText('Find in Files...');
        fireEvent.click(findInFilesButton);
        expect(mockHandlers.onFindInFiles).toHaveBeenCalled();
      });
    });

    test('Replace 클릭 시 onReplace 호출', async () => {
      renderMenuBar();
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const replaceButton = screen.getByText('Replace...');
        fireEvent.click(replaceButton);
        expect(mockHandlers.onReplace).toHaveBeenCalled();
      });
    });

    test('Preferences 클릭 시 onPreferences 호출', async () => {
      renderMenuBar();
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const preferencesButton = screen.getByText('Preferences...');
        fireEvent.click(preferencesButton);
        expect(mockHandlers.onPreferences).toHaveBeenCalled();
      });
    });
  });

  describe('View 메뉴 테스트', () => {
    test('View 메뉴 열기', async () => {
      renderMenuBar();
      const viewMenu = screen.getByText('View');
      fireEvent.click(viewMenu);
      
      await waitFor(() => {
        expect(screen.getByText('Explorer Panel')).toBeInTheDocument();
      });
    });

    test('Explorer Panel 클릭 시 onTogglePanel 호출', async () => {
      renderMenuBar();
      const viewMenu = screen.getByText('View');
      fireEvent.click(viewMenu);
      
      await waitFor(() => {
        const explorerButton = screen.getByText('Explorer Panel');
        fireEvent.click(explorerButton);
        expect(mockHandlers.onTogglePanel).toHaveBeenCalledWith('explorer');
      });
    });

    test('Properties Panel 클릭 시 onTogglePanel 호출', async () => {
      renderMenuBar();
      const viewMenu = screen.getByText('View');
      fireEvent.click(viewMenu);
      
      await waitFor(() => {
        const propertiesButton = screen.getByText('Properties Panel');
        fireEvent.click(propertiesButton);
        expect(mockHandlers.onTogglePanel).toHaveBeenCalledWith('properties');
      });
    });

    test('Map View 클릭 시 onViewMode 호출', async () => {
      renderMenuBar();
      const viewMenu = screen.getByText('View');
      fireEvent.click(viewMenu);
      
      await waitFor(() => {
        const mapViewButton = screen.getByText('Map View');
        fireEvent.click(mapViewButton);
        expect(mockHandlers.onViewMode).toHaveBeenCalledWith('map');
      });
    });

    test('List View 클릭 시 onViewMode 호출', async () => {
      renderMenuBar();
      const viewMenu = screen.getByText('View');
      fireEvent.click(viewMenu);
      
      await waitFor(() => {
        const listViewButton = screen.getByText('List View');
        fireEvent.click(listViewButton);
        expect(mockHandlers.onViewMode).toHaveBeenCalledWith('list');
      });
    });

    test('Tree View 클릭 시 onViewMode 호출', async () => {
      renderMenuBar();
      const viewMenu = screen.getByText('View');
      fireEvent.click(viewMenu);
      
      await waitFor(() => {
        const treeViewButton = screen.getByText('Tree View');
        fireEvent.click(treeViewButton);
        expect(mockHandlers.onViewMode).toHaveBeenCalledWith('tree');
      });
    });

    test('Split View 클릭 시 onViewMode 호출', async () => {
      renderMenuBar();
      const viewMenu = screen.getByText('View');
      fireEvent.click(viewMenu);
      
      await waitFor(() => {
        const splitViewButton = screen.getByText('Split View');
        fireEvent.click(splitViewButton);
        expect(mockHandlers.onViewMode).toHaveBeenCalledWith('split');
      });
    });

    test('Zoom In 클릭 시 onZoom 호출', async () => {
      renderMenuBar();
      const viewMenu = screen.getByText('View');
      fireEvent.click(viewMenu);
      
      await waitFor(() => {
        const zoomInButton = screen.getByText('Zoom In');
        fireEvent.click(zoomInButton);
        expect(mockHandlers.onZoom).toHaveBeenCalledWith('in');
      });
    });

    test('Zoom Out 클릭 시 onZoom 호출', async () => {
      renderMenuBar();
      const viewMenu = screen.getByText('View');
      fireEvent.click(viewMenu);
      
      await waitFor(() => {
        const zoomOutButton = screen.getByText('Zoom Out');
        fireEvent.click(zoomOutButton);
        expect(mockHandlers.onZoom).toHaveBeenCalledWith('out');
      });
    });

    test('Zoom to Fit 클릭 시 onZoom 호출', async () => {
      renderMenuBar();
      const viewMenu = screen.getByText('View');
      fireEvent.click(viewMenu);
      
      await waitFor(() => {
        const zoomFitButton = screen.getByText('Zoom to Fit');
        fireEvent.click(zoomFitButton);
        expect(mockHandlers.onZoom).toHaveBeenCalledWith('fit');
      });
    });

    test('Show Grid 클릭 시 onGridToggle 호출', async () => {
      renderMenuBar();
      const viewMenu = screen.getByText('View');
      fireEvent.click(viewMenu);
      
      await waitFor(() => {
        const gridButton = screen.getByText('Show Grid');
        fireEvent.click(gridButton);
        expect(mockHandlers.onGridToggle).toHaveBeenCalled();
      });
    });

    test('Grid Settings 클릭 시 onGridSettings 호출', async () => {
      renderMenuBar();
      const viewMenu = screen.getByText('View');
      fireEvent.click(viewMenu);
      
      await waitFor(() => {
        const gridSettingsButton = screen.getByText('Grid Settings...');
        fireEvent.click(gridSettingsButton);
        expect(mockHandlers.onGridSettings).toHaveBeenCalled();
      });
    });

    test('Fullscreen 클릭 시 onFullscreen 호출', async () => {
      renderMenuBar();
      const viewMenu = screen.getByText('View');
      fireEvent.click(viewMenu);
      
      await waitFor(() => {
        const fullscreenButton = screen.getByText('Fullscreen');
        fireEvent.click(fullscreenButton);
        expect(mockHandlers.onFullscreen).toHaveBeenCalled();
      });
    });
  });

  describe('Entity 메뉴 테스트', () => {
    test('Entity 메뉴 열기', async () => {
      renderMenuBar();
      const entityMenu = screen.getByText('Entity');
      fireEvent.click(entityMenu);
      
      await waitFor(() => {
        expect(screen.getByText('New Region...')).toBeInTheDocument();
      });
    });

    test('New Region 클릭 시 onNewEntity 호출', async () => {
      renderMenuBar();
      const entityMenu = screen.getByText('Entity');
      fireEvent.click(entityMenu);
      
      await waitFor(() => {
        const newRegionButton = screen.getByText('New Region...');
        fireEvent.click(newRegionButton);
        expect(mockHandlers.onNewEntity).toHaveBeenCalledWith('region');
      });
    });

    test('New Location 클릭 시 onNewEntity 호출', async () => {
      renderMenuBar();
      const entityMenu = screen.getByText('Entity');
      fireEvent.click(entityMenu);
      
      await waitFor(() => {
        const newLocationButton = screen.getByText('New Location...');
        fireEvent.click(newLocationButton);
        expect(mockHandlers.onNewEntity).toHaveBeenCalledWith('location');
      });
    });

    test('New Cell 클릭 시 onNewEntity 호출', async () => {
      renderMenuBar();
      const entityMenu = screen.getByText('Entity');
      fireEvent.click(entityMenu);
      
      await waitFor(() => {
        const newCellButton = screen.getByText('New Cell...');
        fireEvent.click(newCellButton);
        expect(mockHandlers.onNewEntity).toHaveBeenCalledWith('cell');
      });
    });

    test('New Character (NPC) 클릭 시 onNewEntity 호출', async () => {
      renderMenuBar();
      const entityMenu = screen.getByText('Entity');
      fireEvent.click(entityMenu);
      
      await waitFor(() => {
        const newCharacterButton = screen.getByText('New Character (NPC)...');
        fireEvent.click(newCharacterButton);
        expect(mockHandlers.onNewEntity).toHaveBeenCalledWith('entity');
      });
    });

    test('New World Object 클릭 시 onNewEntity 호출', async () => {
      renderMenuBar();
      const entityMenu = screen.getByText('Entity');
      fireEvent.click(entityMenu);
      
      await waitFor(() => {
        const newWorldObjectButton = screen.getByText('New World Object...');
        fireEvent.click(newWorldObjectButton);
        expect(mockHandlers.onNewEntity).toHaveBeenCalledWith('world_object');
      });
    });

    test('Entity Properties 클릭 시 onEntityProperties 호출', async () => {
      renderMenuBar({ hasSelection: true });
      const entityMenu = screen.getByText('Entity');
      fireEvent.click(entityMenu);
      
      await waitFor(() => {
        const propertiesButton = screen.getByText('Entity Properties...');
        fireEvent.click(propertiesButton);
        expect(mockHandlers.onEntityProperties).toHaveBeenCalled();
      });
    });

    test('Entity Relationships 클릭 시 onEntityRelationships 호출', async () => {
      renderMenuBar({ hasSelection: true });
      const entityMenu = screen.getByText('Entity');
      fireEvent.click(entityMenu);
      
      await waitFor(() => {
        const relationshipsButton = screen.getByText('Entity Relationships...');
        fireEvent.click(relationshipsButton);
        expect(mockHandlers.onEntityRelationships).toHaveBeenCalled();
      });
    });
  });

  describe('Tools 메뉴 테스트', () => {
    test('Tools 메뉴 열기', async () => {
      renderMenuBar();
      const toolsMenu = screen.getByText('Tools');
      fireEvent.click(toolsMenu);
      
      await waitFor(() => {
        expect(screen.getByText('Dialogue Knowledge Manager...')).toBeInTheDocument();
      });
    });

    test('Dialogue Knowledge Manager 클릭 시 onKnowledgeManager 호출', async () => {
      renderMenuBar();
      const toolsMenu = screen.getByText('Tools');
      fireEvent.click(toolsMenu);
      
      await waitFor(() => {
        const knowledgeButton = screen.getByText('Dialogue Knowledge Manager...');
        fireEvent.click(knowledgeButton);
        expect(mockHandlers.onKnowledgeManager).toHaveBeenCalled();
      });
    });
  });

  describe('Help 메뉴 테스트', () => {
    test('Help 메뉴 열기', async () => {
      renderMenuBar();
      const helpMenu = screen.getByText('Help');
      fireEvent.click(helpMenu);
      
      await waitFor(() => {
        expect(screen.getByText('Documentation')).toBeInTheDocument();
      });
    });

    test('Documentation 클릭 시 onDocumentation 호출', async () => {
      renderMenuBar();
      const helpMenu = screen.getByText('Help');
      fireEvent.click(helpMenu);
      
      await waitFor(() => {
        const docButton = screen.getByText('Documentation');
        fireEvent.click(docButton);
        expect(mockHandlers.onDocumentation).toHaveBeenCalled();
      });
    });

    test('Keyboard Shortcuts 클릭 시 onKeyboardShortcuts 호출', async () => {
      renderMenuBar();
      const helpMenu = screen.getByText('Help');
      fireEvent.click(helpMenu);
      
      await waitFor(() => {
        const shortcutsButton = screen.getByText('Keyboard Shortcuts...');
        fireEvent.click(shortcutsButton);
        expect(mockHandlers.onKeyboardShortcuts).toHaveBeenCalled();
      });
    });

    test('About World Editor 클릭 시 onAbout 호출', async () => {
      renderMenuBar();
      const helpMenu = screen.getByText('Help');
      fireEvent.click(helpMenu);
      
      await waitFor(() => {
        const aboutButton = screen.getByText('About World Editor...');
        fireEvent.click(aboutButton);
        expect(mockHandlers.onAbout).toHaveBeenCalled();
      });
    });
  });

  describe('툴바 버튼 테스트', () => {
    test('줌인 버튼 클릭 시 onZoom 호출', () => {
      renderMenuBar();
      const zoomInButton = screen.getByTitle('확대 (Ctrl+=)');
      fireEvent.click(zoomInButton);
      expect(mockHandlers.onZoom).toHaveBeenCalledWith('in');
    });

    test('줌아웃 버튼 클릭 시 onZoom 호출', () => {
      renderMenuBar();
      const zoomOutButton = screen.getByTitle('축소 (Ctrl+-)');
      fireEvent.click(zoomOutButton);
      expect(mockHandlers.onZoom).toHaveBeenCalledWith('out');
    });

    test('그리드 표시 버튼 클릭 시 onGridToggle 호출', () => {
      renderMenuBar();
      const gridButton = screen.getByTitle('그리드 표시 (Ctrl+G)');
      fireEvent.click(gridButton);
      expect(mockHandlers.onGridToggle).toHaveBeenCalled();
    });
  });

  describe('비활성화 상태 테스트', () => {
    test('canUndo가 false이면 Undo 버튼 비활성화', async () => {
      renderMenuBar({ canUndo: false });
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const undoButton = screen.getByText('Undo');
        expect(undoButton).toBeInTheDocument();
        // 비활성화된 버튼은 클릭해도 호출되지 않아야 함
        fireEvent.click(undoButton);
        expect(mockHandlers.onUndo).not.toHaveBeenCalled();
      });
    });

    test('hasSelection이 false이면 Cut 버튼 비활성화', async () => {
      renderMenuBar({ hasSelection: false });
      const editMenu = screen.getByText('Edit');
      fireEvent.click(editMenu);
      
      await waitFor(() => {
        const cutButton = screen.getByText('Cut');
        expect(cutButton).toBeInTheDocument();
        // 비활성화된 버튼은 클릭해도 호출되지 않아야 함
        fireEvent.click(cutButton);
        expect(mockHandlers.onCut).not.toHaveBeenCalled();
      });
    });

    test('hasSelection이 false이면 Entity Properties 버튼 비활성화', async () => {
      renderMenuBar({ hasSelection: false });
      const entityMenu = screen.getByText('Entity');
      fireEvent.click(entityMenu);
      
      await waitFor(() => {
        const propertiesButton = screen.getByText('Entity Properties...');
        expect(propertiesButton).toBeInTheDocument();
        // 비활성화된 버튼은 클릭해도 호출되지 않아야 함
        fireEvent.click(propertiesButton);
        expect(mockHandlers.onEntityProperties).not.toHaveBeenCalled();
      });
    });
  });
});
