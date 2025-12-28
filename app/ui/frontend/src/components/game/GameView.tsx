/**
 * 메인 게임 뷰 컴포넌트 - RPG 엔진용
 */

import { useEffect, useState, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { BackgroundLayer } from './BackgroundLayer';
import { CharacterLayer } from './CharacterLayer';
import { LocationLayer } from './LocationLayer';
import { MessageLayer } from './MessageLayer';
import { ChoiceLayer } from './ChoiceLayer';
import { InteractionLayer } from './InteractionLayer';
import { ContextMenu } from './ContextMenu';
import { ObjectMenu } from './ObjectMenu';
import { InfoPanel } from './InfoPanel';
import { SaveLoadMenu } from './SaveLoadMenu';
import { ObjectInventoryModal } from './ObjectInventoryModal';
import { useGameStore } from '../../store/gameStore';
import { gameApi } from '../../services/gameApi';
import { GameAction, WorldObjectInfo, EntityInfo } from '../../types/game';
import type { GameScreenType } from '../../hooks/game/useGameNavigation';

interface GameViewProps {
  onNavigate?: (screen: GameScreenType) => void;
}

export const GameView: React.FC<GameViewProps> = ({ onNavigate }) => {
  const { 
    gameState, 
    currentCell, 
    currentMessage,
    setGameState, 
    setCurrentCell, 
    setCurrentMessage,
    setLoading, 
    setError,
    isAutoMode,
    setAutoMode,
    isSkipMode,
    setSkipMode,
    addHistory,
  } = useGameStore();
  
  const [availableActions, setAvailableActions] = useState<GameAction[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isInfoPanelOpen, setIsInfoPanelOpen] = useState(false);
  const [isSaveLoadMenuOpen, setIsSaveLoadMenuOpen] = useState(false);
  const [saveLoadMode, setSaveLoadMode] = useState<'save' | 'load'>('save');
  const [interactionTarget, setInteractionTarget] = useState<{ object?: WorldObjectInfo; entity?: EntityInfo } | null>(null);
  const [selectedObjectId, setSelectedObjectId] = useState<string | undefined>(undefined);
  const [discoveredObjects, setDiscoveredObjects] = useState<Set<string>>(new Set());
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; target: { object?: WorldObjectInfo; entity?: EntityInfo } } | null>(null);
  const [showObjectInventoryModal, setShowObjectInventoryModal] = useState(false);
  const [pickupObjectId, setPickupObjectId] = useState<string | null>(null);
  const [pickupObjectName, setPickupObjectName] = useState<string>('');
  const autoTimerRef = useRef<number | null>(null);

  // 게임 초기화 함수 (MainGameScreen에서도 처리하지만, GameView가 독립적으로 사용될 수 있도록 유지)
  const initializeGame = async () => {
    try {
      setLoading(true);
      setError(null);

      // 헬스 체크 (옵션)
      try {
        await gameApi.healthCheck();
      } catch (error) {
        console.warn('헬스 체크 실패, 게임 시작 계속 진행:', error);
      }

      // 새 게임 시작
      const playerTemplateId = 'e655a931-d989-4ca6-b3ce-737f6b426978';
      const startCellId = 'CELL_INN_ROOM_001';
      const response = await gameApi.startNewGame(playerTemplateId, startCellId);
      setGameState(response.game_state);

      // 현재 셀 정보 로드
      const cell = await gameApi.getCurrentCell(response.game_state.session_id);
      setCurrentCell(cell);

      // 초기 메시지 설정
      setCurrentMessage({
        text: cell.description || `${cell.cell_name}에 도착했습니다.`,
        message_type: 'narration',
        timestamp: Date.now(),
      });

      // 사용 가능한 액션 조회
      const actions = await gameApi.getAvailableActions(response.game_state.session_id);
      setAvailableActions(actions);

      setIsInitialized(true);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : '게임을 시작할 수 없습니다.';
      setError(errorMessage);
      console.error('게임 초기화 실패:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // MainGameScreen에서 초기화가 완료되면 isInitialized를 true로 설정
  useEffect(() => {
    if (gameState && currentCell && !isInitialized) {
      setIsInitialized(true);
      // 액션 로드
      if (gameState.session_id) {
        gameApi.getAvailableActions(gameState.session_id).then(setAvailableActions);
      }
    }
  }, [gameState, currentCell, isInitialized]);

  // 메시지 클릭으로 진행
  const handleMessageClick = () => {
    if (!currentMessage) return;
    
    // 다음 액션 표시 (메시지가 끝나면)
    // 현재는 액션이 이미 표시되어 있으므로 아무것도 하지 않음
  };

  // 메시지 타이핑 완료
  const handleMessageComplete = useCallback(() => {
    if (!currentCell) return;
    
    // 히스토리에 추가
    if (currentMessage) {
      addHistory({
        cellId: currentCell.cell_id,
        characterName: currentMessage.character_name,
        text: currentMessage.text,
        timestamp: Date.now(),
      });
    }
  }, [currentCell, currentMessage, addHistory]);

  // 액션 선택 처리
  const handleActionSelect = async (action: GameAction) => {
    if (!gameState) return;

    try {
      setLoading(true);
      
      switch (action.action_type) {
        case 'move':
          if (action.target_id) {
            const response = await gameApi.movePlayer(gameState.session_id, action.target_id);
            setGameState(response.game_state);
            
            // 새로운 셀 정보 로드
            const newCell = await gameApi.getCurrentCell(gameState.session_id);
            setCurrentCell(newCell);
            
            // 이동 메시지
            setCurrentMessage({
              text: `${newCell.cell_name}로 이동했습니다.`,
              message_type: 'narration',
              timestamp: Date.now(),
            });
            
            // 새로운 액션 조회
            const actions = await gameApi.getAvailableActions(gameState.session_id);
            setAvailableActions(actions);
          }
          break;
          
        case 'dialogue':
          if (action.target_id) {
            const dialogue = await gameApi.startDialogue(gameState.session_id, action.target_id);
            // 대화 처리 (추후 구현)
            setCurrentMessage({
              text: dialogue.messages[0]?.text || '대화를 시작합니다.',
              character_name: dialogue.npc_name,
              message_type: 'dialogue',
              timestamp: Date.now(),
            });
          }
          break;
          
        case 'interact':
          if (action.target_id) {
            const response = await gameApi.interactWithEntity(gameState.session_id, action.target_id);
            setCurrentMessage({
              text: response.message || `${action.target_name}와 상호작용했습니다.`,
              message_type: 'system',
              timestamp: Date.now(),
            });
          }
          break;
          
        case 'observe':
          // 주변 관찰하기 - 모든 오브젝트 발견
          if (currentCell && currentCell.objects) {
            // 모든 오브젝트 발견 처리 (object_id 또는 runtime_object_id 사용)
            const allObjectIds = currentCell.objects.map(obj => 
              obj.object_id || (obj as any).runtime_object_id || (obj as any).game_object_id
            ).filter(id => id);
            setDiscoveredObjects(prev => new Set([...prev, ...allObjectIds]));
            
            // 메시지 표시
            const objectNames = currentCell.objects.map(obj => obj.object_name).join(', ');
            setCurrentMessage({
              text: action.description || `주변을 관찰하니 ${objectNames} 등이 보입니다.`,
              message_type: 'narration',
              timestamp: Date.now(),
            });
            
            // 새로운 액션 조회 (개별 오브젝트 액션 포함)
            const actions = await gameApi.getAvailableActions(gameState.session_id);
            setAvailableActions(actions);
          }
          break;
          
        case 'examine':
          // 개별 관찰하기 - 엔티티만 처리 (오브젝트는 컨텍스트 메뉴에서)
          if (action.target_id && currentCell) {
            const targetEntity = currentCell.entities.find(e => e.entity_id === action.target_id);
            
            if (targetEntity) {
              try {
                const response = await gameApi.interactWithEntity(
                  gameState.session_id,
                  action.target_id,
                  'examine'
                );
                
                setCurrentMessage({
                  text: response.message,
                  message_type: 'narration',
                  timestamp: Date.now(),
                });
              } catch (error) {
                setCurrentMessage({
                  text: action.description || `${action.target_name}를 살펴봅니다.`,
                  message_type: 'narration',
                  timestamp: Date.now(),
                });
              }
            } else {
              setCurrentMessage({
                text: action.description || `${action.target_name}를 살펴봅니다.`,
                message_type: 'narration',
                timestamp: Date.now(),
              });
            }
          }
          break;
          
        case 'open':
        case 'close':
        case 'light':
        case 'extinguish':
        case 'sit':
        case 'rest':
        case 'pickup':
          // 오브젝트 상호작용 - 직접 처리
          if (action.target_id && action.target_type === 'object') {
            try {
              const response = await gameApi.interactWithObject(
                gameState.session_id,
                action.target_id,
                action.action_type
              );
              
              setCurrentMessage({
                text: response.message || `${action.target_name}와 상호작용했습니다.`,
                message_type: 'system',
                timestamp: Date.now(),
              });
              
              // 상태 변경 액션의 경우 셀 정보 새로고침
              if (['open', 'close', 'light', 'extinguish'].includes(action.action_type)) {
                const cell = await gameApi.getCurrentCell(gameState.session_id);
                setCurrentCell(cell);
                const actions = await gameApi.getAvailableActions(gameState.session_id);
                setAvailableActions(actions);
              }
            } catch (error) {
              setError(error instanceof Error ? error.message : '상호작용 실패');
              setCurrentMessage({
                text: `상호작용에 실패했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`,
                message_type: 'system',
                timestamp: Date.now(),
              });
            }
          }
          break;
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : '액션을 처리할 수 없습니다.';
      setError(errorMessage);
      console.error('액션 처리 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  // 키보드 단축키 처리
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // ESC: 정보 패널 토글
      if (e.key === 'Escape') {
        setIsInfoPanelOpen((prev) => !prev);
      }
      // I: 인벤토리 (정보 패널 열기)
      else if (e.key === 'i' || e.key === 'I') {
        setIsInfoPanelOpen(true);
      }
      // S: 저장 메뉴
      else if (e.key === 's' || e.key === 'S' && e.ctrlKey) {
        e.preventDefault();
        setSaveLoadMode('save');
        setIsSaveLoadMenuOpen(true);
      }
      // L: 불러오기 메뉴
      else if (e.key === 'l' || e.key === 'L' && e.ctrlKey) {
        e.preventDefault();
        setSaveLoadMode('load');
        setIsSaveLoadMenuOpen(true);
      }
      // A: 자동 모드 토글
      else if (e.key === 'a' || e.key === 'A') {
        setAutoMode(!isAutoMode);
      }
      // Ctrl: 스킵 모드
      else if (e.key === 'Control') {
        setSkipMode(true);
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.key === 'Control') {
        setSkipMode(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [isAutoMode, setSkipMode, setAutoMode]);

  // 컴포넌트 언마운트 시 타이머 정리
  useEffect(() => {
    return () => {
      if (autoTimerRef.current) {
        window.clearTimeout(autoTimerRef.current);
      }
    };
  }, []);

  // 로딩 상태
  if (!isInitialized || !currentCell || !gameState) {
    return (
      <div className="flex items-center justify-center h-full bg-gradient-to-b from-[#fafafa] via-[#f8f9fa] to-[#f0f7fa]">
        <div className="text-center">
          <motion.div
            className="text-sm font-light text-black/60 mb-6 tracking-wider"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0.6, 0.8, 0.6] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            로딩 중...
          </motion.div>
          <motion.div
            className="w-1 h-12 bg-black/20 mx-auto"
            animate={{ 
              scaleY: [1, 0.3, 1],
              opacity: [0.3, 0.6, 0.3]
            }}
            transition={{ 
              duration: 1.2, 
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        </div>
      </div>
    );
  }

  const showChoices = availableActions.length > 0 && currentMessage;

  // 배경 이미지 (셀에서 가져오기, 추후 구현)
  const backgroundImage = undefined; // currentCell?.background_image;
  
  // 캐릭터 정보 (셀의 엔티티에서 가져오기, 추후 구현)
  const characters = currentCell?.entities
    ?.filter((e) => e.entity_type === 'npc')
    .map((e) => ({
      character_id: e.entity_id,
      character_name: e.entity_name,
      position: 'center' as const,
      visible: true,
    })) || [];

  return (
    <motion.div
      className="game-container relative w-full h-full"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
      style={{ 
        position: 'relative', 
        width: '100%', 
        height: '100%',
        background: 'linear-gradient(180deg, #fafafa 0%, #f8f9fa 50%, #f0f7fa 100%)',
        overflow: 'hidden',
        margin: 0,
        padding: 0
      }}
    >
      {/* 레이어 구조 - novel_game 스타일 */}
      <BackgroundLayer background={backgroundImage} />
      <CharacterLayer characters={characters} />
      
      {/* 왼쪽 오브젝트 리스트 (발견된 것만 표시) */}
      {currentCell && discoveredObjects.size > 0 && (
        <ObjectMenu
          objects={(currentCell.objects || []).filter(obj => {
            const objId = obj.object_id || (obj as any).runtime_object_id || (obj as any).game_object_id;
            return objId && discoveredObjects.has(objId);
          })}
          selectedObjectId={selectedObjectId}
          onObjectSelect={(object) => {
            // 오브젝트 선택 시 컨텍스트 메뉴 표시 (화면 중앙)
            const centerX = window.innerWidth / 2;
            const centerY = window.innerHeight / 2;
            const objId = object.object_id || (object as any).runtime_object_id || (object as any).game_object_id;
            setContextMenu({
              x: centerX,
              y: centerY,
              target: { object }
            });
            setSelectedObjectId(objId);
          }}
        />
      )}
      
      {/* 상호작용 가능한 오브젝트/엔티티 레이어 - 발견된 것만 표시 */}
      {currentCell && (
        <InteractionLayer
          objects={(currentCell.objects || []).filter(obj => {
            const objId = obj.object_id || (obj as any).runtime_object_id || (obj as any).game_object_id;
            return objId && discoveredObjects.has(objId);
          })}
          entities={currentCell.entities || []}
          onObjectClick={(object, event) => {
            // 심즈 스타일 컨텍스트 메뉴 표시
            const objId = object.object_id || (object as any).runtime_object_id || (object as any).game_object_id;
            setContextMenu({
              x: event.clientX,
              y: event.clientY,
              target: { object }
            });
            setSelectedObjectId(objId);
          }}
          onEntityClick={(entity, event) => {
            // 심즈 스타일 컨텍스트 메뉴 표시
            setContextMenu({
              x: event.clientX,
              y: event.clientY,
              target: { entity }
            });
          }}
        />
      )}
      
      {/* 현재 위치 HUD */}
      {currentCell && (
        <LocationLayer 
          cell={currentCell}
          gameDate={gameState ? {
            year: 1273,
            month: 3,
            day: 15,
            season: '봄'
          } : undefined}
        />
      )}
      
      {/* 정보 패널 토글 버튼 */}
      <motion.button
        className="fixed z-30 bg-white/20 backdrop-blur-md border border-black/10 px-4 py-2 rounded-lg text-sm font-light text-black/80 hover:bg-white/30 transition-colors"
        onClick={() => setIsInfoPanelOpen(true)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        style={{
          position: 'fixed',
          top: currentCell && currentCell.objects && currentCell.objects.length > 0 ? '5.5rem' : '5.5rem', // ObjectMenu가 있으면 아래에 배치
          right: '1rem',
          zIndex: 30,
        }}
      >
        정보 (I)
      </motion.button>
      
      {currentMessage && (
        <MessageLayer
          message={currentMessage.text}
          characterName={currentMessage.character_name}
          messageType={currentMessage.message_type}
          onMessageComplete={handleMessageComplete}
          onClick={!showChoices ? handleMessageClick : undefined}
          isClickable={!showChoices}
        />
      )}
      
      {/* 선택지 레이어 - 컨텍스트 메뉴가 없을 때만 표시 */}
      {showChoices && !contextMenu && (
        <ChoiceLayer
          actions={availableActions}
          onActionSelect={handleActionSelect}
        />
      )}

      {/* 상태 표시 오버레이 */}
      {(isAutoMode || isSkipMode) && (
        <motion.div
          className="fixed top-4 right-4 z-30 bg-black/60 text-white px-4 py-2 rounded-lg text-sm font-light backdrop-blur-sm"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          style={{
            position: 'fixed',
            top: '9rem', // 정보 버튼 아래에 배치
            right: '1rem',
            zIndex: 30,
          }}
        >
          {isAutoMode && '자동 진행'}
          {isSkipMode && '스킵'}
        </motion.div>
      )}

      {/* 정보 패널 */}
      <InfoPanel
        isOpen={isInfoPanelOpen}
        onClose={() => setIsInfoPanelOpen(false)}
      />

      {/* 저장/불러오기 메뉴 */}
      <SaveLoadMenu
        isOpen={isSaveLoadMenuOpen}
        onClose={() => setIsSaveLoadMenuOpen(false)}
        mode={saveLoadMode}
      />

      {/* 오브젝트 인벤토리 모달 */}
      {pickupObjectId && (
        <ObjectInventoryModal
          isOpen={showObjectInventoryModal}
          onClose={() => {
            setShowObjectInventoryModal(false);
            setPickupObjectId(null);
          }}
          objectId={pickupObjectId}
          sessionId={gameState?.session_id || ''}
          objectName={pickupObjectName}
          onItemSelected={async (itemId: string) => {
            if (!gameState || !pickupObjectId) return;
            
            try {
              setLoading(true);
              const response = await gameApi.pickupFromObject(
                gameState.session_id,
                pickupObjectId,
                itemId
              );
              
              setCurrentMessage({
                text: response.message,
                message_type: 'system',
                timestamp: Date.now(),
              });
              
              // 성공한 경우에만 셀 정보 새로고침
              if (response.success) {
                const cell = await gameApi.getCurrentCell(gameState.session_id);
                setCurrentCell(cell);
                const actions = await gameApi.getAvailableActions(gameState.session_id);
                setAvailableActions(actions);
              }
            } catch (error) {
              console.error('아이템 획득 실패:', error);
              setError('아이템 획득에 실패했습니다.');
            } finally {
              setLoading(false);
            }
          }}
        />
      )}

      {/* 컨텍스트 메뉴 (심즈 스타일) */}
      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          actions={(() => {
            const actions: Array<{ id: string; label: string; icon?: string }> = [];
            
            if (contextMenu.target.object) {
              const obj = contextMenu.target.object;
              // interaction_type은 properties 또는 최상위 레벨에 있을 수 있음
              const interactionType = obj.properties?.interaction_type || (obj as any).interaction_type;
              const contents = (obj.properties?.contents as string[]) || [];
              
              // 조사하기 (항상 가능)
              actions.push({ id: 'examine', label: '조사', icon: '🔍' });
              
              // 상호작용 타입에 따른 액션
              if (interactionType === 'openable') {
                actions.push({ id: 'open', label: '열기', icon: '📦' });
              } else if (interactionType === 'lightable') {
                actions.push({ id: 'light', label: '불', icon: '🕯️' });
              } else if (interactionType === 'sitable') {
                actions.push({ id: 'sit', label: '앉기', icon: '🪑' });
              } else if (interactionType === 'restable') {
                actions.push({ id: 'rest', label: '쉬기', icon: '🛏️' });
              }
              
              // 내용물이 있으면 줍기
              if (contents.length > 0) {
                actions.push({ id: 'pickup', label: '줍기', icon: '📥' });
              }
            } else if (contextMenu.target.entity) {
              const entity = contextMenu.target.entity;
              
              // 조사하기 (항상 가능)
              actions.push({ id: 'examine', label: '조사', icon: '🔍' });
              
              // 대화하기
              if (entity.dialogue_id) {
                actions.push({ id: 'dialogue', label: '대화', icon: '💬' });
              }
              
              // 상호작용하기
              if (entity.can_interact) {
                actions.push({ id: 'interact', label: '상호작용', icon: '🤝' });
              }
            }
            
            return actions;
          })()}
          onActionSelect={async (actionId) => {
            if (!contextMenu || !gameState) return;
            
            const target = contextMenu.target.object || contextMenu.target.entity;
            if (!target) return;
            
            // object_id 우선, 없으면 runtime_object_id 또는 game_object_id 사용
            const targetId = contextMenu.target.object 
              ? (contextMenu.target.object.object_id || (contextMenu.target.object as any).runtime_object_id || (contextMenu.target.object as any).game_object_id || '')
              : (contextMenu.target.entity?.entity_id || '');
            
            try {
              setLoading(true);
              setContextMenu(null);
              
              if (contextMenu.target.object) {
                const obj = contextMenu.target.object;
                const objId = obj.object_id || (obj as any).runtime_object_id || (obj as any).game_object_id || targetId;
                
                if (actionId === 'pickup') {
                  // 오브젝트 인벤토리 모달 표시
                  setPickupObjectId(objId);
                  setPickupObjectName(obj.object_name || '오브젝트');
                  setShowObjectInventoryModal(true);
                } else {
                  // 열기, 불 켜기, 앉기, 쉬기, 조사하기 등 일반 상호작용
                  console.log('[GameView] Interacting with object:', { objId, actionId });
                  const response = await gameApi.interactWithObject(
                    gameState.session_id,
                    objId,
                    actionId
                  );
                  
                  console.log('[GameView] Interaction response:', response);
                  
                  // 응답 확인
                  if (response && response.message) {
                    setCurrentMessage({
                      text: response.message,
                      message_type: actionId === 'examine' ? 'narration' : 'system',
                      timestamp: Date.now(),
                    });
                  } else {
                    console.warn('[GameView] No message in response:', response);
                    setCurrentMessage({
                      text: `${contextMenu.target.object?.object_name || '오브젝트'}와 상호작용했습니다.`,
                      message_type: 'system',
                      timestamp: Date.now(),
                    });
                  }
                  
                  // 열기 액션의 경우 contents가 변경될 수 있으므로 셀 정보 새로고침
                  if (actionId === 'open') {
                    const cell = await gameApi.getCurrentCell(gameState.session_id);
                    setCurrentCell(cell);
                    const actions = await gameApi.getAvailableActions(gameState.session_id);
                    setAvailableActions(actions);
                  }
                }
              } else if (contextMenu.target.entity) {
                const response = await gameApi.interactWithEntity(
                  gameState.session_id,
                  targetId,
                  actionId
                );
                setCurrentMessage({
                  text: response.message,
                  message_type: actionId === 'dialogue' ? 'dialogue' : 'system',
                  timestamp: Date.now(),
                });
              }
            } catch (error) {
              const errorMessage = error instanceof Error ? error.message : '상호작용 실패';
              setError(errorMessage);
              console.error('상호작용 실패:', error);
              
              // 에러 메시지도 표시
              setCurrentMessage({
                text: `상호작용에 실패했습니다: ${errorMessage}`,
                message_type: 'system',
                timestamp: Date.now(),
              });
            } finally {
              setLoading(false);
            }
          }}
          onClose={() => setContextMenu(null)}
        />
      )}

    </motion.div>
  );
};

