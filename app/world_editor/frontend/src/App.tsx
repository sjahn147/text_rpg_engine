/**
 * 월드 에디터 메인 앱 컴포넌트
 */
import React, { useState, useEffect } from 'react';
import { MapCanvas } from './components/MapCanvas';
import { InfoPanel } from './components/InfoPanel';
import { PinTreeView } from './components/PinTreeView';
import { PinEditorNew as PinEditor } from './components/PinEditorNew';
import { EntityExplorer, EntityType } from './components/EntityExplorer';
import { EntityEditor } from './components/EntityEditor';
import { MenuBar } from './components/MenuBar';
import { StatusBar } from './components/StatusBar';
import { SettingsModal } from './components/SettingsModal';
import { DialogueKnowledgeManager } from './components/DialogueKnowledgeManager';
import { SearchResultsModal } from './components/SearchResultsModal';
import { KeyboardShortcutsModal } from './components/KeyboardShortcutsModal';
import { AboutModal } from './components/AboutModal';
  import { 
  regionsApi, locationsApi, cellsApi, entitiesApi, 
  worldObjectsApi, effectCarriersApi, itemsApi, searchApi,
  managementApi, relationshipsApi, mapHierarchyApi, mapApi, projectApi
} from './services/api';
import { HierarchicalMapView, MapLevel } from './components/HierarchicalMapView';
import { CellEntityManager } from './components/CellEntityManager';
import { useWorldEditor } from './hooks/useWorldEditor';
import { useWebSocket } from './hooks/useWebSocket';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { useUndoRedo } from './hooks/useUndoRedo';
import { useSettings } from './hooks/useSettings';
import { EditorTool, WebSocketMessage } from './types';

