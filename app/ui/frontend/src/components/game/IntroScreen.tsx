/**
 * 인트로 화면 컴포넌트
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface IntroScreenProps {
  onComplete: () => void;
}

export const IntroScreen: React.FC<IntroScreenProps> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  const introSteps = [
    {
      title: "레크로스타",
      subtitle: "휴양지",
      text: "한적한 휴양지 레크로스타에 도착했습니다.",
      duration: 3000,
    },
    {
      title: "여관",
      subtitle: "내 방",
      text: "여관의 내 방에서 하루를 시작합니다.",
      duration: 3000,
    },
  ];

  useEffect(() => {
    if (currentStep < introSteps.length) {
      const timer = setTimeout(() => {
        if (currentStep === introSteps.length - 1) {
          // 마지막 스텝 후 페이드 아웃
          setIsVisible(false);
          setTimeout(() => {
            onComplete();
          }, 1000);
        } else {
          setCurrentStep(currentStep + 1);
        }
      }, introSteps[currentStep].duration);

      return () => clearTimeout(timer);
    }
  }, [currentStep, onComplete]);

  const currentIntro = introSteps[currentStep];

  if (!isVisible) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 bg-gradient-to-b from-[#fafafa] via-[#f8f9fa] to-[#f0f7fa]"
        initial={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 1 }}
      >
        {/* 인트로 화면 위치 HUD */}
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
                {currentIntro.title}
              </div>
              <div style={{
                fontSize: '0.875rem',
                fontWeight: 300,
                color: 'rgba(0, 0, 0, 0.65)',
                marginBottom: '0.75rem',
                lineHeight: 1.4,
              }}>
                {currentIntro.subtitle || '레크로스타'}
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
                  제 1273년, 새싹의 달
                </div>
                <div style={{ color: 'rgba(0, 0, 0, 0.6)' }}>
                  15일 · 봄
                </div>
              </div>
            </div>
          </div>
        </motion.div>
        <motion.div
          key={currentStep}
          className="absolute bottom-0 left-0 right-0 pb-8 px-8 z-20"
          initial={{ y: 120, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 120, opacity: 0 }}
          transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
          style={{ 
            position: 'absolute', 
            bottom: 0, 
            left: 0, 
            right: 0, 
            paddingBottom: '2rem', 
            paddingLeft: '2rem', 
            paddingRight: '2rem', 
            zIndex: 20,
            width: '100%',
            pointerEvents: 'auto',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'flex-end',
            boxSizing: 'border-box'
          }}
        >
          <div
            className="message-box"
            style={{
              background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.08) 100%)',
              backdropFilter: 'blur(20px)',
              WebkitBackdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: 0,
              boxShadow: '0 4px 24px rgba(0, 0, 0, 0.08)',
              padding: '28px 36px',
              minHeight: '140px',
              maxWidth: '900px',
              width: 'calc(100% - 4rem)',
              margin: '0 auto',
              position: 'relative',
              zIndex: 20,
              display: 'block',
            }}
          >
            <motion.p
              className="text-lg font-light text-black/70 max-w-md mx-auto leading-relaxed text-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.6 }}
            >
              {currentIntro.text}
            </motion.p>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

