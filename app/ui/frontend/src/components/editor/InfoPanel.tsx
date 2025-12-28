/**
 * 정보 패널 컴포넌트
 */
import React, { useState } from 'react';
import { PinData, RoadData, RegionData, LocationData, CellData, DnDLocationInfo } from '../types';
import { DnDInfoForm } from './DnDInfoForm';
import { regionsApi, locationsApi, cellsApi } from '../../services/api';

interface InfoPanelProps {
  selectedPin: PinData | null;
  selectedRoad: RoadData | null;
  regions: RegionData[];
  locations: LocationData[];
  cells: CellData[];
  onUpdate: (data: any) => void;
}

export const InfoPanel: React.FC<InfoPanelProps> = ({
  selectedPin,
  selectedRoad,
  regions,
  locations,
  cells,
  onUpdate,
}) => {
  const [showDnDForm, setShowDnDForm] = useState(false);
  const [dndData, setDndData] = useState<DnDLocationInfo | null>(null);

  // 선택된 엔티티 데이터 가져오기
  const getEntityData = () => {
    if (!selectedPin) return null;

    if (selectedPin.pin_type === 'region') {
      return regions.find(r => r.region_id === selectedPin.game_data_id);
    } else if (selectedPin.pin_type === 'location') {
      return locations.find(l => l.location_id === selectedPin.game_data_id);
    } else if (selectedPin.pin_type === 'cell') {
      return cells.find(c => c.cell_id === selectedPin.game_data_id);
    }
    return null;
  };

  const entityData = getEntityData();

  const handleDnDSave = async (data: DnDLocationInfo) => {
    if (!selectedPin || !entityData) return;

    // D&D 정보를 region_properties 또는 location_properties에 저장
    const properties = {
      ...(entityData as any)[`${selectedPin.pin_type}_properties`],
      dnd_info: data,
    };

    try {
      if (selectedPin.pin_type === 'region') {
        await regionsApi.update(selectedPin.game_data_id, {
          region_properties: properties,
        });
      } else if (selectedPin.pin_type === 'location') {
        await locationsApi.update(selectedPin.game_data_id, {
          location_properties: properties,
        });
      } else if (selectedPin.pin_type === 'cell') {
        await cellsApi.update(selectedPin.game_data_id, {
          cell_properties: properties,
        });
      }

      setShowDnDForm(false);
      onUpdate({ type: 'dnd_info_updated', data });
    } catch (error) {
      console.error('D&D 정보 저장 실패:', error);
    }
  };

  const loadDnDData = () => {
    if (!entityData) return;

    const properties = entityData[`${selectedPin?.pin_type}_properties` as keyof typeof entityData] as any;
    const dndInfo = properties?.dnd_info;

    if (dndInfo) {
      setDndData(dndInfo);
    } else {
      setDndData(null);
    }
    setShowDnDForm(true);
  };

  if (showDnDForm && selectedPin) {
    return (
      <DnDInfoForm
        gameDataId={selectedPin.game_data_id}
        pinType={selectedPin.pin_type}
        initialData={dndData || undefined}
        onSave={handleDnDSave}
        onCancel={() => setShowDnDForm(false)}
      />
    );
  }

  return (
    <div style={{ padding: '20px', height: '100%', overflowY: 'auto' }}>
      <h3>정보 패널</h3>

      {selectedPin && (
        <div style={{ marginTop: '20px' }}>
          <h4>선택된 핀</h4>
          <p><strong>ID:</strong> {selectedPin.pin_id}</p>
          <p><strong>타입:</strong> {selectedPin.pin_type}</p>
          <p><strong>게임 데이터 ID:</strong> {selectedPin.game_data_id}</p>
          <p><strong>위치:</strong> ({selectedPin.x}, {selectedPin.y})</p>
          <p><strong>아이콘:</strong> {selectedPin.icon_type}</p>

          {entityData && (
            <div style={{ marginTop: '20px' }}>
              <h5>엔티티 정보</h5>
              {selectedPin.pin_type === 'region' && (
                <div>
                  <p><strong>이름:</strong> {(entityData as RegionData).region_name}</p>
                  <p><strong>설명:</strong> {(entityData as RegionData).region_description || '없음'}</p>
                </div>
              )}
              {selectedPin.pin_type === 'location' && (
                <div>
                  <p><strong>이름:</strong> {(entityData as LocationData).location_name}</p>
                  <p><strong>설명:</strong> {(entityData as LocationData).location_description || '없음'}</p>
                </div>
              )}
              {selectedPin.pin_type === 'cell' && (
                <div>
                  <p><strong>이름:</strong> {(entityData as CellData).cell_name || '없음'}</p>
                  <p><strong>크기:</strong> {(entityData as CellData).matrix_width} x {(entityData as CellData).matrix_height}</p>
                </div>
              )}

              <button
                onClick={loadDnDData}
                style={{
                  marginTop: '10px',
                  padding: '8px 16px',
                  backgroundColor: '#4ECDC4',
                  color: 'white',
                  border: 'none',
                  cursor: 'pointer',
                }}
              >
                D&D 정보 {dndData ? '편집' : '추가'}
              </button>
            </div>
          )}
        </div>
      )}

      {selectedRoad && (
        <div style={{ marginTop: '20px' }}>
          <h4>선택된 도로</h4>
          <p><strong>ID:</strong> {selectedRoad.road_id}</p>
          <p><strong>타입:</strong> {selectedRoad.road_type}</p>
          <p><strong>거리:</strong> {selectedRoad.distance || 'N/A'}</p>
          <p><strong>이동 시간:</strong> {selectedRoad.travel_time || 'N/A'} 분</p>
          <p><strong>위험도:</strong> {selectedRoad.danger_level}/10</p>
        </div>
      )}

      {!selectedPin && !selectedRoad && (
        <div style={{ marginTop: '20px', color: '#999' }}>
          항목을 선택하면 정보가 여기에 표시됩니다.
        </div>
      )}
    </div>
  );
};

