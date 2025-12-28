/**
 * 아이템 상세 모달 - 아이템 정보 표시 및 액션
 */
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ItemEffect {
  type: string;
  value: number;
  description?: string;
}

interface ItemData {
  item_id: string;
  name: string;
  description?: string;
  item_type: string;
  quantity?: number;
  rarity?: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  effects?: ItemEffect[];
  value?: number;
  weight?: number;
  is_consumable?: boolean;
  is_equippable?: boolean;
  equipment_slot?: string;
  image_url?: string;
}

interface ItemDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  item: ItemData | null;
  onUse?: (itemId: string) => void;
  onEquip?: (itemId: string) => void;
  onDrop?: (itemId: string) => void;
}

export const ItemDetailModal: React.FC<ItemDetailModalProps> = ({
  isOpen,
  onClose,
  item,
  onUse,
  onEquip,
  onDrop,
}) => {
  if (!isOpen || !item) return null;

  const getRarityColor = (rarity?: string) => {
    const colors: Record<string, string> = {
      common: 'text-gray-600',
      uncommon: 'text-green-600',
      rare: 'text-blue-600',
      epic: 'text-purple-600',
      legendary: 'text-yellow-600',
    };
    return colors[rarity || 'common'];
  };

  const getRarityLabel = (rarity?: string) => {
    const labels: Record<string, string> = {
      common: '일반',
      uncommon: '고급',
      rare: '희귀',
      epic: '영웅',
      legendary: '전설',
    };
    return labels[rarity || 'common'];
  };

  const getItemTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      weapon: '무기',
      armor: '방어구',
      accessory: '장신구',
      consumable: '소비품',
      material: '재료',
      quest: '퀘스트',
      key: '열쇠',
    };
    return labels[type] || type;
  };

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-[60] bg-black/50 backdrop-blur-sm flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="bg-white p-6 rounded-lg shadow-xl w-full max-w-md"
          initial={{ y: -30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 30, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* 헤더 */}
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className={`text-xl font-medium ${getRarityColor(item.rarity)}`}>
                {item.name}
                {item.quantity && item.quantity > 1 && (
                  <span className="text-black/60 ml-2">x{item.quantity}</span>
                )}
              </h3>
              <div className="flex items-center gap-2 text-sm text-black/60 mt-1">
                <span>{getItemTypeLabel(item.item_type)}</span>
                {item.rarity && (
                  <>
                    <span>•</span>
                    <span className={getRarityColor(item.rarity)}>
                      {getRarityLabel(item.rarity)}
                    </span>
                  </>
                )}
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-black/60 hover:text-black/90 transition-colors text-xl"
            >
              ✕
            </button>
          </div>

          {/* 설명 */}
          {item.description && (
            <p className="text-black/70 mb-4 text-sm border-l-2 border-black/10 pl-3">
              {item.description}
            </p>
          )}

          {/* 효과 */}
          {item.effects && item.effects.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-black/80 mb-2">효과</h4>
              <div className="space-y-1">
                {item.effects.map((effect, index) => (
                  <div key={index} className="text-sm text-emerald-600">
                    + {effect.description || `${effect.type} +${effect.value}`}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 추가 정보 */}
          <div className="grid grid-cols-2 gap-3 mb-6 text-sm">
            {item.value !== undefined && (
              <div>
                <span className="text-black/50">가치:</span>
                <span className="text-black/80 ml-2">{item.value} G</span>
              </div>
            )}
            {item.weight !== undefined && (
              <div>
                <span className="text-black/50">무게:</span>
                <span className="text-black/80 ml-2">{item.weight}</span>
              </div>
            )}
            {item.equipment_slot && (
              <div>
                <span className="text-black/50">장착 부위:</span>
                <span className="text-black/80 ml-2">{item.equipment_slot}</span>
              </div>
            )}
          </div>

          {/* 액션 버튼 */}
          <div className="flex flex-wrap gap-2">
            {item.is_consumable && onUse && (
              <button
                onClick={() => onUse(item.item_id)}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded transition-colors text-sm"
              >
                사용하기
              </button>
            )}
            {item.is_equippable && onEquip && (
              <button
                onClick={() => onEquip(item.item_id)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors text-sm"
              >
                장착하기
              </button>
            )}
            {onDrop && (
              <button
                onClick={() => onDrop(item.item_id)}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded transition-colors text-sm"
              >
                버리기
              </button>
            )}
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded transition-colors text-sm ml-auto"
            >
              닫기
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

