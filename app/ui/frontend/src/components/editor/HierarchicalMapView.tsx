/**
 * 계층적 맵 뷰 컴포넌트
 * World -> Region -> Location -> Cell 계층 구조를 관리
 */
import React, { useState, useEffect } from 'react';
import { MapCanvas } from './MapCanvas';
import { EntityPlacementModal } from './EntityPlacementModal';
import { mapHierarchyApi, locationsApi, cellsApi } from '../../services/api';
import { MapMetadata, PinData, RoadData } from '../../types';

export type MapLevel = 'world' | 'region' | 'location' | 'cell';

interface HierarchicalMapViewProps {
  currentLevel: MapLevel;
  currentEntityId: string | null;
  onLevelChange: (level: MapLevel, entityId: string | null) => void;
  onEntitySelect?: (entityId: string, entityType: string) => void;
}

interface LocationData {
  location_id: string;
  location_name: string;
  location_type: string | null;
  location_description: string | null;
  region_id?: string;
  properties: any;
  position: { x: number | null; y: number | null };
}

interface CellData {
  cell_id: string;
  cell_name: string;
  location_id?: string;
  matrix_width: number;
  matrix_height: number;
  cell_description: string | null;
  cell_properties: any;
  position: { x: number | null; y: number | null };
}

export const HierarchicalMapView: React.FC<HierarchicalMapViewProps> = ({
  currentLevel,
  currentEntityId,
  onLevelChange,
  onEntitySelect,
}) => {
  const [mapMetadata, setMapMetadata] = useState<MapMetadata | null>(null);
  const [pins, setPins] = useState<PinData[]>([]);
  const [roads, setRoads] = useState<RoadData[]>([]);
  const [locations, setLocations] = useState<LocationData[]>([]);
  const [cells, setCells] = useState<CellData[]>([]);
  const [selectedPin, setSelectedPin] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentTool, setCurrentTool] = useState<'select' | 'pin' | 'pan'>('select');
  const [placementModalOpen, setPlacementModalOpen] = useState(false);
  const [placementPosition, setPlacementPosition] = useState<{ x: number; y: number } | null>(null);

  // 맵 데이터 로드
  useEffect(() => {
    const loadMapData = async () => {
      if (!currentEntityId) return;

      try {
        setLoading(true);

        if (currentLevel === 'region') {
          // Region Map 로드
          const [mapRes, locationsRes] = await Promise.all([
            mapHierarchyApi.getRegionMap(currentEntityId),
            mapHierarchyApi.getRegionLocations(currentEntityId),
          ]);

          setMapMetadata(mapRes.data);
          setLocations(locationsRes.data);
          
          // Location을 Pin으로 변환
          const locationPins: PinData[] = locationsRes.data
            .filter((loc: LocationData) => loc.position.x !== null && loc.position.y !== null)
            .map((loc: LocationData) => ({
              pin_id: `LOC_${loc.location_id}`,
              pin_name: loc.location_name,
              game_data_id: loc.location_id,
              pin_type: 'location',
              x: loc.position.x!,
              y: loc.position.y!,
              icon_type: 'default',
              color: '#4A90E2',
              size: 12,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            }));
          
          setPins(locationPins);
          setCells([]);
        } else if (currentLevel === 'location') {
          // Location Map 로드
          const [mapRes, cellsRes] = await Promise.all([
            mapHierarchyApi.getLocationMap(currentEntityId),
            mapHierarchyApi.getLocationCells(currentEntityId),
          ]);

          setMapMetadata(mapRes.data);
          setCells(cellsRes.data);
          
          // Cell을 Pin으로 변환
          const cellPins: PinData[] = cellsRes.data
            .filter((cell: CellData) => cell.position.x !== null && cell.position.y !== null)
            .map((cell: CellData) => ({
              pin_id: `CELL_${cell.cell_id}`,
              pin_name: cell.cell_name,
              game_data_id: cell.cell_id,
              pin_type: 'cell',
              x: cell.position.x!,
              y: cell.position.y!,
              icon_type: 'default',
              color: '#50C878',
              size: 10,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            }));
          
          setPins(cellPins);
          setLocations([]);
        }

        setRoads([]);
      } catch (error) {
        console.error('맵 데이터 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadMapData();
  }, [currentLevel, currentEntityId]);

  // 핀 클릭 핸들러 (선택만)
  const handlePinClick = (pinId: string) => {
    setSelectedPin(pinId);
  };

  // 핀 더블 클릭 핸들러 (하위 레벨로 이동)
  const handlePinDoubleClick = (pinId: string) => {
    const pin = pins.find(p => p.pin_id === pinId);
    if (!pin) return;

    if (currentLevel === 'region' && pin.pin_type === 'location') {
      // Location 더블 클릭 시 Location Map으로 이동
      onLevelChange('location', pin.game_data_id);
      if (onEntitySelect) {
        onEntitySelect(pin.game_data_id, 'location');
      }
    } else if (currentLevel === 'location' && pin.pin_type === 'cell') {
      // Cell 더블 클릭 시 Cell Entity 관리로 이동
      onLevelChange('cell', pin.game_data_id);
      if (onEntitySelect) {
        onEntitySelect(pin.game_data_id, 'cell');
      }
    }
  };

  // 핀 드래그 핸들러
  const handlePinDrag = async (pinId: string, x: number, y: number) => {
    const pin = pins.find(p => p.pin_id === pinId);
    if (!pin || !currentEntityId) return;

    // 좌표 유효성 검사
    if (!isFinite(x) || !isFinite(y) || x < 0 || y < 0) {
      console.warn('유효하지 않은 좌표:', { x, y });
      return;
    }

    try {
      if (currentLevel === 'region' && pin.pin_type === 'location') {
        await mapHierarchyApi.updateLocationPosition(
          currentEntityId,
          pin.game_data_id,
          { x, y }
        );
      } else if (currentLevel === 'location' && pin.pin_type === 'cell') {
        await mapHierarchyApi.updateCellPosition(
          currentEntityId,
          pin.game_data_id,
          { x, y }
        );
      }

      // 로컬 상태 업데이트
      setPins(prevPins =>
        prevPins.map(p =>
          p.pin_id === pinId ? { ...p, x, y } : p
        )
      );
    } catch (error) {
      console.error('핀 위치 업데이트 실패:', error);
      // 에러 발생 시 원래 위치로 복원
      setPins(prevPins =>
        prevPins.map(p =>
          p.pin_id === pinId ? { ...p, x: pin.x, y: pin.y } : p
        )
      );
    }
  };

  // 맵 클릭 핸들러 (Location/Cell 배치)
  const handleMapClick = async (x: number, y: number) => {
    if (currentTool !== 'pin' || !currentEntityId) return;

    // 배치 모달 열기
    setPlacementPosition({ x, y });
    setPlacementModalOpen(true);
  };

  // Entity 배치 핸들러
  const handleEntityPlacement = async (entityId: string, position: { x: number; y: number }) => {
    if (!currentEntityId) return;

    try {
      if (currentLevel === 'region') {
        await mapHierarchyApi.placeLocationInRegion(
          currentEntityId,
          entityId,
          position
        );
      } else if (currentLevel === 'location') {
        await mapHierarchyApi.placeCellInLocation(
          currentEntityId,
          entityId,
          position
        );
      }

      // 데이터 다시 로드
      const loadMapData = async () => {
        if (currentLevel === 'region') {
          const locationsRes = await mapHierarchyApi.getRegionLocations(currentEntityId);
          setLocations(locationsRes.data);
          const locationPins: PinData[] = locationsRes.data
            .filter((loc: LocationData) => loc.position.x !== null && loc.position.y !== null)
            .map((loc: LocationData) => ({
              pin_id: `LOC_${loc.location_id}`,
              pin_name: loc.location_name,
              game_data_id: loc.location_id,
              pin_type: 'location',
              x: loc.position.x!,
              y: loc.position.y!,
              icon_type: 'default',
              color: '#4A90E2',
              size: 12,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            }));
          setPins(locationPins);
        } else if (currentLevel === 'location') {
          const cellsRes = await mapHierarchyApi.getLocationCells(currentEntityId);
          setCells(cellsRes.data);
          const cellPins: PinData[] = cellsRes.data
            .filter((cell: CellData) => cell.position.x !== null && cell.position.y !== null)
            .map((cell: CellData) => ({
              pin_id: `CELL_${cell.cell_id}`,
              pin_name: cell.cell_name,
              game_data_id: cell.cell_id,
              pin_type: 'cell',
              x: cell.position.x!,
              y: cell.position.y!,
              icon_type: 'default',
              color: '#50C878',
              size: 10,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            }));
          setPins(cellPins);
        }
      };
      await loadMapData();
    } catch (error) {
      console.error('Entity 배치 실패:', error);
      alert('Entity 배치에 실패했습니다.');
    }
  };

  if (loading || !mapMetadata) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>맵 로딩 중...</p>
      </div>
    );
  }

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* 현재 뷰 레벨 표시 및 Breadcrumb 네비게이션 */}
      <div style={{
        padding: '10px',
        backgroundColor: '#f5f5f5',
        borderBottom: '1px solid #ddd',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
      }}>
        {/* 현재 뷰 레벨 표시 */}
        <div style={{
          padding: '5px 15px',
          backgroundColor: '#4A90E2',
          color: '#fff',
          borderRadius: '4px',
          fontWeight: 'bold',
          fontSize: '14px',
        }}>
          {currentLevel === 'world' && 'World Map'}
          {currentLevel === 'region' && 'Region Map'}
          {currentLevel === 'location' && 'Location Map'}
          {currentLevel === 'cell' && 'Cell Entity Manager'}
        </div>

        <div style={{ width: '1px', height: '20px', backgroundColor: '#ddd' }} />

        {/* Breadcrumb 네비게이션 */}
        <button
          onClick={() => onLevelChange('world', null)}
          style={{ padding: '5px 10px', cursor: 'pointer', border: '1px solid #ddd', borderRadius: '4px' }}
        >
          World
        </button>
        {currentLevel === 'region' && currentEntityId && (
          <>
            <span>→</span>
            <span>Region: {currentEntityId}</span>
          </>
        )}
        {currentLevel === 'location' && currentEntityId && (
          <>
            <span>→</span>
            <span>Location: {currentEntityId}</span>
          </>
        )}
        {currentLevel === 'cell' && currentEntityId && (
          <>
            <span>→</span>
            <span>Cell: {currentEntityId}</span>
          </>
        )}
        {currentLevel !== 'world' && (
          <button
            onClick={() => {
              if (currentLevel === 'region') {
                onLevelChange('world', null);
              } else if (currentLevel === 'location') {
                // 부모 Region ID 찾기
                const location = locations.find(loc => loc.location_id === currentEntityId);
                if (location?.region_id) {
                  onLevelChange('region', location.region_id);
                } else {
                  onLevelChange('region', null);
                }
              } else if (currentLevel === 'cell') {
                // 부모 Location ID 찾기
                const cell = cells.find(c => c.cell_id === currentEntityId);
                if (cell?.location_id) {
                  onLevelChange('location', cell.location_id);
                } else {
                  onLevelChange('location', null);
                }
              }
            }}
            style={{ marginLeft: 'auto', padding: '5px 10px', cursor: 'pointer', border: '1px solid #ddd', borderRadius: '4px' }}
          >
            ← 상위로
          </button>
        )}
      </div>

      {/* 안내 메시지 */}
      <div style={{
        padding: '8px 10px',
        backgroundColor: '#e3f2fd',
        borderBottom: '1px solid #ddd',
        fontSize: '12px',
        color: '#1976d2',
      }}>
        💡 <strong>팁:</strong> 핀을 클릭하면 선택되고, 더블 클릭하면 하위 레벨로 이동합니다.
      </div>

      {/* 툴바 */}
      <div style={{
        padding: '10px',
        backgroundColor: '#f9f9f9',
        borderBottom: '1px solid #ddd',
        display: 'flex',
        gap: '10px',
      }}>
        <button
          onClick={() => setCurrentTool('select')}
          style={{
            padding: '5px 15px',
            cursor: 'pointer',
            backgroundColor: currentTool === 'select' ? '#4A90E2' : '#fff',
            color: currentTool === 'select' ? '#fff' : '#000',
            border: '1px solid #ddd',
          }}
        >
          선택
        </button>
        <button
          onClick={() => setCurrentTool('pin')}
          style={{
            padding: '5px 15px',
            cursor: 'pointer',
            backgroundColor: currentTool === 'pin' ? '#4A90E2' : '#fff',
            color: currentTool === 'pin' ? '#fff' : '#000',
            border: '1px solid #ddd',
          }}
        >
          {currentLevel === 'region' ? 'Location 배치' : 'Cell 배치'}
        </button>
        <button
          onClick={() => setCurrentTool('pan')}
          style={{
            padding: '5px 15px',
            cursor: 'pointer',
            backgroundColor: currentTool === 'pan' ? '#4A90E2' : '#fff',
            color: currentTool === 'pan' ? '#fff' : '#000',
            border: '1px solid #ddd',
          }}
        >
          이동
        </button>
      </div>

      {/* 맵 캔버스 */}
      <MapCanvas
        mapState={mapMetadata}
        pins={pins}
        roads={roads}
        selectedPin={selectedPin}
        selectedRoad={null}
        currentTool={currentTool}
        onPinClick={handlePinClick}
        onPinDoubleClick={handlePinDoubleClick}
        onPinDrag={handlePinDrag}
        onRoadClick={() => {}}
        onMapClick={handleMapClick}
        currentMapLevel={currentLevel}
      />

      {/* Entity 배치 모달 */}
      {currentEntityId && (
        <EntityPlacementModal
          isOpen={placementModalOpen}
          level={currentLevel === 'region' ? 'region' : 'location'}
          parentId={currentEntityId}
          position={placementPosition}
          onClose={() => {
            setPlacementModalOpen(false);
            setPlacementPosition(null);
          }}
          onSelect={handleEntityPlacement}
        />
      )}
    </div>
  );
};

