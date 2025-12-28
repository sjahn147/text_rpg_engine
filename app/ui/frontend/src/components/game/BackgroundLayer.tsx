/**
 * 배경 레이어 컴포넌트 - novel_game 스타일
 */

import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

interface BackgroundLayerProps {
  background?: string;
}

export const BackgroundLayer: React.FC<BackgroundLayerProps> = ({ background }) => {
  const bgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (background && bgRef.current) {
      // 배경 이미지 페이드 전환
      bgRef.current.style.opacity = '0';
      setTimeout(() => {
        if (bgRef.current) {
          bgRef.current.style.backgroundImage = `url(${background})`;
          bgRef.current.style.opacity = '0.75';
        }
      }, 100);
    }
  }, [background]);

  return (
    <>
      {/* 하얀색 위주 배경 (하늘색 약간) */}
      <div className="absolute inset-0 w-full h-full bg-gradient-to-b from-[#fafafa] via-[#f8f9fa] to-[#f0f7fa] z-0" />
      {/* 배경 이미지 */}
      <div
        ref={bgRef}
        className="absolute inset-0 w-full h-full bg-cover bg-center bg-no-repeat z-0"
        style={{
          backgroundImage: background ? `url(${background})` : undefined,
          opacity: background ? 0.75 : 0,
          transition: 'opacity 1.2s cubic-bezier(0.4, 0, 0.2, 1)',
        }}
      />
      {/* 상단 그라데이션 오버레이 */}
      <div className="absolute inset-0 w-full h-full bg-gradient-to-b from-transparent via-transparent to-[rgba(240,247,250,0.2)] pointer-events-none z-0" />
    </>
  );
};

