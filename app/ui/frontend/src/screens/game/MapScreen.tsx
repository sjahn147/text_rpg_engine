/**
 * 지도 화면 - 현재 위치, 연결된 셀, 지역 정보
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';
import { gameApi } from '../../services/gameApi';

interface MapScreenProps {
  onClose: () => void;
}

interface CellNode {
  id: string;
  name: string;
  type: string;
  isCurrentLocation: boolean;
  isAccessible: boolean;
  position: { x: number; y: number };
}

interface CellConnection {
  from: string;
  to: string;
  direction?: string;
}

export const MapScreen: React.FC<MapScreenProps> = ({ onClose }) => {
  const { gameState, currentCell } = useGameStore();
  const [cells, setCells] = useState<CellNode[]>([]);
  const [connections, setConnections] = useState<CellConnection[]>([]);
  const [selectedCell, setSelectedCell] = useState<CellNode | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMapData();
  }, [gameState, currentCell]);

  const loadMapData = async () => {
    setLoading(true);
    
    try {
      // 현재 셀 정보와 연결된 셀들을 기반으로 지도 데이터 생성
      const currentCellId = currentCell?.cell_id || gameState?.current_cell_id;
      const connectedCells = currentCell?.connected_cells || [];
      
      // 중앙에 현재 셀 배치
      const centerX = 200;
      const centerY = 150;
      const radius = 100;
      
      const mapCells: CellNode[] = [];
      const mapConnections: CellConnection[] = [];
      
      // 현재 셀
      if (currentCellId) {
        mapCells.push({
          id: currentCellId,
          name: currentCell?.cell_name || '현재 위치',
          type: 'current',
          isCurrentLocation: true,
          isAccessible: true,
          position: { x: centerX, y: centerY },
        });
      }
      
      // 연결된 셀들을 원형으로 배치
      connectedCells.forEach((cell: any, index: number) => {
        const angle = (index / connectedCells.length) * 2 * Math.PI - Math.PI / 2;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);
        
        mapCells.push({
          id: cell.cell_id || cell.runtime_cell_id || `cell-${index}`,
          name: cell.cell_name || cell.name || `영역 ${index + 1}`,
          type: cell.direction || 'unknown',
          isCurrentLocation: false,
          isAccessible: true,
          position: { x, y },
        });
        
        // 연결 추가
        if (currentCellId) {
          mapConnections.push({
            from: currentCellId,
            to: cell.cell_id || cell.runtime_cell_id || `cell-${index}`,
            direction: cell.direction,
          });
        }
      });
      
      setCells(mapCells);
      setConnections(mapConnections);
    } catch (error) {
      console.error('지도 데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDirectionLabel = (direction?: string) => {
    const labels: Record<string, string> = {
      north: '북',
      south: '남',
      east: '동',
      west: '서',
      up: '위',
      down: '아래',
      in: '안',
      out: '밖',
    };
    return direction ? labels[direction] || direction : '';
  };

  const getCellColor = (cell: CellNode) => {
    if (cell.isCurrentLocation) return '#3b82f6'; // blue-500
    if (!cell.isAccessible) return '#9ca3af'; // gray-400
    return '#10b981'; // emerald-500
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
          className="bg-white p-8 rounded-lg shadow-xl w-full max-w-3xl max-h-[80vh] flex flex-col"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 50, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* 헤더 */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-light text-black/90">지도</h2>
            <button
              onClick={onClose}
              className="text-black/60 hover:text-black/90 transition-colors text-2xl"
            >
              ✕
            </button>
          </div>

          {/* 지도 영역 */}
          <div className="flex-1 flex gap-6 overflow-hidden">
            {/* SVG 지도 */}
            <div className="flex-1 bg-black/5 rounded-lg relative overflow-hidden">
              {loading ? (
                <div className="absolute inset-0 flex items-center justify-center text-black/60">
                  로딩 중...
                </div>
              ) : cells.length === 0 ? (
                <div className="absolute inset-0 flex items-center justify-center text-black/60">
                  지도 정보가 없습니다.
                </div>
              ) : (
                <svg
                  viewBox="0 0 400 300"
                  className="w-full h-full"
                  style={{ minHeight: '300px' }}
                >
                  {/* 연결선 */}
                  {connections.map((conn, index) => {
                    const fromCell = cells.find(c => c.id === conn.from);
                    const toCell = cells.find(c => c.id === conn.to);
                    if (!fromCell || !toCell) return null;
                    
                    return (
                      <line
                        key={`conn-${index}`}
                        x1={fromCell.position.x}
                        y1={fromCell.position.y}
                        x2={toCell.position.x}
                        y2={toCell.position.y}
                        stroke="#d1d5db"
                        strokeWidth="2"
                        strokeDasharray="4 4"
                      />
                    );
                  })}
                  
                  {/* 셀 노드 */}
                  {cells.map((cell) => (
                    <g
                      key={cell.id}
                      className="cursor-pointer"
                      onClick={() => setSelectedCell(cell)}
                    >
                      {/* 노드 원 */}
                      <circle
                        cx={cell.position.x}
                        cy={cell.position.y}
                        r={cell.isCurrentLocation ? 25 : 20}
                        fill={getCellColor(cell)}
                        stroke={selectedCell?.id === cell.id ? '#1f2937' : 'white'}
                        strokeWidth={selectedCell?.id === cell.id ? 3 : 2}
                        className="transition-all"
                      />
                      
                      {/* 셀 이름 */}
                      <text
                        x={cell.position.x}
                        y={cell.position.y + 35}
                        textAnchor="middle"
                        className="text-xs fill-gray-700"
                        style={{ fontSize: '10px' }}
                      >
                        {cell.name.length > 10 ? cell.name.slice(0, 10) + '...' : cell.name}
                      </text>
                      
                      {/* 현재 위치 표시 */}
                      {cell.isCurrentLocation && (
                        <text
                          x={cell.position.x}
                          y={cell.position.y + 5}
                          textAnchor="middle"
                          className="fill-white font-bold"
                          style={{ fontSize: '12px' }}
                        >
                          현재
                        </text>
                      )}
                    </g>
                  ))}
                </svg>
              )}
            </div>

            {/* 셀 정보 패널 */}
            <div className="w-64 border-l border-black/10 pl-6">
              <h3 className="text-lg font-light text-black/90 mb-4">위치 정보</h3>
              
              {selectedCell ? (
                <div className="space-y-4">
                  <div>
                    <div className="text-xs text-black/40 mb-1">이름</div>
                    <div className="text-sm text-black/80 font-medium">{selectedCell.name}</div>
                  </div>
                  
                  <div>
                    <div className="text-xs text-black/40 mb-1">상태</div>
                    <div className="text-sm text-black/80">
                      {selectedCell.isCurrentLocation ? '현재 위치' : 
                       selectedCell.isAccessible ? '이동 가능' : '이동 불가'}
                    </div>
                  </div>
                  
                  {selectedCell.type !== 'current' && (
                    <div>
                      <div className="text-xs text-black/40 mb-1">방향</div>
                      <div className="text-sm text-black/80">
                        {getDirectionLabel(selectedCell.type) || selectedCell.type}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-sm text-black/60">
                  지도에서 위치를 선택하세요.
                </div>
              )}

              {/* 범례 */}
              <div className="mt-8">
                <div className="text-xs text-black/40 mb-2">범례</div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-blue-500"></div>
                    <span className="text-xs text-black/60">현재 위치</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-emerald-500"></div>
                    <span className="text-xs text-black/60">이동 가능</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-gray-400"></div>
                    <span className="text-xs text-black/60">이동 불가</span>
                  </div>
                </div>
              </div>
            </div>
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

