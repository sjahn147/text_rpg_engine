/**
 * 오브젝트 인벤토리 모달 컴포넌트
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { gameApi } from '../../services/gameApi';

interface ObjectInventoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  objectId: string;
  sessionId: string;
  objectName?: string;
  onItemSelected: (itemId: string) => void;
}

export const ObjectInventoryModal: React.FC<ObjectInventoryModalProps> = ({
  isOpen,
  onClose,
  objectId,
  sessionId,
  objectName,
  onItemSelected,
}) => {
  const [contents, setContents] = useState<Array<{ item_id: string; name: string }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && objectId && sessionId) {
      loadContents();
    }
  }, [isOpen, objectId, sessionId]);

  const loadContents = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await gameApi.getObjectContents(sessionId, objectId);
      if (result.success) {
        setContents(result.contents || []);
      } else {
        setError('인벤토리를 불러올 수 없습니다.');
      }
    } catch (err) {
      console.error('오브젝트 인벤토리 로드 실패:', err);
      setError('인벤토리를 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleItemClick = (itemId: string) => {
    onItemSelected(itemId);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 50, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          onClick={(e) => e.stopPropagation()}
        >
          <h2 className="text-2xl font-light text-black/90 mb-6">
            {objectName || '오브젝트'} 내용물
          </h2>

          {loading && (
            <div className="text-black/60 text-sm py-4 text-center">로딩 중...</div>
          )}

          {error && (
            <div className="text-red-600 text-sm py-4 text-center">{error}</div>
          )}

          {!loading && !error && (
            <>
              {contents.length === 0 ? (
                <div className="text-black/60 text-sm py-4 text-center">
                  내용물이 없습니다.
                </div>
              ) : (
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {contents.map((item) => (
                    <button
                      key={item.item_id}
                      onClick={() => handleItemClick(item.item_id)}
                      className="w-full p-3 bg-black/5 rounded text-sm text-black/80 hover:bg-black/10 transition-colors text-left"
                    >
                      {item.name || item.item_id}
                    </button>
                  ))}
                </div>
              )}
            </>
          )}

          <div className="mt-6 flex justify-end">
            <button
              onClick={onClose}
              className="bg-gray-300 text-gray-800 px-4 py-2 rounded hover:bg-gray-400 transition-colors"
            >
              닫기
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

