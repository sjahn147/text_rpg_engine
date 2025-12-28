/**
 * 저널 화면 - 이벤트 기록, 퀘스트, 검색, 필터
 */
import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';

interface JournalScreenProps {
  onClose: () => void;
}

type TabType = 'all' | 'events' | 'dialogues' | 'discoveries' | 'quests';

interface JournalEntry {
  id: string;
  type: 'event' | 'dialogue' | 'discovery' | 'quest' | 'action';
  timestamp: string;
  content: string;
  characterName?: string;
  location?: string;
  tags?: string[];
}

export const JournalScreen: React.FC<JournalScreenProps> = ({ onClose }) => {
  const { history, gameState } = useGameStore();
  const [activeTab, setActiveTab] = useState<TabType>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEntry, setSelectedEntry] = useState<JournalEntry | null>(null);

  // 히스토리를 저널 엔트리로 변환
  const journalEntries: JournalEntry[] = useMemo(() => {
    return history.map((entry, index) => {
      // 엔트리 타입 추론
      let entryType: JournalEntry['type'] = 'action';
      if (entry.characterName && entry.characterName !== '플레이어') {
        entryType = 'dialogue';
      } else if (entry.text.includes('발견') || entry.text.includes('획득')) {
        entryType = 'discovery';
      } else if (entry.text.includes('퀘스트') || entry.text.includes('목표')) {
        entryType = 'quest';
      } else if (entry.text.includes('이벤트') || entry.text.includes('발생')) {
        entryType = 'event';
      }

      return {
        id: `entry-${index}`,
        type: entryType,
        timestamp: new Date().toLocaleString('ko-KR'), // 실제로는 entry에서 timestamp를 가져와야 함
        content: entry.text,
        characterName: entry.characterName,
        location: gameState?.current_location,
        tags: [],
      };
    }).reverse(); // 최신 항목이 먼저 표시되도록
  }, [history, gameState]);

  // 필터링된 엔트리
  const filteredEntries = useMemo(() => {
    let filtered = journalEntries;

    // 탭 필터
    if (activeTab !== 'all') {
      const typeMap: Record<TabType, JournalEntry['type'][]> = {
        all: [],
        events: ['event'],
        dialogues: ['dialogue'],
        discoveries: ['discovery'],
        quests: ['quest'],
      };
      filtered = filtered.filter(entry => typeMap[activeTab].includes(entry.type));
    }

    // 검색 필터
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(entry =>
        entry.content.toLowerCase().includes(query) ||
        (entry.characterName && entry.characterName.toLowerCase().includes(query)) ||
        (entry.location && entry.location.toLowerCase().includes(query))
      );
    }

    return filtered;
  }, [journalEntries, activeTab, searchQuery]);

  const getTypeLabel = (type: JournalEntry['type']) => {
    const labels: Record<JournalEntry['type'], string> = {
      event: '이벤트',
      dialogue: '대화',
      discovery: '발견',
      quest: '퀘스트',
      action: '행동',
    };
    return labels[type];
  };

  const getTypeColor = (type: JournalEntry['type']) => {
    const colors: Record<JournalEntry['type'], string> = {
      event: 'bg-purple-100 text-purple-800',
      dialogue: 'bg-blue-100 text-blue-800',
      discovery: 'bg-green-100 text-green-800',
      quest: 'bg-yellow-100 text-yellow-800',
      action: 'bg-gray-100 text-gray-800',
    };
    return colors[type];
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
          className="bg-white p-8 rounded-lg shadow-xl w-full max-w-4xl max-h-[85vh] flex flex-col"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 50, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* 헤더 */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-light text-black/90">저널</h2>
            <button
              onClick={onClose}
              className="text-black/60 hover:text-black/90 transition-colors text-2xl"
            >
              ✕
            </button>
          </div>

          {/* 검색 및 탭 */}
          <div className="mb-6">
            {/* 검색 */}
            <div className="mb-4">
              <input
                type="text"
                placeholder="저널 검색..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-black/10 rounded focus:outline-none focus:border-black/30 text-black/80"
              />
            </div>

            {/* 탭 */}
            <div className="flex gap-2 flex-wrap">
              {(['all', 'events', 'dialogues', 'discoveries', 'quests'] as TabType[]).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 text-sm font-light transition-colors rounded ${
                    activeTab === tab
                      ? 'bg-black/10 text-black/90'
                      : 'text-black/60 hover:text-black/80 hover:bg-black/5'
                  }`}
                >
                  {tab === 'all' ? '전체' :
                   tab === 'events' ? '이벤트' :
                   tab === 'dialogues' ? '대화' :
                   tab === 'discoveries' ? '발견' : '퀘스트'}
                  <span className="ml-1 text-xs text-black/40">
                    ({tab === 'all' 
                      ? journalEntries.length 
                      : journalEntries.filter(e => {
                          if (tab === 'events') return e.type === 'event';
                          if (tab === 'dialogues') return e.type === 'dialogue';
                          if (tab === 'discoveries') return e.type === 'discovery';
                          if (tab === 'quests') return e.type === 'quest';
                          return false;
                        }).length
                    })
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* 컨텐츠 영역 */}
          <div className="flex-1 flex gap-6 overflow-hidden">
            {/* 엔트리 목록 */}
            <div className="flex-1 overflow-y-auto space-y-3 pr-2">
              {filteredEntries.length === 0 ? (
                <div className="text-black/60 text-center py-8">
                  {searchQuery ? '검색 결과가 없습니다.' : '저널 항목이 없습니다.'}
                </div>
              ) : (
                filteredEntries.map((entry) => (
                  <div
                    key={entry.id}
                    className={`p-4 border rounded cursor-pointer transition-colors ${
                      selectedEntry?.id === entry.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-black/10 hover:bg-black/5'
                    }`}
                    onClick={() => setSelectedEntry(entry)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <span className={`text-xs px-2 py-1 rounded ${getTypeColor(entry.type)}`}>
                        {getTypeLabel(entry.type)}
                      </span>
                      <span className="text-xs text-black/40">{entry.timestamp}</span>
                    </div>
                    <div className="text-sm text-black/80 line-clamp-2">
                      {entry.characterName && (
                        <span className="font-medium mr-1">{entry.characterName}:</span>
                      )}
                      {entry.content}
                    </div>
                    {entry.location && (
                      <div className="mt-1 text-xs text-black/40">
                        {entry.location}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            {/* 상세 보기 */}
            {selectedEntry && (
              <motion.div
                className="w-80 border-l border-black/10 pl-6 overflow-y-auto"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <h3 className="text-lg font-light text-black/90 mb-4">상세 정보</h3>
                
                <div className="space-y-4">
                  <div>
                    <div className="text-xs text-black/40 mb-1">유형</div>
                    <span className={`text-xs px-2 py-1 rounded ${getTypeColor(selectedEntry.type)}`}>
                      {getTypeLabel(selectedEntry.type)}
                    </span>
                  </div>
                  
                  <div>
                    <div className="text-xs text-black/40 mb-1">시간</div>
                    <div className="text-sm text-black/70">{selectedEntry.timestamp}</div>
                  </div>
                  
                  {selectedEntry.characterName && (
                    <div>
                      <div className="text-xs text-black/40 mb-1">인물</div>
                      <div className="text-sm text-black/70">{selectedEntry.characterName}</div>
                    </div>
                  )}
                  
                  {selectedEntry.location && (
                    <div>
                      <div className="text-xs text-black/40 mb-1">장소</div>
                      <div className="text-sm text-black/70">{selectedEntry.location}</div>
                    </div>
                  )}
                  
                  <div>
                    <div className="text-xs text-black/40 mb-1">내용</div>
                    <div className="text-sm text-black/80 whitespace-pre-wrap">
                      {selectedEntry.content}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
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

