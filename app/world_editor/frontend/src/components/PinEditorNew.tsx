/**
 * 핀 전문 편집기 패널 - 5개 탭 구조
 */
import React, { useState, useEffect } from 'react';
import { PinData, RegionData, LocationData, CellData, DnDLocationInfo } from '../types';
import { regionsApi, locationsApi, cellsApi, pinsApi } from '../services/api';
import { CollapsibleSection } from './ui/CollapsibleSection';
import { FormField } from './ui/FormField';
import { InputField } from './ui/InputField';
import { DetailSectionEditor, DetailSection } from './ui/DetailSectionEditor';
import { Tabs } from './ui/Tabs';
import { LocationEditorModal } from './LocationEditorModal';
import { CellEditorModal } from './CellEditorModal';
import { EntityEditorModal } from './EntityEditorModal';
import { EntityPickerModal } from './EntityPickerModal';
import { managementApi, entitiesApi } from '../services/api';

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

export const PinEditorNew: React.FC<PinEditorProps> = ({
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
  const [cellEntities, setCellEntities] = useState<any[]>([]);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [locationModalOpen, setLocationModalOpen] = useState(false);
  const [selectedLocationId, setSelectedLocationId] = useState<string | null>(null);
  const [cellModalOpen, setCellModalOpen] = useState(false);
  const [selectedCellId, setSelectedCellId] = useState<string | null>(null);
  const [npcs, setNpcs] = useState<any[]>([]);
  const [editingEntityId, setEditingEntityId] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [showConnectDialog, setShowConnectDialog] = useState(false);
  const [entityPickerOpen, setEntityPickerOpen] = useState(false);
  const [entityPickerTarget, setEntityPickerTarget] = useState<'location' | 'cell' | null>(null);

  // 게임플레이 설정
  const [playSettings, setPlaySettings] = useState({
    climate: '',
    danger_level: 1,
    recommended_level_min: 1,
    recommended_level_max: 10,
    bgm: '',
    ambient_effects: '',
  });

  // 지역 정보 (구조화된 정보)
  const [regionInfo, setRegionInfo] = useState<DnDLocationInfo>({
    name: '',
    description: '',
    type: '',
    demographics: {
      population: 0,
      races: {},
      classes: {},
    },
    economy: {
      primary_industry: '',
      trade_goods: [],
      gold_value: 0,
    },
    government: {
      type: '',
      leader: '',
      laws: [],
    },
    culture: {
      religion: [],
      customs: [],
      festivals: [],
    },
    lore: {
      history: '',
      legends: [],
      secrets: [],
    },
    npcs: [],
    quests: [],
    shops: [],
  });

  // 상세 정보 섹션
  const [detailSections, setDetailSections] = useState<DetailSection[]>([]);

  // Location 정보 상태
  const [locationInfo, setLocationInfo] = useState({
    ownership: {
      owner_entity_id: '',
      ownership_type: '',
    },
    lore: {
      history: '',
      legends: [] as string[],
    },
    detail_sections: [] as DetailSection[],
  });

  // Cell 정보 상태
  const [cellInfo, setCellInfo] = useState({
    ownership: {
      owner_entity_id: '',
      is_private: false,
    },
    lore: {
      history: '',
      legends: [] as string[],
    },
    detail_sections: [] as DetailSection[],
    environment: {
      terrain: '',
      weather: '',
      lighting: '',
    },
  });

  // 핀 데이터 로드 및 연결된 게임 데이터 찾기
  useEffect(() => {
    const loadGameData = async () => {
      if (!pin) {
        setCurrentRegion(null);
        setCurrentLocation(null);
        setCurrentCell(null);
        setRegionLocations([]);
        setLocationCells([]);
        setCellEntities([]);
        return;
      }

      setLoading(true);
      try {
        // 연결 상태 확인
        const isTemporaryId = pin.game_data_id.startsWith('PIN_');
        let connected = false;
        
        if (pin.pin_type === 'region') {
          const region = regions.find(r => r.region_id === pin.game_data_id);
          setCurrentRegion(region || null);
          setCurrentLocation(null);
          setCurrentCell(null);
          setLocationCells([]);
          setCellEntities([]);
          setNpcs([]);
          connected = !!region && !isTemporaryId;

          if (region) {
            let loadedLocations: LocationData[] = [];
            try {
              const response = await locationsApi.getByRegion(region.region_id);
              loadedLocations = response.data || [];
              setRegionLocations(loadedLocations);
            } catch (error) {
              console.error('Location 로드 실패:', error);
              setRegionLocations([]);
            }

            // NPCs 로드 (region의 모든 locations와 cells에 속한 NPCs)
            try {
              const allNpcs: any[] = [];
              for (const loc of loadedLocations) {
                // Location의 NPCs
                try {
                  const npcResponse = await entitiesApi.getByLocation(loc.location_id);
                  if (npcResponse.data) {
                    allNpcs.push(...(Array.isArray(npcResponse.data) ? npcResponse.data : [npcResponse.data]));
                  }
                } catch (e) {
                  // NPC가 없을 수 있음
                }
                
                // Location의 Cells에 속한 NPCs
                try {
                  const cellsResponse = await cellsApi.getByLocation(loc.location_id);
                  const locationCells = cellsResponse.data || [];
                  for (const cell of locationCells) {
                    try {
                      const cellNpcResponse = await entitiesApi.getByCell(cell.cell_id);
                      if (cellNpcResponse.data) {
                        allNpcs.push(...(Array.isArray(cellNpcResponse.data) ? cellNpcResponse.data : [cellNpcResponse.data]));
                      }
                    } catch (e) {
                      // NPC가 없을 수 있음
                    }
                  }
                } catch (e) {
                  // Cells가 없을 수 있음
                }
              }
              setNpcs(allNpcs);
            } catch (error) {
              console.error('NPC 로드 실패:', error);
              setNpcs([]);
            }

            // 게임플레이 설정 로드
            if (region.region_properties?.dnd_stats) {
              setPlaySettings({
                climate: region.region_properties.dnd_stats.climate || '',
                danger_level: region.region_properties.dnd_stats.danger_level || 1,
                recommended_level_min: region.region_properties.dnd_stats.recommended_level?.min || 1,
                recommended_level_max: region.region_properties.dnd_stats.recommended_level?.max || 10,
                bgm: region.region_properties.dnd_stats.bgm || '',
                ambient_effects: Array.isArray(region.region_properties.dnd_stats.ambient_effects)
                  ? region.region_properties.dnd_stats.ambient_effects.join(', ')
                  : region.region_properties.dnd_stats.ambient_effects || '',
              });
            }

            // Region 정보 로드 (region_properties에서)
            if (region.region_properties?.dnd_structured_info) {
              setRegionInfo(region.region_properties.dnd_structured_info);
            } else {
              // 기본값으로 초기화
              setRegionInfo({
                name: region.region_name || '',
                description: region.region_description || '',
                type: region.region_type || '',
                demographics: { population: 0, races: {}, classes: {} },
                economy: { primary_industry: '', trade_goods: [], gold_value: 0 },
                government: { type: '', leader: '', laws: [] },
                culture: { religion: [], customs: [], festivals: [] },
                lore: { history: '', legends: [], secrets: [] },
                npcs: [],
                quests: [],
                shops: [],
              });
            }

            // 상세 정보 섹션 로드
            if (region.region_properties?.detail_sections) {
              setDetailSections(region.region_properties.detail_sections);
            } else {
              setDetailSections([]);
            }
          }
        } else if (pin.pin_type === 'location') {
          const location = locations.find(l => l.location_id === pin.game_data_id);
          setCurrentLocation(location || null);
          setCurrentRegion(null);
          setCurrentCell(null);
          setRegionLocations([]);
          setCellEntities([]);
          setNpcs([]);
          connected = !!location && !isTemporaryId;

          if (location) {
            const region = regions.find(r => r.region_id === location.region_id);
            setCurrentRegion(region || null);

            // Location의 Cells 로드
            let loadedCells: CellData[] = [];
            try {
              const cellsResponse = await cellsApi.getByLocation(location.location_id);
              loadedCells = cellsResponse.data || [];
              setLocationCells(loadedCells);
            } catch (error) {
              console.error('Cells 로드 실패:', error);
              setLocationCells([]);
            }

            // Location의 Entities 로드 (Location과 하위 Cells 모두)
            try {
              const allNpcs: any[] = [];
              
              // Location의 직접 NPCs
              try {
                const entitiesResponse = await entitiesApi.getByLocation(location.location_id);
                if (entitiesResponse.data) {
                  allNpcs.push(...(Array.isArray(entitiesResponse.data) ? entitiesResponse.data : [entitiesResponse.data]));
                }
              } catch (e) {
                // NPC가 없을 수 있음
              }
              
              // Location의 Cells에 속한 NPCs
              for (const cell of loadedCells) {
                try {
                  const cellNpcResponse = await entitiesApi.getByCell(cell.cell_id);
                  if (cellNpcResponse.data) {
                    allNpcs.push(...(Array.isArray(cellNpcResponse.data) ? cellNpcResponse.data : [cellNpcResponse.data]));
                  }
                } catch (e) {
                  // NPC가 없을 수 있음
                }
              }
              
              setNpcs(allNpcs);
            } catch (error) {
              console.error('Entities 로드 실패:', error);
              setNpcs([]);
            }

            // Location 게임플레이 설정 로드 (건물: background_music, ambient_effects)
            setPlaySettings({
              climate: '',
              danger_level: 1,
              recommended_level_min: 1,
              recommended_level_max: 10,
              bgm: location.location_properties?.background_music || '',
              ambient_effects: Array.isArray(location.location_properties?.ambient_effects)
                ? location.location_properties.ambient_effects.join(', ')
                : (location.location_properties?.ambient_effects || ''),
            });

            // Location 정보 로드
            setLocationInfo({
              ownership: {
                owner_entity_id: location.location_properties?.ownership?.owner_entity_id || '',
                ownership_type: location.location_properties?.ownership?.ownership_type || '',
              },
              lore: {
                history: location.location_properties?.lore?.history || '',
                legends: Array.isArray(location.location_properties?.lore?.legends)
                  ? location.location_properties.lore.legends
                  : [],
              },
              detail_sections: Array.isArray(location.location_properties?.detail_sections)
                ? location.location_properties.detail_sections
                : [],
            });
          }
        } else if (pin.pin_type === 'cell') {
          const cell = cells.find(c => c.cell_id === pin.game_data_id);
          setCurrentCell(cell || null);
          setCurrentLocation(null);
          setCurrentRegion(null);
          setRegionLocations([]);
          setLocationCells([]);
          setNpcs([]);
          connected = !!cell && !isTemporaryId;

          if (cell) {
            // Cell의 Location 찾기
            const location = locations.find(l => l.location_id === cell.location_id);
            setCurrentLocation(location || null);

            // Location의 Region 찾기
            if (location) {
              const region = regions.find(r => r.region_id === location.region_id);
              setCurrentRegion(region || null);
            }

            // Cell의 Entities 로드
            try {
              const entitiesResponse = await entitiesApi.getByCell(cell.cell_id);
              setCellEntities(Array.isArray(entitiesResponse.data) ? entitiesResponse.data : [entitiesResponse.data]);
            } catch (error) {
              console.error('Cell Entities 로드 실패:', error);
              setCellEntities([]);
            }

            // Cell 게임플레이 설정 로드 (방: cell_properties의 terrain, weather 등)
            setPlaySettings({
              climate: cell.cell_properties?.weather || '',
              danger_level: cell.cell_status === 'dangerous' ? 5 : 
                           cell.cell_status === 'locked' ? 3 : 1,
              recommended_level_min: 1,
              recommended_level_max: 10,
              bgm: '',
              ambient_effects: cell.cell_properties?.terrain || '',
            });

            // Cell 정보 로드
            setCellInfo({
              ownership: {
                owner_entity_id: cell.cell_properties?.ownership?.owner_entity_id || '',
                is_private: cell.cell_properties?.ownership?.is_private || false,
              },
              lore: {
                history: cell.cell_properties?.lore?.history || '',
                legends: Array.isArray(cell.cell_properties?.lore?.legends)
                  ? cell.cell_properties.lore.legends
                  : [],
              },
              detail_sections: Array.isArray(cell.cell_properties?.detail_sections)
                ? cell.cell_properties.detail_sections
                : [],
              environment: {
                terrain: cell.cell_properties?.environment?.terrain || cell.cell_properties?.terrain || '',
                weather: cell.cell_properties?.environment?.weather || cell.cell_properties?.weather || '',
                lighting: cell.cell_properties?.environment?.lighting || '',
              },
            });
          }
        }
        
        setIsConnected(connected);
        if (!connected && !isTemporaryId) {
          // 연결되지 않은 핀인 경우
          setShowConnectDialog(true);
        }
      } catch (error) {
        console.error('게임 데이터 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadGameData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pin?.pin_id, pin?.game_data_id]); // pin의 ID만 의존성으로 사용하여 불필요한 리렌더링 방지

  const handleSaveAll = async () => {
    if (!pin) return;

    try {
      setSaving(true);

      // 게임플레이 설정 및 지역 정보 저장
      if (pin.pin_type === 'region' && currentRegion) {
        const properties = {
          ...(currentRegion.region_properties || {}),
          dnd_stats: {
            climate: playSettings.climate,
            danger_level: playSettings.danger_level,
            recommended_level: {
              min: playSettings.recommended_level_min,
              max: playSettings.recommended_level_max,
            },
            bgm: playSettings.bgm,
            ambient_effects: playSettings.ambient_effects.split(',').map(s => s.trim()).filter(s => s),
          },
          dnd_structured_info: regionInfo,
          detail_sections: detailSections,
        };
        await regionsApi.update(currentRegion.region_id, { region_properties: properties });
      } else if (pin.pin_type === 'location' && currentLocation) {
        // Location: 건물 설정 (background_music, ambient_effects) + 정보 탭 데이터
        const properties = {
          ...(currentLocation.location_properties || {}),
          background_music: playSettings.bgm,
          ambient_effects: playSettings.ambient_effects.split(',').map(s => s.trim()).filter(s => s),
          ownership: locationInfo.ownership.owner_entity_id ? {
            owner_entity_id: locationInfo.ownership.owner_entity_id,
            ownership_type: locationInfo.ownership.ownership_type,
          } : undefined,
          lore: locationInfo.lore.history || locationInfo.lore.legends.length > 0 ? {
            history: locationInfo.lore.history,
            legends: locationInfo.lore.legends.filter(l => l.trim()),
          } : undefined,
          detail_sections: locationInfo.detail_sections.length > 0 ? locationInfo.detail_sections : undefined,
        };
        // undefined 값 제거
        Object.keys(properties).forEach(key => {
          if (properties[key as keyof typeof properties] === undefined) {
            delete properties[key as keyof typeof properties];
          }
        });
        await locationsApi.update(currentLocation.location_id, { location_properties: properties });
      } else if (pin.pin_type === 'cell' && currentCell) {
        // Cell: 방 설정 (terrain, weather는 cell_properties에 저장) + 정보 탭 데이터
        const properties = {
          ...(currentCell.cell_properties || {}),
          terrain: playSettings.ambient_effects || '',
          weather: playSettings.climate || '',
          ownership: cellInfo.ownership.owner_entity_id ? {
            owner_entity_id: cellInfo.ownership.owner_entity_id,
            is_private: cellInfo.ownership.is_private,
          } : undefined,
          lore: cellInfo.lore.history || cellInfo.lore.legends.length > 0 ? {
            history: cellInfo.lore.history,
            legends: cellInfo.lore.legends.filter(l => l.trim()),
          } : undefined,
          detail_sections: cellInfo.detail_sections.length > 0 ? cellInfo.detail_sections : undefined,
          environment: cellInfo.environment.terrain || cellInfo.environment.weather || cellInfo.environment.lighting ? {
            terrain: cellInfo.environment.terrain,
            weather: cellInfo.environment.weather,
            lighting: cellInfo.environment.lighting,
          } : undefined,
        };
        // undefined 값 제거
        Object.keys(properties).forEach(key => {
          if (properties[key as keyof typeof properties] === undefined) {
            delete properties[key as keyof typeof properties];
          }
        });
        await cellsApi.updateProperties(currentCell.cell_id, properties);
      }

      if (onRefresh) {
        await onRefresh();
      }
      alert('저장되었습니다.');
    } catch (error) {
      console.error('저장 실패:', error);
      alert('저장에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  if (!pin) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#999', fontSize: '10px' }}>
        핀을 선택하세요
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', fontSize: '10px' }}>
        로딩 중...
      </div>
    );
  }

  return (
    <div style={{
      height: '100%',
      width: '100%',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#fff',
      overflow: 'hidden',
      minHeight: 0,
    }}>
      {/* Header (고정) */}
      <div style={{
        flexShrink: 0,
        padding: '8px 12px',
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E0E0E0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {onClose && (
            <button
              onClick={onClose}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '14px',
                color: '#666',
                cursor: 'pointer',
                padding: '2px 4px',
              }}
            >
              ×
            </button>
          )}
          <span style={{ fontSize: '11px', fontWeight: 'bold', color: '#333' }}>
            {pin.pin_type === 'region' ? 'Region' : pin.pin_type === 'location' ? 'Location' : 'Cell'} Editor
          </span>
        </div>
      </div>
      
      <div style={{
        flexShrink: 0,
        padding: '4px 12px',
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E0E0E0',
        fontSize: '9px',
        color: '#999',
      }}>
        {pin.pin_name || `새 핀 ${pin.pin_id.slice(-4)}`}
      </div>

      {/* Tabs (고정) */}
      <div style={{ flexShrink: 0 }}>
        <Tabs
          tabs={[
            { id: 'overview', label: '개요' },
            { id: 'entities', label: '엔티티' },
            { id: 'info', label: '정보' },
            { id: 'settings', label: '설정' },
            { id: 'metadata', label: '메타' },
          ]}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
      </div>

      {/* Content (스크롤 가능) */}
      <div style={{
        flex: '1 1 auto',
        overflowY: 'scroll',
        overflowX: 'hidden',
        padding: '12px',
        minHeight: 0,
        WebkitOverflowScrolling: 'touch',
      }}>
        {/* 개요 탭 */}
        {activeTab === 'overview' && (currentRegion || currentLocation) && (
          <>
            <CollapsibleSection title="지역 기본 정보" defaultExpanded={true}>
              {currentRegion && (
                <>
                  <FormField label="ID" labelWidth={80}>
                    <InputField
                      type="text"
                      value={currentRegion.region_id}
                      onChange={() => {}}
                      readOnly
                      copyButton
                    />
                  </FormField>
                  <FormField label="이름" labelWidth={80}>
                    <InputField
                      type="text"
                      value={currentRegion.region_name}
                      onChange={async (value) => {
                        try {
                          await regionsApi.update(currentRegion.region_id, { region_name: value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                        }
                      }}
                    />
                  </FormField>
                  <FormField label="타입" labelWidth={80}>
                    <InputField
                      type="text"
                      value={currentRegion.region_type || ''}
                      onChange={async (value) => {
                        try {
                          await regionsApi.update(currentRegion.region_id, { region_type: value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                        }
                      }}
                    />
                  </FormField>
                  <FormField label="설명" labelWidth={80}>
                    <InputField
                      type="textarea"
                      value={currentRegion.region_description || ''}
                      onChange={async (value) => {
                        try {
                          await regionsApi.update(currentRegion.region_id, { region_description: value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                        }
                      }}
                      rows={5}
                    />
                  </FormField>
                </>
              )}
              {currentLocation && (
                <>
                  <FormField label="ID" labelWidth={80}>
                    <InputField
                      type="text"
                      value={currentLocation.location_id}
                      onChange={() => {}}
                      readOnly
                      copyButton
                    />
                  </FormField>
                  <FormField label="이름" labelWidth={80}>
                    <InputField
                      type="text"
                      value={currentLocation.location_name}
                      onChange={async (value) => {
                        try {
                          await locationsApi.update(currentLocation.location_id, { location_name: value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                        }
                      }}
                    />
                  </FormField>
                  <FormField label="타입" labelWidth={80}>
                    <InputField
                      type="text"
                      value={currentLocation.location_type || ''}
                      onChange={async (value) => {
                        try {
                          await locationsApi.update(currentLocation.location_id, { location_type: value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                        }
                      }}
                    />
                  </FormField>
                  <FormField label="설명" labelWidth={80}>
                    <InputField
                      type="textarea"
                      value={currentLocation.location_description || ''}
                      onChange={async (value) => {
                        try {
                          await locationsApi.update(currentLocation.location_id, { location_description: value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                        }
                      }}
                      rows={5}
                    />
                  </FormField>
                </>
              )}
              {currentCell && (
                <>
                  <FormField label="ID" labelWidth={80}>
                    <InputField
                      type="text"
                      value={currentCell.cell_id}
                      onChange={() => {}}
                      readOnly
                      copyButton
                    />
                  </FormField>
                  <FormField label="이름" labelWidth={80}>
                    <InputField
                      type="text"
                      value={currentCell.cell_name || ''}
                      onChange={async (value) => {
                        try {
                          await cellsApi.update(currentCell.cell_id, { cell_name: value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                        }
                      }}
                    />
                  </FormField>
                  <FormField label="크기" labelWidth={80}>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <div style={{ width: '60px' }}>
                        <InputField
                          type="number"
                          value={String(currentCell.matrix_width || 10)}
                          onChange={async (value) => {
                            try {
                              await cellsApi.update(currentCell.cell_id, { matrix_width: parseInt(value, 10) });
                              if (onRefresh) await onRefresh();
                            } catch (error) {
                              console.error('업데이트 실패:', error);
                            }
                          }}
                        />
                      </div>
                      <span style={{ fontSize: '10px', color: '#999' }}>×</span>
                      <div style={{ width: '60px' }}>
                        <InputField
                          type="number"
                          value={String(currentCell.matrix_height || 10)}
                          onChange={async (value) => {
                            try {
                              await cellsApi.update(currentCell.cell_id, { matrix_height: parseInt(value, 10) });
                              if (onRefresh) await onRefresh();
                            } catch (error) {
                              console.error('업데이트 실패:', error);
                            }
                          }}
                        />
                      </div>
                    </div>
                  </FormField>
                  <FormField label="설명" labelWidth={80}>
                    <InputField
                      type="textarea"
                      value={currentCell.cell_description || ''}
                      onChange={async (value) => {
                        try {
                          await cellsApi.update(currentCell.cell_id, { cell_description: value });
                          if (onRefresh) await onRefresh();
                        } catch (error) {
                          console.error('업데이트 실패:', error);
                        }
                      }}
                      rows={5}
                    />
                  </FormField>
                  {currentLocation && (
                    <FormField label="위치" labelWidth={80}>
                      <InputField
                        type="text"
                        value={`${currentLocation.location_name} (${currentLocation.location_id})`}
                        onChange={() => {}}
                        readOnly
                      />
                    </FormField>
                  )}
                </>
              )}
            </CollapsibleSection>
          </>
        )}

        {/* 엔티티 탭 - Region */}
        {activeTab === 'entities' && currentRegion && !currentLocation && !currentCell && (
          <>
            <CollapsibleSection 
              title="Locations" 
              count={regionLocations.length}
              defaultExpanded={true}
              actionButton={
                <button
                  onClick={async (e) => {
                    e.stopPropagation();
                    const locationName = prompt('Location 이름을 입력하세요:');
                    if (locationName && currentRegion) {
                      try {
                        await managementApi.createLocation({
                          region_id: currentRegion.region_id,
                          location_name: locationName,
                        });
                        if (onRefresh) await onRefresh();
                      } catch (error) {
                        console.error('Location 생성 실패:', error);
                        alert('Location 생성에 실패했습니다.');
                      }
                    }
                  }}
                  style={{
                    fontSize: '9px',
                    padding: '2px 8px',
                    backgroundColor: '#4CAF50',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '2px',
                    cursor: 'pointer',
                  }}
                >
                  + Add
                </button>
              }
            >
              {regionLocations.map((location) => {
                const locationCells = cells.filter(c => c.location_id === location.location_id);
                return (
                  <div key={location.location_id} style={{
                    marginBottom: '8px',
                    padding: '8px',
                    backgroundColor: '#f9f9f9',
                    border: '1px solid #E0E0E0',
                    borderRadius: '2px',
                  }}>
                    <div style={{ fontSize: '10px', fontWeight: 'bold', color: '#333' }}>
                      {location.location_id}
                    </div>
                    <div style={{ fontSize: '10px', color: '#666', marginTop: '2px' }}>
                      {location.location_name}
                    </div>
                    <div style={{ fontSize: '9px', color: '#999', marginTop: '2px' }}>
                      Type: {location.location_type || 'N/A'} | Cells: {locationCells.length}
                    </div>
                    <div style={{ marginTop: '4px', display: 'flex', gap: '4px' }}>
                      <button
                        onClick={() => {
                          setSelectedLocationId(location.location_id);
                          setLocationModalOpen(true);
                        }}
                        style={{
                          fontSize: '8px',
                          padding: '2px 6px',
                          backgroundColor: '#2196F3',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '2px',
                          cursor: 'pointer',
                        }}
                      >
                        편집
                      </button>
                      <button
                        onClick={async () => {
                          const cellName = prompt('Cell 이름을 입력하세요:');
                          if (cellName) {
                            try {
                              await managementApi.createCell({
                                location_id: location.location_id,
                                cell_name: cellName,
                                matrix_width: 10,
                                matrix_height: 10,
                              });
                              // Location 목록 새로고침 (로컬 상태만 업데이트)
                              if (currentRegion) {
                                try {
                                  const response = await locationsApi.getByRegion(currentRegion.region_id);
                                  setRegionLocations(response.data || []);
                                } catch (error) {
                                  console.error('Location 로드 실패:', error);
                                }
                              }
                              // onRefresh() 호출하지 않음 - 전체 새로고침 방지
                            } catch (error) {
                              console.error('Cell 생성 실패:', error);
                              alert('Cell 생성에 실패했습니다.');
                            }
                          }
                        }}
                        style={{
                          fontSize: '8px',
                          padding: '2px 6px',
                          backgroundColor: '#4CAF50',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '2px',
                          cursor: 'pointer',
                        }}
                      >
                        + Cell
                      </button>
                    </div>
                    {locationCells.length > 0 && (
                      <div style={{ marginTop: '8px' }}>
                        <CollapsibleSection title="Cells" defaultExpanded={false}>
                          {locationCells.map((cell) => (
                          <div key={cell.cell_id} style={{
                            marginBottom: '4px',
                            padding: '4px',
                            fontSize: '9px',
                            color: '#666',
                            backgroundColor: '#fff',
                            border: '1px solid #E0E0E0',
                            borderRadius: '2px',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                          }}>
                            <span>
                              {cell.cell_id} - {cell.cell_name || 'Unnamed'} ({cell.matrix_width}x{cell.matrix_height})
                            </span>
                            <button
                              onClick={() => {
                                setSelectedCellId(cell.cell_id);
                                setCellModalOpen(true);
                              }}
                              style={{
                                fontSize: '8px',
                                padding: '2px 6px',
                                backgroundColor: '#2196F3',
                                color: '#fff',
                                border: 'none',
                                borderRadius: '2px',
                                cursor: 'pointer',
                              }}
                            >
                              편집
                            </button>
                          </div>
                        ))}
                        </CollapsibleSection>
                      </div>
                    )}
                  </div>
                );
              })}
            </CollapsibleSection>

            <CollapsibleSection 
              title="인물 (NPCs)" 
              count={npcs.length}
              defaultExpanded={true}
              actionButton={
                <button
                  onClick={async (e) => {
                    e.stopPropagation();
                    const npcName = prompt('NPC 이름을 입력하세요:');
                    if (npcName && currentRegion && regionLocations.length > 0) {
                      const locationId = regionLocations[0].location_id; // 첫 번째 location에 추가
                      try {
                        // Entity ID 생성 (간단한 방식)
                        const entityId = `NPC_${npcName.toUpperCase().replace(/\s+/g, '_')}_${Date.now()}`;
                        await entitiesApi.create({
                          entity_id: entityId,
                          entity_type: 'npc',
                          entity_name: npcName,
                          entity_description: '',
                          entity_properties: {
                            location_id: locationId,
                            region_id: currentRegion.region_id,
                          },
                        });
                        // NPC 목록 새로고침 (로컬 상태만 업데이트, 전체 새로고침 방지)
                        if (currentRegion && regionLocations.length > 0) {
                          try {
                            const allNpcs: any[] = [];
                            for (const loc of regionLocations) {
                              try {
                                const npcResponse = await entitiesApi.getByLocation(loc.location_id);
                                if (npcResponse.data) {
                                  allNpcs.push(...(Array.isArray(npcResponse.data) ? npcResponse.data : [npcResponse.data]));
                                }
                              } catch (e) {
                                // NPC가 없을 수 있음
                              }
                            }
                            setNpcs(allNpcs);
                          } catch (error) {
                            console.error('NPC 로드 실패:', error);
                          }
                        }
                        // onRefresh() 호출하지 않음 - 전체 새로고침 방지
                      } catch (error) {
                        console.error('NPC 생성 실패:', error);
                        alert('NPC 생성에 실패했습니다.');
                      }
                    } else if (regionLocations.length === 0) {
                      alert('먼저 Location을 생성해주세요.');
                    }
                  }}
                  style={{
                    fontSize: '9px',
                    padding: '2px 8px',
                    backgroundColor: '#4CAF50',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '2px',
                    cursor: 'pointer',
                  }}
                >
                  + Add
                </button>
              }
            >
              {npcs.length === 0 ? (
                <div style={{ fontSize: '9px', color: '#999', padding: '8px' }}>
                  인물이 없습니다.
                </div>
              ) : (
                npcs.map((npc) => (
                  <div key={npc.entity_id} style={{
                    marginBottom: '4px',
                    padding: '4px 8px',
                    fontSize: '9px',
                    color: '#666',
                    backgroundColor: '#fff',
                    border: '1px solid #E0E0E0',
                    borderRadius: '2px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '8px',
                  }}>
                    <span style={{ flex: 1 }}>{npc.entity_id} - {npc.entity_name}</span>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <button
                        onClick={async (e) => {
                          e.stopPropagation();
                          setEditingEntityId(npc.entity_id);
                        }}
                        style={{
                          fontSize: '9px',
                          padding: '2px 6px',
                          backgroundColor: '#2196F3',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '2px',
                          cursor: 'pointer',
                        }}
                      >
                        편집
                      </button>
                      <button
                        onClick={async (e) => {
                          e.stopPropagation();
                          if (confirm(`정말로 "${npc.entity_name}"을(를) 삭제하시겠습니까?`)) {
                            try {
                              await entitiesApi.delete(npc.entity_id);
                              // NPC 목록 새로고침 (로컬 상태만 업데이트)
                              if (currentRegion && regionLocations.length > 0) {
                                try {
                                  const allNpcs: any[] = [];
                                  for (const loc of regionLocations) {
                                    try {
                                      const npcResponse = await entitiesApi.getByLocation(loc.location_id);
                                      if (npcResponse.data) {
                                        allNpcs.push(...(Array.isArray(npcResponse.data) ? npcResponse.data : [npcResponse.data]));
                                      }
                                    } catch (e) {
                                      // NPC가 없을 수 있음
                                    }
                                  }
                                  setNpcs(allNpcs);
                                } catch (error) {
                                  console.error('NPC 로드 실패:', error);
                                }
                              }
                            } catch (error) {
                              console.error('NPC 삭제 실패:', error);
                              alert('NPC 삭제에 실패했습니다.');
                            }
                          }
                        }}
                        style={{
                          fontSize: '9px',
                          padding: '2px 6px',
                          backgroundColor: '#f44336',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '2px',
                          cursor: 'pointer',
                        }}
                      >
                        삭제
                      </button>
                    </div>
                  </div>
                ))
              )}
            </CollapsibleSection>
          </>
        )}

        {/* 엔티티 탭 - Location */}
        {activeTab === 'entities' && currentLocation && !currentCell && (
          <>
            <CollapsibleSection 
              title="Cells" 
              count={locationCells.length}
              defaultExpanded={true}
              actionButton={
                <button
                  onClick={async (e) => {
                    e.stopPropagation();
                    const cellName = prompt('Cell 이름을 입력하세요:');
                    if (cellName && currentLocation) {
                      try {
                        await managementApi.createCell({
                          location_id: currentLocation.location_id,
                          cell_name: cellName,
                          matrix_width: 10,
                          matrix_height: 10,
                        });
                        // Cells 목록 새로고침
                        try {
                          const response = await cellsApi.getByLocation(currentLocation.location_id);
                          setLocationCells(response.data || []);
                        } catch (error) {
                          console.error('Cells 로드 실패:', error);
                        }
                        if (onRefresh) await onRefresh();
                      } catch (error) {
                        console.error('Cell 생성 실패:', error);
                        alert('Cell 생성에 실패했습니다.');
                      }
                    }
                  }}
                  style={{
                    fontSize: '9px',
                    padding: '2px 8px',
                    backgroundColor: '#4CAF50',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '2px',
                    cursor: 'pointer',
                  }}
                >
                  + Add
                </button>
              }
            >
              {locationCells.length === 0 ? (
                <div style={{ fontSize: '9px', color: '#999', padding: '8px' }}>
                  Cell이 없습니다.
                </div>
              ) : (
                locationCells.map((cell) => (
                  <div key={cell.cell_id} style={{
                    marginBottom: '4px',
                    padding: '4px 8px',
                    fontSize: '9px',
                    color: '#666',
                    backgroundColor: '#fff',
                    border: '1px solid #E0E0E0',
                    borderRadius: '2px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '8px',
                  }}>
                    <span style={{ flex: 1 }}>{cell.cell_id} - {cell.cell_name || 'Unnamed'} ({cell.matrix_width}x{cell.matrix_height})</span>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <button
                        onClick={() => {
                          setSelectedCellId(cell.cell_id);
                          setCellModalOpen(true);
                        }}
                        style={{
                          fontSize: '9px',
                          padding: '2px 6px',
                          backgroundColor: '#2196F3',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '2px',
                          cursor: 'pointer',
                        }}
                      >
                        편집
                      </button>
                    </div>
                  </div>
                ))
              )}
            </CollapsibleSection>

            <CollapsibleSection 
              title="인물 (NPCs)" 
              count={npcs.length}
              defaultExpanded={true}
              actionButton={
                <button
                  onClick={async (e) => {
                    e.stopPropagation();
                    const npcName = prompt('NPC 이름을 입력하세요:');
                    if (npcName && currentLocation) {
                      try {
                        const entityId = `NPC_${npcName.toUpperCase().replace(/\s+/g, '_')}_${Date.now()}`;
                        await entitiesApi.create({
                          entity_id: entityId,
                          entity_type: 'npc',
                          entity_name: npcName,
                          entity_description: '',
                          entity_properties: {
                            location_id: currentLocation.location_id,
                            region_id: currentLocation.region_id,
                          },
                        });
                        // NPC 목록 새로고침 (Location과 하위 Cells 모두)
                        try {
                          const allNpcs: any[] = [];
                          // Location의 직접 NPCs
                          try {
                            const entitiesResponse = await entitiesApi.getByLocation(currentLocation.location_id);
                            if (entitiesResponse.data) {
                              allNpcs.push(...(Array.isArray(entitiesResponse.data) ? entitiesResponse.data : [entitiesResponse.data]));
                            }
                          } catch (e) {
                            // NPC가 없을 수 있음
                          }
                          // Location의 Cells에 속한 NPCs
                          for (const cell of locationCells) {
                            try {
                              const cellNpcResponse = await entitiesApi.getByCell(cell.cell_id);
                              if (cellNpcResponse.data) {
                                allNpcs.push(...(Array.isArray(cellNpcResponse.data) ? cellNpcResponse.data : [cellNpcResponse.data]));
                              }
                            } catch (e) {
                              // NPC가 없을 수 있음
                            }
                          }
                          setNpcs(allNpcs);
                        } catch (error) {
                          console.error('NPC 로드 실패:', error);
                        }
                        if (onRefresh) await onRefresh();
                      } catch (error) {
                        console.error('NPC 생성 실패:', error);
                        alert('NPC 생성에 실패했습니다.');
                      }
                    }
                  }}
                  style={{
                    fontSize: '9px',
                    padding: '2px 8px',
                    backgroundColor: '#4CAF50',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '2px',
                    cursor: 'pointer',
                  }}
                >
                  + Add
                </button>
              }
            >
              {npcs.length === 0 ? (
                <div style={{ fontSize: '9px', color: '#999', padding: '8px' }}>
                  인물이 없습니다.
                </div>
              ) : (
                npcs.map((npc) => (
                  <div key={npc.entity_id} style={{
                    marginBottom: '4px',
                    padding: '4px 8px',
                    fontSize: '9px',
                    color: '#666',
                    backgroundColor: '#fff',
                    border: '1px solid #E0E0E0',
                    borderRadius: '2px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '8px',
                  }}>
                    <span style={{ flex: 1 }}>{npc.entity_id} - {npc.entity_name}</span>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <button
                        onClick={async (e) => {
                          e.stopPropagation();
                          setEditingEntityId(npc.entity_id);
                        }}
                        style={{
                          fontSize: '9px',
                          padding: '2px 6px',
                          backgroundColor: '#2196F3',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '2px',
                          cursor: 'pointer',
                        }}
                      >
                        편집
                      </button>
                      <button
                        onClick={async (e) => {
                          e.stopPropagation();
                          if (confirm(`정말로 "${npc.entity_name}"을(를) 삭제하시겠습니까?`)) {
                            try {
                              await entitiesApi.delete(npc.entity_id);
                              // NPC 목록 새로고침 (Location과 하위 Cells 모두)
                              try {
                                const allNpcs: any[] = [];
                                // Location의 직접 NPCs
                                try {
                                  const entitiesResponse = await entitiesApi.getByLocation(currentLocation!.location_id);
                                  if (entitiesResponse.data) {
                                    allNpcs.push(...(Array.isArray(entitiesResponse.data) ? entitiesResponse.data : [entitiesResponse.data]));
                                  }
                                } catch (e) {
                                  // NPC가 없을 수 있음
                                }
                                // Location의 Cells에 속한 NPCs
                                for (const cell of locationCells) {
                                  try {
                                    const cellNpcResponse = await entitiesApi.getByCell(cell.cell_id);
                                    if (cellNpcResponse.data) {
                                      allNpcs.push(...(Array.isArray(cellNpcResponse.data) ? cellNpcResponse.data : [cellNpcResponse.data]));
                                    }
                                  } catch (e) {
                                    // NPC가 없을 수 있음
                                  }
                                }
                                setNpcs(allNpcs);
                              } catch (error) {
                                console.error('NPC 로드 실패:', error);
                              }
                            } catch (error) {
                              console.error('NPC 삭제 실패:', error);
                              alert('NPC 삭제에 실패했습니다.');
                            }
                          }
                        }}
                        style={{
                          fontSize: '9px',
                          padding: '2px 6px',
                          backgroundColor: '#f44336',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '2px',
                          cursor: 'pointer',
                        }}
                      >
                        삭제
                      </button>
                    </div>
                  </div>
                ))
              )}
            </CollapsibleSection>
          </>
        )}

        {/* 엔티티 탭 - Cell */}
        {activeTab === 'entities' && currentCell && (
          <>
            <CollapsibleSection 
              title="인물 (NPCs)" 
              count={cellEntities.length}
              defaultExpanded={true}
              actionButton={
                <button
                  onClick={async (e) => {
                    e.stopPropagation();
                    const npcName = prompt('NPC 이름을 입력하세요:');
                    if (npcName && currentCell) {
                      try {
                        const entityId = `NPC_${npcName.toUpperCase().replace(/\s+/g, '_')}_${Date.now()}`;
                        await entitiesApi.create({
                          entity_id: entityId,
                          entity_type: 'npc',
                          entity_name: npcName,
                          entity_description: '',
                          entity_properties: {
                            cell_id: currentCell.cell_id,
                            location_id: currentCell.location_id,
                          },
                        });
                        // NPC 목록 새로고침
                        try {
                          const entitiesResponse = await entitiesApi.getByCell(currentCell.cell_id);
                          setCellEntities(Array.isArray(entitiesResponse.data) ? entitiesResponse.data : [entitiesResponse.data]);
                        } catch (error) {
                          console.error('NPC 로드 실패:', error);
                        }
                        if (onRefresh) await onRefresh();
                      } catch (error) {
                        console.error('NPC 생성 실패:', error);
                        alert('NPC 생성에 실패했습니다.');
                      }
                    }
                  }}
                  style={{
                    fontSize: '9px',
                    padding: '2px 8px',
                    backgroundColor: '#4CAF50',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '2px',
                    cursor: 'pointer',
                  }}
                >
                  + Add
                </button>
              }
            >
              {cellEntities.length === 0 ? (
                <div style={{ fontSize: '9px', color: '#999', padding: '8px' }}>
                  인물이 없습니다.
                </div>
              ) : (
                cellEntities.map((npc) => (
                  <div key={npc.entity_id} style={{
                    marginBottom: '4px',
                    padding: '4px 8px',
                    fontSize: '9px',
                    color: '#666',
                    backgroundColor: '#fff',
                    border: '1px solid #E0E0E0',
                    borderRadius: '2px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '8px',
                  }}>
                    <span style={{ flex: 1 }}>{npc.entity_id} - {npc.entity_name}</span>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <button
                        onClick={async (e) => {
                          e.stopPropagation();
                          setEditingEntityId(npc.entity_id);
                        }}
                        style={{
                          fontSize: '9px',
                          padding: '2px 6px',
                          backgroundColor: '#2196F3',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '2px',
                          cursor: 'pointer',
                        }}
                      >
                        편집
                      </button>
                      <button
                        onClick={async (e) => {
                          e.stopPropagation();
                          if (confirm(`정말로 "${npc.entity_name}"을(를) 삭제하시겠습니까?`)) {
                            try {
                              await entitiesApi.delete(npc.entity_id);
                              // NPC 목록 새로고침
                              try {
                                const entitiesResponse = await entitiesApi.getByCell(currentCell!.cell_id);
                                setCellEntities(Array.isArray(entitiesResponse.data) ? entitiesResponse.data : [entitiesResponse.data]);
                              } catch (error) {
                                console.error('NPC 로드 실패:', error);
                              }
                            } catch (error) {
                              console.error('NPC 삭제 실패:', error);
                              alert('NPC 삭제에 실패했습니다.');
                            }
                          }
                        }}
                        style={{
                          fontSize: '9px',
                          padding: '2px 6px',
                          backgroundColor: '#f44336',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '2px',
                          cursor: 'pointer',
                        }}
                      >
                        삭제
                      </button>
                    </div>
                  </div>
                ))
              )}
            </CollapsibleSection>
          </>
        )}

        {/* 정보 탭 - Region/Location/Cell 정보 표시 */}
        {activeTab === 'info' && currentRegion && pin?.pin_type === 'region' && (
          <>
            <CollapsibleSection title="경제" defaultExpanded={true}>
              <FormField label="주요 산업" labelWidth={100}>
                <InputField
                  type="text"
                  value={regionInfo.economy.primary_industry}
                  onChange={(value) => setRegionInfo({
                    ...regionInfo,
                    economy: {
                      ...regionInfo.economy,
                      primary_industry: value,
                    },
                  })}
                />
              </FormField>
              <FormField label="거래 품목" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={regionInfo.economy.trade_goods.join(', ')}
                  onChange={(value) => setRegionInfo({
                    ...regionInfo,
                    economy: {
                      ...regionInfo.economy,
                      trade_goods: value.split(',').map(s => s.trim()).filter(s => s),
                    },
                  })}
                  rows={3}
                  placeholder="쉼표로 구분하여 입력"
                />
              </FormField>
              <FormField label="골드 가치" labelWidth={100}>
                <InputField
                  type="number"
                  value={regionInfo.economy.gold_value}
                  onChange={(value) => setRegionInfo({
                    ...regionInfo,
                    economy: {
                      ...regionInfo.economy,
                      gold_value: parseInt(value) || 0,
                    },
                  })}
                />
              </FormField>
            </CollapsibleSection>

            <CollapsibleSection title="정치/행정" defaultExpanded={false}>
              <FormField label="정부 형태" labelWidth={100}>
                <InputField
                  type="select"
                  value={regionInfo.government.type}
                  onChange={(value) => setRegionInfo({
                    ...regionInfo,
                    government: {
                      ...regionInfo.government,
                      type: value,
                    },
                  })}
                  options={['', 'democracy', 'monarchy', 'theocracy', 'oligarchy', 'republic', 'dictatorship']}
                />
              </FormField>
              <FormField label="지도자" labelWidth={100}>
                <InputField
                  type="text"
                  value={regionInfo.government.leader}
                  onChange={(value) => setRegionInfo({
                    ...regionInfo,
                    government: {
                      ...regionInfo.government,
                      leader: value,
                    },
                  })}
                />
              </FormField>
              <FormField label="법률" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={regionInfo.government.laws.join('\n')}
                  onChange={(value) => setRegionInfo({
                    ...regionInfo,
                    government: {
                      ...regionInfo.government,
                      laws: value.split('\n').map(s => s.trim()).filter(s => s),
                    },
                  })}
                  rows={5}
                  placeholder="한 줄에 하나씩 입력"
                />
              </FormField>
            </CollapsibleSection>

            <CollapsibleSection title="사회/문화" defaultExpanded={false}>
              <FormField label="총 인구" labelWidth={100}>
                <InputField
                  type="number"
                  value={regionInfo.demographics.population}
                  onChange={(value) => setRegionInfo({
                    ...regionInfo,
                    demographics: {
                      ...regionInfo.demographics,
                      population: parseInt(value) || 0,
                    },
                  })}
                />
              </FormField>
              <FormField label="종족 분포" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={Object.entries(regionInfo.demographics.races || {}).map(([k, v]) => `${k}: ${v}`).join('\n')}
                  onChange={(value) => {
                    const races: Record<string, number> = {};
                    value.split('\n').forEach(line => {
                      const [key, val] = line.split(':').map(s => s.trim());
                      if (key && val) races[key] = parseInt(val) || 0;
                    });
                    setRegionInfo({
                      ...regionInfo,
                      demographics: {
                        ...regionInfo.demographics,
                        races,
                      },
                    });
                  }}
                  rows={5}
                  placeholder="종족명: 인구수 (한 줄에 하나씩)"
                />
              </FormField>
              <FormField label="직업 분포" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={Object.entries(regionInfo.demographics.classes || {}).map(([k, v]) => `${k}: ${v}`).join('\n')}
                  onChange={(value) => {
                    const classes: Record<string, number> = {};
                    value.split('\n').forEach(line => {
                      const [key, val] = line.split(':').map(s => s.trim());
                      if (key && val) classes[key] = parseInt(val) || 0;
                    });
                    setRegionInfo({
                      ...regionInfo,
                      demographics: {
                        ...regionInfo.demographics,
                        classes,
                      },
                    });
                  }}
                  rows={5}
                  placeholder="직업명: 인구수 (한 줄에 하나씩)"
                />
              </FormField>
              <FormField label="종교" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={regionInfo.culture.religion.join(', ')}
                  onChange={(value) => setRegionInfo({
                    ...regionInfo,
                    culture: {
                      ...regionInfo.culture,
                      religion: value.split(',').map(s => s.trim()).filter(s => s),
                    },
                  })}
                  rows={2}
                  placeholder="쉼표로 구분하여 입력"
                />
              </FormField>
              <FormField label="풍습" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={regionInfo.culture.customs.join('\n')}
                  onChange={(value) => setRegionInfo({
                    ...regionInfo,
                    culture: {
                      ...regionInfo.culture,
                      customs: value.split('\n').map(s => s.trim()).filter(s => s),
                    },
                  })}
                  rows={5}
                  placeholder="한 줄에 하나씩 입력"
                />
              </FormField>
              <FormField label="축제" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={regionInfo.culture.festivals.join('\n')}
                  onChange={(value) => setRegionInfo({
                    ...regionInfo,
                    culture: {
                      ...regionInfo.culture,
                      festivals: value.split('\n').map(s => s.trim()).filter(s => s),
                    },
                  })}
                  rows={3}
                  placeholder="한 줄에 하나씩 입력"
                />
              </FormField>
            </CollapsibleSection>

            <CollapsibleSection title="지리/환경" defaultExpanded={false}>
              <FormField label="기후" labelWidth={100}>
                <InputField
                  type="select"
                  value={playSettings.climate}
                  onChange={(value) => setPlaySettings({ ...playSettings, climate: value })}
                  options={['', 'temperate', 'tropical', 'arctic', 'desert', 'mediterranean']}
                />
              </FormField>
              <FormField label="지형" labelWidth={100}>
                <InputField
                  type="textarea"
                  value=""
                  onChange={() => {}}
                  rows={3}
                  placeholder="지형 정보를 입력하세요"
                />
              </FormField>
            </CollapsibleSection>

            <CollapsibleSection title="역사/로어" defaultExpanded={false}>
              <FormField label="역사" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={regionInfo.lore.history}
                  onChange={(value) => setRegionInfo({
                    ...regionInfo,
                    lore: {
                      ...regionInfo.lore,
                      history: value,
                    },
                  })}
                  rows={8}
                />
              </FormField>
              <FormField label="전설" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={regionInfo.lore.legends.join('\n')}
                  onChange={(value) => setRegionInfo({
                    ...regionInfo,
                    lore: {
                      ...regionInfo.lore,
                      legends: value.split('\n').map(s => s.trim()).filter(s => s),
                    },
                  })}
                  rows={5}
                  placeholder="한 줄에 하나씩 입력"
                />
              </FormField>
              <FormField label="비밀" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={regionInfo.lore.secrets.join('\n')}
                  onChange={(value) => setRegionInfo({
                    ...regionInfo,
                    lore: {
                      ...regionInfo.lore,
                      secrets: value.split('\n').map(s => s.trim()).filter(s => s),
                    },
                  })}
                  rows={5}
                  placeholder="한 줄에 하나씩 입력"
                />
              </FormField>
            </CollapsibleSection>

            <CollapsibleSection title="상세 정보" defaultExpanded={false}>
              <DetailSectionEditor
                sections={detailSections}
                onChange={setDetailSections}
              />
            </CollapsibleSection>
          </>
        )}

        {/* 정보 탭 - Location 정보 표시 및 편집 */}
        {activeTab === 'info' && currentLocation && pin?.pin_type === 'location' && (
          <>
            <CollapsibleSection title="기본 정보" defaultExpanded={true}>
              <FormField label="이름" labelWidth={100}>
                <InputField
                  type="text"
                  value={currentLocation.location_name || ''}
                  onChange={() => {}}
                  readOnly
                />
              </FormField>
              <FormField label="설명" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={currentLocation.location_description || ''}
                  onChange={() => {}}
                  readOnly
                  rows={3}
                />
              </FormField>
              <FormField label="타입" labelWidth={100}>
                <InputField
                  type="text"
                  value={currentLocation.location_type || ''}
                  onChange={() => {}}
                  readOnly
                />
              </FormField>
              <FormField label="주인" labelWidth={100}>
                <InputField
                  type="text"
                  value={currentLocation.owner_name || ''}
                  onChange={() => {}}
                  readOnly
                  placeholder="주인이 없습니다 (SSOT: entities 테이블에서 조회)"
                />
              </FormField>
            </CollapsibleSection>

            <CollapsibleSection title="소유권" defaultExpanded={false}>
              <FormField label="주인 Entity ID" labelWidth={100}>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <div style={{ flex: 1 }}>
                    <InputField
                      type="text"
                      value={locationInfo.ownership.owner_entity_id}
                      onChange={() => {}}
                      readOnly
                      placeholder="엔티티를 선택하세요"
                    />
                  </div>
                  <button
                    onClick={() => {
                      setEntityPickerTarget('location');
                      setEntityPickerOpen(true);
                    }}
                    style={{
                      padding: '6px 12px',
                      border: '1px solid #E0E0E0',
                      borderRadius: '4px',
                      backgroundColor: '#fff',
                      cursor: 'pointer',
                      fontSize: '12px',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    검색
                  </button>
                  {locationInfo.ownership.owner_entity_id && (
                    <button
                      onClick={() => setLocationInfo({
                        ...locationInfo,
                        ownership: {
                          ...locationInfo.ownership,
                          owner_entity_id: '',
                        },
                      })}
                      style={{
                        padding: '6px 12px',
                        border: '1px solid #E0E0E0',
                        borderRadius: '4px',
                        backgroundColor: '#fff',
                        cursor: 'pointer',
                        fontSize: '12px',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      제거
                    </button>
                  )}
                </div>
              </FormField>
              <FormField label="소유 유형" labelWidth={100}>
                <InputField
                  type="select"
                  value={locationInfo.ownership.ownership_type}
                  onChange={(value) => setLocationInfo({
                    ...locationInfo,
                    ownership: {
                      ...locationInfo.ownership,
                      ownership_type: value,
                    },
                  })}
                  options={['', 'private', 'public', 'guild', 'government']}
                />
              </FormField>
            </CollapsibleSection>

            <CollapsibleSection title="로어" defaultExpanded={false}>
              <FormField label="역사" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={locationInfo.lore.history}
                  onChange={(value) => setLocationInfo({
                    ...locationInfo,
                    lore: {
                      ...locationInfo.lore,
                      history: value,
                    },
                  })}
                  rows={5}
                  placeholder="위치의 역사를 입력하세요"
                />
              </FormField>
              <FormField label="전설" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={locationInfo.lore.legends.join('\n')}
                  onChange={(value) => setLocationInfo({
                    ...locationInfo,
                    lore: {
                      ...locationInfo.lore,
                      legends: value.split('\n').map(s => s.trim()).filter(s => s),
                    },
                  })}
                  rows={3}
                  placeholder="한 줄에 하나씩 입력"
                />
              </FormField>
            </CollapsibleSection>

            <CollapsibleSection title="상세 정보" defaultExpanded={false}>
              <DetailSectionEditor
                sections={locationInfo.detail_sections}
                onChange={(sections) => setLocationInfo({
                  ...locationInfo,
                  detail_sections: sections,
                })}
              />
            </CollapsibleSection>
          </>
        )}

        {/* 정보 탭 - Cell 정보 표시 및 편집 */}
        {activeTab === 'info' && currentCell && pin?.pin_type === 'cell' && (
          <>
            <CollapsibleSection title="기본 정보" defaultExpanded={true}>
              <FormField label="이름" labelWidth={100}>
                <InputField
                  type="text"
                  value={currentCell.cell_name || ''}
                  onChange={() => {}}
                  readOnly
                />
              </FormField>
              <FormField label="설명" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={currentCell.cell_description || ''}
                  onChange={() => {}}
                  readOnly
                  rows={3}
                />
              </FormField>
              <FormField label="크기" labelWidth={100}>
                <InputField
                  type="text"
                  value={`${currentCell.matrix_width} x ${currentCell.matrix_height}`}
                  onChange={() => {}}
                  readOnly
                />
              </FormField>
              <FormField label="상태" labelWidth={100}>
                <InputField
                  type="text"
                  value={currentCell.cell_status || 'active'}
                  onChange={() => {}}
                  readOnly
                />
              </FormField>
              <FormField label="타입" labelWidth={100}>
                <InputField
                  type="text"
                  value={currentCell.cell_type || 'indoor'}
                  onChange={() => {}}
                  readOnly
                />
              </FormField>
              <FormField label="주인" labelWidth={100}>
                <InputField
                  type="text"
                  value={currentCell.owner_name || ''}
                  onChange={() => {}}
                  readOnly
                  placeholder="주인이 없습니다 (SSOT: entities 테이블에서 조회)"
                />
              </FormField>
            </CollapsibleSection>

            <CollapsibleSection title="소유권" defaultExpanded={false}>
              <FormField label="주인 Entity ID" labelWidth={100}>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <div style={{ flex: 1 }}>
                    <InputField
                      type="text"
                      value={cellInfo.ownership.owner_entity_id}
                      onChange={() => {}}
                      readOnly
                      placeholder="엔티티를 선택하세요"
                    />
                  </div>
                  <button
                    onClick={() => {
                      setEntityPickerTarget('cell');
                      setEntityPickerOpen(true);
                    }}
                    style={{
                      padding: '6px 12px',
                      border: '1px solid #E0E0E0',
                      borderRadius: '4px',
                      backgroundColor: '#fff',
                      cursor: 'pointer',
                      fontSize: '12px',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    검색
                  </button>
                  {cellInfo.ownership.owner_entity_id && (
                    <button
                      onClick={() => setCellInfo({
                        ...cellInfo,
                        ownership: {
                          ...cellInfo.ownership,
                          owner_entity_id: '',
                        },
                      })}
                      style={{
                        padding: '6px 12px',
                        border: '1px solid #E0E0E0',
                        borderRadius: '4px',
                        backgroundColor: '#fff',
                        cursor: 'pointer',
                        fontSize: '12px',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      제거
                    </button>
                  )}
                </div>
              </FormField>
              <FormField label="Private 여부" labelWidth={100}>
                <InputField
                  type="select"
                  value={cellInfo.ownership.is_private ? 'true' : 'false'}
                  onChange={(value) => setCellInfo({
                    ...cellInfo,
                    ownership: {
                      ...cellInfo.ownership,
                      is_private: value === 'true',
                    },
                  })}
                  options={['false', 'true']}
                />
              </FormField>
            </CollapsibleSection>

            <CollapsibleSection title="로어" defaultExpanded={false}>
              <FormField label="역사" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={cellInfo.lore.history}
                  onChange={(value) => setCellInfo({
                    ...cellInfo,
                    lore: {
                      ...cellInfo.lore,
                      history: value,
                    },
                  })}
                  rows={5}
                  placeholder="셀의 역사를 입력하세요"
                />
              </FormField>
              <FormField label="전설" labelWidth={100}>
                <InputField
                  type="textarea"
                  value={cellInfo.lore.legends.join('\n')}
                  onChange={(value) => setCellInfo({
                    ...cellInfo,
                    lore: {
                      ...cellInfo.lore,
                      legends: value.split('\n').map(s => s.trim()).filter(s => s),
                    },
                  })}
                  rows={3}
                  placeholder="한 줄에 하나씩 입력"
                />
              </FormField>
            </CollapsibleSection>

            <CollapsibleSection title="상세 정보" defaultExpanded={false}>
              <DetailSectionEditor
                sections={cellInfo.detail_sections}
                onChange={(sections) => setCellInfo({
                  ...cellInfo,
                  detail_sections: sections,
                })}
              />
            </CollapsibleSection>

            <CollapsibleSection title="환경" defaultExpanded={false}>
              <FormField label="지형" labelWidth={100}>
                <InputField
                  type="text"
                  value={cellInfo.environment.terrain}
                  onChange={(value) => setCellInfo({
                    ...cellInfo,
                    environment: {
                      ...cellInfo.environment,
                      terrain: value,
                    },
                  })}
                  placeholder="예: grass, stone, water"
                />
              </FormField>
              <FormField label="날씨" labelWidth={100}>
                <InputField
                  type="text"
                  value={cellInfo.environment.weather}
                  onChange={(value) => setCellInfo({
                    ...cellInfo,
                    environment: {
                      ...cellInfo.environment,
                      weather: value,
                    },
                  })}
                  placeholder="예: sunny, rainy, foggy"
                />
              </FormField>
              <FormField label="조명" labelWidth={100}>
                <InputField
                  type="text"
                  value={cellInfo.environment.lighting}
                  onChange={(value) => setCellInfo({
                    ...cellInfo,
                    environment: {
                      ...cellInfo.environment,
                      lighting: value,
                    },
                  })}
                  placeholder="예: bright, dim, dark"
                />
              </FormField>
            </CollapsibleSection>
          </>
        )}

        {/* 설정 탭 - Region: 게임플레이 설정, Location: 건물 설정, Cell: 방 설정 */}
        {activeTab === 'settings' && currentRegion && (
          <>
            <CollapsibleSection title="게임플레이 설정" defaultExpanded={true}>
              <FormField label="기후" labelWidth={100}>
                <InputField
                  type="select"
                  value={playSettings.climate}
                  onChange={(value) => setPlaySettings({ ...playSettings, climate: value })}
                  options={['', 'temperate', 'tropical', 'arctic', 'desert', 'mediterranean']}
                />
              </FormField>
              <FormField label="위험도" labelWidth={100}>
                <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                  <InputField
                    type="number"
                    value={playSettings.danger_level}
                    onChange={(value) => setPlaySettings({ ...playSettings, danger_level: parseInt(value) || 1 })}
                    min={1}
                    max={10}
                  />
                  <span style={{ fontSize: '9px', color: '#999' }}>[1-10]</span>
                </div>
              </FormField>
              <FormField label="권장 레벨" labelWidth={100}>
                <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                  <span style={{ fontSize: '9px', color: '#999' }}>Min:</span>
                  <InputField
                    type="number"
                    value={playSettings.recommended_level_min}
                    onChange={(value) => setPlaySettings({ ...playSettings, recommended_level_min: parseInt(value) || 1 })}
                    min={1}
                  />
                  <span style={{ fontSize: '9px', color: '#999' }}>Max:</span>
                  <InputField
                    type="number"
                    value={playSettings.recommended_level_max}
                    onChange={(value) => setPlaySettings({ ...playSettings, recommended_level_max: parseInt(value) || 10 })}
                    min={1}
                  />
                </div>
              </FormField>
              <FormField label="BGM" labelWidth={100}>
                <InputField
                  type="text"
                  value={playSettings.bgm}
                  onChange={(value) => setPlaySettings({ ...playSettings, bgm: value })}
                  placeholder="peaceful_01"
                />
              </FormField>
              <FormField label="Ambient Effects" labelWidth={100}>
                <InputField
                  type="text"
                  value={playSettings.ambient_effects}
                  onChange={(value) => setPlaySettings({ ...playSettings, ambient_effects: value })}
                  placeholder="birds, wind (쉼표로 구분)"
                />
              </FormField>
            </CollapsibleSection>
          </>
        )}

        {/* 설정 탭 - Location: 건물 설정 (배경음악, 앰비언트 효과) */}
        {activeTab === 'settings' && currentLocation && (
          <>
            <CollapsibleSection title="건물 설정" defaultExpanded={true}>
              <FormField label="배경음악 (Background Music)" labelWidth={150}>
                <InputField
                  type="text"
                  value={playSettings.bgm}
                  onChange={(value) => setPlaySettings({ ...playSettings, bgm: value })}
                  placeholder="peaceful_01"
                />
              </FormField>
              <FormField label="앰비언트 효과 (Ambient Effects)" labelWidth={150}>
                <InputField
                  type="text"
                  value={playSettings.ambient_effects}
                  onChange={(value) => setPlaySettings({ ...playSettings, ambient_effects: value })}
                  placeholder="birds, wind (쉼표로 구분)"
                />
              </FormField>
            </CollapsibleSection>
          </>
        )}

        {/* 설정 탭 - Cell: 방 설정 (상태, 타입, 지형, 날씨) */}
        {activeTab === 'settings' && currentCell && (
          <>
            <CollapsibleSection title="방 설정" defaultExpanded={true}>
              <FormField label="상태 (Status)" labelWidth={120}>
                <InputField
                  type="select"
                  value={currentCell.cell_status || 'active'}
                  onChange={async (value) => {
                    try {
                      await cellsApi.update(currentCell.cell_id, { cell_status: value });
                      if (onRefresh) await onRefresh();
                    } catch (error) {
                      console.error('업데이트 실패:', error);
                    }
                  }}
                  options={['active', 'inactive', 'locked', 'dangerous']}
                />
              </FormField>
              <FormField label="타입 (Type)" labelWidth={120}>
                <InputField
                  type="select"
                  value={currentCell.cell_type || 'indoor'}
                  onChange={async (value) => {
                    try {
                      await cellsApi.update(currentCell.cell_id, { cell_type: value });
                      if (onRefresh) await onRefresh();
                    } catch (error) {
                      console.error('업데이트 실패:', error);
                    }
                  }}
                  options={['indoor', 'outdoor', 'dungeon', 'shop', 'tavern', 'temple']}
                />
              </FormField>
              <FormField label="지형 (Terrain)" labelWidth={120}>
                <InputField
                  type="text"
                  value={currentCell.cell_properties?.terrain || ''}
                  onChange={async (value) => {
                    try {
                      const properties = {
                        ...(currentCell.cell_properties || {}),
                        terrain: value,
                      };
                      await cellsApi.updateProperties(currentCell.cell_id, properties);
                      if (onRefresh) await onRefresh();
                    } catch (error) {
                      console.error('업데이트 실패:', error);
                    }
                  }}
                  placeholder="stone, wooden_floor, grass"
                />
              </FormField>
              <FormField label="날씨 (Weather)" labelWidth={120}>
                <InputField
                  type="text"
                  value={currentCell.cell_properties?.weather || ''}
                  onChange={async (value) => {
                    try {
                      const properties = {
                        ...(currentCell.cell_properties || {}),
                        weather: value,
                      };
                      await cellsApi.updateProperties(currentCell.cell_id, properties);
                      if (onRefresh) await onRefresh();
                    } catch (error) {
                      console.error('업데이트 실패:', error);
                    }
                  }}
                  placeholder="clear, rain, snow"
                />
              </FormField>
            </CollapsibleSection>
          </>
        )}

        {/* 메타 탭 */}
        {activeTab === 'metadata' && (
          <>
            <CollapsibleSection title="핀 메타데이터" defaultExpanded={true}>
              <FormField label="핀 이름" labelWidth={100}>
                <InputField
                  type="text"
                  value={pin.pin_name || ''}
                  onChange={(value) => {
                    if (onPinUpdate) {
                      onPinUpdate(pin.pin_id, { pin_name: value });
                    }
                  }}
                  placeholder="새 핀 01"
                />
              </FormField>
              <FormField label="Pin ID" labelWidth={100}>
                <InputField
                  type="text"
                  value={pin.pin_id}
                  onChange={() => {}}
                  readOnly
                  copyButton
                />
              </FormField>
              <FormField label="Game Data ID" labelWidth={100}>
                <InputField
                  type="text"
                  value={pin.game_data_id}
                  onChange={() => {}}
                  readOnly
                  copyButton
                />
              </FormField>
              <FormField label="Pin Type" labelWidth={80}>
                <InputField
                  type="select"
                  value={pin.pin_type}
                  onChange={() => {}}
                  options={['region', 'location', 'cell']}
                  readOnly
                />
              </FormField>
              <FormField label="위치" labelWidth={80}>
                <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                  <span style={{ fontSize: '9px', color: '#999' }}>X:</span>
                  <InputField
                    type="number"
                    value={pin.x}
                    onChange={(value) => {
                      if (onPinUpdate) {
                        onPinUpdate(pin.pin_id, { x: parseInt(value) });
                      }
                    }}
                  />
                  <span style={{ fontSize: '9px', color: '#999' }}>Y:</span>
                  <InputField
                    type="number"
                    value={pin.y}
                    onChange={(value) => {
                      if (onPinUpdate) {
                        onPinUpdate(pin.pin_id, { y: parseInt(value) });
                      }
                    }}
                  />
                </div>
              </FormField>
              <FormField label="아이콘" labelWidth={80}>
                <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                  <InputField
                    type="select"
                    value={pin.icon_type}
                    onChange={(value) => {
                      if (onPinUpdate) {
                        onPinUpdate(pin.pin_id, { icon_type: value });
                      }
                    }}
                    options={['default', 'town', 'dungeon', 'forest']}
                  />
                  <span style={{ fontSize: '9px', color: '#999' }}>Size:</span>
                  <InputField
                    type="number"
                    value={pin.size}
                    onChange={(value) => {
                      if (onPinUpdate) {
                        onPinUpdate(pin.pin_id, { size: parseInt(value) });
                      }
                    }}
                  />
                </div>
              </FormField>
              <FormField label="색상" labelWidth={80}>
                <InputField
                  type="color"
                  value={pin.color}
                  onChange={(value) => {
                    if (onPinUpdate) {
                      onPinUpdate(pin.pin_id, { color: value });
                    }
                  }}
                />
              </FormField>
            </CollapsibleSection>
          </>
        )}
      </div>

      {/* Footer (고정) */}
      <div style={{
        flexShrink: 0,
        padding: '6px 12px',
        backgroundColor: '#FFFFFF',
        borderTop: '1px solid #E0E0E0',
        display: 'flex',
        justifyContent: 'flex-end',
        gap: '8px',
      }}>
        <button
          onClick={handleSaveAll}
          disabled={saving}
          style={{
            fontSize: '9px',
            fontWeight: 'medium',
            padding: '6px 12px',
            backgroundColor: saving ? '#ccc' : '#4CAF50',
            color: '#fff',
            border: 'none',
            borderRadius: '2px',
            cursor: saving ? 'not-allowed' : 'pointer',
          }}
        >
          Save All
        </button>
        <button
          onClick={() => {
            if (onRefresh) onRefresh();
          }}
          style={{
            fontSize: '9px',
            fontWeight: 'medium',
            padding: '6px 12px',
            backgroundColor: '#999999',
            color: '#fff',
            border: 'none',
            borderRadius: '2px',
            cursor: 'pointer',
          }}
        >
          Reset
        </button>
        {onPinDelete && (
          <button
            onClick={async () => {
              if (confirm('핀을 삭제하시겠습니까?')) {
                await onPinDelete(pin.pin_id);
              }
            }}
            style={{
              fontSize: '9px',
              fontWeight: 'medium',
              padding: '6px 12px',
              backgroundColor: '#F44336',
              color: '#fff',
              border: 'none',
              borderRadius: '2px',
              cursor: 'pointer',
            }}
          >
            Delete Pin
          </button>
        )}
      </div>

      {/* Location 편집 모달 */}
      {currentRegion && (
        <LocationEditorModal
          isOpen={locationModalOpen}
          onClose={() => {
            setLocationModalOpen(false);
            setSelectedLocationId(null);
          }}
          locationId={selectedLocationId}
          regionId={currentRegion.region_id}
          onSave={async () => {
            // Location 목록 새로고침 (로컬 상태만 업데이트)
            if (currentRegion) {
              try {
                const response = await locationsApi.getByRegion(currentRegion.region_id);
                setRegionLocations(response.data || []);
              } catch (error) {
                console.error('Location 로드 실패:', error);
              }
            }
            // onRefresh() 호출하지 않음 - 전체 새로고침 방지
          }}
        />
      )}

      {/* Cell 편집 모달 */}
      <CellEditorModal
        isOpen={cellModalOpen}
        onClose={() => {
          setCellModalOpen(false);
          setSelectedCellId(null);
        }}
        cellId={selectedCellId}
        onSave={async () => {
          // Location 목록 새로고침 (로컬 상태만 업데이트)
          if (currentRegion) {
            try {
              const response = await locationsApi.getByRegion(currentRegion.region_id);
              setRegionLocations(response.data || []);
            } catch (error) {
              console.error('Location 로드 실패:', error);
            }
          }
          // onRefresh() 호출하지 않음 - 전체 새로고침 방지
        }}
      />
      <EntityEditorModal
        isOpen={editingEntityId !== null}
        onClose={() => {
          setEditingEntityId(null);
        }}
        entityId={editingEntityId}
        onSave={async () => {
          // NPC 목록 새로고침 (로컬 상태만 업데이트)
          if (currentRegion && regionLocations.length > 0) {
            try {
              const allNpcs: any[] = [];
              for (const loc of regionLocations) {
                try {
                  const npcResponse = await entitiesApi.getByLocation(loc.location_id);
                  if (npcResponse.data) {
                    allNpcs.push(...(Array.isArray(npcResponse.data) ? npcResponse.data : [npcResponse.data]));
                  }
                } catch (e) {
                  // NPC가 없을 수 있음
                }
              }
              setNpcs(allNpcs);
            } catch (error) {
              console.error('NPC 로드 실패:', error);
            }
          }
          // onRefresh() 호출하지 않음 - 전체 새로고침 방지
        }}
      />

      {/* Entity Picker Modal */}
      <EntityPickerModal
        isOpen={entityPickerOpen}
        onClose={() => {
          setEntityPickerOpen(false);
          setEntityPickerTarget(null);
        }}
        onSelect={(entityId, entityName) => {
          if (entityPickerTarget === 'location') {
            setLocationInfo({
              ...locationInfo,
              ownership: {
                ...locationInfo.ownership,
                owner_entity_id: entityId,
              },
            });
          } else if (entityPickerTarget === 'cell') {
            setCellInfo({
              ...cellInfo,
              ownership: {
                ...cellInfo.ownership,
                owner_entity_id: entityId,
              },
            });
          }
        }}
        currentEntityId={
          entityPickerTarget === 'location'
            ? locationInfo.ownership.owner_entity_id
            : entityPickerTarget === 'cell'
            ? cellInfo.ownership.owner_entity_id
            : undefined
        }
      />
    </div>
  );
};
