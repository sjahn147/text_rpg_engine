/**
 * 저장/불러오기 화면 - 전체 화면으로 변경
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';
import { gameApi } from '../../services/gameApi';

interface SaveLoadScreenProps {
  onClose: () => void;
  mode: 'save' | 'load';
}

interface SaveSlot {
  slot_id: number;
  session_id?: string;
  player_name?: string;
  location?: string;
  play_time?: number;
  save_date?: string;
  is_empty: boolean;
}

export const SaveLoadScreen: React.FC<SaveLoadScreenProps> = ({ onClose, mode }) => {
  const { gameState } = useGameStore();
  const [slots, setSlots] = useState<SaveSlot[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSaveSlots();
  }, []);

  const loadSaveSlots = async () => {
    // TODO: 저장 슬롯 목록 API 호출
    // 현재는 더미 데이터 사용
    const dummySlots: SaveSlot[] = Array.from({ length: 10 }, (_, i) => ({
      slot_id: i + 1,
      is_empty: true,
    }));
    
    // 첫 번째 슬롯에 현재 게임 상태 표시 (시뮬레이션)
    if (gameState?.session_id) {
      dummySlots[0] = {
        slot_id: 1,
        session_id: gameState.session_id,
        player_name: '플레이어',
        location: gameState.current_location || '알 수 없음',
        play_time: gameState.play_time || 0,
        save_date: new Date().toLocaleString('ko-KR'),
        is_empty: false,
      };
    }
    
    setSlots(dummySlots);
  };

  const handleSave = async (slotId: number) => {
    if (!gameState?.session_id) {
      setError('저장할 게임이 없습니다.');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // TODO: 저장 API 호출
      // await gameApi.saveGame(gameState.session_id, slotId);
      
      console.log('게임 저장:', slotId, gameState.session_id);
      
      // 슬롯 업데이트
      const updatedSlots = [...slots];
      updatedSlots[slotId - 1] = {
        slot_id: slotId,
        session_id: gameState.session_id,
        player_name: '플레이어',
        location: gameState.current_location || '알 수 없음',
        play_time: gameState.play_time || 0,
        save_date: new Date().toLocaleString('ko-KR'),
        is_empty: false,
      };
      setSlots(updatedSlots);
      
      // 성공 메시지
      alert('게임이 저장되었습니다.');
      onClose();
    } catch (err) {
      console.error('저장 실패:', err);
      setError('게임 저장에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoad = async (slotId: number) => {
    const slot = slots.find(s => s.slot_id === slotId);
    if (!slot || slot.is_empty) {
      setError('저장된 게임이 없습니다.');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // TODO: 불러오기 API 호출
      // await gameApi.loadGame(slot.session_id);
      
      console.log('게임 불러오기:', slotId, slot.session_id);
      
      // 성공 메시지
      alert('게임을 불러왔습니다.');
      onClose();
    } catch (err) {
      console.error('불러오기 실패:', err);
      setError('게임 불러오기에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (slotId: number) => {
    const slot = slots.find(s => s.slot_id === slotId);
    if (!slot || slot.is_empty) {
      return;
    }
    
    if (!confirm('이 저장 데이터를 삭제하시겠습니까?')) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // TODO: 삭제 API 호출
      // await gameApi.deleteSave(slotId);
      
      // 슬롯 업데이트
      const updatedSlots = [...slots];
      updatedSlots[slotId - 1] = {
        slot_id: slotId,
        is_empty: true,
      };
      setSlots(updatedSlots);
    } catch (err) {
      console.error('삭제 실패:', err);
      setError('저장 데이터 삭제에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const formatPlayTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}시간 ${mins}분` : `${mins}분`;
  };

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
            <h2 className="text-2xl font-light text-black/90">
              {mode === 'save' ? '게임 저장' : '게임 불러오기'}
            </h2>
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

          {/* 슬롯 목록 */}
          <div className="flex-1 overflow-y-auto space-y-3">
            {slots.map((slot) => (
              <div
                key={slot.slot_id}
                className={`p-4 border rounded transition-colors cursor-pointer ${
                  selectedSlot === slot.slot_id
                    ? 'border-blue-500 bg-blue-50'
                    : slot.is_empty
                    ? 'border-black/10 bg-black/5'
                    : 'border-black/10 hover:bg-black/5'
                }`}
                onClick={() => setSelectedSlot(slot.slot_id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="font-medium text-black/90">
                      슬롯 {slot.slot_id}
                    </div>
                    {slot.is_empty ? (
                      <div className="text-sm text-black/60 mt-1">
                        비어 있음
                      </div>
                    ) : (
                      <div className="text-sm text-black/60 mt-1">
                        <span>{slot.player_name}</span>
                        <span className="mx-2">•</span>
                        <span>{slot.location}</span>
                        <span className="mx-2">•</span>
                        <span>{formatPlayTime(slot.play_time || 0)}</span>
                      </div>
                    )}
                    {!slot.is_empty && slot.save_date && (
                      <div className="text-xs text-black/40 mt-1">
                        저장: {slot.save_date}
                      </div>
                    )}
                  </div>
                  
                  {selectedSlot === slot.slot_id && (
                    <div className="flex gap-2">
                      {mode === 'save' ? (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleSave(slot.slot_id);
                          }}
                          disabled={loading}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors disabled:opacity-50"
                        >
                          저장
                        </button>
                      ) : (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleLoad(slot.slot_id);
                          }}
                          disabled={loading || slot.is_empty}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors disabled:opacity-50"
                        >
                          불러오기
                        </button>
                      )}
                      {!slot.is_empty && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(slot.slot_id);
                          }}
                          disabled={loading}
                          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors disabled:opacity-50"
                        >
                          삭제
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* 하단 버튼 */}
          <div className="mt-6 flex justify-end">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded transition-colors"
            >
              닫기
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

