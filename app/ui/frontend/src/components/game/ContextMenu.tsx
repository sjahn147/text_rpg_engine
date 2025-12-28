/**
 * 컨텍스트 메뉴 컴포넌트 - 심즈 스타일 상호작용 메뉴
 * 오브젝트/엔티티를 클릭했을 때 해당 위치에 나타나는 원형 메뉴
 */
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ContextMenuAction {
  id: string;
  label: string;
  icon?: string;
  description?: string;
}

interface ContextMenuProps {
  x: number;
  y: number;
  actions: ContextMenuAction[];
  onActionSelect: (actionId: string) => void;
  onClose: () => void;
}

export const ContextMenu: React.FC<ContextMenuProps> = ({
  x,
  y,
  actions,
  onActionSelect,
  onClose,
}) => {
  if (actions.length === 0) return null;

  // 원형 메뉴 계산
  const radius = 80;
  const angleStep = (2 * Math.PI) / actions.length;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          zIndex: 50,
          pointerEvents: 'auto',
        }}
      >
        {/* 중앙 버튼 */}
        <motion.div
          className="absolute rounded-full bg-white/95 backdrop-blur-xl border-2 border-black/20 shadow-2xl cursor-pointer"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0, opacity: 0 }}
          transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
          onClick={(e) => e.stopPropagation()}
          style={{
            position: 'absolute',
            left: `${x}px`,
            top: `${y}px`,
            transform: 'translate(-50%, -50%)',
            width: '60px',
            height: '60px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px',
            color: 'rgba(0, 0, 0, 0.8)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)',
          }}
        >
          ×
        </motion.div>

        {/* 액션 버튼들 (원형 배치) */}
        {actions.map((action, index) => {
          const angle = index * angleStep - Math.PI / 2; // 위쪽부터 시작
          const actionX = x + Math.cos(angle) * radius;
          const actionY = y + Math.sin(angle) * radius;

          return (
            <motion.button
              key={action.id}
              className="absolute rounded-full bg-white/95 backdrop-blur-xl border-2 border-black/20 shadow-xl cursor-pointer"
              initial={{ scale: 0, opacity: 0, x: x, y: y }}
              animate={{ 
                scale: 1, 
                opacity: 1, 
                x: actionX - x,
                y: actionY - y,
              }}
              exit={{ scale: 0, opacity: 0, x: 0, y: 0 }}
              transition={{ 
                duration: 0.3, 
                delay: index * 0.05,
                ease: [0.34, 1.56, 0.64, 1]
              }}
              onClick={(e) => {
                e.stopPropagation();
                onActionSelect(action.id);
              }}
              whileHover={{ scale: 1.15 }}
              whileTap={{ scale: 0.9 }}
              style={{
                position: 'absolute',
                left: `${x}px`,
                top: `${y}px`,
                transform: 'translate(-50%, -50%)',
                width: '70px',
                height: '70px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px',
                fontWeight: 500,
                color: 'rgba(0, 0, 0, 0.9)',
                boxShadow: '0 4px 16px rgba(0, 0, 0, 0.12)',
                padding: '0.5rem',
              }}
            >
              <div style={{ fontSize: '20px', marginBottom: '0.25rem' }}>
                {action.icon || '○'}
              </div>
              <div style={{ fontSize: '10px', textAlign: 'center', lineHeight: '1.2' }}>
                {action.label}
              </div>
            </motion.button>
          );
        })}
      </motion.div>
    </AnimatePresence>
  );
};

