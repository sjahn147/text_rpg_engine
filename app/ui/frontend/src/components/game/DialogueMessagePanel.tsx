/**
 * 대화/메시지 패널 컴포넌트 - 일본 노벨 게임 스타일 통합
 * 
 * 대화, 내레이션, 메시지, 선택지를 자연스럽게 통합하여 표시합니다.
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { List as FixedSizeList } from 'react-window';
import { useGameStore } from '../../store/gameStore';
import { GameAction } from '../../types/game';
import { toast } from '../common/Toast';

interface DialogueMessagePanelProps {
  availableActions?: GameAction[];
  onActionSelect?: (action: GameAction) => void;
  onChoiceSelect?: (choiceId: string) => void;
  onClose?: () => void; // 대화 닫기 핸들러
}

const DialogueMessagePanelComponent: React.FC<DialogueMessagePanelProps> = ({
  availableActions = [],
  onActionSelect,
  onChoiceSelect,
  onClose,
}) => {
  const {
    currentDialogue,
    currentMessage,
    textSpeed,
    isSkipMode,
  } = useGameStore();

  const historyRef = useRef<HTMLDivElement>(null);
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  // 패널 높이 조정 기능
  const [panelHeight, setPanelHeight] = useState(() => {
    // localStorage에서 저장된 높이 불러오기
    try {
      const saved = localStorage.getItem('dialoguePanelHeight');
      if (saved) {
        const height = parseInt(saved, 10);
        if (height >= 150 && height <= 400) {
          return height;
        }
      }
    } catch (error) {
      console.warn('Failed to load panel height from localStorage:', error);
    }
    return 250; // 기본값
  });
  const [isResizing, setIsResizing] = useState(false);
  const resizeStartY = useRef<number>(0);
  const resizeStartHeight = useRef<number>(0);

  // 텍스트 타이핑 효과
  useEffect(() => {
    if (currentMessage?.text) {
      setDisplayedText('');
      setIsTyping(true);

      if (isSkipMode) {
        setDisplayedText(currentMessage.text);
        setIsTyping(false);
        return;
      }

      let index = 0;
      const timer = setInterval(() => {
        if (index < currentMessage.text.length) {
          setDisplayedText(currentMessage.text.slice(0, index + 1));
          index++;
        } else {
          setIsTyping(false);
          clearInterval(timer);
        }
      }, textSpeed);

      return () => clearInterval(timer);
    }
  }, [currentMessage, textSpeed, isSkipMode]);

  // 자동 스크롤
  useEffect(() => {
    if (historyRef.current) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight;
    }
  }, [currentDialogue, currentMessage, displayedText]);

  // 높이 조정 핸들러
  const handleResizeStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsResizing(true);
    resizeStartY.current = e.clientY;
    resizeStartHeight.current = panelHeight;
  }, [panelHeight]);

  const handleResizeMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return;
    
    const deltaY = resizeStartY.current - e.clientY; // 위로 드래그하면 높이 증가
    const newHeight = Math.max(150, Math.min(400, resizeStartHeight.current + deltaY));
    setPanelHeight(newHeight);
  }, [isResizing]);

  const handleResizeEnd = useCallback(() => {
    if (isResizing) {
      setIsResizing(false);
      // localStorage에 저장
      try {
        localStorage.setItem('dialoguePanelHeight', panelHeight.toString());
      } catch (error) {
        console.warn('Failed to save panel height to localStorage:', error);
      }
    }
  }, [isResizing, panelHeight]);

  // 리사이즈 이벤트 리스너
  useEffect(() => {
    if (isResizing) {
      window.addEventListener('mousemove', handleResizeMove);
      window.addEventListener('mouseup', handleResizeEnd);
      document.body.style.cursor = 'ns-resize';
      document.body.style.userSelect = 'none';
      
      return () => {
        window.removeEventListener('mousemove', handleResizeMove);
        window.removeEventListener('mouseup', handleResizeEnd);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
    }
  }, [isResizing, handleResizeMove, handleResizeEnd]);

  // 표시 조건: 대화, 메시지, 또는 선택지가 있을 때만 표시
  const shouldShow = currentDialogue || currentMessage || (availableActions && availableActions.length > 0);

  if (!shouldShow) {
    return null;
  }

  // 대화 중인 NPC 정보 추출
  const npcName = currentDialogue?.npc_name || currentMessage?.character_name;
  const npcPortrait = currentDialogue ? currentDialogue.npc_name : null;

  // 선택지 목록 - 대화 중일 때는 대화 선택지와 topic 선택지 표시
  const choices = React.useMemo(() => {
    if (!currentDialogue) {
      return [];
    }
    
    const choiceList: GameAction[] = [];
    
    // available_topics를 우선 사용 (모든 키워드 표시)
    if (currentDialogue.available_topics && currentDialogue.available_topics.length > 0) {
      const topicChoices = currentDialogue.available_topics.map(topic => {
        // topic을 읽기 좋은 형식으로 변환
        const topicText = topic
          .replace(/[\[\]]/g, '')
          .replace(/_/g, ' ')
          .replace(/\b\w/g, (l) => l.toUpperCase());
        
        const actionId = `${currentDialogue.dialogue_id}_topic_${topic}`;
        
        return {
          action_id: actionId,
          action_type: 'dialogue' as const,
          text: topicText,
          target_id: currentDialogue.dialogue_id,
          description: `${topicText}에 대해 이야기한다.`,
        };
      });
      choiceList.push(...topicChoices);
    }
    
    // available_topics가 없을 때만 choices 사용 (하위 호환성)
    if (choiceList.length === 0 && currentDialogue.choices && currentDialogue.choices.length > 0) {
      const dialogueChoices = currentDialogue.choices.map(choice => ({
        action_id: choice.choice_id,
        action_type: 'dialogue' as const,
        text: choice.text,
        target_id: currentDialogue.dialogue_id,
        description: choice.text,
      }));
      choiceList.push(...dialogueChoices);
    }
    
    return choiceList;
  }, [currentDialogue]);

  // 선택지 클릭 핸들러
  const handleChoiceClick = (action: GameAction) => {
    if (action.action_type === 'dialogue' && onChoiceSelect) {
      onChoiceSelect(action.action_id);
    } else if (onActionSelect) {
      onActionSelect(action);
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 50 }}
        transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
        className="fixed bottom-0 left-0 z-30 flex items-end pb-20 px-6 pointer-events-none"
        style={{
          width: 'auto',
          maxWidth: '600px',
        }}
      >
        <div
          className="pointer-events-auto"
          data-dialogue-panel
          style={{
            width: '100%',
            maxWidth: '550px',
          }}
        >
          {/* 메시지 패널 */}
          <motion.div
            className="bg-white/95 backdrop-blur-md rounded-xl shadow-xl border border-white/60 relative"
            style={{
              padding: '1.25rem 1.75rem',
              height: `${panelHeight}px`,
              minHeight: '150px',
              maxHeight: '400px',
              overflowY: 'auto',
              scrollbarWidth: 'thin',
              scrollbarColor: 'rgba(0, 0, 0, 0.2) rgba(0, 0, 0, 0.05)',
            }}
          >
            {/* 크기 조정 핸들 */}
            <div
              onMouseDown={handleResizeStart}
              className="absolute top-0 left-0 right-0 h-2 cursor-ns-resize hover:bg-black/10 transition-colors rounded-t-xl flex items-center justify-center group"
              style={{
                zIndex: 10,
              }}
              title="드래그하여 크기 조정"
            >
              <div className="w-12 h-1 bg-gray-400/60 group-hover:bg-gray-500/80 rounded-full transition-colors" />
            </div>
            {/* 컨트롤 버튼 영역 (대화 중일 때만 표시) */}
            {currentDialogue && onClose && (
              <div className="absolute top-2 right-2 flex gap-2 z-10">
                {/* 대화로 돌아가기 버튼 (다른 오브젝트와 상호작용 중일 때) */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    // 대화 패널로 포커스 이동 (스크롤)
                    if (historyRef.current) {
                      historyRef.current.scrollTop = historyRef.current.scrollHeight;
                    }
                  }}
                  className="w-8 h-8 rounded-full bg-blue-500/80 hover:bg-blue-500 text-white text-xs flex items-center justify-center transition-colors"
                  aria-label="대화로 돌아가기"
                  title="대화로 돌아가기"
                >
                  💬
                </button>
                {/* 닫기 버튼 */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onClose();
                  }}
                  className="w-8 h-8 rounded-full bg-black/10 hover:bg-black/20 flex items-center justify-center transition-colors"
                  aria-label="대화 닫기"
                  title="대화 닫기 (ESC)"
                >
                  <span className="text-lg text-black/70">×</span>
                </button>
              </div>
            )}
            {/* NPC 포트레이트 (대화 중일 때만, 메시지 박스 내부 좌측) */}
            {npcPortrait && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="absolute left-4 top-4"
                style={{
                  width: '80px',
                  height: '100px',
                }}
              >
                {/* 포트레이트 이미지 영역 */}
                <div
                  className="w-full h-full rounded-lg bg-white/30 backdrop-blur-sm border border-white/40 shadow-md flex items-center justify-center"
                  style={{
                    background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.2) 100%)',
                  }}
                >
                  <span className="text-4xl">👤</span>
                </div>
                {/* NPC 이름 */}
                {npcName && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mt-1 text-center text-xs font-medium text-black/90"
                  >
                    {npcName}
                  </motion.div>
                )}
              </motion.div>
            )}
            
            {/* 메시지 내용 (포트레이트가 있으면 오른쪽으로 여백) */}
            <div style={{ marginLeft: npcPortrait ? '100px' : '0', display: 'flex', flexDirection: 'column', height: '100%' }}>
              {/* 대화 중일 때: 대화 히스토리만 표시 (중복 방지) */}
              {currentDialogue && currentDialogue.messages.length > 0 ? (
                <div
                  ref={historyRef}
                  className="space-y-2 flex-1 overflow-y-auto"
                  style={{
                    maxHeight: choices.length > 0 ? '120px' : '180px', // 선택지가 있으면 히스토리 영역 축소
                    minHeight: '60px',
                    scrollbarWidth: 'thin',
                    scrollbarColor: 'rgba(0, 0, 0, 0.2) rgba(0, 0, 0, 0.05)',
                  }}
                >
                  {currentDialogue.messages.map((message, index) => (
                    <motion.div
                      key={message.message_id || index}
                      className="text-base leading-relaxed text-black/95"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                    >
                      {message.character_name && (
                        <span className="font-semibold text-black/90 mr-2">
                          {message.character_name}:
                        </span>
                      )}
                      <span>{message.text}</span>
                    </motion.div>
                  ))}
                </div>
              ) : (
                /* 대화 중이 아닐 때: 현재 메시지 표시 (내레이션/일반 메시지) */
                currentMessage && (
                  <motion.div
                    className={`text-base leading-relaxed flex-1 ${
                      currentMessage.message_type === 'narration' ? 'italic text-black/80' : 'text-black/95'
                    }`}
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
                )
              )}
            </div>

            {/* 선택지 버튼 영역 - 항상 하단에 고정 (sticky) */}
            {choices.length > 0 && (
              <motion.div
                className="mt-4 space-y-2 flex-shrink-0"
                style={{ 
                  marginLeft: npcPortrait ? '100px' : '0',
                  position: 'sticky',
                  bottom: 0,
                  background: 'rgba(255, 255, 255, 0.95)',
                  paddingTop: '8px',
                  marginTop: '8px',
                  borderTop: '1px solid rgba(0, 0, 0, 0.1)',
                }}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.2 }}
              >
                <div 
                  className="space-y-2"
                  style={{
                    maxHeight: '120px',
                    overflowY: 'auto',
                    scrollbarWidth: 'thin',
                    scrollbarColor: 'rgba(0, 0, 0, 0.2) rgba(0, 0, 0, 0.05)',
                  }}
                >
                  {choices.length > 10 ? (
                    // 큰 리스트는 가상화 사용
                    <div style={{ height: Math.min(300, choices.length * 56) }}>
                      <FixedSizeList
                        height={Math.min(300, choices.length * 56)}
                        itemCount={choices.length}
                        itemSize={56}
                        width="100%"
                      >
                        {({ index, style }) => {
                          const choice = choices[index];
                          return (
                            <div style={style} className="px-2">
                              <motion.button
                                onClick={() => handleChoiceClick(choice)}
                                className="w-full px-4 py-3 rounded-lg text-left text-sm font-light transition-all"
                                style={{
                                  background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.25) 100%)',
                                  border: '1px solid rgba(0, 0, 0, 0.12)',
                                  color: 'rgba(0, 0, 0, 0.95)',
                                  backdropFilter: 'blur(15px)',
                                  WebkitBackdropFilter: 'blur(15px)',
                                  boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)',
                                }}
                                whileHover={{
                                  scale: 1.02,
                                  background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.35) 100%)',
                                  boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
                                  borderColor: 'rgba(0, 0, 0, 0.2)',
                                }}
                                whileTap={{ scale: 0.98 }}
                              >
                                {choice.text}
                              </motion.button>
                            </div>
                          );
                        }}
                      </FixedSizeList>
                    </div>
                  ) : (
                    // 작은 리스트는 일반 렌더링
                    choices.map((choice, index) => (
                      <motion.button
                        key={choice.action_id}
                        onClick={() => handleChoiceClick(choice)}
                        className="w-full px-4 py-3 rounded-lg text-left text-sm font-light transition-all"
                        style={{
                          background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.25) 100%)',
                          border: '1px solid rgba(0, 0, 0, 0.12)',
                          color: 'rgba(0, 0, 0, 0.95)',
                          backdropFilter: 'blur(15px)',
                          WebkitBackdropFilter: 'blur(15px)',
                          boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)',
                        }}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.05 }}
                        whileHover={{
                          scale: 1.02,
                          background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.35) 100%)',
                          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
                          borderColor: 'rgba(0, 0, 0, 0.2)',
                        }}
                        whileTap={{ scale: 0.98 }}
                      >
                        {choice.text}
                      </motion.button>
                    ))
                  )}
                </div>
              </motion.div>
            )}

            {/* 클릭 진행 표시 */}
            {!isTyping && (currentMessage || currentDialogue) && choices.length === 0 && (
              <motion.div
                className="text-center mt-4 text-black/50 text-sm"
                style={{ marginLeft: npcPortrait ? '100px' : '0' }}
                initial={{ opacity: 0 }}
                animate={{ opacity: [0.5, 0.7, 0.5] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                ▼ 클릭하여 진행
              </motion.div>
            )}
          </motion.div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export const DialogueMessagePanel = React.memo(DialogueMessagePanelComponent);

