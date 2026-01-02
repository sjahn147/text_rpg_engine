/**
 * 월드 에디터 메인 앱 컴포넌트
 */
import React, { useState, useEffect } from 'react';
import { MenuBar } from '../components/editor/MenuBar';
import { StatusBar } from '../components/editor/StatusBar';
import { SettingsModal } from '../components/editor/SettingsModal';
import { DialogueKnowledgeManager } from '../components/editor/DialogueKnowledgeManager';
import { SearchResultsModal } from '../components/editor/SearchResultsModal';
import { KeyboardShortcutsModal } from '../components/editor/KeyboardShortcutsModal';
import { AboutModal } from '../components/editor/AboutModal';
import { EditorLayout } from '../components/editor/layout/EditorLayout';
import { 
  regionsApi, locationsApi, cellsApi, entitiesApi, 
  worldObjectsApi, effectCarriersApi, itemsApi, searchApi,
  managementApi, relationshipsApi, mapHierarchyApi, mapApi, projectApi
} from '../services/api';
import { useWorldEditor } from '../hooks/useWorldEditor';
import { useWebSocket } from '../hooks/useWebSocket';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';
import { useUndoRedo } from '../hooks/useUndoRedo';
import { useSettings } from '../hooks/useSettings';
import { EditorTool, WebSocketMessage } from '../types';
import { EntityType } from '../components/editor/EntityExplorer';
// 커스텀 훅 import
import { useEditorState } from '../hooks/editor/useEditorState';
import { useMapEditor } from '../hooks/editor/useMapEditor';
import { useRoadDrawing } from '../hooks/editor/useRoadDrawing';
import { useEditorModals } from '../hooks/editor/useEditorModals';
import { useEditorSearch } from '../hooks/editor/useEditorSearch';
import { useEditorBackup } from '../hooks/editor/useEditorBackup';
import { useMapControls } from '../hooks/editor/useMapControls';

