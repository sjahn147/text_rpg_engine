/**
 * 정보 패널 컴포넌트 (인벤토리, 시간, 저널, 지도 등)
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';
import { gameApi } from '../../services/gameApi';
import { CombineModal } from './CombineModal';

interface InfoPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

type TabType = 'inventory' | 'map' | 'journal' | 'time';

export const InfoPanel: React.FC<InfoPanelProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<TabType>('inventory');
  const { gameState, history } = useGameStore();
  const [inventory, setInventory] = useState<Array<{ item_id: string; quantity: number; name?: string }>>([]);
  const [isCombineModalOpen, setIsCombineModalOpen] = useState(false);

  // 인벤토리 로드
  useEffect(() => {
    if (isOpen && activeTab === 'inventory' && gameState) {
      loadInventory();
    }
  }, [isOpen, activeTab, gameState]);

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

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            key="info-panel-backdrop"
            className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          >
            <motion.div
              key="info-panel-content"
              className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md max-h-[80vh] flex flex-col"
              initial={{ y: -50, opacity: 0, scale: 0.95 }}
              animate={{ y: 0, opacity: 1, scale: 1 }}
              exit={{ y: 50, opacity: 0, scale: 0.95 }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* 헤더 */}
              <div className="flex-shrink-0 pb-6 border-b border-black/10">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-light text-black/90">정보</h2>
                  <button
                    onClick={onClose}
                    className="text-black/60 hover:text-black/90 transition-colors text-2xl leading-none w-8 h-8 flex items-center justify-center"
                    aria-label="닫기"
                  >
                    ×
                  </button>
                </div>
                
                {/* 탭 */}
                <div className="flex gap-2">
                  {(['inventory', 'map', 'journal', 'time'] as TabType[]).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-4 py-2 text-sm font-light transition-colors rounded ${
                        activeTab === tab
                          ? 'bg-black/10 text-black/90'
                          : 'text-black/60 hover:text-black/80'
                      }`}
                    >
                      {tab === 'inventory' ? '인벤토리' :
                       tab === 'map' ? '지도' :
                       tab === 'journal' ? '저널' : '시간'}
                    </button>
                  ))}
                </div>
              </div>

              {/* 컨텐츠 */}
              <div className="flex-1 overflow-y-auto pt-6 min-h-0">
                <AnimatePresence mode="wait">
                  {activeTab === 'inventory' && (
                    <motion.div
                      key="inventory"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                    >
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-light text-black/90">인벤토리</h3>
                        <button
                          onClick={() => setIsCombineModalOpen(true)}
                          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-light rounded transition-colors"
                        >
                          조합
                        </button>
                      </div>
                      <div className="space-y-2">
                        {inventory.length === 0 ? (
                          <div className="text-black/60 text-sm py-4 text-center">
                            아이템이 없습니다.
                          </div>
                        ) : (
                          inventory.map((item) => (
                            <div
                              key={item.item_id}
                              className="p-3 bg-black/5 rounded text-sm text-black/80"
                            >
                              <div className="flex items-center justify-between">
                                <span>{item.name || item.item_id}</span>
                                <span className="text-black/60">x{item.quantity}</span>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'map' && (
                    <motion.div
                      key="map"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                    >
                      <h3 className="text-lg font-light text-black/90 mb-4">지도</h3>
                      <div className="text-black/60 text-sm">
                        {gameState?.current_location ? (
                          <p>현재 위치: {gameState.current_location}</p>
                        ) : (
                          <p>지도 정보가 없습니다.</p>
                        )}
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'journal' && (
                    <motion.div
                      key="journal"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                    >
                      <h3 className="text-lg font-light text-black/90 mb-4">저널</h3>
                      <div className="space-y-3">
                        {history.length > 0 ? (
                          history.map((entry, index) => (
                            <div key={index} className="text-sm text-black/70 border-b border-black/5 pb-2">
                              {entry.characterName && (
                                <div className="font-medium text-black/80 mb-1">
                                  {entry.characterName}
                                </div>
                              )}
                              <div className="text-black/60">{entry.text}</div>
                            </div>
                          ))
                        ) : (
                          <p className="text-black/60 text-sm">저널 항목이 없습니다.</p>
                        )}
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'time' && (
                    <motion.div
                      key="time"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                    >
                      <h3 className="text-lg font-light text-black/90 mb-4">시간</h3>
                      <div className="text-black/60 text-sm">
                        {gameState?.play_time !== undefined ? (
                          <p>플레이 시간: {Math.floor(gameState.play_time / 60)}분</p>
                        ) : (
                          <p>시간 정보가 없습니다.</p>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
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
        </>
      )}
    </AnimatePresence>
  );
};
