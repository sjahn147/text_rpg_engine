/**
 * 게임 관련 타입 정의 (RPG 엔진용)
 */

// 게임 상태
export interface GameState {
  session_id: string;
  player_id: string;
  current_cell_id: string;
  current_location: string;
  play_time: number;
  flags: Record<string, boolean>;
  variables: Record<string, unknown>;
  save_date: string;
  version: string;
}

// 셀 정보
export interface CellInfo {
  cell_id: string;
  cell_name: string;
  description: string;
  location_name: string;
  region_name: string;
  entities: EntityInfo[];
  objects: WorldObjectInfo[];
  connected_cells: ConnectedCell[];
}

// 엔티티 정보
export interface EntityInfo {
  entity_id?: string; // game_entity_id (선택적)
  runtime_entity_id?: string; // runtime_entity_id (우선 사용)
  entity_name: string;
  entity_type: 'player' | 'npc' | 'creature';
  description?: string;
  position?: { x: number; y: number; z: number };
  current_position?: { x: number; y: number; z: number; runtime_cell_id?: string }; // API 응답 형식
  can_interact: boolean;
  dialogue_id?: string;
}

// 월드 오브젝트 정보
export interface WorldObjectInfo {
  object_id: string;
  object_name: string;
  description?: string;
  position: { x: number; y: number; z: number };
  can_interact: boolean;
  properties?: {
    contents?: string[]; // 아이템/장비/Effect Carrier ID 목록
    [key: string]: any;
  };
}

// 연결된 셀
export interface ConnectedCell {
  cell_id: string;
  cell_name: string;
  direction: string;
}

// 액션 (선택지)
export interface GameAction {
  action_id: string;
  action_type: 'move' | 'dialogue' | 'interact' | 'examine' | 'observe' | 'open' | 'close' | 'light' | 'extinguish' | 'sit' | 'rest' | 'pickup';
  text: string;
  target_id?: string;
  target_name?: string;
  target_type?: 'object' | 'entity'; // 추가: 타겟 타입
  description?: string;
}

// 메시지
export interface GameMessage {
  text: string;
  character_name?: string;
  message_type: 'narration' | 'dialogue' | 'system';
  timestamp: number;
}

// 대화 정보
export interface DialogueInfo {
  dialogue_id: string;
  npc_name: string;
  messages: DialogueMessage[];
  choices?: DialogueChoice[];
}

export interface DialogueMessage {
  text: string;
  character_name?: string;
  message_id: string;
}

export interface DialogueChoice {
  choice_id: string;
  text: string;
  next_message_id?: string;
  conditions?: Condition[];
}

export interface Condition {
  condition_type: string;
  target: string;
  operator: string;
  value: unknown;
}

