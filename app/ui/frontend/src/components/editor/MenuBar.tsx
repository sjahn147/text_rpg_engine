/**
 * 메뉴바 컴포넌트 (개선된 버전)
 */
import React, { useState, useEffect, useRef } from 'react';
import { 
  FiFile, FiFolder, FiSave, FiDownload, FiUpload,
  FiRotateCcw, FiRotateCw, FiScissors, FiCopy, FiClipboard,
  FiTrash2, FiSearch, FiSettings, FiGrid, FiZoomIn, FiZoomOut,
  FiMaximize2, FiPlus, FiEdit, FiLayers, FiEye, FiEyeOff,
  FiHelpCircle, FiInfo, FiX
} from 'react-icons/fi';
import { 
  MdSelectAll, MdDeselect, MdFindReplace, MdFullscreen,
  MdViewList, MdViewModule, MdViewQuilt, MdViewComfy
} from 'react-icons/md';

interface MenuBarProps {
  currentTool?: 'select' | 'pin' | 'road';
  onToolChange?: (tool: 'select' | 'pin' | 'road') => void;
  onNewProject?: () => void;
  onOpenProject?: () => void;
  onSaveProject?: () => void;
  onSaveProjectAs?: () => void;
  onImport?: (type: 'map' | 'entities' | 'regions') => void;
  onExport?: (type: 'map' | 'entities' | 'regions' | 'full') => void;
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
  onTogglePanel?: (panel: string) => void;
  onViewMode?: (mode: 'map' | 'list' | 'tree' | 'split') => void;
  onZoom?: (action: 'in' | 'out' | 'fit' | 'selection') => void;
  onGridToggle?: () => void;
  onGridSettings?: () => void;
  onFullscreen?: () => void;
  onNewEntity?: (type: string) => void;
  onEntityProperties?: () => void;
  onEntityRelationships?: () => void;
  onBatchOperations?: (operation: string) => void;
  onValidate?: (type: string) => void;
  onLayout?: (layout: string) => void;
  onDocumentation?: () => void;
  onKeyboardShortcuts?: () => void;
  onAbout?: () => void;
  onKnowledgeManager?: () => void;
  canUndo?: boolean;
  canRedo?: boolean;
  canPaste?: boolean;
  hasSelection?: boolean;
  gridEnabled?: boolean;
}

