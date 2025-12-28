/**
 * 오브젝트 메뉴 컴포넌트 - 상단에 오브젝트 목록을 탭 형태로 표시
 */
import React from 'react';
import { motion } from 'framer-motion';
import { WorldObjectInfo } from '../../types/game';

interface ObjectMenuProps {
  objects: WorldObjectInfo[];
  selectedObjectId?: string;
  onObjectSelect: (object: WorldObjectInfo) => void;
}

export const ObjectMenu: React.FC<ObjectMenuProps> = ({
  objects,
  selectedObjectId,
  onObjectSelect,
}) => {
  if (objects.length === 0) return null;

  return (
    <motion.div
      className="fixed left-0 top-0 bottom-0 z-40"
      initial={{ x: -300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -300, opacity: 0 }}
      transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        bottom: 0,
        width: '200px',
        zIndex: 40,
        padding: '1rem',
        background: 'linear-gradient(90deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.85) 100%)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderRight: '1px solid rgba(0, 0, 0, 0.08)',
        boxShadow: '2px 0 16px rgba(0, 0, 0, 0.06)',
        overflowY: 'auto',
        overflowX: 'hidden',
      }}
    >
      <div
        className="flex flex-col gap-2"
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem',
        }}
      >
        {objects.map((obj, index) => (
          <motion.button
            key={obj.object_id}
            onClick={() => onObjectSelect(obj)}
            className="w-full text-left px-4 py-3 rounded-lg text-sm font-light transition-all"
            style={{
              padding: '0.75rem 1rem',
              borderRadius: '0.5rem',
              fontSize: '0.875rem',
              fontWeight: selectedObjectId === obj.object_id ? 500 : 300,
              color: selectedObjectId === obj.object_id ? 'rgba(0, 0, 0, 0.95)' : 'rgba(0, 0, 0, 0.7)',
              background: selectedObjectId === obj.object_id
                ? 'linear-gradient(90deg, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0.4) 100%)'
                : 'linear-gradient(90deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.15) 100%)',
              border: selectedObjectId === obj.object_id
                ? '1px solid rgba(0, 0, 0, 0.2)'
                : '1px solid rgba(0, 0, 0, 0.1)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
              boxShadow: selectedObjectId === obj.object_id
                ? '0 2px 8px rgba(0, 0, 0, 0.1)'
                : '0 1px 4px rgba(0, 0, 0, 0.05)',
              cursor: 'pointer',
              width: '100%',
              textAlign: 'left',
            }}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            whileHover={{
              scale: 1.02,
              background: 'linear-gradient(90deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.3) 100%)',
            }}
            whileTap={{ scale: 0.98 }}
          >
            {obj.object_name}
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
};

