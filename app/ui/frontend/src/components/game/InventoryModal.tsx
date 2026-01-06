/**
 * 인벤토리 모달 컴포넌트
 * 
 * 인벤토리 아이템 조회, 장착 아이템 관리, 아이템 사용/드롭 기능 제공
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { List as FixedSizeList } from 'react-window';
import { gameApi } from '../../services/gameApi';
import { ItemDetailModal } from '../modals/ItemDetailModal';
import { ConfirmModal } from '../modals/ConfirmModal';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { toast } from '../common/Toast';

interface InventoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string;
}

interface InventoryItem {
  item_id: string;
  name?: string;
  quantity: number;
  item_type?: string;
  rarity?: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  description?: string;
  is_consumable?: boolean;
  is_equippable?: boolean;
  equipment_slot?: string;
  effect_carrier?: {
    effect_id: string;
    name: string;
    carrier_type: string;
  };
}

interface EquippedItem {
  slot_type: string;
  item?: InventoryItem;
}

type TabType = 'inventory' | 'equipped';

export const InventoryModal: React.FC<InventoryModalProps> = ({
  isOpen,
  onClose,
  sessionId,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('inventory');
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [equippedItems, setEquippedItems] = useState<EquippedItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [isItemDetailOpen, setIsItemDetailOpen] = useState(false);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [pendingAction, setPendingAction] = useState<{ type: 'drop' | 'use'; itemId: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // ESC 키로 닫기
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // 데이터 로드
  useEffect(() => {
    if (isOpen && sessionId) {
      loadInventory();
      loadEquippedItems();
    }
  }, [isOpen, sessionId]);

  const loadInventory = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await gameApi.getCharacterInventory(sessionId);
      // API 응답 형식에 따라 처리
      if (Array.isArray(data)) {
        setInventory(data);
      } else if (data.inventory) {
        setInventory(data.inventory);
      } else {
        setInventory([]);
      }
    } catch (err) {
      console.error('인벤토리 로드 실패:', err);
      setError('인벤토리를 불러올 수 없습니다.');
      toast.error('인벤토리를 불러올 수 없습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadEquippedItems = async () => {
    try {
      const data = await gameApi.getCharacterEquipped(sessionId);
      // API 응답 형식에 따라 처리
      if (Array.isArray(data)) {
        setEquippedItems(data);
      } else if (data.equipped_items) {
        // 슬롯 타입별로 변환
        const slots = data.equipped_items.slots || {};
        const equipped: EquippedItem[] = Object.entries(slots).map(([slotType, item]) => ({
          slot_type: slotType,
          item: item as InventoryItem,
        }));
        setEquippedItems(equipped);
      } else {
        setEquippedItems([]);
      }
    } catch (err) {
      console.error('장착 아이템 로드 실패:', err);
      // 에러는 조용히 처리 (장착 아이템이 없을 수도 있음)
    }
  };

  // 필터링된 인벤토리
  const filteredInventory = inventory.filter((item) => {
    if (filterType && item.item_type !== filterType) return false;
    if (searchQuery && !item.name?.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  // 아이템 클릭 핸들러
  const handleItemClick = (item: InventoryItem) => {
    setSelectedItem(item);
    setIsItemDetailOpen(true);
  };

  // 아이템 사용
  const handleUseItem = async (itemId: string) => {
    try {
      const response = await gameApi.useItem(sessionId, itemId);
      if (response.success) {
        toast.success('아이템을 사용했습니다.');
        await loadInventory();
        setIsItemDetailOpen(false);
      } else {
        toast.error(response.message || '아이템 사용에 실패했습니다.');
      }
    } catch (err) {
      console.error('아이템 사용 실패:', err);
      toast.error('아이템 사용에 실패했습니다.');
    }
  };

  // 아이템 장착
  const handleEquipItem = async (itemId: string) => {
    try {
      const response = await gameApi.equipItem(sessionId, itemId);
      if (response.success) {
        toast.success('아이템을 장착했습니다.');
        await loadInventory();
        await loadEquippedItems();
        setIsItemDetailOpen(false);
      } else {
        toast.error(response.message || '아이템 장착에 실패했습니다.');
      }
    } catch (err) {
      console.error('아이템 장착 실패:', err);
      toast.error('아이템 장착에 실패했습니다.');
    }
  };

  // 아이템 해제
  const handleUnequipItem = async (itemId: string) => {
    try {
      const response = await gameApi.unequipItem(sessionId, itemId);
      if (response.success) {
        toast.success('아이템을 해제했습니다.');
        await loadInventory();
        await loadEquippedItems();
      } else {
        toast.error(response.message || '아이템 해제에 실패했습니다.');
      }
    } catch (err) {
      console.error('아이템 해제 실패:', err);
      toast.error('아이템 해제에 실패했습니다.');
    }
  };

  // 아이템 버리기 확인
  const handleDropClick = (itemId: string) => {
    setPendingAction({ type: 'drop', itemId });
    setIsConfirmOpen(true);
  };

  // 아이템 사용 확인
  const handleUseClick = (itemId: string) => {
    setPendingAction({ type: 'use', itemId });
    setIsConfirmOpen(true);
  };

  // 확인 다이얼로그 확인
  const handleConfirm = async () => {
    if (!pendingAction) return;

    setIsConfirmOpen(false);
    setIsItemDetailOpen(false);

    try {
      if (pendingAction.type === 'drop') {
        const response = await gameApi.dropItem(sessionId, pendingAction.itemId);
        if (response.success) {
          toast.success('아이템을 버렸습니다.');
          await loadInventory();
        } else {
          toast.error(response.message || '아이템 버리기에 실패했습니다.');
        }
      } else if (pendingAction.type === 'use') {
        await handleUseItem(pendingAction.itemId);
      }
    } catch (err) {
      console.error('액션 실행 실패:', err);
      toast.error('액션 실행에 실패했습니다.');
    } finally {
      setPendingAction(null);
    }
  };

  // Effect Carrier 타입별 색상
  const getEffectCarrierColor = (type: string) => {
    const colors: Record<string, string> = {
      skill: 'bg-blue-500',
      buff: 'bg-green-500',
      item: 'bg-gray-500',
      blessing: 'bg-yellow-500',
      curse: 'bg-red-500',
      ritual: 'bg-purple-500',
    };
    return colors[type] || 'bg-gray-500';
  };

  // 아이템 타입 레이블
  const getItemTypeLabel = (type?: string) => {
    const labels: Record<string, string> = {
      weapon: '무기',
      armor: '방어구',
      accessory: '장신구',
      consumable: '소비품',
      material: '재료',
      quest: '퀘스트',
      key: '열쇠',
    };
    return labels[type || ''] || type || '기타';
  };

  // 슬롯 타입 레이블
  const getSlotTypeLabel = (slotType: string) => {
    const labels: Record<string, string> = {
      weapon: '무기',
      armor: '방어구',
      accessory: '장신구',
      shield: '방패',
      helmet: '투구',
      boots: '신발',
    };
    return labels[slotType] || slotType;
  };

  if (!isOpen) return null;

  return (
    <>
      <AnimatePresence>
        <motion.div
          className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="bg-white/95 backdrop-blur-md rounded-lg shadow-xl w-full max-w-[900px] max-h-[80vh] flex flex-col"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* 헤더 */}
            <div className="flex-shrink-0 px-6 py-4 border-b border-black/10">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-light text-black/90">인벤토리</h2>
                <button
                  onClick={onClose}
                  className="text-black/60 hover:text-black/90 transition-colors text-2xl leading-none w-8 h-8 flex items-center justify-center"
                  aria-label="닫기"
                >
                  ×
                </button>
              </div>

              {/* 탭 */}
              <div className="flex gap-2 mt-4">
                {(['inventory', 'equipped'] as TabType[]).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-4 py-2 text-sm font-light transition-colors rounded ${
                      activeTab === tab
                        ? 'bg-black/10 text-black/90'
                        : 'text-black/60 hover:text-black/80'
                    }`}
                  >
                    {tab === 'inventory' ? '인벤토리' : '장착 아이템'}
                  </button>
                ))}
              </div>
            </div>

            {/* 필터/검색 (인벤토리 탭만) */}
            {activeTab === 'inventory' && (
              <div className="flex-shrink-0 px-6 py-3 border-b border-black/10 flex gap-2">
                <input
                  type="text"
                  placeholder="검색..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 px-3 py-2 border border-black/10 rounded text-sm"
                />
                <select
                  value={filterType || ''}
                  onChange={(e) => setFilterType(e.target.value || null)}
                  className="px-3 py-2 border border-black/10 rounded text-sm"
                >
                  <option value="">전체</option>
                  <option value="weapon">무기</option>
                  <option value="armor">방어구</option>
                  <option value="accessory">장신구</option>
                  <option value="consumable">소비품</option>
                  <option value="material">재료</option>
                </select>
              </div>
            )}

            {/* 컨텐츠 */}
            <div className="flex-1 overflow-y-auto px-6 py-4 min-h-0">
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <LoadingSpinner />
                </div>
              ) : error ? (
                <div className="text-red-600 text-sm py-4 text-center">{error}</div>
              ) : (
                <AnimatePresence mode="wait">
                  {activeTab === 'inventory' && (
                    <motion.div
                      key="inventory"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                    >
                      {filteredInventory.length === 0 ? (
                        <div className="text-black/60 text-sm py-8 text-center">
                          {searchQuery || filterType ? '검색 결과가 없습니다.' : '인벤토리가 비어있습니다.'}
                        </div>
                      ) : filteredInventory.length > 10 ? (
                        // 큰 리스트는 가상화 사용
                        <div style={{ height: Math.min(400, filteredInventory.length * 60) }}>
                          <FixedSizeList
                            height={Math.min(400, filteredInventory.length * 60)}
                            itemCount={filteredInventory.length}
                            itemSize={60}
                            width="100%"
                          >
                            {({ index, style }) => {
                              const item = filteredInventory[index];
                              return (
                                <div style={style} className="px-2">
                                  <button
                                    onClick={() => handleItemClick(item)}
                                    className="w-full p-3 bg-black/5 rounded hover:bg-black/10 transition-colors text-left"
                                  >
                                    <div className="flex items-center justify-between">
                                      <div className="flex items-center gap-2">
                                        <span className="text-sm text-black/80">
                                          {item.name || item.item_id}
                                        </span>
                                        {item.effect_carrier && (
                                          <span
                                            className={`${getEffectCarrierColor(item.effect_carrier.carrier_type)} text-white text-xs px-2 py-0.5 rounded`}
                                            title={item.effect_carrier.name}
                                          >
                                            {item.effect_carrier.carrier_type}
                                          </span>
                                        )}
                                      </div>
                                      <span className="text-black/60 text-sm">x{item.quantity}</span>
                                    </div>
                                  </button>
                                </div>
                              );
                            }}
                          </FixedSizeList>
                        </div>
                      ) : (
                        // 작은 리스트는 일반 렌더링
                        <div className="grid grid-cols-4 gap-3">
                          {filteredInventory.map((item) => (
                            <button
                              key={item.item_id}
                              onClick={() => handleItemClick(item)}
                              className="p-3 bg-black/5 rounded hover:bg-black/10 transition-colors text-left relative"
                            >
                              <div className="flex flex-col items-center gap-2">
                                {/* 아이템 아이콘 영역 (placeholder) */}
                                <div className="w-10 h-10 bg-black/10 rounded flex items-center justify-center">
                                  <span className="text-xl">📦</span>
                                </div>
                                {/* Effect Carrier 배지 */}
                                {item.effect_carrier && (
                                  <span
                                    className={`absolute top-1 right-1 ${getEffectCarrierColor(item.effect_carrier.carrier_type)} text-white text-xs px-1.5 py-0.5 rounded`}
                                    title={item.effect_carrier.name}
                                  >
                                    {item.effect_carrier.carrier_type[0].toUpperCase()}
                                  </span>
                                )}
                                {/* 아이템 이름 */}
                                <div className="text-xs text-black/80 text-center line-clamp-2 w-full">
                                  {item.name || item.item_id}
                                </div>
                                {/* 수량 */}
                                {item.quantity > 1 && (
                                  <span className="text-xs text-black/60">x{item.quantity}</span>
                                )}
                              </div>
                            </button>
                          ))}
                        </div>
                      )}
                    </motion.div>
                  )}

                  {activeTab === 'equipped' && (
                    <motion.div
                      key="equipped"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                    >
                      {equippedItems.length === 0 ? (
                        <div className="text-black/60 text-sm py-8 text-center">
                          장착된 아이템이 없습니다.
                        </div>
                      ) : (
                        <div className="grid grid-cols-3 gap-4">
                          {equippedItems.map((equipped) => (
                            <div
                              key={equipped.slot_type}
                              className="flex flex-col items-center gap-2"
                            >
                              <div className="text-sm font-medium text-black/80">
                                {getSlotTypeLabel(equipped.slot_type)}
                              </div>
                              {equipped.item ? (
                                <button
                                  onClick={() => {
                                    if (equipped.item) {
                                      handleItemClick(equipped.item);
                                    }
                                  }}
                                  className="w-full p-4 bg-black/5 rounded hover:bg-black/10 transition-colors relative"
                                >
                                  <div className="flex flex-col items-center gap-2">
                                    <div className="w-16 h-16 bg-black/10 rounded flex items-center justify-center">
                                      <span className="text-2xl">⚔️</span>
                                    </div>
                                    {equipped.item.effect_carrier && (
                                      <span
                                        className={`absolute top-1 right-1 ${getEffectCarrierColor(equipped.item.effect_carrier.carrier_type)} text-white text-xs px-1.5 py-0.5 rounded`}
                                        title={equipped.item.effect_carrier.name}
                                      >
                                        {equipped.item.effect_carrier.carrier_type[0].toUpperCase()}
                                      </span>
                                    )}
                                    <div className="text-sm text-black/80 text-center">
                                      {equipped.item.name || equipped.item.item_id}
                                    </div>
                                  </div>
                                </button>
                              ) : (
                                <div className="w-full p-4 bg-black/5 border-2 border-dashed border-black/20 rounded text-center text-sm text-black/40">
                                  비어있음
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              )}
            </div>
          </motion.div>
        </motion.div>
      </AnimatePresence>

      {/* 아이템 상세 모달 */}
      {selectedItem && (
        <ItemDetailModal
          isOpen={isItemDetailOpen}
          onClose={() => {
            setIsItemDetailOpen(false);
            setSelectedItem(null);
          }}
          item={selectedItem}
          onUse={selectedItem.is_consumable ? () => handleUseClick(selectedItem.item_id) : undefined}
          onEquip={selectedItem.is_equippable ? () => handleEquipItem(selectedItem.item_id) : undefined}
          onDrop={() => handleDropClick(selectedItem.item_id)}
        />
      )}

      {/* 확인 다이얼로그 */}
      <ConfirmModal
        isOpen={isConfirmOpen}
        onClose={() => {
          setIsConfirmOpen(false);
          setPendingAction(null);
        }}
        onConfirm={handleConfirm}
        title="확인"
        message={
          pendingAction?.type === 'drop'
            ? '정말 이 아이템을 버리시겠습니까?'
            : '이 아이템을 사용하시겠습니까?'
        }
      />
    </>
  );
};

