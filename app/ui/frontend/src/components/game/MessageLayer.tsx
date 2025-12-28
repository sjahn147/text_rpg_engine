/**
 * 메시지 레이어 컴포넌트 - RPG 엔진용
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';

interface MessageLayerProps {
  message?: string;
  characterName?: string;
  messageType?: 'narration' | 'dialogue' | 'system';
  onMessageComplete?: () => void;
  onClick?: () => void;
  isClickable?: boolean;
}

export const MessageLayer: React.FC<MessageLayerProps> = ({
  message,
  characterName,
  messageType = 'dialogue',
  onMessageComplete,
  onClick,
  isClickable = false,
}) => {
  const { textSpeed, isSkipMode } = useGameStore();
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (message) {
      setDisplayedText('');
      setIsTyping(true);
      
      // 스킵 모드면 즉시 완료
      if (isSkipMode) {
        setDisplayedText(message);
        setIsTyping(false);
        if (onMessageComplete) {
          onMessageComplete();
        }
        return;
      }
      
      let index = 0;
      const timer = setInterval(() => {
        if (index < message.length) {
          setDisplayedText(message.slice(0, index + 1));
          index++;
        } else {
          setIsTyping(false);
          clearInterval(timer);
          if (onMessageComplete) {
            onMessageComplete();
          }
        }
      }, textSpeed);

      return () => clearInterval(timer);
    }
  }, [message, onMessageComplete, textSpeed, isSkipMode]);

  const handleClick = () => {
    if (isClickable && !isTyping && onClick) {
      onClick();
    }
  };

  if (!message) return null;

  return (
    <motion.div
      className="absolute bottom-0 left-0 right-0 pb-8 px-8 z-20"
      initial={{ y: 120, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      exit={{ y: 120, opacity: 0 }}
      transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
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
        className={`message-box ${isClickable && !isTyping ? 'cursor-pointer' : ''}`}
        onClick={handleClick}
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
        {characterName && messageType !== 'narration' && (
          <motion.div
            className="text-black/70 text-base font-light mb-3 tracking-wider text-center"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
          >
            {characterName}
          </motion.div>
        )}
        <motion.div
          className="text-black/90 text-lg leading-loose min-h-[80px] font-light tracking-wide text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          {displayedText}
          {isTyping && (
            <motion.span
              className="inline-block ml-1 text-black/60"
              animate={{ opacity: [0.6, 1, 0.6] }}
              transition={{ duration: 0.8, repeat: Infinity }}
            >
              |
            </motion.span>
          )}
        </motion.div>
        {!isTyping && isClickable && (
          <motion.div
            className="text-black/50 text-center mt-6 text-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0.5, 0.7, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            ▼
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

