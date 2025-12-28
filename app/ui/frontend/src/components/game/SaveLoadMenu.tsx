/**
 * 저장/불러오기 메뉴 컴포넌트
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';

interface SaveLoadMenuProps {
  isOpen: boolean;
  onClose: () => void;
  mode: 'save' | 'load';
}

export const SaveLoadMenu: React.FC<SaveLoadMenuProps> = ({ isOpen, onClose, mode }) => {
  const [selectedSlot, setSelectedSlot] = useState<number | null>(null);
  const { gameState } = useGameStore();
  const slots = Array.from({ length: 10 }, (_, i) => i + 1);

  if (!isOpen) return null;

  const handleSave = async (slotId: number) => {
    // TODO: 저장 API 호출
    console.log('저장:', slotId, gameState);
    onClose();
  };

  const handleLoad = async (slotId: number) => {
    // TODO: 불러오기 API 호출
    console.log('불러오기:', slotId);
    onClose();
  };

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="bg-white/95 backdrop-blur-md rounded-lg shadow-2xl p-8 max-w-md w-full mx-4"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-light text-black/90">
              {mode === 'save' ? '게임 저장' : '게임 불러오기'}
            </h2>
            <button
              onClick={onClose}
              className="text-black/60 hover:text-black/90 transition-colors"
            >
              ✕
            </button>
          </div>

          <div className="space-y-2">
            {slots.map((slot) => (
              <button
                key={slot}
                onClick={() => {
                  setSelectedSlot(slot);
                  if (mode === 'save') {
                    handleSave(slot);
                  } else {
                    handleLoad(slot);
                  }
                }}
                className={`w-full p-4 text-left border border-black/10 rounded transition-colors ${
                  selectedSlot === slot
                    ? 'bg-black/10 border-black/20'
                    : 'hover:bg-black/5'
                }`}
              >
                <div className="font-light text-black/90">슬롯 {slot}</div>
                <div className="text-sm text-black/60 mt-1">
                  {mode === 'save' ? '저장하기' : '불러오기'}
                </div>
              </button>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

