/**
 * 월드 에디터 상태 관리 Hook
 */
import { useState, useEffect, useCallback } from 'react';
import { MapMetadata, PinData, RoadData, RegionData, LocationData, CellData } from '../types';
import { mapApi, pinsApi, roadsApi, regionsApi, locationsApi, cellsApi } from '../services/api';

export const useWorldEditor = () => {
  const [mapState, setMapState] = useState<MapMetadata | null>(null);
  const [pins, setPins] = useState<PinData[]>([]);
  const [roads, setRoads] = useState<RoadData[]>([]);
  const [regions, setRegions] = useState<RegionData[]>([]);
  const [locations, setLocations] = useState<LocationData[]>([]);
  const [cells, setCells] = useState<CellData[]>([]);
  const [selectedPin, setSelectedPin] = useState<string | null>(null);
  const [selectedRoad, setSelectedRoad] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // 초기 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // 병렬로 모든 데이터 로드 (에러는 조용히 처리)
        const [mapRes, pinsRes, roadsRes, regionsRes, locationsRes, cellsRes] = await Promise.all([
          mapApi.get().catch(() => ({ data: null })),
          pinsApi.getAll().catch(() => ({ data: [] })),
          roadsApi.getAll().catch(() => ({ data: [] })),
          regionsApi.getAll().catch(() => ({ data: [] })),
          locationsApi.getAll().catch(() => ({ data: [] })),
          cellsApi.getAll().catch(() => ({ data: [] })),
        ]);

        setMapState(mapRes.data);
        setPins(pinsRes.data || []);
        setRoads(roadsRes.data || []);
        setRegions(regionsRes.data || []);
        setLocations(locationsRes.data || []);
        setCells(cellsRes.data || []);
      } catch (error) {
        console.error('데이터 로드 실패:', error);
        // 에러가 발생해도 기본값으로 설정하여 화면이 표시되도록 함
        setMapState(null);
        setPins([]);
        setRoads([]);
        setRegions([]);
        setLocations([]);
        setCells([]);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // 핀 추가
  const addPin = useCallback(async (pinData: Omit<PinData, 'pin_id' | 'created_at' | 'updated_at'>) => {
    try {
      console.log('핀 추가 요청:', pinData);
      
      // 데이터 타입 검증 및 변환
      const validatedData = {
        ...pinData,
        x: typeof pinData.x === 'number' ? pinData.x : parseFloat(String(pinData.x)),
        y: typeof pinData.y === 'number' ? pinData.y : parseFloat(String(pinData.y)),
        size: typeof pinData.size === 'number' ? Math.round(pinData.size) : parseInt(String(pinData.size || 20), 10),
      };
      
      const response = await pinsApi.create(validatedData);
      console.log('핀 추가 응답:', response.data);
      setPins(prev => {
        const newPins = [...prev, response.data];
        console.log('업데이트된 핀 목록:', newPins);
        return newPins;
      });
      return response.data;
    } catch (error: any) {
      console.error('핀 추가 실패:', error);
      if (error.response) {
        console.error('에러 응답:', error.response.data);
        console.error('에러 상태:', error.response.status);
      }
      if (error instanceof Error) {
        console.error('에러 상세:', error.message, error.stack);
      }
      throw error;
    }
  }, []);

  // 핀 업데이트
  const updatePin = useCallback(async (pinId: string, updates: Partial<PinData>) => {
    try {
      const response = await pinsApi.update(pinId, updates);
      setPins(prev => prev.map(p => p.pin_id === pinId ? response.data : p));
      return response.data;
    } catch (error) {
      console.error('핀 업데이트 실패:', error);
      throw error;
    }
  }, []);

  // 핀 삭제
  const deletePin = useCallback(async (pinId: string) => {
    try {
      await pinsApi.delete(pinId);
      setPins(prev => prev.filter(p => p.pin_id !== pinId));
      if (selectedPin === pinId) {
        setSelectedPin(null);
      }
    } catch (error) {
      console.error('핀 삭제 실패:', error);
      throw error;
    }
  }, [selectedPin]);

  // 도로 추가
  const addRoad = useCallback(async (roadData: Omit<RoadData, 'road_id' | 'created_at' | 'updated_at'>) => {
    try {
      const response = await roadsApi.create(roadData);
      setRoads(prev => [...prev, response.data]);
      return response.data;
    } catch (error) {
      console.error('도로 추가 실패:', error);
      throw error;
    }
  }, []);

  // 도로 업데이트
  const updateRoad = useCallback(async (roadId: string, updates: Partial<RoadData>) => {
    try {
      const response = await roadsApi.update(roadId, updates);
      setRoads(prev => prev.map(r => r.road_id === roadId ? response.data : r));
      return response.data;
    } catch (error) {
      console.error('도로 업데이트 실패:', error);
      throw error;
    }
  }, []);

  // 도로 삭제
  const deleteRoad = useCallback(async (roadId: string) => {
    try {
      await roadsApi.delete(roadId);
      setRoads(prev => prev.filter(r => r.road_id !== roadId));
      if (selectedRoad === roadId) {
        setSelectedRoad(null);
      }
    } catch (error) {
      console.error('도로 삭제 실패:', error);
      throw error;
    }
  }, [selectedRoad]);

  // 지도 메타데이터 업데이트
  const updateMap = useCallback(async (updates: Partial<MapMetadata>) => {
    if (!mapState) return;
    
    try {
      const response = await mapApi.update(mapState.map_id, updates);
      setMapState(response.data);
      return response.data;
    } catch (error) {
      console.error('지도 업데이트 실패:', error);
      throw error;
    }
  }, [mapState]);

  // 데이터 새로고침
  const refreshData = useCallback(async () => {
    try {
      setLoading(true);
      
      // 병렬로 모든 데이터 로드
      const [mapRes, pinsRes, roadsRes, regionsRes, locationsRes, cellsRes] = await Promise.all([
        mapApi.get(),
        pinsApi.getAll(),
        roadsApi.getAll(),
        regionsApi.getAll(),
        locationsApi.getAll(),
        cellsApi.getAll(),
      ]);

      setMapState(mapRes.data);
      setPins(pinsRes.data);
      setRoads(roadsRes.data);
      setRegions(regionsRes.data);
      setLocations(locationsRes.data);
      setCells(cellsRes.data);
    } catch (error) {
      console.error('데이터 새로고침 실패:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
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
  };
};

