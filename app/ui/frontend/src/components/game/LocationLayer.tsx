/**
 * 위치 레이어 컴포넌트 - 현재 셀/위치 정보 표시
 */

import React from 'react';
import { motion } from 'framer-motion';
import { CellInfo } from '../../types/game';

interface LocationLayerProps {
  cell: CellInfo;
  gameDate?: {
    year: number;
    month: number;
    day: number;
    season?: string;
  };
}

// 판타지 날짜 포맷팅
const formatFantasyDate = (date?: { year: number; month: number; day: number; season?: string }) => {
  if (!date) {
    // 기본 날짜 (게임 시작일)
    return {
      year: 1273,
      month: 3,
      day: 15,
      season: '봄'
    };
  }
  return date;
};

const getMonthName = (month: number): string => {
  const months = ['새싹의 달', '꽃의 달', '햇살의 달', '열매의 달', '수확의 달', '낙엽의 달', '서리의 달', '눈의 달', '얼음의 달', '바람의 달', '비의 달', '별의 달'];
  return months[month - 1] || '알 수 없는 달';
};

const getSeasonName = (month: number): string => {
  if (month >= 3 && month <= 5) return '봄';
  if (month >= 6 && month <= 8) return '여름';
  if (month >= 9 && month <= 11) return '가을';
  return '겨울';
};

export const LocationLayer: React.FC<LocationLayerProps> = ({ cell, gameDate }) => {
  const date = formatFantasyDate(gameDate);
  const monthName = getMonthName(date.month);
  const seasonName = gameDate?.season || getSeasonName(date.month);

  return (
    <motion.div
      className="fixed top-4 right-4 z-30"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
      style={{
        position: 'fixed',
        top: '1rem',
        right: '1rem',
        zIndex: 30,
      }}
    >
      <div 
        className="bg-white/20 backdrop-blur-md border border-black/10 rounded-lg shadow-lg"
        style={{
          background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.12) 100%)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(0, 0, 0, 0.12)',
          borderRadius: '0.5rem',
          padding: 0,
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.12)',
          overflow: 'hidden',
          minWidth: '240px',
        }}
      >
        {/* 본문 */}
        <div style={{ padding: '1.25rem 1.5rem' }}>
          <div style={{
            fontSize: '1.125rem',
            fontWeight: 400,
            color: 'rgba(0, 0, 0, 0.95)',
            marginBottom: '0.5rem',
            lineHeight: 1.4,
          }}>
            {cell.cell_name}
          </div>
          <div style={{
            fontSize: '0.875rem',
            fontWeight: 300,
            color: 'rgba(0, 0, 0, 0.65)',
            marginBottom: '0.75rem',
            lineHeight: 1.4,
          }}>
            {cell.location_name} · {cell.region_name}
          </div>
          
          {/* 날짜 구분선 */}
          <div style={{
            height: '1px',
            background: 'linear-gradient(90deg, transparent, rgba(0, 0, 0, 0.1), transparent)',
            margin: '0.75rem 0',
          }} />
          
          {/* 날짜 정보 */}
          <div style={{
            fontSize: '0.8125rem',
            fontWeight: 300,
            color: 'rgba(0, 0, 0, 0.7)',
            lineHeight: 1.5,
          }}>
            <div style={{ marginBottom: '0.25rem' }}>
              제 {date.year}년, {monthName}
            </div>
            <div style={{ color: 'rgba(0, 0, 0, 0.6)' }}>
              {date.day}일 · {seasonName}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