export const EditorMode: React.FC = () => {
  const [currentTool, setCurrentTool] = useState<EditorTool>('select');
  const [mousePosition, setMousePosition] = useState<{ x: number; y: number } | null>(null);
  const [fps, setFps] = useState<number | undefined>(undefined);

  // 커스텀 훅으로 상태 관리 추출
  const editorState = useEditorState();
  const mapEditor = useMapEditor();
  const roadDrawing = useRoadDrawing();
  const modals = useEditorModals();
  const search = useEditorSearch();

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

  // WebSocket 메시지 처리
  const handleWebSocketMessage = (message: WebSocketMessage) => {
    if (message.type === 'pin_update') {
      // 핀 업데이트 동기화
    } else if (message.type === 'road_update') {
      // 도로 업데이트 동기화
    } else if (message.type === 'map_update') {
      // 지도 업데이트 동기화
    }
  };

  // WebSocket 연결
  const { sendMessage, connected: websocketConnected } = useWebSocket(handleWebSocketMessage);

  // 백업/복원 훅
  const backup = useEditorBackup(
    (status, message) => {
      editorState.setStatus(status);
      editorState.setStatusMessage(message);
      if (message) {
        setTimeout(() => editorState.setStatusMessage(''), status === 'ready' ? 2000 : 3000);
      }
    },
    refreshData
  );

  // 지도 컨트롤 훅
  const mapControls = useMapControls(
    mapState,
    updateMap,
    selectedPin,
    pins,
    (message) => {
      editorState.setStatusMessage(message);
      setTimeout(() => editorState.setStatusMessage(''), 2000);
    }
  );

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

  // 핀 클릭 핸들러
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
    if (pin.pin_type === 'region' && mapEditor.mapViewMode === 'world') {
      mapEditor.navigateToRegion(pin.game_data_id);
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
      if (!roadDrawing.roadDrawingState.fromPinId) {
        // 첫 번째 핀 선택
        roadDrawing.startDrawing(pinId);
        setSelectedPin(pinId);
      } else {
        // 두 번째 핀 선택 - 도로 생성
        try {
          const fromPin = pins.find(p => p.pin_id === roadDrawing.roadDrawingState.fromPinId);
          const toPin = pins.find(p => p.pin_id === pinId);
          
          if (!fromPin || !toPin) {
            alert('핀을 찾을 수 없습니다.');
            roadDrawing.cancelDrawing();
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

          // 핀 타입에 따라 from/to 설정
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
          
          sendMessage({
            type: 'road_update',
            data: { road_id: newRoad.road_id },
          });
          
          setSelectedRoad(newRoad.road_id);
          roadDrawing.finishDrawing();
        } catch (error) {
          console.error('도로 추가 실패:', error);
          alert('도로 추가에 실패했습니다.');
          roadDrawing.cancelDrawing();
        }
      }
    } else {
      handlePinClick(pinId);
    }
  };

  // 맵 클릭 핸들러 (핀 추가)
  const handleMapClick = async (x: number, y: number) => {
    if (currentTool === 'pin') {
      try {
        const pinX = Math.round(x);
        const pinY = Math.round(y);
        
        // 기본 핀 이름 생성
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
          x: Number(pinX),
          y: Number(pinY),
          pin_name: defaultPinName,
          pin_type: 'region' as const,
          game_data_id: `PIN_${Date.now()}`,
          color: '#FF6B9D',
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
        
        if (sendMessage) {
          sendMessage({
            type: 'pin_update',
            data: { pin_id: newPin.pin_id, x: pinX, y: pinY },
          });
        }
        
        setSelectedPin(newPin.pin_id);
        setCurrentTool('select');
      } catch (error) {
        console.error('핀 추가 실패:', error);
        alert(`핀 추가에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
      }
    }
  };

  // 단축키 시스템
  useKeyboardShortcuts({
    onNewProject: () => {
      alert('현재 시스템은 데이터베이스를 직접 사용합니다. "새 프로젝트" 기능은 지원하지 않습니다.');
    },
    onOpenProject: backup.restoreBackup,
    onSaveProject: async () => {
      await backup.saveBackup();
    },
    onSaveProjectAs: async () => {
      const filename = prompt('백업 파일 이름을 입력하세요:', `world_backup_${new Date().toISOString().split('T')[0]}.json`);
      if (filename) {
        await backup.saveBackup(filename);
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
          editorState.setStatusMessage('핀이 잘라내기되었습니다.');
          setTimeout(() => editorState.setStatusMessage(''), 2000);
        }
      } else if (editorState.selectedEntityId && editorState.selectedEntityType) {
        try {
          let entityData: any;
          switch (editorState.selectedEntityType) {
            case 'region':
              entityData = { type: 'region', data: (await regionsApi.getById(editorState.selectedEntityId)).data };
              break;
            case 'location':
              entityData = { type: 'location', data: (await locationsApi.getById(editorState.selectedEntityId)).data };
              break;
            case 'cell':
              entityData = { type: 'cell', data: (await cellsApi.getById(editorState.selectedEntityId)).data };
              break;
            case 'entity':
              entityData = { type: 'entity', data: (await entitiesApi.getById(editorState.selectedEntityId)).data };
              break;
            default:
              alert('이 엔티티 타입은 잘라내기를 지원하지 않습니다.');
              return;
          }
          await navigator.clipboard.writeText(JSON.stringify(entityData, null, 2));
          if (confirm('잘라낸 엔티티를 삭제하시겠습니까?')) {
            if (editorState.selectedEntityType === 'region') {
              await regionsApi.delete(editorState.selectedEntityId);
            } else if (editorState.selectedEntityType === 'location') {
              await locationsApi.delete(editorState.selectedEntityId);
            } else if (editorState.selectedEntityType === 'cell') {
              await cellsApi.delete(editorState.selectedEntityId);
            } else {
              await entitiesApi.delete(editorState.selectedEntityId);
            }
            editorState.setSelectedEntityId(null);
            editorState.setSelectedEntityType(undefined);
            await refreshData();
          }
          editorState.setStatusMessage('엔티티가 잘라내기되었습니다.');
          setTimeout(() => editorState.setStatusMessage(''), 2000);
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
          editorState.setStatusMessage('핀이 클립보드에 복사되었습니다.');
          setTimeout(() => editorState.setStatusMessage(''), 2000);
        }
      } else if (editorState.selectedEntityId && editorState.selectedEntityType) {
        try {
          let entityData: any;
          switch (editorState.selectedEntityType) {
            case 'region':
              entityData = { type: 'region', data: (await regionsApi.getById(editorState.selectedEntityId)).data };
              break;
            case 'location':
              entityData = { type: 'location', data: (await locationsApi.getById(editorState.selectedEntityId)).data };
              break;
            case 'cell':
              entityData = { type: 'cell', data: (await cellsApi.getById(editorState.selectedEntityId)).data };
              break;
            case 'entity':
              entityData = { type: 'entity', data: (await entitiesApi.getById(editorState.selectedEntityId)).data };
              break;
            default:
              alert('이 엔티티 타입은 복사를 지원하지 않습니다.');
              return;
          }
          await navigator.clipboard.writeText(JSON.stringify(entityData, null, 2));
          editorState.setStatusMessage('엔티티가 클립보드에 복사되었습니다.');
          setTimeout(() => editorState.setStatusMessage(''), 2000);
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
            pin_id: undefined,
            pin_name: `${pinData.pin_name || '새 핀'} (복사)`,
            x: pinData.x + 20,
            y: pinData.y + 20,
          };
          delete (newPinData as any).created_at;
          delete (newPinData as any).updated_at;
          await addPin(newPinData);
          editorState.setStatusMessage('핀이 붙여넣기되었습니다.');
          setTimeout(() => editorState.setStatusMessage(''), 2000);
        } else if (data.type && data.data) {
          const entityData = data.data;
          try {
            if (data.type === 'region') {
              delete entityData.region_id;
              entityData.region_name = `${entityData.region_name} (복사)`;
              await regionsApi.create(entityData);
            } else if (data.type === 'location') {
              delete entityData.location_id;
              entityData.location_name = `${entityData.location_name} (복사)`;
              await managementApi.createLocation(entityData);
            } else if (data.type === 'cell') {
              delete entityData.cell_id;
              entityData.cell_name = `${entityData.cell_name || '셀'} (복사)`;
              await managementApi.createCell(entityData);
            } else if (data.type === 'entity') {
              delete entityData.entity_id;
              entityData.entity_name = `${entityData.entity_name} (복사)`;
              await entitiesApi.create(entityData);
            }
            await refreshData();
            editorState.setStatusMessage('엔티티가 붙여넣기되었습니다.');
            setTimeout(() => editorState.setStatusMessage(''), 2000);
          } catch (error) {
            alert(`엔티티 붙여넣기 실패: ${error instanceof Error ? error.message : String(error)}`);
          }
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
            pin_id: undefined,
            pin_name: `${pin.pin_name || '새 핀'} (복사)`,
            x: pin.x + 20,
            y: pin.y + 20,
          };
          delete (newPinData as any).created_at;
          delete (newPinData as any).updated_at;
          await addPin(newPinData);
          editorState.setStatusMessage('핀이 복제되었습니다.');
          setTimeout(() => editorState.setStatusMessage(''), 2000);
        }
      } else if (editorState.selectedEntityId && editorState.selectedEntityType) {
        try {
          let entityData: any;
          switch (editorState.selectedEntityType) {
            case 'region':
              entityData = (await regionsApi.getById(editorState.selectedEntityId)).data;
              delete entityData.region_id;
              entityData.region_name = `${entityData.region_name} (복사)`;
              await regionsApi.create(entityData);
              break;
            case 'location':
              entityData = (await locationsApi.getById(editorState.selectedEntityId)).data;
              delete entityData.location_id;
              entityData.location_name = `${entityData.location_name} (복사)`;
              await managementApi.createLocation(entityData);
              break;
            case 'cell':
              entityData = (await cellsApi.getById(editorState.selectedEntityId)).data;
              delete entityData.cell_id;
              entityData.cell_name = `${entityData.cell_name || '셀'} (복사)`;
              await managementApi.createCell(entityData);
              break;
            case 'entity':
              entityData = (await entitiesApi.getById(editorState.selectedEntityId)).data;
              delete entityData.entity_id;
              entityData.entity_name = `${entityData.entity_name} (복사)`;
              await entitiesApi.create(entityData);
              break;
            default:
              alert('이 엔티티 타입은 복제를 지원하지 않습니다.');
              return;
          }
          await refreshData();
          editorState.setStatusMessage('엔티티가 복제되었습니다.');
          setTimeout(() => editorState.setStatusMessage(''), 2000);
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
      } else if (editorState.selectedEntityId) {
        if (confirm('선택한 엔티티를 삭제하시겠습니까?')) {
          try {
            await entitiesApi.delete(editorState.selectedEntityId);
            editorState.setSelectedEntityId(null);
            await refreshData();
            editorState.setStatusMessage('엔티티가 삭제되었습니다.');
          } catch (error) {
            console.error('엔티티 삭제 실패:', error);
            alert(`엔티티 삭제에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
          }
        }
      }
    },
    onSelectAll: () => {
      if (pins.length > 0) {
        const allPinIds = new Set(pins.map(p => p.pin_id));
        editorState.setSelectedPins(allPinIds);
        setSelectedPin(pins[0].pin_id);
        editorState.setStatusMessage(`${pins.length}개의 핀이 선택되었습니다.`);
        setTimeout(() => editorState.setStatusMessage(''), 2000);
      }
    },
    onDeselectAll: () => {
      setSelectedPin(null);
      setSelectedRoad(null);
      editorState.clearSelection();
    },
    onFind: async () => {
      const query = prompt('검색할 키워드를 입력하세요:');
      if (query) {
        try {
          editorState.setStatus('loading');
          editorState.setStatusMessage('검색 중...');
          await search.performSearch(query);
          modals.openSearchResults();
          editorState.setStatus('ready');
          editorState.setStatusMessage('');
        } catch (error) {
          editorState.setStatus('error');
          editorState.setStatusMessage('검색 실패');
          alert(`검색 실패: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
    },
    onFindInFiles: async () => {
      const query = prompt('파일에서 검색할 키워드를 입력하세요:');
      if (query) {
        try {
          editorState.setStatus('loading');
          editorState.setStatusMessage('검색 중...');
          await search.performSearch(query);
          modals.openSearchResults();
          editorState.setStatus('ready');
          editorState.setStatusMessage('');
        } catch (error) {
          editorState.setStatus('error');
          editorState.setStatusMessage('검색 실패');
          alert(`검색 실패: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
    },
    onReplace: async () => {
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
        
        editorState.setStatus('saving');
        editorState.setStatusMessage('바꾸는 중...');
        
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
        editorState.setStatus('ready');
        editorState.setStatusMessage(`${successCount}개의 항목이 바뀌었습니다.`);
        setTimeout(() => editorState.setStatusMessage(''), 3000);
      } catch (error) {
        editorState.setStatus('error');
        editorState.setStatusMessage('바꾸기 실패');
        alert(`바꾸기 실패: ${error instanceof Error ? error.message : String(error)}`);
      }
    },
    onPreferences: () => {
      modals.openSettings();
    },
    onToggleExplorer: () => {
      editorState.setExplorerMode(editorState.explorerMode === 'explorer' ? 'map' : 'explorer');
    },
    onToggleProperties: () => {
      if (selectedPin || editorState.selectedEntityId) {
        setSelectedPin(null);
        editorState.setSelectedEntityId(null);
        editorState.setSelectedEntityType(undefined);
      } else {
        if (pins.length > 0) {
          setSelectedPin(pins[0].pin_id);
        }
      }
    },
    onToggleConsole: () => {
      alert('콘솔 패널은 추후 구현 예정입니다.');
    },
    onViewMode: (mode) => {
      if (mode === 'map') {
        editorState.setExplorerMode('map');
      } else {
        editorState.setExplorerMode('explorer');
      }
    },
    onZoom: (action) => {
      if (action === 'in') {
        mapControls.zoomIn();
      } else if (action === 'out') {
        mapControls.zoomOut();
      } else if (action === 'fit') {
        mapControls.zoomToFit();
      } else if (action === 'selection') {
        mapControls.zoomToSelection();
      }
    },
    onGridToggle: mapControls.toggleGrid,
    onFullscreen: () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
      } else {
        document.exitFullscreen();
      }
    },
    onEntityProperties: () => {
      if (editorState.selectedEntityType && editorState.selectedEntityId) {
        // 이미 편집기가 열려있음
      } else if (selectedPin) {
        // 핀 편집기 열기
      }
    },
    onDocumentation: () => {
      window.open('https://docs.example.com', '_blank');
    },
  });

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
            roadDrawing.cancelDrawing();
          }
        }}
        gridEnabled={mapState?.grid_enabled || false}
        onNewProject={() => {
          alert('현재 시스템은 데이터베이스를 직접 사용합니다. "새 프로젝트" 기능은 지원하지 않습니다.');
        }}
        onOpenProject={backup.restoreBackup}
        onSaveProject={async () => {
          await backup.saveBackup();
        }}
        onSaveProjectAs={async () => {
          const filename = prompt('백업 파일 이름을 입력하세요:', `world_backup_${new Date().toISOString().split('T')[0]}.json`);
          if (filename) {
            await backup.saveBackup(filename);
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
              editorState.setStatus('loading');
              editorState.setStatusMessage('가져오는 중...');
              
              if (type === 'map') {
                const reader = new FileReader();
                reader.onload = async (event) => {
                  const imageData = event.target?.result as string;
                  try {
                    if (mapState) {
                      await updateMap({ background_image: imageData });
                      editorState.setStatus('ready');
                      editorState.setStatusMessage('지도 이미지가 가져와졌습니다.');
                      setTimeout(() => editorState.setStatusMessage(''), 2000);
                    }
                  } catch (error) {
                    editorState.setStatus('error');
                    editorState.setStatusMessage('이미지 가져오기 실패');
                    alert(`이미지 가져오기 실패: ${error instanceof Error ? error.message : String(error)}`);
                  }
                };
                reader.readAsDataURL(file);
              } else if (type === 'entities') {
                const text = await file.text();
                const data = JSON.parse(text);
                const entities = Array.isArray(data) ? data : [data];
                const response = await projectApi.importEntities(entities);
                const stats = response.data.stats;
                await refreshData();
                editorState.setStatus('ready');
                editorState.setStatusMessage(`${stats.entities}개의 엔티티가 가져와졌습니다.`);
                setTimeout(() => editorState.setStatusMessage(''), 2000);
              } else if (type === 'regions') {
                const text = await file.text();
                let regions: any[];
                if (file.name.endsWith('.csv')) {
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
                  const parsed = JSON.parse(text);
                  regions = Array.isArray(parsed) ? parsed : [parsed];
                }
                const response = await projectApi.importRegions(regions);
                const stats = response.data.stats;
                await refreshData();
                editorState.setStatus('ready');
                editorState.setStatusMessage(`${stats.regions}개의 지역이 가져와졌습니다.`);
                setTimeout(() => editorState.setStatusMessage(''), 2000);
              }
            } catch (error) {
              editorState.setStatus('error');
              editorState.setStatusMessage('가져오기 실패');
              alert(`가져오기 실패: ${error instanceof Error ? error.message : String(error)}`);
            }
          };
          input.click();
        }}
        onExport={async (type) => {
          try {
            editorState.setStatus('saving');
            editorState.setStatusMessage('내보내는 중...');
            
            if (type === 'map') {
              if (mapState) {
                const mapData = JSON.stringify(mapState, null, 2);
                const blob = new Blob([mapData], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `map_metadata_${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                URL.revokeObjectURL(url);
                editorState.setStatusMessage('맵 메타데이터가 내보내졌습니다.');
                setTimeout(() => editorState.setStatusMessage(''), 2000);
              } else {
                alert('내보낼 맵이 없습니다.');
              }
            } else if (type === 'entities') {
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
              const [regionsRes, locationsRes, cellsRes, worldObjectsRes, effectCarriersRes, itemsRes] = await Promise.all([
                regionsApi.getAll(),
                locationsApi.getAll(),
                cellsApi.getAll(),
                worldObjectsApi.getAll(),
                effectCarriersApi.getAll(),
                itemsApi.getAll(),
              ]);
              
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
            
            editorState.setStatus('ready');
            editorState.setStatusMessage('내보내기 완료');
            setTimeout(() => editorState.setStatusMessage(''), 2000);
          } catch (error) {
            editorState.setStatus('error');
            editorState.setStatusMessage('내보내기 실패');
            alert(`내보내기 실패: ${error instanceof Error ? error.message : String(error)}`);
          }
        }}
        onUndo={undo}
        onRedo={redo}
        canUndo={canUndo}
        canRedo={canRedo}
        canPaste={true}
        hasSelection={!!(selectedPin || editorState.selectedEntityId)}
        onCut={async () => {
          if (selectedPin) {
            const pin = pins.find(p => p.pin_id === selectedPin);
            if (pin) {
              await navigator.clipboard.writeText(JSON.stringify({ type: 'pin', data: pin }, null, 2));
              await deletePin(selectedPin);
              setSelectedPin(null);
              editorState.setStatusMessage('핀이 잘라내기되었습니다.');
              setTimeout(() => editorState.setStatusMessage(''), 2000);
            }
          } else if (editorState.selectedEntityId && editorState.selectedEntityType) {
            try {
              let entityData: any;
              switch (editorState.selectedEntityType) {
                case 'region':
                  entityData = { type: 'region', data: (await regionsApi.getById(editorState.selectedEntityId)).data };
                  break;
                case 'location':
                  entityData = { type: 'location', data: (await locationsApi.getById(editorState.selectedEntityId)).data };
                  break;
                case 'cell':
                  entityData = { type: 'cell', data: (await cellsApi.getById(editorState.selectedEntityId)).data };
                  break;
                case 'entity':
                  entityData = { type: 'entity', data: (await entitiesApi.getById(editorState.selectedEntityId)).data };
                  break;
                default:
                  alert('이 엔티티 타입은 잘라내기를 지원하지 않습니다.');
                  return;
              }
              await navigator.clipboard.writeText(JSON.stringify(entityData, null, 2));
              if (confirm('잘라낸 엔티티를 삭제하시겠습니까?')) {
                if (editorState.selectedEntityType === 'region') {
                  await regionsApi.delete(editorState.selectedEntityId);
                } else if (editorState.selectedEntityType === 'location') {
                  await locationsApi.delete(editorState.selectedEntityId);
                } else if (editorState.selectedEntityType === 'cell') {
                  await cellsApi.delete(editorState.selectedEntityId);
                } else {
                  await entitiesApi.delete(editorState.selectedEntityId);
                }
                editorState.setSelectedEntityId(null);
                editorState.setSelectedEntityType(undefined);
                await refreshData();
              }
              editorState.setStatusMessage('엔티티가 잘라내기되었습니다.');
              setTimeout(() => editorState.setStatusMessage(''), 2000);
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
              editorState.setStatusMessage('핀이 클립보드에 복사되었습니다.');
              setTimeout(() => editorState.setStatusMessage(''), 2000);
            }
          } else if (editorState.selectedEntityId && editorState.selectedEntityType) {
            try {
              let entityData: any;
              switch (editorState.selectedEntityType) {
                case 'region':
                  entityData = { type: 'region', data: (await regionsApi.getById(editorState.selectedEntityId)).data };
                  break;
                case 'location':
                  entityData = { type: 'location', data: (await locationsApi.getById(editorState.selectedEntityId)).data };
                  break;
                case 'cell':
                  entityData = { type: 'cell', data: (await cellsApi.getById(editorState.selectedEntityId)).data };
                  break;
                case 'entity':
                  entityData = { type: 'entity', data: (await entitiesApi.getById(editorState.selectedEntityId)).data };
                  break;
                default:
                  alert('이 엔티티 타입은 복사를 지원하지 않습니다.');
                  return;
              }
              await navigator.clipboard.writeText(JSON.stringify(entityData, null, 2));
              editorState.setStatusMessage('엔티티가 클립보드에 복사되었습니다.');
              setTimeout(() => editorState.setStatusMessage(''), 2000);
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
                pin_id: undefined,
                pin_name: `${pinData.pin_name || '새 핀'} (복사)`,
                x: pinData.x + 20,
                y: pinData.y + 20,
              };
              delete (newPinData as any).created_at;
              delete (newPinData as any).updated_at;
              await addPin(newPinData);
              editorState.setStatusMessage('핀이 붙여넣기되었습니다.');
              setTimeout(() => editorState.setStatusMessage(''), 2000);
            } else if (data.type && data.data) {
              const entityData = data.data;
              try {
                if (data.type === 'region') {
                  delete entityData.region_id;
                  entityData.region_name = `${entityData.region_name} (복사)`;
                  await regionsApi.create(entityData);
                } else if (data.type === 'location') {
                  delete entityData.location_id;
                  entityData.location_name = `${entityData.location_name} (복사)`;
                  await managementApi.createLocation(entityData);
                } else if (data.type === 'cell') {
                  delete entityData.cell_id;
                  entityData.cell_name = `${entityData.cell_name || '셀'} (복사)`;
                  await managementApi.createCell(entityData);
                } else if (data.type === 'entity') {
                  delete entityData.entity_id;
                  entityData.entity_name = `${entityData.entity_name} (복사)`;
                  await entitiesApi.create(entityData);
                }
                await refreshData();
                editorState.setStatusMessage('엔티티가 붙여넣기되었습니다.');
                setTimeout(() => editorState.setStatusMessage(''), 2000);
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
                pin_id: undefined,
                pin_name: `${pin.pin_name || '새 핀'} (복사)`,
                x: pin.x + 20,
                y: pin.y + 20,
              };
              delete (newPinData as any).created_at;
              delete (newPinData as any).updated_at;
              await addPin(newPinData);
              editorState.setStatusMessage('핀이 복제되었습니다.');
              setTimeout(() => editorState.setStatusMessage(''), 2000);
            }
          } else if (editorState.selectedEntityId && editorState.selectedEntityType) {
            try {
              let entityData: any;
              switch (editorState.selectedEntityType) {
                case 'region':
                  entityData = (await regionsApi.getById(editorState.selectedEntityId)).data;
                  delete entityData.region_id;
                  entityData.region_name = `${entityData.region_name} (복사)`;
                  await regionsApi.create(entityData);
                  break;
                case 'location':
                  entityData = (await locationsApi.getById(editorState.selectedEntityId)).data;
                  delete entityData.location_id;
                  entityData.location_name = `${entityData.location_name} (복사)`;
                  await managementApi.createLocation(entityData);
                  break;
                case 'cell':
                  entityData = (await cellsApi.getById(editorState.selectedEntityId)).data;
                  delete entityData.cell_id;
                  entityData.cell_name = `${entityData.cell_name || '셀'} (복사)`;
                  await managementApi.createCell(entityData);
                  break;
                case 'entity':
                  entityData = (await entitiesApi.getById(editorState.selectedEntityId)).data;
                  delete entityData.entity_id;
                  entityData.entity_name = `${entityData.entity_name} (복사)`;
                  await entitiesApi.create(entityData);
                  break;
                default:
                  alert('이 엔티티 타입은 복제를 지원하지 않습니다.');
                  return;
              }
              await refreshData();
              editorState.setStatusMessage('엔티티가 복제되었습니다.');
              setTimeout(() => editorState.setStatusMessage(''), 2000);
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
          } else if (editorState.selectedEntityId) {
            if (confirm('선택한 엔티티를 삭제하시겠습니까?')) {
              try {
                await entitiesApi.delete(editorState.selectedEntityId);
                editorState.setSelectedEntityId(null);
                await refreshData();
                editorState.setStatusMessage('엔티티가 삭제되었습니다.');
              } catch (error) {
                console.error('엔티티 삭제 실패:', error);
                alert(`엔티티 삭제에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
              }
            }
          }
        }}
        onSelectAll={() => {
          if (pins.length > 0) {
            const allPinIds = new Set(pins.map(p => p.pin_id));
            editorState.setSelectedPins(allPinIds);
            setSelectedPin(pins[0].pin_id);
            editorState.setStatusMessage(`${pins.length}개의 핀이 선택되었습니다.`);
            setTimeout(() => editorState.setStatusMessage(''), 2000);
          }
        }}
        onDeselectAll={() => {
          setSelectedPin(null);
          setSelectedRoad(null);
          editorState.clearSelection();
        }}
        onFind={async () => {
          const query = prompt('검색할 키워드를 입력하세요:');
          if (query) {
            try {
              editorState.setStatus('loading');
              editorState.setStatusMessage('검색 중...');
              await search.performSearch(query);
              modals.openSearchResults();
              editorState.setStatus('ready');
              editorState.setStatusMessage('');
            } catch (error) {
              editorState.setStatus('error');
              editorState.setStatusMessage('검색 실패');
              alert(`검색 실패: ${error instanceof Error ? error.message : String(error)}`);
            }
          }
        }}
        onFindInFiles={async () => {
          const query = prompt('파일에서 검색할 키워드를 입력하세요:');
          if (query) {
            try {
              editorState.setStatus('loading');
              editorState.setStatusMessage('검색 중...');
              await search.performSearch(query);
              modals.openSearchResults();
              editorState.setStatus('ready');
              editorState.setStatusMessage('');
            } catch (error) {
              editorState.setStatus('error');
              editorState.setStatusMessage('검색 실패');
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
            
            editorState.setStatus('saving');
            editorState.setStatusMessage('바꾸는 중...');
            
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
            editorState.setStatus('ready');
            editorState.setStatusMessage(`${successCount}개의 항목이 바뀌었습니다.`);
            setTimeout(() => editorState.setStatusMessage(''), 3000);
          } catch (error) {
            editorState.setStatus('error');
            editorState.setStatusMessage('바꾸기 실패');
            alert(`바꾸기 실패: ${error instanceof Error ? error.message : String(error)}`);
          }
        }}
        onPreferences={() => modals.openSettings()}
        onKnowledgeManager={() => modals.openKnowledgeManager()}
        onTogglePanel={(panel) => {
          if (panel === 'explorer') {
            editorState.setExplorerMode(editorState.explorerMode === 'explorer' ? 'map' : 'explorer');
          } else if (panel === 'properties') {
            if (selectedPin || editorState.selectedEntityId) {
              setSelectedPin(null);
              editorState.setSelectedEntityId(null);
              editorState.setSelectedEntityType(undefined);
            } else {
              if (pins.length > 0) {
                setSelectedPin(pins[0].pin_id);
              }
            }
          }
        }}
        onViewMode={(mode) => {
          if (mode === 'map') {
            editorState.setExplorerMode('map');
          } else {
            editorState.setExplorerMode('explorer');
          }
        }}
        onZoom={(action) => {
          if (action === 'in') {
            mapControls.zoomIn();
          } else if (action === 'out') {
            mapControls.zoomOut();
          } else if (action === 'fit') {
            mapControls.zoomToFit();
          } else if (action === 'selection') {
            mapControls.zoomToSelection();
          }
        }}
        onGridToggle={mapControls.toggleGrid}
        onGridSettings={() => {
          const size = prompt('그리드 크기를 입력하세요 (기본값: 50):', String(mapState?.grid_size || 50));
          if (size) {
            const gridSize = parseInt(size, 10);
            if (!isNaN(gridSize) && gridSize > 0) {
              updateMap({ grid_size: gridSize });
              editorState.setStatusMessage(`그리드 크기가 ${gridSize}로 설정되었습니다.`);
              setTimeout(() => editorState.setStatusMessage(''), 2000);
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
          if (editorState.selectedEntityType && editorState.selectedEntityId) {
            // 이미 편집기가 열려있음
          }
        }}
        onEntityRelationships={async () => {
          if (editorState.selectedEntityType && editorState.selectedEntityId) {
            try {
              const response = await relationshipsApi.getRelationships(editorState.selectedEntityType, editorState.selectedEntityId);
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
            editorState.setStatus('loading');
            editorState.setStatusMessage('검증 중...');
            
            if (type === 'all') {
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
              const response = await projectApi.validateOrphans();
              const orphans = response.data.orphans;
              
              if (orphans.length === 0) {
                alert('고아 엔티티가 없습니다.');
              } else {
                alert(`고아 엔티티 ${orphans.length}개 발견:\n\n${orphans.slice(0, 10).join('\n')}${orphans.length > 10 ? `\n... 외 ${orphans.length - 10}개` : ''}`);
              }
            } else if (type === 'duplicates') {
              const response = await projectApi.validateDuplicates();
              const duplicates = response.data.duplicates;
              
              if (duplicates.length === 0) {
                alert('중복된 이름이 없습니다.');
              } else {
                alert(`중복 발견: ${duplicates.length}개\n\n${duplicates.slice(0, 10).join('\n')}${duplicates.length > 10 ? `\n... 외 ${duplicates.length - 10}개` : ''}`);
              }
            }
            
            editorState.setStatus('ready');
            editorState.setStatusMessage('');
          } catch (error) {
            editorState.setStatus('error');
            editorState.setStatusMessage('검증 실패');
            alert(`검증 실패: ${error instanceof Error ? error.message : String(error)}`);
          }
        }}
        onLayout={(layout) => {
          alert(`레이아웃 "${layout}" 변경 기능은 추후 구현 예정입니다.`);
        }}
        onDocumentation={() => window.open('https://docs.example.com', '_blank')}
        onKeyboardShortcuts={() => modals.openKeyboardShortcuts()}
        onAbout={() => modals.openAbout()}
      />
      {currentTool === 'road' && roadDrawing.isDrawing() && (
        <div style={{
          padding: '10px',
          backgroundColor: '#fff3cd',
          borderBottom: '1px solid #ffc107',
          textAlign: 'center',
        }}>
          도로 그리기 모드: 첫 번째 핀을 선택했습니다. 두 번째 핀을 선택하세요.
        </div>
      )}
      <EditorLayout
        sidebarProps={{
          explorerMode: editorState.explorerMode,
          onExplorerModeChange: editorState.setExplorerMode,
          onEntitySelect: (entityType, entityId) => {
            editorState.setSelectedEntityType(entityType);
            editorState.setSelectedEntityId(entityId);
            setSelectedPin(null);
            setSelectedRoad(null);
          },
          onAddPinToMap: async (entityType, entityId, entityName) => {
            if (!mapState) return;
            
            const centerX = (mapState.width || 1000) / 2;
            const centerY = (mapState.height || 1000) / 2;
            
            try {
              const pinType: 'region' | 'location' | 'cell' = entityType === 'region' ? 'region' : 
                             entityType === 'location' ? 'location' : 'cell';
              
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
              
              setSelectedPin(newPin.pin_id);
              
              if (sendMessage) {
                sendMessage({
                  type: 'pin_update',
                  data: { pin_id: newPin.pin_id, x: centerX, y: centerY },
                });
              }
              
              editorState.setStatusMessage(`${entityName} 핀이 맵에 추가되었습니다.`);
              setTimeout(() => editorState.setStatusMessage(''), 2000);
            } catch (error) {
              console.error('핀 추가 실패:', error);
              alert(`핀 추가에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
            }
          },
          pins,
          regions,
          locations,
          cells,
          selectedPin,
          onPinSelect: (pinId) => {
            setSelectedPin(pinId);
            setSelectedRoad(null);
            setCurrentTool('select');
          },
          searchQuery: search.searchQuery,
          onSearchQueryChange: search.setSearchQuery,
        }}
        mainAreaProps={{
          mapViewMode: mapEditor.mapViewMode,
          currentMapLevel: mapEditor.currentMapLevel,
          currentMapEntityId: mapEditor.currentMapEntityId,
          selectedCellId: mapEditor.selectedCellId,
          mapState,
          pins,
          roads,
          selectedPin,
          selectedRoad,
          currentTool,
          onPinClick: handlePinClick,
          onPinDoubleClick: handlePinDoubleClick,
          onPinDrag: handlePinDrag,
          onRoadClick: handleRoadClick,
          onMapClick: handleMapClick,
          onMouseMove: (x, y) => setMousePosition({ x: Math.round(x), y: Math.round(y) }),
          onNavigateToCell: (cellId, previousLocationId) => {
            mapEditor.navigateToCell(cellId, previousLocationId);
          },
          onNavigateToLocation: (locationId) => {
            mapEditor.navigateToLocation(locationId);
          },
          onNavigateToRegion: (regionId) => {
            mapEditor.navigateToRegion(regionId);
          },
          onNavigateBack: () => {
            mapEditor.navigateBack();
          },
          explorerMode: editorState.explorerMode,
          selectedEntityType: editorState.selectedEntityType,
          selectedEntityId: editorState.selectedEntityId,
          onEntitySave: async (entityType, entityId, data) => {
            await refreshData();
          },
          onEntityDelete: async (entityType, entityId) => {
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
                editorState.setStatusMessage(`${entityType === 'region' ? '지역' : entityType === 'location' ? '위치' : entityType === 'cell' ? '셀' : '엔티티'}이(가) 삭제되었습니다.`);
              } catch (error) {
                console.error('삭제 실패:', error);
                alert(`삭제에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
              }
            }
          },
          onEntityClose: () => {
            editorState.setSelectedEntityType(undefined);
            editorState.setSelectedEntityId(null);
          },
          regions,
          locations,
          cells,
          onPinUpdate: async (pinId, updates) => {
            await updatePin(pinId, updates);
            if (sendMessage) {
              sendMessage({
                type: 'pin_update',
                data: { pin_id: pinId, ...updates },
              });
            }
            await refreshData();
          },
          onPinDelete: async (pinId) => {
            if (confirm('정말로 이 핀을 삭제하시겠습니까?')) {
              await deletePin(pinId);
              await refreshData();
              if (selectedPin === pinId) {
                setSelectedPin(null);
              }
            }
          },
          onPinClose: () => {
            setSelectedPin(null);
          },
          onRefresh: refreshData,
          sendMessage,
          showCellManager: mapEditor.mapViewMode === 'cell',
        }}
      />
      <StatusBar
        status={editorState.status}
        statusMessage={editorState.statusMessage}
        selectedEntityType={editorState.selectedEntityType}
        selectedEntityId={editorState.selectedEntityId || undefined}
        selectedCount={selectedPin || editorState.selectedEntityId ? 1 : 0}
        mouseX={mousePosition?.x}
        mouseY={mousePosition?.y}
        selectedX={selectedPin ? pins.find(p => p.pin_id === selectedPin)?.x : undefined}
        selectedY={selectedPin ? pins.find(p => p.pin_id === selectedPin)?.y : undefined}
        zoomLevel={(mapState?.zoom_level || 1.0) * 100}
        fps={fps}
        websocketConnected={websocketConnected}
        autoSaveEnabled={settings.autoSaveInterval > 0}
        autoSaveStatus={editorState.status === 'saving' ? 'saving' : 'saved'}
      />
      <SettingsModal
        isOpen={modals.settingsModalOpen}
        onClose={modals.closeSettings}
      />
      <DialogueKnowledgeManager
        isOpen={modals.knowledgeManagerOpen}
        onClose={modals.closeKnowledgeManager}
      />
      <SearchResultsModal
        isOpen={modals.searchResultsModalOpen}
        onClose={modals.closeSearchResults}
        results={search.searchResults.map(result => ({
          ...result,
          name: result.entity_name,
        }))}
        onResultClick={(entityType, entityId) => {
          if (entityType === 'region' || entityType === 'location' || entityType === 'cell' || entityType === 'entity') {
            editorState.setSelectedEntityType(entityType as EntityType);
            editorState.setSelectedEntityId(entityId);
            editorState.setExplorerMode('explorer');
          }
        }}
      />
      <KeyboardShortcutsModal
        isOpen={modals.keyboardShortcutsModalOpen}
        onClose={modals.closeKeyboardShortcuts}
      />
      <AboutModal
        isOpen={modals.aboutModalOpen}
        onClose={modals.closeAbout}
      />
    </div>
  );
};
