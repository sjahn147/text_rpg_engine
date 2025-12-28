/**
 * 인벤토리 오버레이 패널 - 게임 중 간략한 인벤토리 확인
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';
import { gameApi } from '../../services/gameApi';

interface InventoryPanelProps {
  isOpen: boolean;
  onClose: () => void;
  position?: 'left' | 'right';
}

interface InventoryItem {
  item_id: string;
  name: string;
  quantity: number;
  item_type?: string;
}

export const InventoryPanel: React.FC<InventoryPanelProps> = ({
  isOpen,
  onClose,
  position = 'right',
}) => {
  const { gameState } = useGameStore();
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && gameState?.session_id) {
      loadInventory();
    }
  }, [isOpen, gameState?.session_id]);

  const loadInventory = async () => {
    if (!gameState?.session_id) return;
    
    setLoading(true);
    try {
      const data = await gameApi.getPlayerInventory(gameState.session_id);
      setInventory(data.inventory || []);
    } catch (error) {
      console.error('인벤토리 로드 실패:', error);
      setInventory([]);
    } finally {
      setLoading(false);
    }
  };

  const panelPosition = position === 'left' 
    ? { left: 0 }
    : { right: 0 };

  const slideDirection = position === 'left' ? -300 : 300;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* 배경 오버레이 */}
          <motion.div
            className="fixed inset-0 z-40 bg-black/20"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          
          {/* 패널 */}
          <motion.div
            className="fixed top-0 bottom-0 z-50 w-72 bg-white shadow-xl flex flex-col"
            style={panelPosition}
            initial={{ x: slideDirection, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: slideDirection, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          >
            {/* 헤더 */}
            <div className="p-4 border-b border-black/10 flex items-center justify-between">
              <h3 className="text-lg font-light text-black/90">인벤토리</h3>
              <button
                onClick={onClose}
                className="text-black/60 hover:text-black/90 transition-colors"
              >
                ✕
              </button>
            </div>

            {/* 컨텐츠 */}
            <div className="flex-1 overflow-y-auto p-4">
              {loading ? (
                <div className="text-center text-black/60 py-8">
                  로딩 중...
                </div>
              ) : inventory.length === 0 ? (
                <div className="text-center text-black/60 py-8">
                  아이템이 없습니다.
                </div>
              ) : (
                <div className="space-y-2">
                  {inventory.map((item) => (
                    <div
                      key={item.item_id}
                      className="p-3 bg-black/5 rounded hover:bg-black/10 transition-colors cursor-pointer"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-black/80">
                          {item.name || item.item_id}
                        </span>
                        <span className="text-xs text-black/60">
                          x{item.quantity}
                        </span>
                      </div>
                      {item.item_type && (
                        <div className="text-xs text-black/50 mt-1">
                          {item.item_type}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* 하단 요약 */}
            <div className="p-4 border-t border-black/10 text-sm text-black/60">
              총 {inventory.reduce((sum, item) => sum + item.quantity, 0)}개 아이템
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

