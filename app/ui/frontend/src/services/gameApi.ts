/**
 * 게임플레이 API 서비스
 * RPG 엔진 백엔드와 통신
 */

import axios, { AxiosInstance } from 'axios';
import { GameState, CellInfo, DialogueInfo, GameAction } from '../types/game';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

export class GameApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    });

    // 에러 핸들링
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  // 게임 세션 시작
  async startNewGame(playerTemplateId: string, startCellId?: string) {
    const response = await this.client.post('/api/gameplay/start', {
      player_template_id: playerTemplateId,
      start_cell_id: startCellId,
    });
    return response.data;
  }

  // 현재 게임 상태 조회
  async getCurrentState(sessionId: string): Promise<GameState> {
    const response = await this.client.get(`/api/gameplay/state/${sessionId}`);
    return response.data;
  }

  // 현재 셀 정보 조회
  async getCurrentCell(sessionId: string): Promise<CellInfo> {
    const response = await this.client.get(`/api/gameplay/cell/${sessionId}`);
    return response.data;
  }

  // 플레이어 이동
  async movePlayer(sessionId: string, targetCellId: string) {
    const response = await this.client.post(`/api/gameplay/move`, {
      session_id: sessionId,
      target_cell_id: targetCellId,
    });
    return response.data;
  }

  // 대화 시작
  async startDialogue(sessionId: string, npcId: string): Promise<DialogueInfo> {
    const response = await this.client.post(`/api/gameplay/dialogue/start`, {
      session_id: sessionId,
      npc_id: npcId,
    });
    return response.data;
  }

  // 대화 진행 (선택지 선택)
  async processDialogueChoice(
    sessionId: string,
    dialogueId: string,
    choiceId: string
  ): Promise<DialogueInfo> {
    const response = await this.client.post(`/api/gameplay/dialogue/choice`, {
      session_id: sessionId,
      dialogue_id: dialogueId,
      choice_id: choiceId,
    });
    return response.data;
  }

  // 엔티티와 상호작용
  async interactWithEntity(sessionId: string, entityId: string, actionType?: string) {
    const response = await this.client.post(`/api/gameplay/interact`, {
      session_id: sessionId,
      entity_id: entityId,
      action_type: actionType,
    });
    return response.data;
  }

  // 오브젝트와 상호작용
  async interactWithObject(sessionId: string, objectId: string, actionType?: string) {
    const response = await this.client.post(`/api/gameplay/interact/object`, {
      session_id: sessionId,
      object_id: objectId,
      action_type: actionType,
    });
    return response.data;
  }

  // 오브젝트의 contents 조회
  async getObjectContents(sessionId: string, objectId: string) {
    const response = await this.client.get(`/api/gameplay/object/${objectId}/contents`, {
      params: { session_id: sessionId },
    });
    return response.data;
  }

  // 아이템 사용
  async useItem(sessionId: string, itemId: string) {
    const response = await this.client.post('/api/gameplay/item/use', {
      session_id: sessionId,
      item_id: itemId,
    });
    return response.data;
  }

  // 아이템 먹기
  async eatItem(sessionId: string, itemId: string) {
    const response = await this.client.post('/api/gameplay/item/eat', {
      session_id: sessionId,
      item_id: itemId,
    });
    return response.data;
  }

  // 아이템 장착
  async equipItem(sessionId: string, itemId: string) {
    const response = await this.client.post('/api/gameplay/item/equip', {
      session_id: sessionId,
      item_id: itemId,
    });
    return response.data;
  }

  // 아이템 해제
  async unequipItem(sessionId: string, itemId: string) {
    const response = await this.client.post('/api/gameplay/item/unequip', {
      session_id: sessionId,
      item_id: itemId,
    });
    return response.data;
  }

  // 아이템 버리기
  async dropItem(sessionId: string, itemId: string) {
    const response = await this.client.post('/api/gameplay/item/drop', {
      session_id: sessionId,
      item_id: itemId,
    });
    return response.data;
  }

  // 오브젝트에서 아이템/장비/Effect Carrier 획득
  async pickupFromObject(sessionId: string, objectId: string, itemId?: string) {
    const response = await this.client.post(`/api/gameplay/interact/object/pickup`, {
      session_id: sessionId,
      object_id: objectId,
      item_id: itemId, // 선택사항
    });
    return response.data;
  }

  // 아이템 조합
  async combineItems(sessionId: string, itemIds: string[]) {
    const response = await this.client.post(`/api/gameplay/combine`, {
      session_id: sessionId,
      items: itemIds,
    });
    return response.data;
  }

  // 플레이어 인벤토리 조회
  async getPlayerInventory(sessionId: string) {
    const response = await this.client.get(`/api/gameplay/inventory/${sessionId}`);
    // API 응답이 {success: true, inventory: [...], equipped_items: [...]} 형태
    return response.data;
  }

  // 플레이어 캐릭터 정보 조회
  async getPlayerCharacter(sessionId: string) {
    const response = await this.client.get(`/api/gameplay/character/${sessionId}`);
    return response.data;
  }

  // 사용 가능한 액션 조회
  async getAvailableActions(sessionId: string): Promise<GameAction[]> {
    const response = await this.client.get(`/api/gameplay/actions/${sessionId}`);
    return response.data;
  }

  // 헬스 체크
  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const gameApi = new GameApiClient();

