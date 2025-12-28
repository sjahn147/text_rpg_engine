/**
 * 인벤토리 화면 - 아이템 관리
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';
import { gameApi } from '../../services/gameApi';
import { CombineModal } from '../../components/game/CombineModal';
import type { GameScreenType } from '../../hooks/game/useGameNavigation';

interface InventoryScreenProps {
  onClose: () => void;
}

interface InventoryItem {
  item_id: string;
  name: string;
  quantity: number;
  item_type?: string;
  consumable?: boolean;
}

interface EquippedItem {
  slot: string;
  item_id: string;
  name: string;
}

export const InventoryScreen: React.FC<InventoryScreenProps> = ({ onClose }) => {
  const { gameState } = useGameStore();
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [equippedItems, setEquippedItems] = useState<EquippedItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isCombineModalOpen, setIsCombineModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (gameState?.session_id) {
      loadInventory();
    }
  }, [gameState?.session_id]);

  const loadInventory = async () => {
    if (!gameState?.session_id) return;
    
    try {
      setLoading(true);
      setError(null);
      const response = await gameApi.getPlayerInventory(gameState.session_id);
      
      // API 응답이 {success: true, inventory: [...], equipped_items: [...]} 형태
      if (response && typeof response === 'object' && 'inventory' in response) {
        setInventory(response.inventory || []);
        setEquippedItems(response.equipped_items || []);
      } else if (Array.isArray(response)) {
        // 배열 형태로 직접 반환되는 경우
        setInventory(response);
        setEquippedItems([]);
      }
    } catch (err) {
      console.error('인벤토리 로드 실패:', err);
      setError('인벤토리를 불러올 수 없습니다.');
      setInventory([]);
      setEquippedItems([]);
    } finally {
      setLoading(false);
    }
  };

  const handleUseItem = async (itemId: string) => {
    if (!gameState?.session_id) return;
    
    try {
      setLoading(true);
      const result = await gameApi.useItem(gameState.session_id, itemId);
      if (result.success) {
        await loadInventory();
      } else {
        setError(result.message || '아이템 사용 실패');
      }
    } catch (err) {
      console.error('아이템 사용 실패:', err);
      setError('아이템 사용에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleEatItem = async (itemId: string) => {
    if (!gameState?.session_id) return;
    
    try {
      setLoading(true);
      const result = await gameApi.eatItem(gameState.session_id, itemId);
      if (result.success) {
        await loadInventory();
      } else {
        setError(result.message || '아이템 먹기 실패');
      }
    } catch (err) {
      console.error('아이템 먹기 실패:', err);
      setError('아이템 먹기에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleEquipItem = async (itemId: string) => {
    if (!gameState?.session_id) return;
    
    try {
      setLoading(true);
      const result = await gameApi.equipItem(gameState.session_id, itemId);
      if (result.success) {
        await loadInventory();
      } else {
        setError(result.message || '아이템 장착 실패');
      }
    } catch (err) {
      console.error('아이템 장착 실패:', err);
      setError('아이템 장착에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleUnequipItem = async (itemId: string) => {
    if (!gameState?.session_id) return;
    
    try {
      setLoading(true);
      const result = await gameApi.unequipItem(gameState.session_id, itemId);
      if (result.success) {
        await loadInventory();
      } else {
        setError(result.message || '아이템 해제 실패');
      }
    } catch (err) {
      console.error('아이템 해제 실패:', err);
      setError('아이템 해제에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleDropItem = async (itemId: string) => {
    if (!gameState?.session_id) return;
    
    if (!confirm('정말 이 아이템을 버리시겠습니까?')) {
      return;
    }
    
    try {
      setLoading(true);
      const result = await gameApi.dropItem(gameState.session_id, itemId);
      if (result.success) {
        await loadInventory();
      } else {
        setError(result.message || '아이템 버리기 실패');
      }
    } catch (err) {
      console.error('아이템 버리기 실패:', err);
      setError('아이템 버리기에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const filteredInventory = inventory.filter(item => {
    if (selectedCategory === 'all') return true;
    if (selectedCategory === 'consumable') return item.consumable === true;
    if (selectedCategory === 'equipment') return item.item_type === 'equipment';
    return true;
  });

  const equippedItemIds = new Set(equippedItems.map(eq => eq.item_id));

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="bg-white p-8 rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 50, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* 헤더 */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-light text-black/90">인벤토리</h2>
            <button
              onClick={onClose}
              className="text-black/60 hover:text-black/90 transition-colors text-2xl"
            >
              ✕
            </button>
          </div>

          {/* 에러 메시지 */}
          {error && (
            <div className="mb-4 p-3 bg-red-100 text-red-800 rounded text-sm">
              {error}
            </div>
          )}

          {/* 카테고리 필터 */}
          <div className="flex gap-2 mb-4">
            {['all', 'consumable', 'equipment'].map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 text-sm font-light transition-colors ${
                  selectedCategory === category
                    ? 'bg-black/10 text-black/90'
                    : 'text-black/60 hover:text-black/80'
                }`}
              >
                {category === 'all' ? '전체' :
                 category === 'consumable' ? '소비품' : '장비'}
              </button>
            ))}
            <button
              onClick={() => setIsCombineModalOpen(true)}
              className="ml-auto px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-light rounded transition-colors"
            >
              조합
            </button>
          </div>

          {/* 장착 슬롯 */}
          {equippedItems.length > 0 && (
            <div className="mb-6 p-4 bg-black/5 rounded">
              <h3 className="text-lg font-light text-black/90 mb-3">장착 중</h3>
              <div className="grid grid-cols-3 gap-3">
                {equippedItems.map((eq) => (
                  <div
                    key={eq.slot}
                    className="p-3 bg-white rounded border border-black/10"
                  >
                    <div className="text-xs text-black/60 mb-1">{eq.slot}</div>
                    <div className="text-sm text-black/80">{eq.name}</div>
                    <button
                      onClick={() => handleUnequipItem(eq.item_id)}
                      className="mt-2 text-xs text-blue-600 hover:text-blue-800"
                    >
                      해제
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 아이템 목록 */}
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="text-center py-8 text-black/60">로딩 중...</div>
            ) : filteredInventory.length === 0 ? (
              <div className="text-center py-8 text-black/60">
                아이템이 없습니다.
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                {filteredInventory.map((item) => (
                  <div
                    key={item.item_id}
                    className={`p-4 rounded border ${
                      equippedItemIds.has(item.item_id)
                        ? 'bg-blue-50 border-blue-200'
                        : 'bg-black/5 border-black/10'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-black/90">{item.name}</span>
                      <span className="text-sm text-black/60">x{item.quantity}</span>
                    </div>
                    <div className="flex gap-2 mt-3">
                      {item.consumable && (
                        <button
                          onClick={() => handleEatItem(item.item_id)}
                          className="px-2 py-1 text-xs bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
                        >
                          먹기
                        </button>
                      )}
                      {item.item_type === 'equipment' && !equippedItemIds.has(item.item_id) && (
                        <button
                          onClick={() => handleEquipItem(item.item_id)}
                          className="px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
                        >
                          장착
                        </button>
                      )}
                      <button
                        onClick={() => handleUseItem(item.item_id)}
                        className="px-2 py-1 text-xs bg-gray-600 hover:bg-gray-700 text-white rounded transition-colors"
                      >
                        사용
                      </button>
                      <button
                        onClick={() => handleDropItem(item.item_id)}
                        className="px-2 py-1 text-xs bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
                      >
                        버리기
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </motion.div>

        {/* 조합 모달 */}
        {isCombineModalOpen && (
          <CombineModal
            isOpen={isCombineModalOpen}
            onClose={() => setIsCombineModalOpen(false)}
            onSuccess={() => {
              loadInventory();
            }}
          />
        )}
      </motion.div>
    </AnimatePresence>
  );
};

