/**
 * 월드 에디터 TypeScript 타입 정의
 */

// 지도 메타데이터
export interface MapMetadata {
  map_id: string;
  map_name: string;
  background_image?: string;
  background_color: string;
  width: number;
  height: number;
  grid_enabled: boolean;
  grid_size: number;
  zoom_level: number;
  viewport_x: number;
  viewport_y: number;
  created_at: string;
  updated_at: string;
}

// 핀 데이터
export interface PinData {
  pin_id: string;
  pin_name: string; // 핀 표시 이름
  game_data_id: string;
  pin_type: 'region' | 'location' | 'cell';
  x: number;
  y: number;
  icon_type: string;
  color: string;
  size: number;
  created_at: string;
  updated_at: string;
}

// 도로 데이터
export interface PathPoint {
  x: number;
  y: number;
}

export interface RoadData {
  road_id: string;
  from_pin_id?: string;
  to_pin_id?: string;
  from_region_id?: string;
  from_location_id?: string;
  to_region_id?: string;
  to_location_id?: string;
  road_type: 'normal' | 'hidden' | 'river' | 'mountain_pass';
  distance?: number;
  travel_time?: number;
  danger_level: number;
  road_properties: Record<string, any>;
  path_coordinates: PathPoint[];
  color?: string;
  width?: number;
  dashed?: boolean;
  created_at: string;
  updated_at: string;
}

// Region/Location/Cell 데이터
export interface RegionData {
  region_id: string;
  region_name: string;
  region_description?: string;
  region_type?: string;
  region_properties?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface LocationData {
  location_id: string;
  region_id: string;
  location_name: string;
  location_description?: string;
  location_type?: string;
  location_properties?: Record<string, any>;
  owner_name?: string; // SSOT: JOIN으로 해결, Properties에 저장하지 않음
  created_at: string;
  updated_at: string;
}

export interface CellData {
  cell_id: string;
  location_id: string;
  cell_name?: string;
  matrix_width: number;
  matrix_height: number;
  cell_description?: string;
  cell_properties?: Record<string, any>;
  cell_status?: string;
  cell_type?: string;
  owner_name?: string; // SSOT: JOIN으로 해결, Properties에 저장하지 않음
  created_at: string;
  updated_at: string;
}

// D&D 스타일 정보
export interface DemographicsInfo {
  population: number;
  races: Record<string, number>;
  classes: Record<string, number>;
}

export interface EconomyInfo {
  primary_industry: string;
  trade_goods: string[];
  gold_value: number;
}

export interface GovernmentInfo {
  type: string;
  leader: string;
  laws: string[];
}

export interface CultureInfo {
  religion: string[];
  customs: string[];
  festivals: string[];
}

export interface LoreInfo {
  history: string;
  legends: string[];
  secrets: string[];
}

export interface DnDLocationInfo {
  name: string;
  description: string;
  type: string;
  demographics: DemographicsInfo;
  economy: EconomyInfo;
  government: GovernmentInfo;
  culture: CultureInfo;
  lore: LoreInfo;
  npcs: Array<Record<string, any>>;
  quests: Array<Record<string, any>>;
  shops: Array<Record<string, any>>;
}

// 편집 도구 타입
export type EditorTool = 'select' | 'pin' | 'road' | 'pan' | 'zoom';

// WebSocket 메시지 타입
export interface WebSocketMessage {
  type: 'ping' | 'pong' | 'pin_update' | 'road_update' | 'map_update';
  data?: any;
  timestamp?: string;
}

