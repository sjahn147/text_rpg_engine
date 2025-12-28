/**
 * 아이템 조합 모달 컴포넌트
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { gameApi } from '../../services/gameApi';
import { useGameStore } from '../../store/gameStore';

interface CombineModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

interface InventoryItem {
  item_id: string;
  quantity: number;
  name?: string;
}

export const CombineModal: React.FC<CombineModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const { gameState } = useGameStore();
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [isCombining, setIsCombining] = useState(false);
  const [successRate, setSuccessRate] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 인벤토리 로드
  useEffect(() => {
    if (isOpen && gameState) {
      loadInventory();
    }
  }, [isOpen, gameState]);

  // 성공률 계산 (간단한 추정)
  useEffect(() => {
    if (selectedItems.length >= 2 && selectedItems.length <= 5) {
      // 기본 성공률 계산 (실제로는 백엔드에서 계산해야 함)
      const baseRate = 0.5;
      const penalty = selectedItems.length * 0.08;
      const estimatedRate = Math.max(0.1, Math.min(0.9, baseRate - penalty));
      setSuccessRate(estimatedRate);
    } else {
      setSuccessRate(null);
    }
  }, [selectedItems]);

  const loadInventory = async () => {
    if (!gameState) return;
    
    try {
      const inventoryData = await gameApi.getPlayerInventory(gameState.session_id);
      setInventory(inventoryData);
    } catch (error) {
      console.error('인벤토리 로드 실패:', error);
      setInventory([]);
    }
  };

  const toggleItemSelection = (itemId: string) => {
    if (selectedItems.includes(itemId)) {
      setSelectedItems(selectedItems.filter(id => id !== itemId));
    } else {
      if (selectedItems.length >= 5) {
        setError('최대 5개까지만 선택할 수 있습니다.');
        return;
      }
      setSelectedItems([...selectedItems, itemId]);
      setError(null);
    }
  };

  const handleCombine = async () => {
    if (!gameState || selectedItems.length < 2) {
      setError('최소 2개의 아이템을 선택해주세요.');
      return;
    }

    setIsCombining(true);
    setError(null);

    try {
      const response = await gameApi.combineItems(
        gameState.session_id,
        selectedItems
      );

      if (response.success) {
        // 성공 시 인벤토리 새로고침
        await loadInventory();
        setSelectedItems([]);
        onSuccess?.();
        onClose();
      } else {
        setError(response.message || '조합에 실패했습니다.');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '조합 중 오류가 발생했습니다.';
      setError(errorMessage);
    } finally {
      setIsCombining(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="bg-white/95 backdrop-blur-md rounded-lg shadow-2xl p-6 w-full max-w-md"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-light text-black/90">아이템 조합</h2>
            <button
              onClick={onClose}
              className="text-black/60 hover:text-black/90 transition-colors"
            >
              ✕
            </button>
          </div>

          {/* 선택된 아이템 표시 */}
          {selectedItems.length > 0 && (
            <div className="mb-4 p-3 bg-black/5 rounded">
              <div className="text-sm text-black/70 mb-2">
                선택된 아이템 ({selectedItems.length}/5):
              </div>
              <div className="flex flex-wrap gap-2">
                {selectedItems.map((itemId) => (
                  <span
                    key={itemId}
                    className="px-2 py-1 bg-black/10 rounded text-sm text-black/80"
                  >
                    {itemId}
                    <button
                      onClick={() => toggleItemSelection(itemId)}
                      className="ml-2 text-black/60 hover:text-black/90"
                    >
                      ✕
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* 성공률 표시 */}
          {successRate !== null && (
            <div className="mb-4 p-3 bg-blue-50 rounded">
              <div className="text-sm text-black/70 mb-1">예상 성공률</div>
              <div className="text-lg font-medium text-blue-700">
                {(successRate * 100).toFixed(1)}%
              </div>
            </div>
          )}

          {/* 인벤토리 목록 */}
          <div className="mb-4 max-h-64 overflow-y-auto">
            <div className="text-sm text-black/70 mb-2">인벤토리</div>
            {inventory.length === 0 ? (
              <div className="text-sm text-black/60 py-4 text-center">
                인벤토리가 비어있습니다.
              </div>
            ) : (
              <div className="space-y-2">
                {inventory.map((item) => (
                  <button
                    key={item.item_id}
                    onClick={() => toggleItemSelection(item.item_id)}
                    className={`w-full text-left px-3 py-2 rounded transition-colors ${
                      selectedItems.includes(item.item_id)
                        ? 'bg-blue-100 text-blue-900'
                        : 'bg-black/5 hover:bg-black/10 text-black/80'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm">
                        {item.name || item.item_id} (x{item.quantity})
                      </span>
                      {selectedItems.includes(item.item_id) && (
                        <span className="text-blue-600">✓</span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* 에러 메시지 */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 rounded text-sm text-red-700">
              {error}
            </div>
          )}

          {/* 버튼 */}
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-black/10 hover:bg-black/20 rounded text-sm font-light transition-colors"
            >
              취소
            </button>
            <button
              onClick={handleCombine}
              disabled={selectedItems.length < 2 || isCombining}
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed rounded text-sm font-light text-white transition-colors"
            >
              {isCombining ? '조합 중...' : '조합하기'}
            </button>
          </div>

          {/* 안내 메시지 */}
          <div className="mt-4 text-xs text-black/50">
            • 최소 2개, 최대 5개의 아이템을 선택할 수 있습니다.
            <br />
            • 조합 실패 시 일부 재료가 소모될 수 있습니다.
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

