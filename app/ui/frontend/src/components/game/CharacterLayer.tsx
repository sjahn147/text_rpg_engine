/**
 * 캐릭터 레이어 컴포넌트 - novel_game 스타일
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface CharacterInfo {
  character_id: string;
  character_name?: string;
  position: 'left' | 'center' | 'right';
  expression?: string;
  visible: boolean;
}

interface CharacterLayerProps {
  characters: CharacterInfo[];
}

const positionClasses = {
  left: 'left-0',
  center: 'left-1/2 -translate-x-1/2',
  right: 'right-0',
};

export const CharacterLayer: React.FC<CharacterLayerProps> = ({ characters }) => {
  if (!characters || characters.length === 0) return null;

  return (
    <div className="absolute inset-0 w-full h-full pointer-events-none z-10">
      <AnimatePresence>
        {characters
          .filter((char) => char.visible)
          .map((char) => (
            <motion.div
              key={char.character_id}
              className={`absolute bottom-0 ${positionClasses[char.position]}`}
              initial={{ opacity: 0, x: char.position === 'left' ? -80 : char.position === 'right' ? 80 : 0 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: char.position === 'left' ? -80 : char.position === 'right' ? 80 : 0 }}
              transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
            >
              {/* 캐릭터 이미지 (추후 구현) */}
              <div className="h-full max-h-[85vh] flex items-end justify-center">
                <div className="text-black/40 text-sm font-light">
                  {char.character_name || char.character_id}
                </div>
              </div>
            </motion.div>
          ))}
      </AnimatePresence>
    </div>
  );
};

