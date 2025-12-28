/**
 * 선택지 레이어 컴포넌트 - RPG 엔진용
 */

import React from 'react';
import { motion } from 'framer-motion';
import { GameAction } from '../../types/game';

interface ChoiceLayerProps {
  actions: GameAction[];
  onActionSelect: (action: GameAction) => void;
}

export const ChoiceLayer: React.FC<ChoiceLayerProps> = ({
  actions,
  onActionSelect,
}) => {
  const handleActionClick = (action: GameAction) => {
    onActionSelect(action);
  };

  if (actions.length === 0) {
    console.log('[ChoiceLayer] No actions, returning null');
    return null;
  }

  console.log('[ChoiceLayer] Rendering with actions:', actions);

  return (
    <motion.div
      className="fixed left-0 right-0 z-30 px-8"
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      exit={{ y: 100, opacity: 0 }}
      transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
      style={{ 
        position: 'fixed', 
        bottom: '12rem', // 메시지 박스 위에 배치
        left: 0, 
        right: 0, 
        zIndex: 30, 
        paddingLeft: '2rem', 
        paddingRight: '2rem',
        width: '100%',
        pointerEvents: 'auto',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        boxSizing: 'border-box'
      }}
    >
      <div 
        className="flex flex-col gap-2 max-w-[600px] mx-auto w-full"
        style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '0.5rem', 
          maxWidth: '600px', 
          margin: '0 auto',
          width: 'calc(100% - 4rem)',
          background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
          backdropFilter: 'blur(10px)',
          WebkitBackdropFilter: 'blur(10px)',
          borderRadius: '1rem',
          padding: '1rem',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
          maxHeight: '60vh', // 최대 높이 제한
          overflowY: 'auto', // 스크롤 가능
          overflowX: 'hidden',
        }}
      >
        {actions.map((action, index) => (
          <motion.button
            key={action.action_id}
            className="choice-button"
            onClick={() => handleActionClick(action)}
            style={{
              background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.25) 100%)',
              border: '1px solid rgba(0, 0, 0, 0.12)',
              borderRadius: '0.75rem',
              padding: '16px 24px',
              color: '#000000',
              fontSize: '15px',
              fontWeight: 400,
              cursor: 'pointer',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              backdropFilter: 'blur(15px)',
              WebkitBackdropFilter: 'blur(15px)',
              textAlign: 'left',
              position: 'relative',
              overflow: 'hidden',
              boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)',
              width: '100%',
              display: 'block',
            }}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ 
              duration: 0.4, 
              delay: index * 0.05,
              ease: [0.4, 0, 0.2, 1]
            }}
            whileHover={{ 
              scale: 1.02,
              background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.35) 100%)',
              boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
            }}
            whileTap={{ scale: 0.98 }}
          >
            {action.text}
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
};

