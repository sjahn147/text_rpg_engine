/**
 * 월드 에디터 API 서비스
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';  // 월드 에디터 전용 포트

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10초 타임아웃
});

// 요청 인터셉터: 에러 로깅만 (개발 환경)
api.interceptors.request.use(
  (config) => config,
  (error) => {
    if (import.meta.env.DEV) {
      console.error('API 요청 오류:', error);
    }
    return Promise.reject(error);
  }
);

// 응답 인터셉터: 에러 처리 개선
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 연결 거부 에러는 조용히 처리 (서버가 시작 중일 수 있음)
    if (error.code === 'ERR_NETWORK' || error.code === 'ECONNREFUSED') {
      if (import.meta.env.DEV) {
        // 개발 환경에서만 한 번만 로그 출력
        if (!(window as any).__api_error_logged) {
          console.warn('백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.');
          (window as any).__api_error_logged = true;
        }
      }
    } else if (error.response) {
      // 서버 응답이 있는 경우만 상세 로그
      if (import.meta.env.DEV) {
        console.error(`API 오류 [${error.response.status}]:`, error.response.data);
      }
    }
    return Promise.reject(error);
  }
);

// Regions API
export const regionsApi = {
  getAll: () => api.get('/api/regions'),
  getById: (id: string) => api.get(`/api/regions/${id}`),
  create: (data: any) => api.post('/api/regions', data),
  update: (id: string, data: any) => api.put(`/api/regions/${id}`, data),
  delete: (id: string) => api.delete(`/api/regions/${id}`),
};

// Locations API
export const locationsApi = {
  getAll: () => api.get('/api/locations'),
  getById: (id: string) => api.get(`/api/locations/${id}`),
  getByRegion: (regionId: string) => api.get(`/api/locations/region/${regionId}`),
  create: (data: any) => api.post('/api/locations', data),
  update: (id: string, data: any) => api.put(`/api/locations/${id}`, data),
  delete: (id: string) => api.delete(`/api/locations/${id}`),
};

// Cells API
export const cellsApi = {
  getAll: () => api.get('/api/cells'),
  getById: (id: string) => api.get(`/api/cells/${id}`),
  getByLocation: (locationId: string) => api.get(`/api/cells/location/${locationId}`),
  create: (data: any) => api.post('/api/cells', data),
  update: (id: string, data: any) => api.put(`/api/cells/${id}`, data),
  delete: (id: string) => api.delete(`/api/cells/${id}`),
  // Cell Properties API
  getProperties: (cellId: string) => api.get(`/api/cells/${cellId}/properties`),
  updateProperties: (cellId: string, properties: any) => 
    api.put(`/api/cells/${cellId}/properties`, { properties }),
};

// Roads API
export const roadsApi = {
  getAll: () => api.get('/api/roads'),
  getById: (id: string) => api.get(`/api/roads/${id}`),
  create: (data: any) => api.post('/api/roads', data),
  update: (id: string, data: any) => api.put(`/api/roads/${id}`, data),
  delete: (id: string) => api.delete(`/api/roads/${id}`),
};

// Pins API
export const pinsApi = {
  getAll: () => api.get('/api/pins'),
  getById: (id: string) => api.get(`/api/pins/${id}`),
  getByGameData: (gameDataId: string, pinType: string) => 
    api.get(`/api/pins/game-data/${gameDataId}/${pinType}`),
  create: (data: any) => api.post('/api/pins', data),
  update: (id: string, data: any) => api.put(`/api/pins/${id}`, data),
  delete: (id: string) => api.delete(`/api/pins/${id}`),
  // 핀 연결 API
  connectToRegion: (data: { pin_id: string; region_id: string; create_if_not_exists?: boolean; region_name?: string }) =>
    api.post('/api/pins/connect/region', data),
  connectToLocation: (data: { pin_id: string; location_id: string; create_if_not_exists?: boolean; location_name?: string; region_id?: string }) =>
    api.post('/api/pins/connect/location', data),
  connectToCell: (data: { pin_id: string; cell_id: string; create_if_not_exists?: boolean; cell_name?: string; location_id?: string }) =>
    api.post('/api/pins/connect/cell', data),
};

// Map Metadata API
export const mapApi = {
  get: (mapId: string = 'default_map') => api.get(`/api/map/${mapId}`),
  create: (data: any) => api.post('/api/map', data),
  update: (mapId: string, data: any) => api.put(`/api/map/${mapId}`, data),
};

// Entities (NPCs) API
export const entitiesApi = {
  getAll: () => api.get('/api/entities'),
  getByCell: (cellId: string) => api.get(`/api/entities/cell/${cellId}`),
  getByLocation: (locationId: string) => api.get(`/api/entities/location/${locationId}`),
  getById: (id: string) => api.get(`/api/entities/${id}`),
  create: (data: any) => api.post('/api/entities', data),
  update: (id: string, data: any) => api.put(`/api/entities/${id}`, data),
  delete: (id: string) => api.delete(`/api/entities/${id}`),
};

// Dialogue API
export const dialogueApi = {
  getContextsByEntity: (entityId: string) => api.get(`/api/dialogue/contexts/entity/${entityId}`),
  getContext: (dialogueId: string) => api.get(`/api/dialogue/contexts/${dialogueId}`),
  createContext: (data: any) => api.post('/api/dialogue/contexts', data),
  updateContext: (dialogueId: string, data: any) => api.put(`/api/dialogue/contexts/${dialogueId}`, data),
  getTopics: (dialogueId: string) => api.get(`/api/dialogue/topics/${dialogueId}`),
  createTopic: (data: any) => api.post('/api/dialogue/topics', data),
  updateTopic: (topicId: string, data: any) => api.put(`/api/dialogue/topics/${topicId}`, data),
  deleteTopic: (topicId: string) => api.delete(`/api/dialogue/topics/${topicId}`),
  // Dialogue Knowledge API
  getAllKnowledge: () => api.get('/api/dialogue/knowledge'),
  getKnowledge: (knowledgeId: string) => api.get(`/api/dialogue/knowledge/${knowledgeId}`),
  getKnowledgeByType: (knowledgeType: string) => api.get(`/api/dialogue/knowledge/type/${knowledgeType}`),
  createKnowledge: (data: any) => api.post('/api/dialogue/knowledge', data),
  updateKnowledge: (knowledgeId: string, data: any) => api.put(`/api/dialogue/knowledge/${knowledgeId}`, data),
  deleteKnowledge: (knowledgeId: string) => api.delete(`/api/dialogue/knowledge/${knowledgeId}`),
};

// Behavior Schedule API
export const behaviorSchedulesApi = {
  getByEntity: (entityId: string) => api.get(`/api/behavior-schedules/entity/${entityId}`),
  getById: (scheduleId: string) => api.get(`/api/behavior-schedules/${scheduleId}`),
  create: (data: any) => api.post('/api/behavior-schedules', data),
  update: (scheduleId: string, data: any) => api.put(`/api/behavior-schedules/${scheduleId}`, data),
  delete: (scheduleId: string) => api.delete(`/api/behavior-schedules/${scheduleId}`),
};

// Location/Cell Management API
export const managementApi = {
  createLocation: (data: { region_id: string; location_name: string; location_type?: string; location_description?: string }) =>
    api.post('/api/manage/locations/create', data),
  getLocationWithCells: (locationId: string) => api.get(`/api/manage/locations/${locationId}/with-cells`),
  createCell: (data: { location_id: string; cell_name: string; matrix_width?: number; matrix_height?: number; cell_description?: string }) =>
    api.post('/api/manage/cells/create', data),
  getCellWithLocation: (cellId: string) => api.get(`/api/manage/cells/${cellId}/full`),
  createEntity: (data: { cell_id: string; entity_name: string; entity_type?: string; entity_description?: string }) =>
    api.post('/api/manage/entities/create', data),
};

// World Objects API
export const worldObjectsApi = {
  getAll: () => api.get('/api/world-objects'),
  getById: (id: string) => api.get(`/api/world-objects/${id}`),
  getByCell: (cellId: string) => api.get(`/api/world-objects/cell/${cellId}`),
  create: (data: any) => api.post('/api/world-objects', data),
  update: (id: string, data: any) => api.put(`/api/world-objects/${id}`, data),
  delete: (id: string) => api.delete(`/api/world-objects/${id}`),
};

// Effect Carriers API
export const effectCarriersApi = {
  getAll: (params?: { carrier_type?: string; source_entity_id?: string; tags?: string }) => {
    const queryParams = new URLSearchParams();
    if (params?.carrier_type) queryParams.append('carrier_type', params.carrier_type);
    if (params?.source_entity_id) queryParams.append('source_entity_id', params.source_entity_id);
    if (params?.tags) queryParams.append('tags', params.tags);
    const query = queryParams.toString();
    return api.get(`/api/effect-carriers${query ? `?${query}` : ''}`);
  },
  getById: (id: string) => api.get(`/api/effect-carriers/${id}`),
  getByEntity: (entityId: string) => api.get(`/api/effect-carriers/entity/${entityId}`),
  getByType: (carrierType: string) => api.get(`/api/effect-carriers/type/${carrierType}`),
  create: (data: any) => api.post('/api/effect-carriers', data),
  update: (id: string, data: any) => api.put(`/api/effect-carriers/${id}`, data),
  delete: (id: string) => api.delete(`/api/effect-carriers/${id}`),
};

// Items API
export const itemsApi = {
  getAll: (itemType?: string) => {
    const query = itemType ? `?item_type=${itemType}` : '';
    return api.get(`/api/items${query}`);
  },
  getById: (id: string) => api.get(`/api/items/${id}`),
  create: (data: any) => api.post('/api/items', data),
  update: (id: string, data: any) => api.put(`/api/items/${id}`, data),
  delete: (id: string) => api.delete(`/api/items/${id}`),
};

// Search API
export const searchApi = {
  search: (query: string, types?: string[]) => {
    const queryParams = new URLSearchParams();
    queryParams.append('q', query);
    if (types && types.length > 0) {
      types.forEach(type => queryParams.append('type', type));
    }
    return api.get(`/api/search?${queryParams.toString()}`);
  },
};

// Project API
export const projectApi = {
  export: () => api.get('/api/project/export'),
  import: (data: any) => api.post('/api/project/import', data),
  importFile: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/project/import/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  importEntities: (entities: any[]) => api.post('/api/project/import/entities', entities),
  importRegions: (regions: any[]) => api.post('/api/project/import/regions', regions),
  validateAll: () => api.get('/api/project/validate/all'),
  validateOrphans: () => api.get('/api/project/validate/orphans'),
  validateDuplicates: () => api.get('/api/project/validate/duplicates'),
};

// Relationships API
export const relationshipsApi = {
  getRelationships: (entityType: string, entityId: string) => 
    api.get(`/api/relationships/${entityType}/${entityId}`),
};

// Map Hierarchy API
export const mapHierarchyApi = {
  // Region Map
  getRegionMap: (regionId: string) => api.get(`/api/maps/region/${regionId}`),
  getRegionLocations: (regionId: string) => api.get(`/api/maps/region/${regionId}/locations`),
  placeLocationInRegion: (regionId: string, locationId: string, position: { x: number; y: number }) =>
    api.post(`/api/maps/region/${regionId}/locations/${locationId}/position`, position),
  updateLocationPosition: (regionId: string, locationId: string, position: { x: number; y: number }) =>
    api.put(`/api/maps/region/${regionId}/locations/${locationId}/position`, position),
  updateRegionMapMetadata: (regionId: string, metadata: any) =>
    api.put(`/api/maps/region/${regionId}/metadata`, metadata),
  
  // Location Map
  getLocationMap: (locationId: string) => api.get(`/api/maps/location/${locationId}`),
  getLocationCells: (locationId: string) => api.get(`/api/maps/location/${locationId}/cells`),
  placeCellInLocation: (locationId: string, cellId: string, position: { x: number; y: number }) =>
    api.post(`/api/maps/location/${locationId}/cells/${cellId}/position`, position),
  updateCellPosition: (locationId: string, cellId: string, position: { x: number; y: number }) =>
    api.put(`/api/maps/location/${locationId}/cells/${cellId}/position`, position),
  updateLocationMapMetadata: (locationId: string, metadata: any) =>
    api.put(`/api/maps/location/${locationId}/metadata`, metadata),
};

export default api;

