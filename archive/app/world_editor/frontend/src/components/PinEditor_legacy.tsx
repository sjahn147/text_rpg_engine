/**
 * 핀 전문 편집기 패널 - 게임 데이터 편집 중심
 */
import React, { useState, useEffect } from 'react';
import { PinData, RegionData, LocationData, CellData, DnDLocationInfo } from '../types';
import { regionsApi, locationsApi, cellsApi, pinsApi } from '../services/api';
import { DnDInfoForm } from './DnDInfoForm';

interface PinEditorProps {
  pin: PinData | null;
  regions: RegionData[];
  locations: LocationData[];
  cells: CellData[];
  onPinUpdate?: (pinId: string, updates: any) => Promise<void>;
  onPinDelete?: (pinId: string) => Promise<void>;
  onClose?: () => void;
  onRefresh?: () => Promise<void>;
}

export const PinEditor: React.FC<PinEditorProps> = ({
  pin,
  regions,
  locations,
  cells,
  onPinUpdate,
  onPinDelete,
  onClose,
  onRefresh,
}) => {
  const [currentRegion, setCurrentRegion] = useState<RegionData | null>(null);
  const [currentLocation, setCurrentLocation] = useState<LocationData | null>(null);
  const [currentCell, setCurrentCell] = useState<CellData | null>(null);
  const [regionLocations, setRegionLocations] = useState<LocationData[]>([]);
  const [locationCells, setLocationCells] = useState<CellData[]>([]);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['region', 'locations', 'cells']));
  const [editingMode, setEditingMode] = useState<'region' | 'location' | 'cell' | 'dnd' | null>(null);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(false);

  // 핀 데이터 로드 및 연결된 게임 데이터 찾기
  useEffect(() => {
    const loadGameData = async () => {
      if (!pin) {
        setCurrentRegion(null);
        setCurrentLocation(null);
        setCurrentCell(null);
        setRegionLocations([]);
        setLocationCells([]);
        return;
      }

      setLoading(true);
      try {
        if (pin.pin_type === 'region') {
          // Region 찾기
          const region = regions.find(r => r.region_id === pin.game_data_id);
          setCurrentRegion(region || null);
          setCurrentLocation(null);
          setCurrentCell(null);

          // 하위 Location 로드
          if (region) {
            try {
              const response = await locationsApi.getByRegion(region.region_id);
              setRegionLocations(response.data || []);
            } catch (error) {
              console.error('Location 로드 실패:', error);
              setRegionLocations([]);
            }
          }
        } else if (pin.pin_type === 'location') {
          // Location 찾기
          const location = locations.find(l => l.location_id === pin.game_data_id);
          setCurrentLocation(location || null);
          setCurrentRegion(null);
          setCurrentCell(null);

          // 상위 Region 찾기
          if (location) {
            const region = regions.find(r => r.region_id === location.region_id);
            setCurrentRegion(region || null);

            // 하위 Cell 로드
            try {
              const response = await cellsApi.getByLocation(location.location_id);
              setLocationCells(response.data || []);
            } catch (error) {
              console.error('Cell 로드 실패:', error);
              setLocationCells([]);
            }
          }
        } else if (pin.pin_type === 'cell') {
          // Cell 찾기
          const cell = cells.find(c => c.cell_id === pin.game_data_id);
          setCurrentCell(cell || null);
          setCurrentRegion(null);
          setCurrentLocation(null);

          // 상위 Location과 Region 찾기
          if (cell) {
            const location = locations.find(l => l.location_id === cell.location_id);
            setCurrentLocation(location || null);
            if (location) {
              const region = regions.find(r => r.region_id === location.region_id);
              setCurrentRegion(region || null);
            }
          }
        }
      } catch (error) {
        console.error('게임 데이터 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadGameData();
  }, [pin, regions, locations, cells]);

  // 섹션 토글
  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  // Region 연결/변경
  const handleConnectRegion = async (regionId: string) => {
    if (!pin || pin.pin_type !== 'region') return;

    try {
      setSaving(true);
      // 핀의 game_data_id를 region_id로 업데이트
      // 실제로는 핀을 삭제하고 새로 만들어야 할 수도 있음
      // 여기서는 핀 업데이트 API가 game_data_id를 변경할 수 없다고 가정
      alert('핀의 게임 데이터 ID는 변경할 수 없습니다. 핀을 삭제하고 새로 만들어주세요.');
    } catch (error) {
      console.error('Region 연결 실패:', error);
      alert('Region 연결에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  // Location 추가
  const handleAddLocation = async () => {
    if (!currentRegion) return;

    const locationName = prompt('새 Location 이름을 입력하세요:');
    if (!locationName) return;

    try {
      setSaving(true);
      const newLocation = await locationsApi.create({
        location_id: `LOC_${Date.now()}`,
        region_id: currentRegion.region_id,
        location_name: locationName,
        location_description: '',
        location_type: '',
        location_properties: {},
      });

      if (onRefresh) {
        await onRefresh();
      }
      alert('Location이 추가되었습니다.');
    } catch (error) {
      console.error('Location 추가 실패:', error);
      alert('Location 추가에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  // Cell 추가
  const handleAddCell = async () => {
    if (!currentLocation) return;

    const cellName = prompt('새 Cell 이름을 입력하세요:');
    if (!cellName) return;

    try {
      setSaving(true);
      const newCell = await cellsApi.create({
        cell_id: `CELL_${Date.now()}`,
        location_id: currentLocation.location_id,
        cell_name: cellName,
        matrix_width: 10,
        matrix_height: 10,
        cell_description: '',
        cell_properties: {},
      });

      if (onRefresh) {
        await onRefresh();
      }
      alert('Cell이 추가되었습니다.');
    } catch (error) {
      console.error('Cell 추가 실패:', error);
      alert('Cell 추가에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  if (!pin) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
        핀을 선택하세요
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        로딩 중...
      </div>
    );
  }

  // D&D 정보 편집 모드
  if (editingMode === 'dnd') {
    const gameData = currentRegion || currentLocation || currentCell;
    if (!gameData) return null;

    const properties = (gameData as any)[
      pin.pin_type === 'region' ? 'region_properties' :
      pin.pin_type === 'location' ? 'location_properties' : 'cell_properties'
    ];
    const dndInfo = properties?.dnd_info;

    return (
      <DnDInfoForm
        gameDataId={pin.game_data_id}
        pinType={pin.pin_type}
        initialData={dndInfo || undefined}
        onSave={async (data) => {
          try {
            setSaving(true);
            const properties = {
              ...((gameData as any)[
                pin.pin_type === 'region' ? 'region_properties' :
                pin.pin_type === 'location' ? 'location_properties' : 'cell_properties'
              ] || {}),
              dnd_info: data,
            };

            if (pin.pin_type === 'region') {
              await regionsApi.update(pin.game_data_id, { region_properties: properties });
            } else if (pin.pin_type === 'location') {
              await locationsApi.update(pin.game_data_id, { location_properties: properties });
            } else if (pin.pin_type === 'cell') {
              await cellsApi.update(pin.game_data_id, { cell_properties: properties });
            }

            if (onRefresh) {
              await onRefresh();
            }
            setEditingMode(null);
            alert('D&D 정보가 저장되었습니다.');
          } catch (error) {
            console.error('D&D 정보 저장 실패:', error);
            alert('저장에 실패했습니다.');
          } finally {
            setSaving(false);
          }
        }}
        onCancel={() => setEditingMode(null)}
      />
    );
  }

  return (
    <div style={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#fff',
    }}>
      {/* 헤더 */}
      <div style={{
        padding: '15px',
        backgroundColor: '#f5f5f5',
        borderBottom: '1px solid #ddd',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold' }}>
            {pin.pin_type === 'region' ? '지역' : pin.pin_type === 'location' ? '위치' : '셀'} 편집
          </h3>
          <div style={{ fontSize: '12px', color: '#666', marginTop: '3px' }}>
            핀 ID: {pin.pin_id}
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            style={{
              padding: '5px 10px',
              backgroundColor: '#f44336',
              color: '#fff',
              border: 'none',
              borderRadius: '3px',
              cursor: 'pointer',
            }}
          >
            ✕
          </button>
        )}
      </div>

      {/* 스크롤 가능한 콘텐츠 */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '15px',
      }}>
        {/* Region 섹션 */}
        {currentRegion && (
          <section style={{ marginBottom: '20px' }}>
            <div
              onClick={() => toggleSection('region')}
              style={{
                padding: '10px',
                backgroundColor: '#FF6B9D',
                color: '#fff',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderRadius: '3px',
                marginBottom: '10px',
              }}
            >
              <strong>지역 (Region): {currentRegion.region_name}</strong>
              <span>{expandedSections.has('region') ? '▼' : '▶'}</span>
            </div>

            {expandedSections.has('region') && (
              <div style={{ padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '3px' }}>
                <div style={{ marginBottom: '10px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                    지역 이름
                  </label>
                  <input
                    type="text"
                    defaultValue={currentRegion.region_name}
                    onBlur={async (e) => {
                      if (e.target.value !== currentRegion.region_name) {
                        try {
                          await regionsApi.update(currentRegion.region_id, { region_name: e.target.value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                          alert('업데이트에 실패했습니다.');
                        }
                      }
                    }}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '3px',
                    }}
                  />
                </div>

                <div style={{ marginBottom: '10px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                    설명
                  </label>
                  <textarea
                    defaultValue={currentRegion.region_description || ''}
                    onBlur={async (e) => {
                      if (e.target.value !== (currentRegion.region_description || '')) {
                        try {
                          await regionsApi.update(currentRegion.region_id, { region_description: e.target.value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                        }
                      }
                    }}
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '3px',
                    }}
                  />
                </div>

                <div style={{ marginBottom: '10px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                    타입
                  </label>
                  <input
                    type="text"
                    defaultValue={currentRegion.region_type || ''}
                    onBlur={async (e) => {
                      if (e.target.value !== (currentRegion.region_type || '')) {
                        try {
                          await regionsApi.update(currentRegion.region_id, { region_type: e.target.value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                        }
                      }
                    }}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '3px',
                    }}
                  />
                </div>

                <button
                  onClick={() => setEditingMode('dnd')}
                  style={{
                    width: '100%',
                    padding: '8px',
                    backgroundColor: '#4ECDC4',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '3px',
                    cursor: 'pointer',
                    marginTop: '10px',
                  }}
                >
                  D&D 정보 편집
                </button>
              </div>
            )}
          </section>
        )}

        {/* Location 섹션 */}
        {pin.pin_type === 'region' && currentRegion && (
          <section style={{ marginBottom: '20px' }}>
            <div
              onClick={() => toggleSection('locations')}
              style={{
                padding: '10px',
                backgroundColor: '#4ECDC4',
                color: '#fff',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderRadius: '3px',
                marginBottom: '10px',
              }}
            >
              <strong>하위 위치 (Locations) ({regionLocations.length})</strong>
              <span>{expandedSections.has('locations') ? '▼' : '▶'}</span>
            </div>

            {expandedSections.has('locations') && (
              <div style={{ padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '3px' }}>
                <button
                  onClick={handleAddLocation}
                  style={{
                    width: '100%',
                    padding: '8px',
                    backgroundColor: '#4CAF50',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '3px',
                    cursor: 'pointer',
                    marginBottom: '10px',
                  }}
                >
                  + Location 추가
                </button>

                {regionLocations.map((location) => (
                  <div
                    key={location.location_id}
                    style={{
                      padding: '8px',
                      marginBottom: '5px',
                      backgroundColor: '#fff',
                      border: '1px solid #ddd',
                      borderRadius: '3px',
                    }}
                  >
                    <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                      {location.location_name}
                    </div>
                    <div style={{ fontSize: '11px', color: '#666' }}>
                      {location.location_description || '설명 없음'}
                    </div>
                    <div style={{ fontSize: '10px', color: '#999', marginTop: '3px' }}>
                      ID: {location.location_id}
                    </div>
                  </div>
                ))}

                {regionLocations.length === 0 && (
                  <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                    하위 Location이 없습니다.
                  </div>
                )}
              </div>
            )}
          </section>
        )}

        {/* Location 편집 (핀이 location인 경우) */}
        {pin.pin_type === 'location' && currentLocation && (
          <section style={{ marginBottom: '20px' }}>
            <div
              onClick={() => toggleSection('location')}
              style={{
                padding: '10px',
                backgroundColor: '#4ECDC4',
                color: '#fff',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderRadius: '3px',
                marginBottom: '10px',
              }}
            >
              <strong>위치 (Location): {currentLocation.location_name}</strong>
              <span>{expandedSections.has('location') ? '▼' : '▶'}</span>
            </div>

            {expandedSections.has('location') && (
              <div style={{ padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '3px' }}>
                <div style={{ marginBottom: '10px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                    위치 이름
                  </label>
                  <input
                    type="text"
                    defaultValue={currentLocation.location_name}
                    onBlur={async (e) => {
                      if (e.target.value !== currentLocation.location_name) {
                        try {
                          await locationsApi.update(currentLocation.location_id, { location_name: e.target.value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                        }
                      }
                    }}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '3px',
                    }}
                  />
                </div>

                <div style={{ marginBottom: '10px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                    설명
                  </label>
                  <textarea
                    defaultValue={currentLocation.location_description || ''}
                    onBlur={async (e) => {
                      if (e.target.value !== (currentLocation.location_description || '')) {
                        try {
                          await locationsApi.update(currentLocation.location_id, { location_description: e.target.value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                        }
                      }
                    }}
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '3px',
                    }}
                  />
                </div>

                <button
                  onClick={() => setEditingMode('dnd')}
                  style={{
                    width: '100%',
                    padding: '8px',
                    backgroundColor: '#4ECDC4',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '3px',
                    cursor: 'pointer',
                    marginTop: '10px',
                  }}
                >
                  D&D 정보 편집
                </button>
              </div>
            )}
          </section>
        )}

        {/* Cell 섹션 */}
        {(pin.pin_type === 'region' || pin.pin_type === 'location') && currentLocation && (
          <section style={{ marginBottom: '20px' }}>
            <div
              onClick={() => toggleSection('cells')}
              style={{
                padding: '10px',
                backgroundColor: '#95E1D3',
                color: '#fff',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderRadius: '3px',
                marginBottom: '10px',
              }}
            >
              <strong>하위 셀 (Cells) ({locationCells.length})</strong>
              <span>{expandedSections.has('cells') ? '▼' : '▶'}</span>
            </div>

            {expandedSections.has('cells') && (
              <div style={{ padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '3px' }}>
                {pin.pin_type === 'location' && (
                  <button
                    onClick={handleAddCell}
                    style={{
                      width: '100%',
                      padding: '8px',
                      backgroundColor: '#4CAF50',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '3px',
                      cursor: 'pointer',
                      marginBottom: '10px',
                    }}
                  >
                    + Cell 추가
                  </button>
                )}

                {locationCells.map((cell) => (
                  <div
                    key={cell.cell_id}
                    style={{
                      padding: '8px',
                      marginBottom: '5px',
                      backgroundColor: '#fff',
                      border: '1px solid #ddd',
                      borderRadius: '3px',
                    }}
                  >
                    <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                      {cell.cell_name || cell.cell_id}
                    </div>
                    <div style={{ fontSize: '11px', color: '#666' }}>
                      크기: {cell.matrix_width} x {cell.matrix_height}
                    </div>
                    <div style={{ fontSize: '10px', color: '#999', marginTop: '3px' }}>
                      ID: {cell.cell_id}
                    </div>
                  </div>
                ))}

                {locationCells.length === 0 && (
                  <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                    하위 Cell이 없습니다.
                  </div>
                )}
              </div>
            )}
          </section>
        )}

        {/* Cell 편집 (핀이 cell인 경우) */}
        {pin.pin_type === 'cell' && currentCell && (
          <section style={{ marginBottom: '20px' }}>
            <div
              onClick={() => toggleSection('cell')}
              style={{
                padding: '10px',
                backgroundColor: '#95E1D3',
                color: '#fff',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderRadius: '3px',
                marginBottom: '10px',
              }}
            >
              <strong>셀 (Cell): {currentCell.cell_name || currentCell.cell_id}</strong>
              <span>{expandedSections.has('cell') ? '▼' : '▶'}</span>
            </div>

            {expandedSections.has('cell') && (
              <div style={{ padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '3px' }}>
                <div style={{ marginBottom: '10px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                    셀 이름
                  </label>
                  <input
                    type="text"
                    defaultValue={currentCell.cell_name || ''}
                    onBlur={async (e) => {
                      if (e.target.value !== (currentCell.cell_name || '')) {
                        try {
                          await cellsApi.update(currentCell.cell_id, { cell_name: e.target.value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                        }
                      }
                    }}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '3px',
                    }}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '10px' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                      너비
                    </label>
                    <input
                      type="number"
                      defaultValue={currentCell.matrix_width}
                      onBlur={async (e) => {
                        const value = parseInt(e.target.value);
                        if (!isNaN(value) && value !== currentCell.matrix_width) {
                          try {
                            await cellsApi.update(currentCell.cell_id, { matrix_width: value });
                            if (onRefresh) await onRefresh();
                          } catch (error) {
                            console.error('업데이트 실패:', error);
                          }
                        }
                      }}
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '3px',
                      }}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                      높이
                    </label>
                    <input
                      type="number"
                      defaultValue={currentCell.matrix_height}
                      onBlur={async (e) => {
                        const value = parseInt(e.target.value);
                        if (!isNaN(value) && value !== currentCell.matrix_height) {
                          try {
                            await cellsApi.update(currentCell.cell_id, { matrix_height: value });
                            if (onRefresh) await onRefresh();
                          } catch (error) {
                            console.error('업데이트 실패:', error);
                          }
                        }
                      }}
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '3px',
                      }}
                    />
                  </div>
                </div>

                <div style={{ marginBottom: '10px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                    설명
                  </label>
                  <textarea
                    defaultValue={currentCell.cell_description || ''}
                    onBlur={async (e) => {
                      if (e.target.value !== (currentCell.cell_description || '')) {
                        try {
                          await cellsApi.update(currentCell.cell_id, { cell_description: e.target.value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                        }
                      }
                    }}
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '3px',
                    }}
                  />
                </div>
              </div>
            )}
          </section>
        )}

        {/* Region이 없는 경우 - 생성/연결 UI */}
        {!currentRegion && pin.pin_type === 'region' && (
          <section style={{ marginBottom: '20px' }}>
            <div style={{
              padding: '15px',
              backgroundColor: '#fff3cd',
              border: '1px solid #ffc107',
              borderRadius: '3px',
            }}>
              <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', fontWeight: 'bold' }}>
                Region 연결 필요
              </h4>
              <p style={{ fontSize: '12px', margin: '0 0 15px 0', color: '#666' }}>
                이 핀에 연결된 Region이 없습니다. Region을 생성하거나 기존 Region을 연결하세요.
              </p>

              <div style={{ display: 'flex', gap: '10px', flexDirection: 'column' }}>
                {/* Region 생성 */}
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                    새 Region 생성
                  </label>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <input
                      type="text"
                      id="new-region-name"
                      placeholder="Region 이름"
                      style={{
                        flex: 1,
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '3px',
                      }}
                    />
                    <button
                      onClick={async () => {
                        const nameInput = document.getElementById('new-region-name') as HTMLInputElement;
                        const regionName = nameInput?.value.trim();
                        if (!regionName) {
                          alert('Region 이름을 입력하세요.');
                          return;
                        }

                        try {
                          setSaving(true);
                          const result = await pinsApi.connectToRegion({
                            pin_id: pin.pin_id,
                            region_id: pin.game_data_id,
                            create_if_not_exists: true,
                            region_name: regionName,
                          });

                          if (onRefresh) {
                            await onRefresh();
                          }
                          alert(result.data?.message || 'Region이 생성되었습니다.');
                        } catch (error) {
                          console.error('Region 생성 실패:', error);
                          alert(`Region 생성에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
                        } finally {
                          setSaving(false);
                        }
                      }}
                      disabled={saving}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: saving ? '#ccc' : '#4CAF50',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '3px',
                        cursor: saving ? 'not-allowed' : 'pointer',
                      }}
                    >
                      {saving ? '생성 중...' : '생성'}
                    </button>
                  </div>
                </div>

                {/* 기존 Region 연결 */}
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                    기존 Region 연결
                  </label>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <select
                      id="existing-region-select"
                      style={{
                        flex: 1,
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '3px',
                      }}
                    >
                      <option value="">Region 선택</option>
                      {regions.map(region => (
                        <option key={region.region_id} value={region.region_id}>
                          {region.region_name} ({region.region_id})
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={async () => {
                        const select = document.getElementById('existing-region-select') as HTMLSelectElement;
                        const selectedRegionId = select?.value;
                        if (!selectedRegionId) {
                          alert('연결할 Region을 선택하세요.');
                          return;
                        }

                        // 핀의 game_data_id를 선택한 region_id로 변경
                        // 하지만 핀의 game_data_id는 변경할 수 없으므로,
                        // 핀을 삭제하고 새로 만들어야 할 수도 있습니다.
                        // 또는 핀 업데이트 API가 game_data_id 변경을 지원하는지 확인 필요
                        
                        try {
                          setSaving(true);
                          const result = await pinsApi.connectToRegion({
                            pin_id: pin.pin_id,
                            region_id: selectedRegionId,
                            create_if_not_exists: false,
                          });

                          if (onRefresh) {
                            await onRefresh();
                          }
                          alert(result.data?.message || 'Region이 연결되었습니다.');
                        } catch (error) {
                          console.error('Region 연결 실패:', error);
                          alert(`Region 연결에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
                        } finally {
                          setSaving(false);
                        }
                      }}
                      disabled={saving || regions.length === 0}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: saving || regions.length === 0 ? '#ccc' : '#2196F3',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '3px',
                        cursor: saving || regions.length === 0 ? 'not-allowed' : 'pointer',
                      }}
                    >
                      {saving ? '연결 중...' : '연결'}
                    </button>
                  </div>
                  {regions.length === 0 && (
                    <div style={{ fontSize: '11px', color: '#999', marginTop: '5px' }}>
                      연결할 Region이 없습니다. 새로 생성하세요.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Location이 없는 경우 */}
        {pin.pin_type === 'location' && !currentLocation && (
          <section style={{ marginBottom: '20px' }}>
            <div style={{
              padding: '15px',
              backgroundColor: '#fff3cd',
              border: '1px solid #ffc107',
              borderRadius: '3px',
            }}>
              <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', fontWeight: 'bold' }}>
                Location 연결 필요
              </h4>
              <p style={{ fontSize: '12px', margin: '0 0 15px 0', color: '#666' }}>
                이 핀에 연결된 Location이 없습니다.
              </p>

              <div style={{ display: 'flex', gap: '10px', flexDirection: 'column' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                    새 Location 생성
                  </label>
                  <div style={{ display: 'flex', gap: '5px', marginBottom: '10px' }}>
                    <select
                      id="location-region-select"
                      style={{
                        flex: 1,
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '3px',
                      }}
                    >
                      <option value="">상위 Region 선택</option>
                      {regions.map(region => (
                        <option key={region.region_id} value={region.region_id}>
                          {region.region_name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <input
                      type="text"
                      id="new-location-name"
                      placeholder="Location 이름"
                      style={{
                        flex: 1,
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '3px',
                      }}
                    />
                    <button
                      onClick={async () => {
                        const nameInput = document.getElementById('new-location-name') as HTMLInputElement;
                        const regionSelect = document.getElementById('location-region-select') as HTMLSelectElement;
                        const locationName = nameInput?.value.trim();
                        const regionId = regionSelect?.value;

                        if (!locationName) {
                          alert('Location 이름을 입력하세요.');
                          return;
                        }
                        if (!regionId) {
                          alert('상위 Region을 선택하세요.');
                          return;
                        }

                        try {
                          setSaving(true);
                          const result = await pinsApi.connectToLocation({
                            pin_id: pin.pin_id,
                            location_id: pin.game_data_id,
                            create_if_not_exists: true,
                            location_name: locationName,
                            region_id: regionId,
                          });

                          if (onRefresh) {
                            await onRefresh();
                          }
                          alert(result.data?.message || 'Location이 생성되었습니다.');
                        } catch (error) {
                          console.error('Location 생성 실패:', error);
                          alert(`Location 생성에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
                        } finally {
                          setSaving(false);
                        }
                      }}
                      disabled={saving || regions.length === 0}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: saving || regions.length === 0 ? '#ccc' : '#4CAF50',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '3px',
                        cursor: saving || regions.length === 0 ? 'not-allowed' : 'pointer',
                      }}
                    >
                      {saving ? '생성 중...' : '생성'}
                    </button>
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                    기존 Location 연결
                  </label>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <select
                      id="existing-location-select"
                      style={{
                        flex: 1,
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '3px',
                      }}
                    >
                      <option value="">Location 선택</option>
                      {locations.map(location => (
                        <option key={location.location_id} value={location.location_id}>
                          {location.location_name} ({location.location_id})
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={async () => {
                        const select = document.getElementById('existing-location-select') as HTMLSelectElement;
                        const selectedLocationId = select?.value;
                        if (!selectedLocationId) {
                          alert('연결할 Location을 선택하세요.');
                          return;
                        }

                        try {
                          setSaving(true);
                          const result = await pinsApi.connectToLocation({
                            pin_id: pin.pin_id,
                            location_id: selectedLocationId,
                            create_if_not_exists: false,
                          });

                          if (onRefresh) {
                            await onRefresh();
                          }
                          alert(result.data?.message || 'Location이 연결되었습니다.');
                        } catch (error) {
                          console.error('Location 연결 실패:', error);
                          alert(`Location 연결에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
                        } finally {
                          setSaving(false);
                        }
                      }}
                      disabled={saving || locations.length === 0}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: saving || locations.length === 0 ? '#ccc' : '#2196F3',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '3px',
                        cursor: saving || locations.length === 0 ? 'not-allowed' : 'pointer',
                      }}
                    >
                      {saving ? '연결 중...' : '연결'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Cell이 없는 경우 */}
        {pin.pin_type === 'cell' && !currentCell && (
          <section style={{ marginBottom: '20px' }}>
            <div style={{
              padding: '15px',
              backgroundColor: '#fff3cd',
              border: '1px solid #ffc107',
              borderRadius: '3px',
            }}>
              <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', fontWeight: 'bold' }}>
                Cell 연결 필요
              </h4>
              <p style={{ fontSize: '12px', margin: '0 0 15px 0', color: '#666' }}>
                이 핀에 연결된 Cell이 없습니다.
              </p>

              <div style={{ display: 'flex', gap: '10px', flexDirection: 'column' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                    새 Cell 생성
                  </label>
                  <div style={{ display: 'flex', gap: '5px', marginBottom: '10px' }}>
                    <select
                      id="cell-location-select"
                      style={{
                        flex: 1,
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '3px',
                      }}
                    >
                      <option value="">상위 Location 선택</option>
                      {locations.map(location => (
                        <option key={location.location_id} value={location.location_id}>
                          {location.location_name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <input
                      type="text"
                      id="new-cell-name"
                      placeholder="Cell 이름"
                      style={{
                        flex: 1,
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '3px',
                      }}
                    />
                    <button
                      onClick={async () => {
                        const nameInput = document.getElementById('new-cell-name') as HTMLInputElement;
                        const locationSelect = document.getElementById('cell-location-select') as HTMLSelectElement;
                        const cellName = nameInput?.value.trim();
                        const locationId = locationSelect?.value;

                        if (!cellName) {
                          alert('Cell 이름을 입력하세요.');
                          return;
                        }
                        if (!locationId) {
                          alert('상위 Location을 선택하세요.');
                          return;
                        }

                        try {
                          setSaving(true);
                          const result = await pinsApi.connectToCell({
                            pin_id: pin.pin_id,
                            cell_id: pin.game_data_id,
                            create_if_not_exists: true,
                            cell_name: cellName,
                            location_id: locationId,
                          });

                          if (onRefresh) {
                            await onRefresh();
                          }
                          alert(result.data?.message || 'Cell이 생성되었습니다.');
                        } catch (error) {
                          console.error('Cell 생성 실패:', error);
                          alert(`Cell 생성에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
                        } finally {
                          setSaving(false);
                        }
                      }}
                      disabled={saving || locations.length === 0}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: saving || locations.length === 0 ? '#ccc' : '#4CAF50',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '3px',
                        cursor: saving || locations.length === 0 ? 'not-allowed' : 'pointer',
                      }}
                    >
                      {saving ? '생성 중...' : '생성'}
                    </button>
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>
                    기존 Cell 연결
                  </label>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <select
                      id="existing-cell-select"
                      style={{
                        flex: 1,
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '3px',
                      }}
                    >
                      <option value="">Cell 선택</option>
                      {cells.map(cell => (
                        <option key={cell.cell_id} value={cell.cell_id}>
                          {cell.cell_name || cell.cell_id} ({cell.cell_id})
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={async () => {
                        const select = document.getElementById('existing-cell-select') as HTMLSelectElement;
                        const selectedCellId = select?.value;
                        if (!selectedCellId) {
                          alert('연결할 Cell을 선택하세요.');
                          return;
                        }

                        try {
                          setSaving(true);
                          const result = await pinsApi.connectToCell({
                            pin_id: pin.pin_id,
                            cell_id: selectedCellId,
                            create_if_not_exists: false,
                          });

                          if (onRefresh) {
                            await onRefresh();
                          }
                          alert(result.data?.message || 'Cell이 연결되었습니다.');
                        } catch (error) {
                          console.error('Cell 연결 실패:', error);
                          alert(`Cell 연결에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`);
                        } finally {
                          setSaving(false);
                        }
                      }}
                      disabled={saving || cells.length === 0}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: saving || cells.length === 0 ? '#ccc' : '#2196F3',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '3px',
                        cursor: saving || cells.length === 0 ? 'not-allowed' : 'pointer',
                      }}
                    >
                      {saving ? '연결 중...' : '연결'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}
      </div>

      {/* 푸터 버튼 */}
      <div style={{
        padding: '15px',
        borderTop: '1px solid #ddd',
        display: 'flex',
        gap: '10px',
        justifyContent: 'flex-end',
      }}>
        {onPinDelete && (
          <button
            onClick={async () => {
              if (!confirm(`핀 "${pin.game_data_id}"를 삭제하시겠습니까?`)) {
                return;
              }
              try {
                if (onPinDelete) {
                  await onPinDelete(pin.pin_id);
                }
                if (onClose) {
                  onClose();
                }
              } catch (error) {
                console.error('삭제 실패:', error);
                alert('삭제에 실패했습니다.');
              }
            }}
            style={{
              padding: '8px 16px',
              backgroundColor: '#f44336',
              color: '#fff',
              border: 'none',
              borderRadius: '3px',
              cursor: 'pointer',
            }}
          >
            핀 삭제
          </button>
        )}
      </div>
    </div>
  );
};
