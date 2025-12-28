/**
 * 오브젝트/엔티티 상호작용 화면 컴포넌트
 * 
 * 오브젝트나 엔티티와 상호작용할 때 표시되는 상세 화면
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { WorldObjectInfo, EntityInfo } from '../../types/game';

interface InteractionScreenProps {
  object?: WorldObjectInfo;
  entity?: EntityInfo;
  onClose: () => void;
  onAction: (actionType: string, targetId: string) => void;
}

export const InteractionScreen: React.FC<InteractionScreenProps> = ({
  object,
  entity,
  onClose,
  onAction,
}) => {
  const [selectedAction, setSelectedAction] = useState<string | null>(null);

  // 오브젝트 또는 엔티티가 없으면 숨김 (항상 렌더링되지만 보이지 않음)
  if (!object && !entity) {
    return null;
  }

  // 상호작용 가능한 액션 목록
  const getAvailableActions = () => {
    if (object) {
      // 오브젝트 액션
      const actions: Array<{ id: string; label: string; description?: string }> = [];
      
      // 오브젝트의 interaction_type에 따른 액션
      const interactionType = object.properties?.interaction_type || 'examine';
      const contents = (object.properties?.contents as string[]) || [];
      
      // 열 수 있는 오브젝트
      if (interactionType === 'openable') {
        actions.push({
          id: 'open',
          label: '열기',
          description: '오브젝트를 엽니다.',
        });
      }
      
      // 불을 켤 수 있는 오브젝트
      if (interactionType === 'lightable') {
        actions.push({
          id: 'light',
          label: '불 켜기',
          description: '오브젝트에 불을 켭니다.',
        });
      }
      
      // 앉을 수 있는 오브젝트
      if (interactionType === 'sitable') {
        actions.push({
          id: 'sit',
          label: '앉기',
          description: '오브젝트에 앉습니다.',
        });
      }
      
      // 쉴 수 있는 오브젝트
      if (interactionType === 'restable') {
        actions.push({
          id: 'rest',
          label: '쉬기',
          description: '오브젝트에서 휴식을 취합니다.',
        });
      }
      
      // contents가 있는 경우 줍기 액션
      if (contents.length > 0) {
        actions.push({
          id: 'pickup',
          label: '아이템 획득',
          description: `인벤토리에 추가합니다. (${contents.length}개 항목)`,
        });
      }
      
      // 기본 상호작용 액션 (위의 특수 액션이 없는 경우)
      if (actions.length === 0) {
        actions.push({
          id: 'interact',
          label: '상호작용하기',
          description: '오브젝트와 상호작용합니다.',
        });
      }

      return actions;
    } else if (entity) {
      // 엔티티 액션
      const actions: Array<{ id: string; label: string; description?: string }> = [];
      
      // 대화하기
      if (entity.dialogue_id) {
        actions.push({
          id: 'dialogue',
          label: '대화하기',
          description: '대화를 시작합니다.',
        });
      }

      // 상호작용하기
      if (entity.can_interact) {
        actions.push({
          id: 'interact',
          label: '상호작용하기',
          description: '엔티티와 상호작용합니다.',
        });
      }

      return actions;
    }

    return [];
  };

  const availableActions = getAvailableActions();

  const handleActionClick = (actionId: string) => {
    setSelectedAction(actionId);
    const targetId = object ? object.object_id : (entity ? entity.entity_id : '');
    onAction(actionId, targetId);
  };

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        style={{
          pointerEvents: 'auto',
        }}
      >
        <motion.div
          className="absolute bg-white/98 backdrop-blur-xl border border-black/10 shadow-2xl"
          initial={{ 
            scale: 0.8,
            opacity: 0,
            x: 50,
            y: '-50%',
          }}
          animate={{ 
            scale: 1,
            opacity: 1,
            x: 0,
            y: '-50%',
          }}
          exit={{ 
            scale: 0.8,
            opacity: 0,
            x: 50,
          }}
          transition={{ 
            duration: 0.35, 
            ease: [0.34, 1.56, 0.64, 1],
          }}
          onClick={(e) => e.stopPropagation()}
          style={{
            right: '2rem',
            top: '50%',
            transform: 'translateY(-50%)',
            width: 'min(90vw, 420px)',
            maxHeight: '85vh',
            overflowY: 'auto',
            borderRadius: '1.5rem',
            padding: '0',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
          }}
        >
          {/* 헤더 */}
          <div className="px-6 py-5 border-b border-black/10 rounded-t-[2rem]">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <h2 className="text-xl font-light text-black/90">
                  {object ? object.object_name : (entity ? entity.entity_name : '')}
                </h2>
                {(object?.description || entity?.description) && (
                  <p className="text-sm text-black/60 mt-1">
                    {object?.description || entity?.description}
                  </p>
                )}
              </div>
              <button
                onClick={onClose}
                className="text-black/60 hover:text-black/90 transition-colors ml-4 flex-shrink-0"
                style={{
                  fontSize: '28px',
                  lineHeight: '1',
                  padding: '0.25rem 0.5rem',
                  borderRadius: '50%',
                  width: '2rem',
                  height: '2rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                ×
              </button>
            </div>
          </div>

          {/* 내용 */}
          <div className="px-6 py-5">
            {/* 상세 정보 */}
            {object && (
              <div className="mb-6">
                <h3 className="text-sm font-medium text-black/70 mb-2">정보</h3>
                <div className="space-y-2 text-sm text-black/60">
                  <div>
                    <span className="font-medium">위치:</span>{' '}
                    ({object.position.x.toFixed(1)}, {object.position.y.toFixed(1)}, {object.position.z.toFixed(1)})
                  </div>
                  {object.can_interact && (
                    <div>
                      <span className="font-medium">상호작용:</span> 가능
                    </div>
                  )}
                </div>
              </div>
            )}

            {entity && (
              <div className="mb-6">
                <h3 className="text-sm font-medium text-black/70 mb-2">정보</h3>
                <div className="space-y-2 text-sm text-black/60">
                  <div>
                    <span className="font-medium">타입:</span> {entity.entity_type}
                  </div>
                  {entity.dialogue_id && (
                    <div>
                      <span className="font-medium">대화:</span> 가능
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* 액션 목록 */}
            <div>
              <h3 className="text-sm font-medium text-black/70 mb-3">액션</h3>
              <div className="space-y-2">
                {availableActions.map((action) => (
                  <motion.button
                    key={action.id}
                    className="w-full text-left px-4 py-3 bg-white/50 hover:bg-white/70 border border-black/10 rounded-xl transition-colors"
                    onClick={() => handleActionClick(action.id)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="font-light text-black/90">{action.label}</div>
                    {action.description && (
                      <div className="text-xs text-black/60 mt-1">
                        {action.description}
                      </div>
                    )}
                  </motion.button>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