export const MenuBar: React.FC<MenuBarProps> = ({
  currentTool = 'select',
  onToolChange,
  onNewProject,
  onOpenProject,
  onSaveProject,
  onSaveProjectAs,
  onImport,
  onExport,
  onUndo,
  onRedo,
  onCut,
  onCopy,
  onPaste,
  onDuplicate,
  onDelete,
  onSelectAll,
  onDeselectAll,
  onFind,
  onFindInFiles,
  onReplace,
  onPreferences,
  onTogglePanel,
  onViewMode,
  onZoom,
  onGridToggle,
  onGridSettings,
  onFullscreen,
  onNewEntity,
  onEntityProperties,
  onEntityRelationships,
  onBatchOperations,
  onValidate,
  onLayout,
  onDocumentation,
  onKeyboardShortcuts,
  onAbout,
  onKnowledgeManager,
  canUndo = false,
  canRedo = false,
  canPaste = false,
  hasSelection = false,
  gridEnabled = false,
}) => {
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const menuBarRef = useRef<HTMLDivElement>(null);

  // 메뉴 외부 클릭 시 닫기
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      // menuBarRef가 있고 클릭이 메뉴바 외부인 경우에만 닫기
      if (menuBarRef.current && !menuBarRef.current.contains(target)) {
        setActiveMenu(null);
      }
    };

    if (activeMenu) {
      // 약간의 지연을 두어 메뉴 아이템 클릭이 먼저 처리되도록
      const timeoutId = setTimeout(() => {
        document.addEventListener('click', handleClickOutside);
      }, 100);
      return () => {
        clearTimeout(timeoutId);
        document.removeEventListener('click', handleClickOutside);
      };
    }
  }, [activeMenu]);

  const handleMenuClick = (menu: string) => {
    setActiveMenu(activeMenu === menu ? null : menu);
  };

  const handleMenuItemClick = (action: (() => void) | undefined) => {
    console.log('MenuBar: handleMenuItemClick called', { action: action ? 'exists' : 'undefined' });
    if (action) {
      try {
        action();
      } catch (error) {
        console.error('MenuBar: Error executing menu action', error);
        alert(`메뉴 실행 중 오류가 발생했습니다: ${error instanceof Error ? error.message : String(error)}`);
      }
    } else {
      console.warn('MenuBar: Menu action is undefined');
    }
    setActiveMenu(null);
  };

  const MenuItem: React.FC<{
    label?: string;
    shortcut?: string;
    icon?: React.ReactNode;
    onClick?: () => void;
    disabled?: boolean;
    separator?: boolean;
  }> = ({ label, shortcut, icon, onClick, disabled = false, separator = false }) => {
    if (separator) {
      return <div style={{ height: '1px', backgroundColor: '#e0e0e0', margin: '4px 8px' }} />;
    }
    return (
      <div
        data-menu-item="true"
        onClick={(e) => {
          e.stopPropagation();
          console.log('MenuBar: MenuItem clicked', { label, disabled, hasOnClick: !!onClick });
          if (!disabled && onClick) {
            console.log('MenuBar: Calling onClick handler', { label });
            // 즉시 실행
            try {
              onClick();
            } catch (error) {
              console.error('MenuBar: Error in onClick handler', error);
              alert(`메뉴 실행 중 오류: ${error instanceof Error ? error.message : String(error)}`);
            }
            // 메뉴 닫기
            setActiveMenu(null);
          } else if (!onClick) {
            console.warn('MenuBar: MenuItem has no onClick handler', { label });
          } else if (disabled) {
            console.log('MenuBar: MenuItem is disabled', { label });
          }
        }}
        style={{
          padding: '6px 24px 6px 32px',
          fontSize: '13px',
          cursor: disabled ? 'not-allowed' : 'pointer',
          backgroundColor: 'transparent',
          color: disabled ? '#999' : '#333',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          whiteSpace: 'nowrap',
          gap: '12px',
        }}
        onMouseEnter={(e) => {
          if (!disabled) {
            e.currentTarget.style.backgroundColor = '#e3f2fd';
          }
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'transparent';
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
          {icon && <span style={{ fontSize: '14px', display: 'flex', alignItems: 'center' }}>{icon}</span>}
          <span>{label}</span>
        </div>
        {shortcut && (
          <span style={{ fontSize: '11px', color: '#999', fontFamily: 'monospace' }}>
            {shortcut}
          </span>
        )}
      </div>
    );
  };

  const SubMenu: React.FC<{
    label: string;
    icon?: React.ReactNode;
    items: Array<{
      label?: string;
      shortcut?: string;
      icon?: React.ReactNode;
      onClick?: () => void;
      disabled?: boolean;
      separator?: boolean;
    }>;
  }> = ({ label, icon, items }) => {
    const subMenuRef = useRef<HTMLDivElement>(null);
    
    return (
      <div style={{ position: 'relative' }} ref={subMenuRef}>
        <div
          onClick={(e) => {
            e.stopPropagation();
            console.log('MenuBar: Menu clicked', label);
            handleMenuClick(label);
          }}
          style={{
            padding: '8px 12px',
            fontSize: '13px',
            cursor: 'pointer',
            backgroundColor: activeMenu === label ? '#e3f2fd' : 'transparent',
            color: '#333',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            borderRadius: '4px',
            transition: 'background-color 0.2s',
          }}
          onMouseEnter={(e) => {
            if (activeMenu !== label) {
              e.currentTarget.style.backgroundColor = '#f5f5f5';
            }
          }}
          onMouseLeave={(e) => {
            if (activeMenu !== label) {
              e.currentTarget.style.backgroundColor = 'transparent';
            }
          }}
        >
          {icon && <span style={{ fontSize: '14px' }}>{icon}</span>}
          <span>{label}</span>
        </div>
        {activeMenu === label && (
          <div
            style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              backgroundColor: '#fff',
              border: '1px solid #ddd',
              borderRadius: '4px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              zIndex: 1000,
              minWidth: '220px',
              padding: '4px 0',
              marginTop: '4px',
            }}
            onClick={(e) => {
              e.stopPropagation();
            }}
            onMouseLeave={(e) => {
              // 마우스가 메뉴 밖으로 나갔을 때만 닫기
              const relatedTarget = e.relatedTarget as Node;
              const currentTarget = e.currentTarget;
              if (relatedTarget && !currentTarget.contains(relatedTarget)) {
                setTimeout(() => {
                  if (activeMenu === label) {
                    setActiveMenu(null);
                  }
                }, 300);
              }
            }}
          >
            {items.map((item, index) => {
              if (item.separator) {
                return <MenuItem key={index} separator={true} />;
              }
              return (
                <MenuItem
                  key={index}
                  label={item.label}
                  shortcut={item.shortcut}
                  icon={item.icon}
                  onClick={item.onClick}
                  disabled={item.disabled}
                />
              );
            })}
          </div>
        )}
      </div>
    );
  };

  // 툴바 버튼 스타일
  const toolButtonStyle = (tool: 'select' | 'pin' | 'road') => ({
    padding: '6px 12px',
    fontSize: '13px',
    cursor: 'pointer',
    backgroundColor: currentTool === tool ? '#2196F3' : 'transparent',
    color: currentTool === tool ? '#fff' : '#333',
    border: '1px solid',
    borderColor: currentTool === tool ? '#2196F3' : '#ddd',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    transition: 'all 0.2s',
  });

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        backgroundColor: '#fafafa',
        borderBottom: '1px solid #e0e0e0',
        fontSize: '13px',
        userSelect: 'none',
        padding: '0 8px',
        gap: '4px',
      }}
    >
      {/* 툴바 버튼 (왼쪽) */}
      <div style={{ display: 'flex', gap: '4px', padding: '4px 0', marginRight: '8px', borderRight: '1px solid #e0e0e0', paddingRight: '8px' }}>
        <button
          onClick={() => onToolChange?.('select')}
          style={toolButtonStyle('select')}
          title="선택 (V)"
        >
          <FiEdit size={14} />
          <span>선택</span>
        </button>
        <button
          onClick={() => onToolChange?.('pin')}
          style={toolButtonStyle('pin')}
          title="핀 추가 (P)"
        >
          <FiPlus size={14} />
          <span>핀</span>
        </button>
        <button
          onClick={() => onToolChange?.('road')}
          style={toolButtonStyle('road')}
          title="도로 그리기 (R)"
        >
          <FiLayers size={14} />
          <span>도로</span>
        </button>
      </div>

      {/* 줌 컨트롤 */}
      <div style={{ display: 'flex', gap: '2px', marginRight: '8px', borderRight: '1px solid #e0e0e0', paddingRight: '8px' }}>
        <button
          onClick={() => onZoom?.('in')}
          style={{
            padding: '6px 8px',
            fontSize: '13px',
            cursor: 'pointer',
            backgroundColor: 'transparent',
            border: '1px solid #ddd',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
          }}
          title="확대 (Ctrl+=)"
        >
          <FiZoomIn size={14} />
        </button>
        <button
          onClick={() => onZoom?.('out')}
          style={{
            padding: '6px 8px',
            fontSize: '13px',
            cursor: 'pointer',
            backgroundColor: 'transparent',
            border: '1px solid #ddd',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
          }}
          title="축소 (Ctrl+-)"
        >
          <FiZoomOut size={14} />
        </button>
        <button
          onClick={onGridToggle}
          style={{
            padding: '6px 8px',
            fontSize: '13px',
            cursor: 'pointer',
            backgroundColor: gridEnabled ? '#2196F3' : 'transparent',
            color: gridEnabled ? '#fff' : '#333',
            border: '1px solid',
            borderColor: gridEnabled ? '#2196F3' : '#ddd',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
          }}
          title="그리드 토글 (Ctrl+G)"
        >
          <FiGrid size={14} />
        </button>
      </div>

      {/* 메뉴 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '2px', flex: 1 }}>
        <SubMenu
          label="File"
          icon={<FiFile size={14} />}
          items={[
            { label: '백업 저장...', shortcut: 'Ctrl+S', icon: <FiSave size={14} />, onClick: onSaveProject },
            { label: '백업 복원...', shortcut: 'Ctrl+O', icon: <FiFolder size={14} />, onClick: onOpenProject },
            { separator: true },
            { label: 'Import Map Image...', icon: <FiUpload size={14} />, onClick: () => onImport?.('map') },
            { label: 'Import Entities (JSON)...', icon: <FiUpload size={14} />, onClick: () => onImport?.('entities') },
            { label: 'Import Regions (CSV)...', icon: <FiUpload size={14} />, onClick: () => onImport?.('regions') },
            { separator: true },
            { label: 'Export Map Image...', icon: <FiDownload size={14} />, onClick: () => onExport?.('map') },
            { label: 'Export Entities (JSON)...', icon: <FiDownload size={14} />, onClick: () => onExport?.('entities') },
            { label: 'Export Regions (CSV)...', icon: <FiDownload size={14} />, onClick: () => onExport?.('regions') },
            { label: 'Export Full World Data...', icon: <FiDownload size={14} />, onClick: () => onExport?.('full') },
          ]}
        />
        <SubMenu
          label="Edit"
          items={[
            { label: 'Undo', shortcut: 'Ctrl+Z', icon: <FiRotateCcw size={14} />, onClick: onUndo, disabled: !canUndo },
            { label: 'Redo', shortcut: 'Ctrl+Y', icon: <FiRotateCw size={14} />, onClick: onRedo, disabled: !canRedo },
            { separator: true },
            { label: 'Cut', shortcut: 'Ctrl+X', icon: <FiScissors size={14} />, onClick: onCut, disabled: !hasSelection },
            { label: 'Copy', shortcut: 'Ctrl+C', icon: <FiCopy size={14} />, onClick: onCopy, disabled: !hasSelection },
            { label: 'Paste', shortcut: 'Ctrl+V', icon: <FiClipboard size={14} />, onClick: onPaste, disabled: !canPaste },
            { label: 'Duplicate', shortcut: 'Ctrl+D', icon: <FiCopy size={14} />, onClick: onDuplicate, disabled: !hasSelection },
            { label: 'Delete', shortcut: 'Del', icon: <FiTrash2 size={14} />, onClick: onDelete, disabled: !hasSelection },
            { separator: true },
            { label: 'Select All', shortcut: 'Ctrl+A', icon: <MdSelectAll size={14} />, onClick: onSelectAll },
            { label: 'Deselect All', shortcut: 'Ctrl+Shift+A', icon: <MdDeselect size={14} />, onClick: onDeselectAll },
            { separator: true },
            { label: 'Find...', shortcut: 'Ctrl+F', icon: <FiSearch size={14} />, onClick: onFind },
            { label: 'Find in Files...', shortcut: 'Ctrl+Shift+F', icon: <FiSearch size={14} />, onClick: onFindInFiles },
            { label: 'Replace...', shortcut: 'Ctrl+H', icon: <MdFindReplace size={14} />, onClick: onReplace },
            { separator: true },
            { label: 'Preferences...', shortcut: 'Ctrl+,', icon: <FiSettings size={14} />, onClick: onPreferences },
          ]}
        />
        <SubMenu
          label="View"
          items={[
            { label: 'Explorer Panel', shortcut: 'Ctrl+Shift+E', icon: <FiLayers size={14} />, onClick: () => onTogglePanel?.('explorer') },
            { label: 'Properties Panel', shortcut: 'Ctrl+Shift+P', icon: <FiEdit size={14} />, onClick: () => onTogglePanel?.('properties') },
            { separator: true },
            { label: 'Map View', shortcut: 'Ctrl+1', icon: <MdViewModule size={14} />, onClick: () => onViewMode?.('map') },
            { label: 'List View', shortcut: 'Ctrl+2', icon: <MdViewList size={14} />, onClick: () => onViewMode?.('list') },
            { label: 'Tree View', shortcut: 'Ctrl+3', icon: <MdViewQuilt size={14} />, onClick: () => onViewMode?.('tree') },
            { label: 'Split View', shortcut: 'Ctrl+4', icon: <MdViewComfy size={14} />, onClick: () => onViewMode?.('split') },
            { separator: true },
            { label: 'Zoom In', shortcut: 'Ctrl+=', icon: <FiZoomIn size={14} />, onClick: () => onZoom?.('in') },
            { label: 'Zoom Out', shortcut: 'Ctrl+-', icon: <FiZoomOut size={14} />, onClick: () => onZoom?.('out') },
            { label: 'Zoom to Fit', shortcut: 'Ctrl+0', icon: <FiZoomIn size={14} />, onClick: () => onZoom?.('fit') },
            { separator: true },
            { label: 'Show Grid', shortcut: 'Ctrl+G', icon: <FiGrid size={14} />, onClick: onGridToggle },
            { label: 'Grid Settings...', icon: <FiSettings size={14} />, onClick: onGridSettings },
            { separator: true },
            { label: 'Fullscreen', shortcut: 'F11', icon: <MdFullscreen size={14} />, onClick: onFullscreen },
          ]}
        />
        <SubMenu
          label="Entity"
          items={[
            { label: 'New Region...', icon: <FiPlus size={14} />, onClick: () => onNewEntity?.('region') },
            { label: 'New Location...', icon: <FiPlus size={14} />, onClick: () => onNewEntity?.('location') },
            { label: 'New Cell...', icon: <FiPlus size={14} />, onClick: () => onNewEntity?.('cell') },
            { label: 'New Character (NPC)...', icon: <FiPlus size={14} />, onClick: () => onNewEntity?.('entity') },
            { label: 'New World Object...', icon: <FiPlus size={14} />, onClick: () => onNewEntity?.('world_object') },
            { separator: true },
            { label: 'Entity Properties...', shortcut: 'Enter', icon: <FiEdit size={14} />, onClick: onEntityProperties, disabled: !hasSelection },
            { label: 'Entity Relationships...', icon: <FiLayers size={14} />, onClick: onEntityRelationships, disabled: !hasSelection },
          ]}
        />
        <SubMenu
          label="Tools"
          items={[
            { label: 'Dialogue Knowledge Manager...', icon: <FiInfo size={14} />, onClick: onKnowledgeManager },
          ]}
        />
        <SubMenu
          label="Help"
          items={[
            { label: 'Documentation', shortcut: 'F1', icon: <FiHelpCircle size={14} />, onClick: onDocumentation },
            { label: 'Keyboard Shortcuts...', icon: <FiHelpCircle size={14} />, onClick: onKeyboardShortcuts },
            { separator: true },
            { label: 'About World Editor...', icon: <FiInfo size={14} />, onClick: onAbout },
          ]}
        />
      </div>
    </div>
  );
};
