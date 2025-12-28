/**
 * 위치 오버레이 패널 - 현재 위치 정보 및 이동 옵션
 */
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';

interface LocationPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onMove?: (cellId: string) => void;
}

export const LocationPanel: React.FC<LocationPanelProps> = ({
  isOpen,
  onClose,
  onMove,
}) => {
  const { currentCell, gameState } = useGameStore();

  const getDirectionLabel = (direction: string) => {
    const labels: Record<string, string> = {
      north: '북쪽',
      south: '남쪽',
      east: '동쪽',
      west: '서쪽',
      up: '위',
      down: '아래',
      in: '안으로',
      out: '밖으로',
    };
    return labels[direction] || direction;
  };

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
          
          {/* 패널 (하단에서 올라옴) */}
          <motion.div
            className="fixed bottom-0 left-0 right-0 z-50 bg-white shadow-xl rounded-t-xl max-h-[60vh] flex flex-col"
            initial={{ y: 300, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 300, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          >
            {/* 헤더 */}
            <div className="p-4 border-b border-black/10 flex items-center justify-between">
              <h3 className="text-lg font-light text-black/90">현재 위치</h3>
              <button
                onClick={onClose}
                className="text-black/60 hover:text-black/90 transition-colors"
              >
                ✕
              </button>
            </div>

            {/* 컨텐츠 */}
            <div className="flex-1 overflow-y-auto p-4">
              {currentCell ? (
                <div className="space-y-4">
                  {/* 위치 정보 */}
                  <div>
                    <h4 className="text-xl font-medium text-black/90 mb-2">
                      {currentCell.cell_name}
                    </h4>
                    <p className="text-black/70 text-sm">
                      {currentCell.description}
                    </p>
                  </div>

                  {/* 연결된 셀 */}
                  {currentCell.connected_cells && currentCell.connected_cells.length > 0 && (
                    <div>
                      <h5 className="text-sm font-medium text-black/80 mb-2">이동 가능한 장소</h5>
                      <div className="grid grid-cols-2 gap-2">
                        {currentCell.connected_cells.map((cell: any, index: number) => (
                          <button
                            key={cell.cell_id || cell.runtime_cell_id || index}
                            onClick={() => onMove?.(cell.cell_id || cell.runtime_cell_id)}
                            className="p-3 bg-black/5 hover:bg-black/10 rounded transition-colors text-left"
                          >
                            <div className="text-sm text-black/80 font-medium">
                              {cell.cell_name || cell.name || `영역 ${index + 1}`}
                            </div>
                            {cell.direction && (
                              <div className="text-xs text-black/50 mt-1">
                                {getDirectionLabel(cell.direction)}
                              </div>
                            )}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 오브젝트 */}
                  {currentCell.objects && currentCell.objects.length > 0 && (
                    <div>
                      <h5 className="text-sm font-medium text-black/80 mb-2">오브젝트</h5>
                      <div className="space-y-1">
                        {currentCell.objects.map((obj: any, index: number) => (
                          <div
                            key={obj.object_id || index}
                            className="text-sm text-black/70 p-2 bg-black/5 rounded"
                          >
                            {obj.object_name || obj.name}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 엔티티 */}
                  {currentCell.entities && currentCell.entities.length > 0 && (
                    <div>
                      <h5 className="text-sm font-medium text-black/80 mb-2">인물</h5>
                      <div className="space-y-1">
                        {currentCell.entities.map((entity: any, index: number) => (
                          <div
                            key={entity.entity_id || index}
                            className="text-sm text-black/70 p-2 bg-black/5 rounded"
                          >
                            {entity.name}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center text-black/60 py-8">
                  위치 정보를 불러올 수 없습니다.
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