const App: React.FC = () => {
  const [currentTool, setCurrentTool] = useState<EditorTool>('select');
  const [roadDrawingState, setRoadDrawingState] = useState<{
    fromPinId: string | null;
    drawing: boolean;
  }>({ fromPinId: null, drawing: false });
  const [explorerMode, setExplorerMode] = useState<'map' | 'explorer'>('map');
  const [selectedEntityType, setSelectedEntityType] = useState<EntityType | undefined>();
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const [mapViewMode, setMapViewMode] = useState<'world' | 'hierarchical' | 'cell'>('world');
  const [currentMapLevel, setCurrentMapLevel] = useState<MapLevel>('world');
  const [currentMapEntityId, setCurrentMapEntityId] = useState<string | null>(null);
  const [selectedCellId, setSelectedCellId] = useState<string | null>(null);
  // Cell에서 뒤로가기 시 이전 Location 정보 저장
  const [previousLocationId, setPreviousLocationId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);
  const [knowledgeManagerOpen, setKnowledgeManagerOpen] = useState(false);
  const [searchResultsModalOpen, setSearchResultsModalOpen] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [keyboardShortcutsModalOpen, setKeyboardShortcutsModalOpen] = useState(false);
  const [aboutModalOpen, setAboutModalOpen] = useState(false);
  const [selectedPins, setSelectedPins] = useState<Set<string>>(new Set());
  const [mousePosition, setMousePosition] = useState<{ x: number; y: number } | null>(null);
  const [fps, setFps] = useState<number | undefined>(undefined);
  const [status, setStatus] = useState<'ready' | 'loading' | 'saving' | 'error'>('ready');
  const [statusMessage, setStatusMessage] = useState<string>('');

  // Undo/Redo 시스템
  const { addAction, undo, redo, canUndo, canRedo } = useUndoRedo({ maxHistorySize: 50 });

  // 설정 시스템
  const { settings } = useSettings();
  const {
    mapState,
    pins,
    roads,
    regions,
    locations,
    cells,
    selectedPin,
    selectedRoad,
    loading,
    setSelectedPin,
    setSelectedRoad,
    addPin,
    updatePin,
    deletePin,
    addRoad,
    updateRoad,
    deleteRoad,
    updateMap,
    refreshData,
  } = useWorldEditor();

  // WebSocket 메시지 처리 (선택적 - 연결 실패해도 앱은 정상 작동)
  const handleWebSocketMessage = (message: WebSocketMessage) => {
    if (message.type === 'pin_update') {
      // 핀 업데이트 동기화
      // console.log('핀 업데이트:', message.data);
    } else if (message.type === 'road_update') {
      // 도로 업데이트 동기화
      // console.log('도로 업데이트:', message.data);
    } else if (message.type === 'map_update') {
      // 지도 업데이트 동기화
      // console.log('지도 업데이트:', message.data);
    }
  };

  // WebSocket 연결 (실패해도 앱은 정상 작동)
  const { sendMessage, connected: websocketConnected } = useWebSocket(handleWebSocketMessage);

  // 백업 저장 함수 (DB 스냅샷)
  const saveBackup = async (filename?: string) => {
    try {
      setStatus('saving');
      setStatusMessage('백업 저장 중...');
      
      // 백엔드 API 호출
      const response = await projectApi.export();
      const projectData = response.data.data;
      
      // 파일로 다운로드
      const data = JSON.stringify(projectData, null, 2);
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || `world_backup_${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      setStatus('ready');
      setStatusMessage('백업 저장 완료');
      setTimeout(() => setStatusMessage(''), 2000);
    } catch (error) {
      setStatus('error');
      setStatusMessage('백업 저장 실패');
      alert(`백업 저장 실패: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  // 백업 복원 함수
  const restoreBackup = async () => {
    if (!confirm('백업을 복원하시겠습니까? 현재 데이터가 모두 덮어씌워집니다.')) {
      return;
    }
    
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      
      try {
        setStatus('loading');
        setStatusMessage('백업 복원 중...');
        
        // 백엔드 API를 통해 파일 업로드
        const response = await projectApi.importFile(file);
        const stats = response.data.stats;
        
        await refreshData();
        setStatus('ready');
        setStatusMessage(`백업 복원 완료: ${JSON.stringify(stats)}`);
        setTimeout(() => setStatusMessage(''), 3000);
      } catch (error) {
        setStatus('error');
        setStatusMessage('백업 복원 실패');
        alert(`백업 복원 실패: ${error instanceof Error ? error.message : String(error)}`);
      }
    };
    input.click();
  };

  // 단축키 시스템
  useKeyboardShortcuts({
    onNewProject: () => {
      alert('현재 시스템은 데이터베이스를 직접 사용합니다. "새 프로젝트" 기능은 지원하지 않습니다.');
    },
    onOpenProject: restoreBackup,
    onSaveProject: async () => {
      await saveBackup();
    },
    onSaveProjectAs: async () => {
      const filename = prompt('백업 파일 이름을 입력하세요:', `world_backup_${new Date().toISOString().split('T')[0]}.json`);
      if (filename) {
        await saveBackup(filename);
      }
    },
    onUndo: undo,
    onRedo: redo,
    onCut: async () => {
      if (selectedPin) {
        const pin = pins.find(p => p.pin_id === selectedPin);
        if (pin) {
          await navigator.clipboard.writeText(JSON.stringify({ type: 'pin', data: pin }, null, 2));
          await deletePin(selectedPin);
          setSelectedPin(null);
          setStatusMessage('핀이 잘라내기되었습니다.');
          setTimeout(() => setStatusMessage(''), 2000);
        }
      } else if (selectedEntityId && selectedEntityType) {
        try {
          let entityData: any;
          switch (selectedEntityType) {
            case 'region':
              const regionRes = await regionsApi.getById(selectedEntityId);
              entityData = { type: 'region', data: regionRes.data };
              break;
            case 'location':
              const locationRes = await locationsApi.getById(selectedEntityId);
              entityData = { type: 'location', data: locationRes.data };
              break;
            case 'cell':
              const cellRes = await cellsApi.getById(selectedEntityId);
              entityData = { type: 'cell', data: cellRes.data };
              break;
            case 'entity':
              const entityRes = await entitiesApi.getById(selectedEntityId);
              entityData = { type: 'entity', data: entityRes.data };
              break;
            default:
              alert('이 엔티티 타입은 잘라내기를 지원하지 않습니다.');
              return;
          }
          await navigator.clipboard.writeText(JSON.stringify(entityData, null, 2));
          // 삭제는 사용자가 확인 후 수행
          if (confirm('잘라낸 엔티티를 삭제하시겠습니까?')) {
            if (selectedEntityType === 'region') {
              await regionsApi.delete(selectedEntityId);
            } else if (selectedEntityType === 'location') {
              await locationsApi.delete(selectedEntityId);
            } else if (selectedEntityType === 'cell') {
              await cellsApi.delete(selectedEntityId);
            } else {
              await entitiesApi.delete(selectedEntityId);
            }
            setSelectedEntityId(null);
            setSelectedEntityType(undefined);
            await refreshData();
          }
          setStatusMessage('엔티티가 잘라내기되었습니다.');
          setTimeout(() => setStatusMessage(''), 2000);
        } catch (error) {
          alert(`잘라내기 실패: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
    },
    onCopy: async () => {
      if (selectedPin) {
        const pin = pins.find(p => p.pin_id === selectedPin);
        if (pin) {
          await navigator.clipboard.writeText(JSON.stringify({ type: 'pin', data: pin }, null, 2));
          setStatusMessage('핀이 클립보드에 복사되었습니다.');
          setTimeout(() => setStatusMessage(''), 2000);
        }
      } else if (selectedEntityId && selectedEntityType) {
        try {
          let entityData: any;
          switch (selectedEntityType) {
            case 'region':
              const regionRes = await regionsApi.getById(selectedEntityId);
              entityData = { type: 'region', data: regionRes.data };
              break;
            case 'location':
              const locationRes = await locationsApi.getById(selectedEntityId);
              entityData = { type: 'location', data: locationRes.data };
              break;
            case 'cell':
              const cellRes = await cellsApi.getById(selectedEntityId);
              entityData = { type: 'cell', data: cellRes.data };
              break;
            case 'entity':
              const entityRes = await entitiesApi.getById(selectedEntityId);
              entityData = { type: 'entity', data: entityRes.data };
              break;
            default:
              alert('이 엔티티 타입은 복사를 지원하지 않습니다.');
              return;
          }
          await navigator.clipboard.writeText(JSON.stringify(entityData, null, 2));
          setStatusMessage('엔티티가 클립보드에 복사되었습니다.');
          setTimeout(() => setStatusMessage(''), 2000);
        } catch (error) {
          alert(`복사 실패: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
    },
    onPaste: async () => {
      try {
        const text = await navigator.clipboard.readText();
        const data = JSON.parse(text);
        
        if (data.type === 'pin' && data.data) {
          const pinData = data.data;
          const newPinData = {
            ...pinData,
            pin_id: `PIN_${Date.now()}`,
            pin_name: `${pinData.pin_name || '새 핀'} (복사)`,
            x: pinData.x + 20,
            y: pinData.y + 20,
          };
          delete (newPinData as any).created_at;
          delete (newPinData as any).updated_at;
          await addPin(newPinData);
          setStatusMessage('핀이 붙여넣기되었습니다.');
          setTimeout(() => setStatusMessage(''), 2000);
        } else if (data.type && data.data) {
          // 엔티티 붙여넣기는 서버 API가 필요
          alert('엔티티 붙여넣기는 추후 구현 예정입니다.');
        } else {
          alert('클립보드에 유효한 데이터가 없습니다.');
        }
      } catch (error) {
        alert('붙여넣기 실패: 클립보드 데이터를 읽을 수 없습니다.');
      }
    },
    onDuplicate: async () => {
      if (selectedPin) {
        const pin = pins.find(p => p.pin_id === selectedPin);
        if (pin) {
          const newPinData = {
            ...pin,
            pin_id: `PIN_${Date.now()}`,
            pin_name: `${pin.pin_name || '새 핀'} (복사)`,
            x: pin.x + 20,
            y: pin.y + 20,
          };
          delete (newPinData as any).created_at;
          delete (newPinData as any).updated_at;
          await addPin(newPinData);
          setStatusMessage('핀이 복제되었습니다.');
          setTimeout(() => setStatusMessage(''), 2000);
        }
      } else if (selectedEntityId && selectedEntityType) {
        try {
          let entityData: any;
          switch (selectedEntityType) {
            case 'region':
              const regionRes = await regionsApi.getById(selectedEntityId);
              entityData = regionRes.data;
              // ID 변경 및 이름에 (복사) 추가
              entityData.region_id = `REG_${Date.now()}`;
              entityData.region_name = `${entityData.region_name} (복사)`;
              await regionsApi.create(entityData);
              break;
            case 'location':
              const locationRes = await locationsApi.getById(selectedEntityId);
              entityData = locationRes.data;
              entityData.location_id = `LOC_${Date.now()}`;
              entityData.location_name = `${entityData.location_name} (복사)`;
              await managementApi.createLocation(entityData);
              break;
            case 'cell':
              const cellRes = await cellsApi.getById(selectedEntityId);
              entityData = cellRes.data;
              entityData.cell_id = `CELL_${Date.now()}`;
              entityData.cell_name = `${entityData.cell_name || '셀'} (복사)`;
              await managementApi.createCell(entityData);
              break;
            case 'entity':
              const entityRes = await entitiesApi.getById(selectedEntityId);
              entityData = entityRes.data;
              entityData.entity_id = `ENT_${Date.now()}`;
              entityData.entity_name = `${entityData.entity_name} (복사)`;
              await entitiesApi.create(entityData);
              break;
            default:
              alert('이 엔티티 타입은 복제를 지원하지 않습니다.');
              return;
          }
          await refreshData();
          setStatusMessage('엔티티가 복제되었습니다.');
          setTimeout(() => setStatusMessage(''), 2000);
        } catch (error) {
          alert(`복제 실패: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
    },
    onDelete: async () => {
      if (selectedPin) {
        if (confirm('선택한 핀을 삭제하시겠습니까?')) {
          await deletePin(selectedPin);
        }
      } else if (selectedEntityId) {
        if (confirm('선택한 엔티티를 삭제하시겠습니까?')) {
          try {
            await entitiesApi.delete(selectedEntityId);
            setSelectedEntityId(null);
            await refreshData();
            setStatusMessage('엔티티가 삭제되었습니다.');
          } catch (error) {
            console.error('엔티티 삭제 실패:', error);
            alert(`엔티티 삭제에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
          }
        }
      }
    },
    onSelectAll: () => {
      // 모든 핀 선택 (다중 선택)
      if (pins.length > 0) {
        const allPinIds = new Set(pins.map(p => p.pin_id));
        setSelectedPins(allPinIds);
        setSelectedPin(pins[0].pin_id); // 첫 번째 핀을 메인 선택으로
        setStatusMessage(`${pins.length}개의 핀이 선택되었습니다.`);
        setTimeout(() => setStatusMessage(''), 2000);
      }
    },
    onDeselectAll: () => {
      setSelectedPin(null);
      setSelectedRoad(null);
      setSelectedEntityType(undefined);
      setSelectedEntityId(null);
      setSelectedPins(new Set());
    },
    onFind: async () => {
      const query = prompt('검색할 키워드를 입력하세요:');
      if (query) {
        try {
          setStatus('loading');
          setStatusMessage('검색 중...');
          const response = await searchApi.search(query);
          setSearchResults(response.data.results || []);
          setSearchResultsModalOpen(true);
          setStatus('ready');
          setStatusMessage('');
        } catch (error) {
          setStatus('error');
          setStatusMessage('검색 실패');
          alert(`검색 실패: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
    },
    onFindInFiles: async () => {
      const query = prompt('파일에서 검색할 키워드를 입력하세요:');
      if (query) {
        try {
          setStatus('loading');
          setStatusMessage('검색 중...');
          const response = await searchApi.search(query);
          setSearchResults(response.data.results || []);
          setSearchResultsModalOpen(true);
          setStatus('ready');
          setStatusMessage('');
        } catch (error) {
          setStatus('error');
          setStatusMessage('검색 실패');
          alert(`검색 실패: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
    },
    onReplace: async () => {
      const findQuery = prompt('찾을 텍스트를 입력하세요:');
      if (!findQuery) return;
      
      const replaceQuery = prompt('바꿀 텍스트를 입력하세요:');
      if (replaceQuery === null) return;
      
      // 검색 결과 가져오기
      try {
        const response = await searchApi.search(findQuery);
        const results = response.data.results || [];
        
        if (results.length === 0) {
          alert('찾을 텍스트가 없습니다.');
          return;
        }
        
        if (!confirm(`${results.length}개의 결과를 찾았습니다. 모두 바꾸시겠습니까?`)) {
          return;
        }
        
        setStatus('saving');
        setStatusMessage('바꾸는 중...');
        
        // 각 결과에 대해 바꾸기 수행
        let successCount = 0;
        for (const result of results) {
          try {
            // 엔티티 타입에 따라 업데이트
            if (result.entity_type === 'region') {
              const regionRes = await regionsApi.getById(result.entity_id);
              const updated = {
                ...regionRes.data,
                region_name: regionRes.data.region_name?.replace(new RegExp(findQuery, 'gi'), replaceQuery),
                region_description: regionRes.data.region_description?.replace(new RegExp(findQuery, 'gi'), replaceQuery),
              };
              await regionsApi.update(result.entity_id, updated);
            } else if (result.entity_type === 'location') {
              const locationRes = await locationsApi.getById(result.entity_id);
              const updated = {
                ...locationRes.data,
                location_name: locationRes.data.location_name?.replace(new RegExp(findQuery, 'gi'), replaceQuery),
                location_description: locationRes.data.location_description?.replace(new RegExp(findQuery, 'gi'), replaceQuery),
              };
              await locationsApi.update(result.entity_id, updated);
            } else if (result.entity_type === 'entity') {
              const entityRes = await entitiesApi.getById(result.entity_id);
              const updated = {
                ...entityRes.data,
                entity_name: entityRes.data.entity_name?.replace(new RegExp(findQuery, 'gi'), replaceQuery),
                entity_description: entityRes.data.entity_description?.replace(new RegExp(findQuery, 'gi'), replaceQuery),
              };
              await entitiesApi.update(result.entity_id, updated);
            }
            successCount++;
          } catch (error) {
            console.error(`바꾸기 실패 (${result.entity_id}):`, error);
          }
        }
        
        await refreshData();
        setStatus('ready');
        setStatusMessage(`${successCount}개의 항목이 바뀌었습니다.`);
        setTimeout(() => setStatusMessage(''), 3000);
      } catch (error) {
        setStatus('error');
        setStatusMessage('바꾸기 실패');
        alert(`바꾸기 실패: ${error instanceof Error ? error.message : String(error)}`);
      }
    },
    onPreferences: () => {
      setSettingsModalOpen(true);
    },
    onToggleExplorer: () => {
      // 탐색기 패널 토글 (왼쪽 사이드바)
      // 현재는 explorerMode로 제어되므로 모드 전환
      setExplorerMode(explorerMode === 'explorer' ? 'map' : 'explorer');
    },
    onToggleProperties: () => {
      // 속성 패널 토글 (오른쪽 사이드바)
      // 현재는 선택된 항목이 있으면 표시되므로 선택 해제/재선택
      if (selectedPin || selectedEntityId) {
        setSelectedPin(null);
        setSelectedEntityId(null);
        setSelectedEntityType(undefined);
      } else {
        // 선택된 항목이 없으면 첫 번째 핀 선택
        if (pins.length > 0) {
          setSelectedPin(pins[0].pin_id);
        }
      }
    },
    onToggleConsole: () => {
      // 콘솔 패널은 현재 구현되지 않음
      alert('콘솔 패널은 추후 구현 예정입니다.');
    },
    onViewMode: (mode) => {
      if (mode === 'map') {
        setExplorerMode('map');
      } else {
        setExplorerMode('explorer');
      }
    },
    onZoom: (action) => {
      if (action === 'in') {
        handleZoomIn();
      } else if (action === 'out') {
        handleZoomOut();
      } else if (action === 'fit') {
        // 맵에 맞춤
        if (mapState) {
          const canvasWidth = window.innerWidth - 600;
          const canvasHeight = window.innerHeight - 100;
          const scaleX = canvasWidth / mapState.width;
          const scaleY = canvasHeight / mapState.height;
          const newZoom = Math.min(scaleX, scaleY, 3) * 0.9; // 약간 여백
          updateMap({ zoom_level: Math.max(0.5, newZoom) });
          setStatusMessage('맵에 맞춤');
          setTimeout(() => setStatusMessage(''), 2000);
        }
      } else if (action === 'selection') {
        // 선택된 핀에 맞춤
        if (selectedPin && mapState) {
          const pin = pins.find(p => p.pin_id === selectedPin);
          if (pin) {
            const newZoom = Math.min(2, (mapState.zoom_level || 1.0) * 1.5);
            updateMap({ zoom_level: newZoom });
            setStatusMessage('선택된 핀에 맞춤');
            setTimeout(() => setStatusMessage(''), 2000);
          }
        } else {
          alert('줌할 대상을 선택하세요.');
        }
      }
    },
    onGridToggle: () => {
      if (mapState) {
        updateMap({ grid_enabled: !mapState.grid_enabled });
      }
    },
    onFullscreen: () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
      } else {
        document.exitFullscreen();
      }
    },
    onEntityProperties: () => {
      if (selectedEntityType && selectedEntityId) {
        // 이미 편집기가 열려있음
      } else if (selectedPin) {
        // 핀 편집기 열기
      }
    },
    onDocumentation: () => {
      window.open('https://docs.example.com', '_blank');
    },
  });

  // FPS 모니터링
  useEffect(() => {
    let lastTime = performance.now();
    let frameCount = 0;
    let fpsValue = 0;

    const measureFPS = () => {
      frameCount++;
      const currentTime = performance.now();
      const delta = currentTime - lastTime;

      if (delta >= 1000) {
        fpsValue = Math.round((frameCount * 1000) / delta);
        setFps(fpsValue);
        frameCount = 0;
        lastTime = currentTime;
      }

      requestAnimationFrame(measureFPS);
    };

    if (settings.debugMode) {
      measureFPS();
    } else {
      setFps(undefined);
    }
  }, [settings.debugMode]);

  // 핀 클릭 핸들러 (선택만)
  const handlePinClick = (pinId: string) => {
    if (currentTool === 'road') {
      handlePinClickForRoad(pinId);
    } else {
      setSelectedPin(pinId);
      setSelectedRoad(null);
    }
  };

  // 핀 더블 클릭 핸들러 (하위 레벨로 이동)
  const handlePinDoubleClick = (pinId: string) => {
    const pin = pins.find(p => p.pin_id === pinId);
    if (!pin) return;

    // Region 핀 더블 클릭 시 Region Map으로 이동
    if (pin.pin_type === 'region' && mapViewMode === 'world') {
      setMapViewMode('hierarchical');
      setCurrentMapLevel('region');
      setCurrentMapEntityId(pin.game_data_id);
    }
  };

  // 핀 드래그 핸들러
  const handlePinDrag = async (pinId: string, x: number, y: number) => {
    const oldPin = pins.find(p => p.pin_id === pinId);
    if (!oldPin) return;
    
    // 좌표 유효성 검사
    if (x < 0 || y < 0 || !isFinite(x) || !isFinite(y)) {
      console.warn('유효하지 않은 좌표:', { x, y });
      return;
    }
    
    const oldX = oldPin.x;
    const oldY = oldPin.y;
    
    try {
      await updatePin(pinId, { x, y });
      
      // Undo/Redo 히스토리에 추가
      addAction({
        type: 'pin_move',
        description: `핀 이동: ${pinId}`,
        undo: async () => {
          await updatePin(pinId, { x: oldX, y: oldY });
        },
        redo: async () => {
          await updatePin(pinId, { x, y });
        },
        timestamp: Date.now(),
      });
      
      sendMessage({
        type: 'pin_update',
        data: { pin_id: pinId, x, y },
      });
    } catch (error) {
      console.error('핀 드래그 실패:', error);
      // 에러 발생 시 원래 위치로 복원
      await updatePin(pinId, { x: oldX, y: oldY });
    }
  };

  // 도로 클릭 핸들러
  const handleRoadClick = (roadId: string) => {
    setSelectedRoad(roadId);
    setSelectedPin(null);
  };

  // 핀 클릭 핸들러 (도로 그리기 모드일 때)
  const handlePinClickForRoad = async (pinId: string) => {
    if (currentTool === 'road') {
      if (!roadDrawingState.fromPinId) {
        // 첫 번째 핀 선택
        setRoadDrawingState({ fromPinId: pinId, drawing: true });
        setSelectedPin(pinId);
      } else {
        // 두 번째 핀 선택 - 도로 생성
        try {
          const fromPin = pins.find(p => p.pin_id === roadDrawingState.fromPinId);
          const toPin = pins.find(p => p.pin_id === pinId);
          
          if (!fromPin || !toPin) {
            alert('핀을 찾을 수 없습니다.');
            setRoadDrawingState({ fromPinId: null, drawing: false });
            return;
          }

          // 도로 데이터 생성
          const roadData: any = {
            road_type: 'normal',
            from_pin_id: fromPin.pin_id,
            to_pin_id: toPin.pin_id,
            path_coordinates: [
              { x: fromPin.x, y: fromPin.y },
              { x: toPin.x, y: toPin.y },
            ],
            danger_level: 0,
            color: '#8B4513',
            width: 2,
            dashed: false,
            road_properties: {},
          };

          // 핀 타입에 따라 from/to 설정 (선택적)
          if (fromPin.pin_type === 'region') {
            roadData.from_region_id = fromPin.game_data_id;
          } else if (fromPin.pin_type === 'location') {
            roadData.from_location_id = fromPin.game_data_id;
          }

          if (toPin.pin_type === 'region') {
            roadData.to_region_id = toPin.game_data_id;
          } else if (toPin.pin_type === 'location') {
            roadData.to_location_id = toPin.game_data_id;
          }

          const newRoad = await addRoad(roadData);
          
          // WebSocket으로 다른 클라이언트에 알림
          sendMessage({
            type: 'road_update',
            data: { road_id: newRoad.road_id },
          });
          
          setSelectedRoad(newRoad.road_id);
          setRoadDrawingState({ fromPinId: null, drawing: false });
        } catch (error) {
          console.error('도로 추가 실패:', error);
          alert('도로 추가에 실패했습니다.');
          setRoadDrawingState({ fromPinId: null, drawing: false });
        }
      }
    } else {
      // 일반 모드에서는 기존 핸들러 사용
      handlePinClick(pinId);
    }
  };

  // 줌 핸들러
  const handleZoomIn = () => {
    if (mapState) {
      const newZoom = Math.min(3, mapState.zoom_level + 0.1);
      updateMap({ zoom_level: newZoom });
    }
  };

  const handleZoomOut = () => {
    if (mapState) {
      const newZoom = Math.max(0.5, mapState.zoom_level - 0.1);
      updateMap({ zoom_level: newZoom });
    }
  };

  // 그리드 토글
  const handleGridToggle = () => {
    if (mapState) {
      updateMap({ grid_enabled: !mapState.grid_enabled });
    }
  };

  // 맵 클릭 핸들러 (핀 추가)
  const handleMapClick = async (x: number, y: number) => {
    console.log('handleMapClick 호출:', { x, y, currentTool });
    
    if (currentTool === 'pin') {
      try {
        // 좌표를 정수로 변환
        const pinX = Math.round(x);
        const pinY = Math.round(y);
        
        console.log('핀 추가 시작:', { pinX, pinY });
        
        // 기본 핀 이름 생성 (새 핀 01, 새 핀 02 형식)
        const existingPinNames = pins.map(p => p.pin_name || '').filter(name => name.startsWith('새 핀 '));
        const pinNumbers = existingPinNames
          .map(name => {
            const match = name.match(/새 핀 (\d+)/);
            return match ? parseInt(match[1]) : 0;
          })
          .filter(num => num > 0);
        const nextPinNumber = pinNumbers.length > 0 ? Math.max(...pinNumbers) + 1 : 1;
        const defaultPinName = `새 핀 ${String(nextPinNumber).padStart(2, '0')}`;
        
        // 기본 핀 데이터 생성
        const pinData = {
          x: Number(pinX), // float로 명시적 변환
          y: Number(pinY), // float로 명시적 변환
          pin_name: defaultPinName,
          pin_type: 'region' as const, // 기본값, 나중에 선택 가능하도록 수정 가능
          game_data_id: `PIN_${Date.now()}`, // 임시 ID
          color: '#FF6B9D',
          icon_type: 'default',
          size: Number(10), // int로 명시적 변환
        };
        
        console.log('핀 데이터:', pinData);
        
        const newPin = await addPin(pinData);
        
        // Undo/Redo 히스토리에 추가
        addAction({
          type: 'pin_create',
          description: `핀 추가: ${newPin.pin_id}`,
          undo: async () => {
            await deletePin(newPin.pin_id);
          },
          redo: async () => {
            await addPin(pinData);
          },
          timestamp: Date.now(),
        });
        
        console.log('핀 추가 성공:', newPin);
        
        // WebSocket으로 다른 클라이언트에 알림
        if (sendMessage) {
          sendMessage({
            type: 'pin_update',
            data: { pin_id: newPin.pin_id, x: pinX, y: pinY },
          });
        }
        
        // 새로 추가된 핀 선택
        setSelectedPin(newPin.pin_id);
        
        // 선택 모드로 전환
        setCurrentTool('select');
      } catch (error) {
        console.error('핀 추가 실패:', error);
        if (error instanceof Error) {
          console.error('에러 상세:', error.message, error.stack);
        }
        alert(`핀 추가에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
      }
    } else {
      console.log('핀 추가 모드가 아님:', currentTool);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100vh',
        gap: '16px'
      }}>
        <div style={{ fontSize: '18px', fontWeight: 'bold' }}>로딩 중...</div>
        <div style={{ fontSize: '12px', color: '#666' }}>
          백엔드 서버에 연결하는 중입니다.
        </div>
        <div style={{ fontSize: '11px', color: '#999' }}>
          서버가 시작되지 않았다면: <code>python app/world_editor/run_server.py</code>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <MenuBar
        currentTool={currentTool === 'pan' || currentTool === 'zoom' ? 'select' : currentTool}
        onToolChange={(tool) => {
          setCurrentTool(tool);
          if (tool !== 'road') {
            setRoadDrawingState({ fromPinId: null, drawing: false });
          }
        }}
        gridEnabled={mapState?.grid_enabled || false}
        onNewProject={() => {
          alert('현재 시스템은 데이터베이스를 직접 사용합니다. "새 프로젝트" 기능은 지원하지 않습니다.');
        }}
        onOpenProject={restoreBackup}
        onSaveProject={async () => {
          await saveBackup();
        }}
        onSaveProjectAs={async () => {
          const filename = prompt('백업 파일 이름을 입력하세요:', `world_backup_${new Date().toISOString().split('T')[0]}.json`);
          if (filename) {
            await saveBackup(filename);
          }
        }}
        onImport={async (type) => {
          const input = document.createElement('input');
          input.type = 'file';
          input.accept = type === 'map' ? 'image/*' : type === 'entities' ? 'application/json' : 'text/csv';
          input.onchange = async (e) => {
            const file = (e.target as HTMLInputElement).files?.[0];
            if (!file) return;
            
            try {
              setStatus('loading');
              setStatusMessage('가져오는 중...');
              
              if (type === 'map') {
                const reader = new FileReader();
                reader.onload = async (event) => {
                  const imageData = event.target?.result as string;
                  try {
                    // Base64 이미지를 서버에 업로드하는 대신, 로컬에서 처리
                    // 실제로는 서버 API를 통해 업로드해야 함
                    if (mapState) {
                      // 맵 메타데이터에 이미지 경로 업데이트 (임시)
                      await updateMap({ background_image: imageData });
                      setStatus('ready');
                      setStatusMessage('지도 이미지가 가져와졌습니다.');
                      setTimeout(() => setStatusMessage(''), 2000);
                    }
                  } catch (error) {
                    setStatus('error');
                    setStatusMessage('이미지 가져오기 실패');
                    alert(`이미지 가져오기 실패: ${error instanceof Error ? error.message : String(error)}`);
                  }
                };
                reader.readAsDataURL(file);
              } else if (type === 'entities') {
                const text = await file.text();
                const data = JSON.parse(text);
                try {
                  // 엔티티 배열인지 확인
                  const entities = Array.isArray(data) ? data : [data];
                  
                  // 백엔드 API 호출
                  const response = await projectApi.importEntities(entities);
                  const stats = response.data.stats;
                  
                  await refreshData();
                  setStatus('ready');
                  setStatusMessage(`${stats.entities}개의 엔티티가 가져와졌습니다.`);
                  setTimeout(() => setStatusMessage(''), 2000);
                } catch (error) {
                  setStatus('error');
                  setStatusMessage('엔티티 가져오기 실패');
                  alert(`엔티티 가져오기 실패: ${error instanceof Error ? error.message : String(error)}`);
                }
              } else if (type === 'regions') {
                const text = await file.text();
                try {
                  // CSV 또는 JSON 파싱
                  let regions: any[];
                  if (file.name.endsWith('.csv')) {
                    // CSV 파싱 (간단한 구현)
                    const lines = text.split('\n').filter(line => line.trim());
                    const headers = lines[0].split(',').map(h => h.trim());
                    regions = lines.slice(1).map(line => {
                      const values = line.split(',').map(v => v.trim());
                      const region: any = {};
                      headers.forEach((header, index) => {
                        region[header] = values[index] || '';
                      });
                      return region;
                    });
                  } else {
                    // JSON 파싱
                    const parsed = JSON.parse(text);
                    regions = Array.isArray(parsed) ? parsed : [parsed];
                  }
                  
                  // 백엔드 API 호출
                  const response = await projectApi.importRegions(regions);
                  const stats = response.data.stats;
                  
                  await refreshData();
                  setStatus('ready');
                  setStatusMessage(`${stats.regions}개의 지역이 가져와졌습니다.`);
                  setTimeout(() => setStatusMessage(''), 2000);
                } catch (error) {
                  setStatus('error');
                  setStatusMessage('지역 가져오기 실패');
                  alert(`지역 가져오기 실패: ${error instanceof Error ? error.message : String(error)}`);
                }
              }
            } catch (error) {
              setStatus('error');
              setStatusMessage('가져오기 실패');
              alert(`가져오기 실패: ${error instanceof Error ? error.message : String(error)}`);
            }
          };
          input.click();
        }}
        onExport={async (type) => {
          try {
            setStatus('saving');
            setStatusMessage('내보내는 중...');
            
            if (type === 'map') {
              // 지도 이미지 내보내기 (Canvas를 이미지로 변환)
              // MapCanvas의 Stage를 이미지로 변환하는 기능이 필요하지만,
              // 현재는 맵 메타데이터만 내보내기
              if (mapState) {
                const mapData = JSON.stringify(mapState, null, 2);
                const blob = new Blob([mapData], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `map_metadata_${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                URL.revokeObjectURL(url);
                setStatusMessage('맵 메타데이터가 내보내졌습니다.');
                setTimeout(() => setStatusMessage(''), 2000);
              } else {
                alert('내보낼 맵이 없습니다.');
              }
            } else if (type === 'entities') {
              // 엔티티는 셀별로 가져오기
              const entities: any[] = [];
              for (const cell of cells) {
                try {
                  const cellEntities = await entitiesApi.getByCell(cell.cell_id);
                  entities.push(...cellEntities.data);
                } catch (e) {
                  // 무시
                }
              }
              const data = JSON.stringify(entities, null, 2);
              const blob = new Blob([data], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `entities_${new Date().toISOString().split('T')[0]}.json`;
              a.click();
              URL.revokeObjectURL(url);
            } else if (type === 'regions') {
              const response = await regionsApi.getAll();
              const data = JSON.stringify(response.data, null, 2);
              const blob = new Blob([data], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `regions_${new Date().toISOString().split('T')[0]}.json`;
              a.click();
              URL.revokeObjectURL(url);
            } else if (type === 'full') {
              // 전체 데이터 내보내기
              // entitiesApi에는 getAll이 없으므로 다른 방법 사용
              const [regionsRes, locationsRes, cellsRes, worldObjectsRes, effectCarriersRes, itemsRes] = await Promise.all([
                regionsApi.getAll(),
                locationsApi.getAll(),
                cellsApi.getAll(),
                worldObjectsApi.getAll(),
                effectCarriersApi.getAll(),
                itemsApi.getAll(),
              ]);
              
              // 엔티티는 셀별로 가져오기 (임시)
              const entities: any[] = [];
              for (const cell of cellsRes.data) {
                try {
                  const cellEntities = await entitiesApi.getByCell(cell.cell_id);
                  entities.push(...cellEntities.data);
                } catch (e) {
                  // 무시
                }
              }
              
              const fullData = {
                regions: regionsRes.data,
                locations: locationsRes.data,
                cells: cellsRes.data,
                entities: entities,
                world_objects: worldObjectsRes.data,
                effect_carriers: effectCarriersRes.data,
                items: itemsRes.data,
                exported_at: new Date().toISOString(),
              };
              
              const data = JSON.stringify(fullData, null, 2);
              const blob = new Blob([data], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `world_data_${new Date().toISOString().split('T')[0]}.json`;
              a.click();
              URL.revokeObjectURL(url);
            }
            
            setStatus('ready');
            setStatusMessage('내보내기 완료');
            setTimeout(() => setStatusMessage(''), 2000);
          } catch (error) {
            setStatus('error');
            setStatusMessage('내보내기 실패');
            alert(`내보내기 실패: ${error instanceof Error ? error.message : String(error)}`);
          }
        }}
        onUndo={undo}
        onRedo={redo}
        canUndo={canUndo}
        canRedo={canRedo}
        canPaste={true}
        hasSelection={!!(selectedPin || selectedEntityId)}
        onCut={async () => {
          if (selectedPin) {
            const pin = pins.find(p => p.pin_id === selectedPin);
            if (pin) {
              await navigator.clipboard.writeText(JSON.stringify({ type: 'pin', data: pin }, null, 2));
              await deletePin(selectedPin);
              setSelectedPin(null);
              setStatusMessage('핀이 잘라내기되었습니다.');
              setTimeout(() => setStatusMessage(''), 2000);
            }
          } else if (selectedEntityId && selectedEntityType) {
            try {
              let entityData: any;
              switch (selectedEntityType) {
                case 'region':
                  const regionRes = await regionsApi.getById(selectedEntityId);
                  entityData = { type: 'region', data: regionRes.data };
                  break;
                case 'location':
                  const locationRes = await locationsApi.getById(selectedEntityId);
                  entityData = { type: 'location', data: locationRes.data };
                  break;
                case 'cell':
                  const cellRes = await cellsApi.getById(selectedEntityId);
                  entityData = { type: 'cell', data: cellRes.data };
                  break;
                case 'entity':
                  const entityRes = await entitiesApi.getById(selectedEntityId);
                  entityData = { type: 'entity', data: entityRes.data };
                  break;
                default:
                  alert('이 엔티티 타입은 잘라내기를 지원하지 않습니다.');
                  return;
              }
              await navigator.clipboard.writeText(JSON.stringify(entityData, null, 2));
              if (confirm('잘라낸 엔티티를 삭제하시겠습니까?')) {
                if (selectedEntityType === 'region') {
                  await regionsApi.delete(selectedEntityId);
                } else if (selectedEntityType === 'location') {
                  await locationsApi.delete(selectedEntityId);
                } else if (selectedEntityType === 'cell') {
                  await cellsApi.delete(selectedEntityId);
                } else {
                  await entitiesApi.delete(selectedEntityId);
                }
                setSelectedEntityId(null);
                setSelectedEntityType(undefined);
                await refreshData();
              }
              setStatusMessage('엔티티가 잘라내기되었습니다.');
              setTimeout(() => setStatusMessage(''), 2000);
            } catch (error) {
              alert(`잘라내기 실패: ${error instanceof Error ? error.message : String(error)}`);
            }
          }
        }}
        onCopy={async () => {
          if (selectedPin) {
            const pin = pins.find(p => p.pin_id === selectedPin);
            if (pin) {
              await navigator.clipboard.writeText(JSON.stringify({ type: 'pin', data: pin }, null, 2));
              setStatusMessage('핀이 클립보드에 복사되었습니다.');
              setTimeout(() => setStatusMessage(''), 2000);
            }
          } else if (selectedEntityId && selectedEntityType) {
            try {
              let entityData: any;
              switch (selectedEntityType) {
                case 'region':
                  const regionRes = await regionsApi.getById(selectedEntityId);
                  entityData = { type: 'region', data: regionRes.data };
                  break;
                case 'location':
                  const locationRes = await locationsApi.getById(selectedEntityId);
                  entityData = { type: 'location', data: locationRes.data };
                  break;
                case 'cell':
                  const cellRes = await cellsApi.getById(selectedEntityId);
                  entityData = { type: 'cell', data: cellRes.data };
                  break;
                case 'entity':
                  const entityRes = await entitiesApi.getById(selectedEntityId);
                  entityData = { type: 'entity', data: entityRes.data };
                  break;
                default:
                  alert('이 엔티티 타입은 복사를 지원하지 않습니다.');
                  return;
              }
              await navigator.clipboard.writeText(JSON.stringify(entityData, null, 2));
              setStatusMessage('엔티티가 클립보드에 복사되었습니다.');
              setTimeout(() => setStatusMessage(''), 2000);
            } catch (error) {
              alert(`복사 실패: ${error instanceof Error ? error.message : String(error)}`);
            }
          }
        }}
        onPaste={async () => {
          try {
            const text = await navigator.clipboard.readText();
            const data = JSON.parse(text);
            
            if (data.type === 'pin' && data.data) {
              const pinData = data.data;
              const newPinData = {
                ...pinData,
                pin_id: `PIN_${Date.now()}`,
                pin_name: `${pinData.pin_name || '새 핀'} (복사)`,
                x: pinData.x + 20,
                y: pinData.y + 20,
              };
              delete (newPinData as any).created_at;
              delete (newPinData as any).updated_at;
              await addPin(newPinData);
              setStatusMessage('핀이 붙여넣기되었습니다.');
              setTimeout(() => setStatusMessage(''), 2000);
            } else if (data.type && data.data) {
              // 엔티티 붙여넣기
              const entityData = data.data;
              try {
                if (data.type === 'region') {
                  entityData.region_id = `REG_${Date.now()}`;
                  entityData.region_name = `${entityData.region_name} (복사)`;
                  await regionsApi.create(entityData);
                } else if (data.type === 'location') {
                  entityData.location_id = `LOC_${Date.now()}`;
                  entityData.location_name = `${entityData.location_name} (복사)`;
                  await managementApi.createLocation(entityData);
                } else if (data.type === 'cell') {
                  entityData.cell_id = `CELL_${Date.now()}`;
                  entityData.cell_name = `${entityData.cell_name || '셀'} (복사)`;
                  await managementApi.createCell(entityData);
                } else if (data.type === 'entity') {
                  entityData.entity_id = `ENT_${Date.now()}`;
                  entityData.entity_name = `${entityData.entity_name} (복사)`;
                  await entitiesApi.create(entityData);
                }
                await refreshData();
                setStatusMessage('엔티티가 붙여넣기되었습니다.');
                setTimeout(() => setStatusMessage(''), 2000);
              } catch (error) {
                alert(`엔티티 붙여넣기 실패: ${error instanceof Error ? error.message : String(error)}`);
              }
            } else {
              alert('클립보드에 유효한 데이터가 없습니다.');
            }
          } catch (error) {
            alert('붙여넣기 실패: 클립보드 데이터를 읽을 수 없습니다.');
          }
        }}
        onDuplicate={async () => {
          if (selectedPin) {
            const pin = pins.find(p => p.pin_id === selectedPin);
            if (pin) {
              const newPinData = {
                ...pin,
                pin_id: `PIN_${Date.now()}`,
                pin_name: `${pin.pin_name || '새 핀'} (복사)`,
                x: pin.x + 20,
                y: pin.y + 20,
              };
              delete (newPinData as any).created_at;
              delete (newPinData as any).updated_at;
              await addPin(newPinData);
              setStatusMessage('핀이 복제되었습니다.');
              setTimeout(() => setStatusMessage(''), 2000);
            }
          } else if (selectedEntityId && selectedEntityType) {
            try {
              let entityData: any;
              switch (selectedEntityType) {
                case 'region':
                  const regionRes = await regionsApi.getById(selectedEntityId);
                  entityData = regionRes.data;
                  entityData.region_id = `REG_${Date.now()}`;
                  entityData.region_name = `${entityData.region_name} (복사)`;
                  await regionsApi.create(entityData);
                  break;
                case 'location':
                  const locationRes = await locationsApi.getById(selectedEntityId);
                  entityData = locationRes.data;
                  entityData.location_id = `LOC_${Date.now()}`;
                  entityData.location_name = `${entityData.location_name} (복사)`;
                  await managementApi.createLocation(entityData);
                  break;
                case 'cell':
                  const cellRes = await cellsApi.getById(selectedEntityId);
                  entityData = cellRes.data;
                  entityData.cell_id = `CELL_${Date.now()}`;
                  entityData.cell_name = `${entityData.cell_name || '셀'} (복사)`;
                  await managementApi.createCell(entityData);
                  break;
                case 'entity':
                  const entityRes = await entitiesApi.getById(selectedEntityId);
                  entityData = entityRes.data;
                  entityData.entity_id = `ENT_${Date.now()}`;
                  entityData.entity_name = `${entityData.entity_name} (복사)`;
                  await entitiesApi.create(entityData);
                  break;
                default:
                  alert('이 엔티티 타입은 복제를 지원하지 않습니다.');
                  return;
              }
              await refreshData();
              setStatusMessage('엔티티가 복제되었습니다.');
              setTimeout(() => setStatusMessage(''), 2000);
            } catch (error) {
              alert(`복제 실패: ${error instanceof Error ? error.message : String(error)}`);
            }
          }
        }}
        onDelete={async () => {
          if (selectedPin) {
            if (confirm('선택한 핀을 삭제하시겠습니까?')) {
              await deletePin(selectedPin);
            }
          } else if (selectedEntityId) {
            if (confirm('선택한 엔티티를 삭제하시겠습니까?')) {
              try {
                await entitiesApi.delete(selectedEntityId);
                setSelectedEntityId(null);
                await refreshData();
                setStatusMessage('엔티티가 삭제되었습니다.');
              } catch (error) {
                console.error('엔티티 삭제 실패:', error);
                alert(`엔티티 삭제에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
              }
            }
          }
        }}
        onSelectAll={() => {
          // 모든 핀 선택 (다중 선택)
          if (pins.length > 0) {
            const allPinIds = new Set(pins.map(p => p.pin_id));
            setSelectedPins(allPinIds);
            setSelectedPin(pins[0].pin_id);
            setStatusMessage(`${pins.length}개의 핀이 선택되었습니다.`);
            setTimeout(() => setStatusMessage(''), 2000);
          }
        }}
        onDeselectAll={() => {
          setSelectedPin(null);
          setSelectedRoad(null);
          setSelectedEntityType(undefined);
          setSelectedEntityId(null);
          setSelectedPins(new Set());
        }}
        onFind={async () => {
          const query = prompt('검색할 키워드를 입력하세요:');
          if (query) {
            try {
              setStatus('loading');
              setStatusMessage('검색 중...');
              const response = await searchApi.search(query);
              setSearchResults(response.data.results || []);
              setSearchResultsModalOpen(true);
              setStatus('ready');
              setStatusMessage('');
            } catch (error) {
              setStatus('error');
              setStatusMessage('검색 실패');
              alert(`검색 실패: ${error instanceof Error ? error.message : String(error)}`);
            }
          }
        }}
        onFindInFiles={async () => {
          const query = prompt('파일에서 검색할 키워드를 입력하세요:');
          if (query) {
            try {
              setStatus('loading');
              setStatusMessage('검색 중...');
              const response = await searchApi.search(query);
              setSearchResults(response.data.results || []);
              setSearchResultsModalOpen(true);
              setStatus('ready');
              setStatusMessage('');
            } catch (error) {
              setStatus('error');
              setStatusMessage('검색 실패');
              alert(`검색 실패: ${error instanceof Error ? error.message : String(error)}`);
            }
          }
        }}
        onReplace={async () => {
          const findQuery = prompt('찾을 텍스트를 입력하세요:');
          if (!findQuery) return;
          
          const replaceQuery = prompt('바꿀 텍스트를 입력하세요:');
          if (replaceQuery === null) return;
          
          try {
            const response = await searchApi.search(findQuery);
            const results = response.data.results || [];
            
            if (results.length === 0) {
              alert('찾을 텍스트가 없습니다.');
              return;
            }
            
            if (!confirm(`${results.length}개의 결과를 찾았습니다. 모두 바꾸시겠습니까?`)) {
              return;
            }
            
            setStatus('saving');
            setStatusMessage('바꾸는 중...');
            
            let successCount = 0;
            for (const result of results) {
              try {
                if (result.entity_type === 'region') {
                  const regionRes = await regionsApi.getById(result.entity_id);
                  const updated = {
                    ...regionRes.data,
                    region_name: regionRes.data.region_name?.replace(new RegExp(findQuery, 'gi'), replaceQuery),
                    region_description: regionRes.data.region_description?.replace(new RegExp(findQuery, 'gi'), replaceQuery),
                  };
                  await regionsApi.update(result.entity_id, updated);
                } else if (result.entity_type === 'location') {
                  const locationRes = await locationsApi.getById(result.entity_id);
                  const updated = {
                    ...locationRes.data,
                    location_name: locationRes.data.location_name?.replace(new RegExp(findQuery, 'gi'), replaceQuery),
                    location_description: locationRes.data.location_description?.replace(new RegExp(findQuery, 'gi'), replaceQuery),
                  };
                  await locationsApi.update(result.entity_id, updated);
                } else if (result.entity_type === 'entity') {
                  const entityRes = await entitiesApi.getById(result.entity_id);
                  const updated = {
                    ...entityRes.data,
                    entity_name: entityRes.data.entity_name?.replace(new RegExp(findQuery, 'gi'), replaceQuery),
                    entity_description: entityRes.data.entity_description?.replace(new RegExp(findQuery, 'gi'), replaceQuery),
                  };
                  await entitiesApi.update(result.entity_id, updated);
                }
                successCount++;
              } catch (error) {
                console.error(`바꾸기 실패 (${result.entity_id}):`, error);
              }
            }
            
            await refreshData();
            setStatus('ready');
            setStatusMessage(`${successCount}개의 항목이 바뀌었습니다.`);
            setTimeout(() => setStatusMessage(''), 3000);
          } catch (error) {
            setStatus('error');
            setStatusMessage('바꾸기 실패');
            alert(`바꾸기 실패: ${error instanceof Error ? error.message : String(error)}`);
          }
        }}
        onPreferences={() => setSettingsModalOpen(true)}
        onKnowledgeManager={() => setKnowledgeManagerOpen(true)}
        onTogglePanel={(panel) => {
          if (panel === 'explorer') {
            setExplorerMode(explorerMode === 'explorer' ? 'map' : 'explorer');
          } else if (panel === 'properties') {
            if (selectedPin || selectedEntityId) {
              setSelectedPin(null);
              setSelectedEntityId(null);
              setSelectedEntityType(undefined);
            } else {
              if (pins.length > 0) {
                setSelectedPin(pins[0].pin_id);
              }
            }
          }
        }}
        onViewMode={(mode) => {
          if (mode === 'map') {
            setExplorerMode('map');
          } else {
            setExplorerMode('explorer');
          }
        }}
        onZoom={(action) => {
          if (action === 'in') handleZoomIn();
          else if (action === 'out') handleZoomOut();
          else if (action === 'fit') {
            // 맵에 맞춤
            if (mapState) {
              const canvasWidth = window.innerWidth - 600;
              const canvasHeight = window.innerHeight - 100;
              const scaleX = canvasWidth / mapState.width;
              const scaleY = canvasHeight / mapState.height;
              const newZoom = Math.min(scaleX, scaleY, 3) * 0.9; // 약간 여백
              updateMap({ zoom_level: Math.max(0.5, newZoom) });
            }
          } else if (action === 'selection') {
            // 선택된 핀에 맞춤
            if (selectedPin && mapState) {
              const pin = pins.find(p => p.pin_id === selectedPin);
              if (pin) {
                // 선택된 핀 중심으로 줌
                const newZoom = Math.min(2, mapState.zoom_level * 1.5);
                updateMap({ zoom_level: newZoom });
                setStatusMessage('선택된 핀에 맞춤');
                setTimeout(() => setStatusMessage(''), 2000);
              }
            } else {
              alert('줌할 대상을 선택하세요.');
            }
          }
        }}
        onGridToggle={handleGridToggle}
        onGridSettings={() => {
          const size = prompt('그리드 크기를 입력하세요 (기본값: 50):', String(mapState?.grid_size || 50));
          if (size) {
            const gridSize = parseInt(size, 10);
            if (!isNaN(gridSize) && gridSize > 0) {
              updateMap({ grid_size: gridSize });
              setStatusMessage(`그리드 크기가 ${gridSize}로 설정되었습니다.`);
              setTimeout(() => setStatusMessage(''), 2000);
            }
          }
        }}
        onFullscreen={() => {
          if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
          } else {
            document.exitFullscreen();
          }
        }}
        onNewEntity={async (type) => {
          if (type === 'region') {
            const name = prompt('지역 이름을 입력하세요:');
            if (name) {
              try {
                await regionsApi.create({
                  region_id: `REG_${name.toUpperCase().replace(/\s+/g, '_')}_${Date.now()}`,
                  region_name: name,
                  region_type: 'continent',
                  region_description: '',
                  region_properties: {},
                });
                await refreshData();
                alert('지역이 생성되었습니다.');
              } catch (error) {
                alert(`지역 생성 실패: ${error instanceof Error ? error.message : String(error)}`);
              }
            }
          } else if (type === 'location') {
            const name = prompt('위치 이름을 입력하세요:');
            if (name) {
              const regionId = prompt('지역 ID를 입력하세요 (선택사항):');
              if (regionId) {
                try {
                  await managementApi.createLocation({
                    region_id: regionId,
                    location_name: name,
                    location_type: 'town',
                    location_description: '',
                  });
                  await refreshData();
                  alert('위치가 생성되었습니다.');
                } catch (error) {
                  alert(`위치 생성 실패: ${error instanceof Error ? error.message : String(error)}`);
                }
              }
            }
          } else if (type === 'cell') {
            const name = prompt('셀 이름을 입력하세요:');
            if (name) {
              const locationId = prompt('위치 ID를 입력하세요:');
              if (locationId) {
                try {
                  await managementApi.createCell({
                    location_id: locationId,
                    cell_name: name,
                    cell_description: '',
                  });
                  await refreshData();
                  alert('셀이 생성되었습니다.');
                } catch (error) {
                  alert(`셀 생성 실패: ${error instanceof Error ? error.message : String(error)}`);
                }
              }
            }
          } else if (type === 'entity') {
            const name = prompt('인물 이름을 입력하세요:');
            if (name) {
              const cellId = prompt('셀 ID를 입력하세요:');
              if (cellId) {
                try {
                  await managementApi.createEntity({
                    cell_id: cellId,
                    entity_name: name,
                    entity_type: 'npc',
                    entity_description: '',
                  });
                  await refreshData();
                  alert('인물이 생성되었습니다.');
                } catch (error) {
                  alert(`인물 생성 실패: ${error instanceof Error ? error.message : String(error)}`);
                }
              }
            }
          } else {
            alert(`${type} 생성 기능은 추후 구현 예정입니다.`);
          }
        }}
        onEntityProperties={() => {
          if (selectedEntityType && selectedEntityId) {
            // 이미 편집기가 열려있음
          }
        }}
        onEntityRelationships={async () => {
          if (selectedEntityType && selectedEntityId) {
            try {
              const response = await relationshipsApi.getRelationships(selectedEntityType, selectedEntityId);
              alert(`관계 정보:\n${JSON.stringify(response.data, null, 2)}`);
            } catch (error) {
              alert(`관계 조회 실패: ${error instanceof Error ? error.message : String(error)}`);
            }
          } else {
            alert('엔티티를 선택하세요.');
          }
        }}
        onBatchOperations={(op) => {
          alert(`일괄 작업 (${op}) 기능은 추후 구현 예정입니다.`);
        }}
        onValidate={async (type) => {
          try {
            setStatus('loading');
            setStatusMessage('검증 중...');
            
            if (type === 'all') {
              // 백엔드 API 호출
              const response = await projectApi.validateAll();
              const issues = response.data.issues;
              const totalIssues = response.data.total_issues;
              
              const allIssues: string[] = [];
              for (const [category, issueList] of Object.entries(issues)) {
                if (Array.isArray(issueList)) {
                  allIssues.push(...issueList.map(String));
                }
              }

              if (totalIssues === 0) {
                alert('검증 완료: 문제가 없습니다.');
              } else {
                alert(`검증 완료: ${totalIssues}개의 문제를 발견했습니다.\n\n${allIssues.slice(0, 10).join('\n')}${allIssues.length > 10 ? `\n... 외 ${allIssues.length - 10}개` : ''}`);
              }
            } else if (type === 'orphans') {
              // 백엔드 API 호출
              const response = await projectApi.validateOrphans();
              const orphans = response.data.orphans;
              
              if (orphans.length === 0) {
                alert('고아 엔티티가 없습니다.');
              } else {
                alert(`고아 엔티티 ${orphans.length}개 발견:\n\n${orphans.slice(0, 10).join('\n')}${orphans.length > 10 ? `\n... 외 ${orphans.length - 10}개` : ''}`);
              }
            } else if (type === 'duplicates') {
              // 백엔드 API 호출
              const response = await projectApi.validateDuplicates();
              const duplicates = response.data.duplicates;
              
              if (duplicates.length === 0) {
                alert('중복된 이름이 없습니다.');
              } else {
                alert(`중복 발견: ${duplicates.length}개\n\n${duplicates.slice(0, 10).join('\n')}${duplicates.length > 10 ? `\n... 외 ${duplicates.length - 10}개` : ''}`);
              }
            }
            
            setStatus('ready');
            setStatusMessage('');
          } catch (error) {
            setStatus('error');
            setStatusMessage('검증 실패');
            alert(`검증 실패: ${error instanceof Error ? error.message : String(error)}`);
          }
        }}
        onLayout={(layout) => {
          // 레이아웃 변경 (현재는 기본 레이아웃만 지원)
          alert(`레이아웃 "${layout}" 변경 기능은 추후 구현 예정입니다.`);
        }}
        onDocumentation={() => window.open('https://docs.example.com', '_blank')}
        onKeyboardShortcuts={() => setKeyboardShortcutsModalOpen(true)}
        onAbout={() => setAboutModalOpen(true)}
      />
      {currentTool === 'road' && roadDrawingState.drawing && (
        <div style={{
          padding: '10px',
          backgroundColor: '#fff3cd',
          borderBottom: '1px solid #ffc107',
          textAlign: 'center',
        }}>
          도로 그리기 모드: 첫 번째 핀을 선택했습니다. 두 번째 핀을 선택하세요.
        </div>
      )}
      <div style={{ display: 'flex', flex: 1, minHeight: 0, overflow: 'hidden' }}>
        {/* 왼쪽 사이드바: 탐색기 또는 핀 트리뷰 */}
        <div style={{ width: '250px', backgroundColor: '#f5f5f5', borderRight: '1px solid #ddd', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ 
            display: 'flex', 
            borderBottom: '1px solid #ddd',
            backgroundColor: '#fff',
          }}>
            <button
              onClick={() => setExplorerMode('map')}
              style={{
                flex: 1,
                padding: '8px',
                border: 'none',
                borderRight: '1px solid #ddd',
                backgroundColor: explorerMode === 'map' ? '#e3f2fd' : '#fff',
                cursor: 'pointer',
                fontSize: '12px',
              }}
            >
              지도
            </button>
            <button
              onClick={() => setExplorerMode('explorer')}
              style={{
                flex: 1,
                padding: '8px',
                border: 'none',
                backgroundColor: explorerMode === 'explorer' ? '#e3f2fd' : '#fff',
                cursor: 'pointer',
                fontSize: '12px',
              }}
            >
              탐색기
            </button>
          </div>
          {explorerMode === 'explorer' ? (
            <EntityExplorer
              onEntitySelect={(entityType, entityId) => {
                setSelectedEntityType(entityType);
                setSelectedEntityId(entityId);
                setSelectedPin(null);
                setSelectedRoad(null);
              }}
              onAddPinToMap={async (entityType, entityId, entityName) => {
                // 맵 중앙에 핀 추가
                if (!mapState) return;
                
                const centerX = (mapState.width || 1000) / 2;
                const centerY = (mapState.height || 1000) / 2;
                
                try {
                  // 핀 타입 결정
                  const pinType: 'region' | 'location' | 'cell' = entityType === 'region' ? 'region' : 
                                 entityType === 'location' ? 'location' : 'cell';
                  
                  // 핀 데이터 생성
                  const pinData = {
                    x: Number(centerX),
                    y: Number(centerY),
                    pin_name: entityName,
                    pin_type: pinType,
                    game_data_id: entityId,
                    color: entityType === 'region' ? '#FF6B9D' : 
                           entityType === 'location' ? '#4A90E2' : '#50C878',
                    icon_type: 'default',
                    size: Number(10),
                  };
                  
                  const newPin = await addPin(pinData);
                  
                  // Undo/Redo 히스토리에 추가
                  addAction({
                    type: 'pin_create',
                    description: `핀 추가: ${newPin.pin_id}`,
                    undo: async () => {
                      await deletePin(newPin.pin_id);
                    },
                    redo: async () => {
                      await addPin(pinData);
                    },
                    timestamp: Date.now(),
                  });
                  
                  // 새로 추가된 핀 선택
                  setSelectedPin(newPin.pin_id);
                  
                  // WebSocket으로 다른 클라이언트에 알림
                  if (sendMessage) {
                    sendMessage({
                      type: 'pin_update',
                      data: { pin_id: newPin.pin_id, x: centerX, y: centerY },
                    });
                  }
                  
                  setStatusMessage(`${entityName} 핀이 맵에 추가되었습니다.`);
                  setTimeout(() => setStatusMessage(''), 2000);
                } catch (error) {
                  console.error('핀 추가 실패:', error);
                  alert(`핀 추가에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
                }
              }}
              selectedEntityType={selectedEntityType}
              selectedEntityId={selectedEntityId}
              searchQuery={searchQuery}
              onSearchQueryChange={setSearchQuery}
            />
          ) : (
            <PinTreeView
              pins={pins}
              selectedPin={selectedPin}
              onPinSelect={(pinId) => {
                setSelectedPin(pinId);
                setSelectedRoad(null);
                setCurrentTool('select');
              }}
              onPinDelete={async (pinId) => {
                try {
                  await deletePin(pinId);
                  if (selectedPin === pinId) {
                    setSelectedPin(null);
                  }
                } catch (error) {
                  console.error('핀 삭제 실패:', error);
                  alert(`핀 삭제에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
                }
              }}
            />
          )}
        </div>
        
        {/* 중앙: 맵 캔버스 또는 계층적 맵 뷰 */}
        <div style={{ flex: 1, minWidth: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          {/* 현재 뷰 레벨 표시 (World Map일 때만) */}
          {mapViewMode === 'world' && (
            <div style={{
              padding: '8px 15px',
              backgroundColor: '#4A90E2',
              color: '#fff',
              fontSize: '14px',
              fontWeight: 'bold',
              borderBottom: '1px solid #ddd',
            }}>
              World Map
            </div>
          )}
          
          {mapViewMode === 'cell' && selectedCellId ? (
            <CellEntityManager
              cellId={selectedCellId}
              onBack={() => {
                // 이전 Location으로 돌아가기
                if (previousLocationId) {
                  setMapViewMode('hierarchical');
                  setCurrentMapLevel('location');
                  setCurrentMapEntityId(previousLocationId);
                  setSelectedCellId(null);
                  setPreviousLocationId(null);
                } else {
                  // 이전 Location 정보가 없으면 hierarchical 모드로만 돌아가기
                  setMapViewMode('hierarchical');
                  setSelectedCellId(null);
                }
              }}
            />
          ) : mapViewMode === 'hierarchical' && currentMapEntityId ? (
            <HierarchicalMapView
              currentLevel={currentMapLevel}
              currentEntityId={currentMapEntityId}
              onLevelChange={(level, entityId) => {
                if (level === 'world') {
                  setMapViewMode('world');
                  setCurrentMapLevel('world');
                  setCurrentMapEntityId(null);
                } else {
                  setCurrentMapLevel(level);
                  setCurrentMapEntityId(entityId);
                }
              }}
              onEntitySelect={async (entityId, entityType) => {
                if (entityType === 'location') {
                  setCurrentMapLevel('location');
                  setCurrentMapEntityId(entityId);
                } else if (entityType === 'cell') {
                  // Cell로 이동하기 전에 현재 Location ID 저장 (뒤로가기용)
                  if (currentMapLevel === 'location' && currentMapEntityId) {
                    setPreviousLocationId(currentMapEntityId);
                  } else {
                    // currentMapEntityId가 없으면 cell에서 location_id 조회
                    try {
                      const { managementApi } = await import('./services/api');
                      const cellData = await managementApi.getCellWithLocation(entityId);
                      if (cellData?.data?.location?.location_id) {
                        setPreviousLocationId(cellData.data.location.location_id);
                      }
                    } catch (error) {
                      console.error('Cell의 Location 정보 조회 실패:', error);
                    }
                  }
                  setMapViewMode('cell');
                  setSelectedCellId(entityId);
                }
              }}
            />
          ) : (
            <MapCanvas
              mapState={mapState}
              pins={pins}
              roads={roads}
              selectedPin={selectedPin}
              selectedRoad={selectedRoad}
              currentTool={currentTool}
              onPinClick={handlePinClick}
              onPinDoubleClick={handlePinDoubleClick}
              onPinDrag={handlePinDrag}
              onRoadClick={handleRoadClick}
              onMapClick={handleMapClick}
              onMouseMove={(x, y) => setMousePosition({ x: Math.round(x), y: Math.round(y) })}
              currentMapLevel={mapViewMode === 'world' ? 'world' : undefined}
            />
          )}
        </div>
        
        {/* 오른쪽 사이드바: 엔티티 편집기 또는 핀 편집기 */}
        <div style={{ width: '350px', backgroundColor: '#f5f5f5', borderLeft: '1px solid #ddd', display: 'flex', flexDirection: 'column', overflow: 'hidden', minHeight: 0 }}>
          {explorerMode === 'explorer' && selectedEntityType && selectedEntityId ? (
            <EntityEditor
              entityType={selectedEntityType}
              entityId={selectedEntityId}
              onSave={async (entityType, entityId, data) => {
                // 저장 로직은 각 모달에서 처리
                await refreshData();
              }}
              onDelete={async (entityType, entityId) => {
                if (confirm(`정말로 이 ${entityType === 'region' ? '지역' : entityType === 'location' ? '위치' : entityType === 'cell' ? '셀' : '엔티티'}를 삭제하시겠습니까?`)) {
                  try {
                    if (entityType === 'region') {
                      await regionsApi.delete(entityId);
                    } else if (entityType === 'location') {
                      await locationsApi.delete(entityId);
                    } else if (entityType === 'cell') {
                      await cellsApi.delete(entityId);
                    } else {
                      await entitiesApi.delete(entityId);
                    }
                    await refreshData();
                    setStatusMessage(`${entityType === 'region' ? '지역' : entityType === 'location' ? '위치' : entityType === 'cell' ? '셀' : '엔티티'}이(가) 삭제되었습니다.`);
                  } catch (error) {
                    console.error('삭제 실패:', error);
                    alert(`삭제에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
                  }
                }
              }}
              onClose={() => {
                setSelectedEntityType(undefined);
                setSelectedEntityId(null);
              }}
            />
          ) : selectedPin ? (
            <PinEditor
              pin={pins.find(p => p.pin_id === selectedPin) || null}
              regions={regions}
              locations={locations}
              cells={cells}
              onPinUpdate={async (pinId, updates) => {
                await updatePin(pinId, updates);
                sendMessage({
                  type: 'pin_update',
                  data: { pin_id: pinId, ...updates },
                });
              }}
              onPinDelete={async (pinId) => {
                await deletePin(pinId);
                setSelectedPin(null);
              }}
              onClose={() => setSelectedPin(null)}
              onRefresh={async () => {
                await refreshData();
              }}
            />
          ) : (
            <InfoPanel
              selectedPin={null}
              selectedRoad={roads.find(r => r.road_id === selectedRoad) || null}
              regions={regions}
              locations={locations}
              cells={cells}
              onUpdate={(data) => {
                console.log('업데이트:', data);
              }}
            />
          )}
        </div>
      </div>
      <StatusBar
        status={status}
        statusMessage={statusMessage}
        selectedEntityType={selectedEntityType}
        selectedEntityId={selectedEntityId || undefined}
        selectedCount={selectedPin || selectedEntityId ? 1 : 0}
        mouseX={mousePosition?.x}
        mouseY={mousePosition?.y}
        selectedX={selectedPin ? pins.find(p => p.pin_id === selectedPin)?.x : undefined}
        selectedY={selectedPin ? pins.find(p => p.pin_id === selectedPin)?.y : undefined}
        zoomLevel={(mapState?.zoom_level || 1.0) * 100}
        fps={fps}
        websocketConnected={websocketConnected}
        autoSaveEnabled={settings.autoSaveInterval > 0}
        autoSaveStatus={status === 'saving' ? 'saving' : 'saved'}
      />
      <SettingsModal
        isOpen={settingsModalOpen}
        onClose={() => setSettingsModalOpen(false)}
      />
      <DialogueKnowledgeManager
        isOpen={knowledgeManagerOpen}
        onClose={() => setKnowledgeManagerOpen(false)}
      />
      <SearchResultsModal
        isOpen={searchResultsModalOpen}
        onClose={() => setSearchResultsModalOpen(false)}
        results={searchResults}
        onResultClick={(entityType, entityId) => {
          if (entityType === 'region' || entityType === 'location' || entityType === 'cell' || entityType === 'entity') {
            setSelectedEntityType(entityType as EntityType);
            setSelectedEntityId(entityId);
            setExplorerMode('explorer');
          }
        }}
      />
      <KeyboardShortcutsModal
        isOpen={keyboardShortcutsModalOpen}
        onClose={() => setKeyboardShortcutsModalOpen(false)}
      />
      <AboutModal
        isOpen={aboutModalOpen}
        onClose={() => setAboutModalOpen(false)}
      />
    </div>
  );
};

export default App;

