/**
 * 게임 오버 화면 - 게임 오버, 엔딩, 재시작
 */
import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';

interface GameOverScreenProps {
  onRestart: () => void;
  onLoadSave: () => void;
  onMainMenu: () => void;
  type?: 'game_over' | 'victory' | 'ending';
  title?: string;
  message?: string;
}

export const GameOverScreen: React.FC<GameOverScreenProps> = ({
  onRestart,
  onLoadSave,
  onMainMenu,
  type = 'game_over',
  title,
  message,
}) => {
  const { gameState, history } = useGameStore();
  const [showStats, setShowStats] = useState(false);

  // 표시될 제목 결정
  const displayTitle = title || (
    type === 'victory' ? '승리!' :
    type === 'ending' ? '엔딩' :
    '게임 오버'
  );

  // 배경 색상
  const bgColor = 
    type === 'victory' ? 'from-emerald-900 via-emerald-800 to-emerald-900' :
    type === 'ending' ? 'from-amber-900 via-amber-800 to-amber-900' :
    'from-red-900 via-red-800 to-red-900';

  // 통계 계산
  const stats = {
    playTime: gameState?.play_time || 0,
    historyCount: history.length,
    location: gameState?.current_location || '알 수 없음',
  };

  const formatPlayTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hours > 0) {
      return `${hours}시간 ${minutes}분 ${secs}초`;
    } else if (minutes > 0) {
      return `${minutes}분 ${secs}초`;
    }
    return `${secs}초`;
  };

  return (
    <AnimatePresence>
      <motion.div
        className={`fixed inset-0 z-50 bg-gradient-to-b ${bgColor} flex flex-col items-center justify-center`}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* 제목 */}
        <motion.h1
          className="text-6xl font-light text-white/90 mb-6"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          {displayTitle}
        </motion.h1>

        {/* 메시지 */}
        {message && (
          <motion.p
            className="text-xl text-white/70 mb-8 text-center max-w-md px-4"
            initial={{ y: -30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            {message}
          </motion.p>
        )}

        {/* 통계 토글 */}
        <motion.button
          className="text-white/60 hover:text-white/80 text-sm mb-4 transition-colors"
          onClick={() => setShowStats(!showStats)}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
        >
          {showStats ? '통계 숨기기' : '통계 보기'}
        </motion.button>

        {/* 통계 패널 */}
        <AnimatePresence>
          {showStats && (
            <motion.div
              className="bg-white/10 backdrop-blur-sm rounded-lg p-6 mb-8 w-80"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="space-y-3">
                <div className="flex justify-between text-white/80">
                  <span>플레이 시간</span>
                  <span>{formatPlayTime(stats.playTime)}</span>
                </div>
                <div className="flex justify-between text-white/80">
                  <span>기록된 행동</span>
                  <span>{stats.historyCount}회</span>
                </div>
                <div className="flex justify-between text-white/80">
                  <span>마지막 위치</span>
                  <span>{stats.location}</span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* 버튼들 */}
        <motion.div
          className="flex flex-col gap-3 w-64"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.9, duration: 0.5 }}
        >
          {type === 'game_over' && (
            <button
              onClick={onLoadSave}
              className="px-8 py-3 bg-white/20 hover:bg-white/30 text-white rounded transition-colors text-lg"
            >
              저장 불러오기
            </button>
          )}
          
          <button
            onClick={onRestart}
            className="px-8 py-3 bg-white/20 hover:bg-white/30 text-white rounded transition-colors text-lg"
          >
            처음부터 다시 시작
          </button>
          
          <button
            onClick={onMainMenu}
            className="px-8 py-3 bg-white/10 hover:bg-white/20 text-white/80 rounded transition-colors"
          >
            메인 메뉴로
          </button>
        </motion.div>

        {/* 하단 장식 */}
        <motion.div
          className="absolute bottom-8 text-white/30 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
        >
          {type === 'ending' ? '이야기가 끝났습니다' : 'Press any key to continue...'}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};


