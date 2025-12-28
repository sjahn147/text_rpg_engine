/**
 * 캐릭터 오버레이 패널 - 게임 중 간략한 캐릭터 정보 확인
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';
import { gameApi } from '../../services/gameApi';

interface CharacterPanelProps {
  isOpen: boolean;
  onClose: () => void;
  position?: 'left' | 'right';
}

interface CharacterData {
  player_id: string;
  name: string;
  entity_type: string;
  current_stats: {
    hp?: number;
    max_hp?: number;
    mp?: number;
    max_mp?: number;
    strength?: number;
    dexterity?: number;
    intelligence?: number;
    constitution?: number;
    [key: string]: number | undefined;
  };
  equipped_items: Array<{
    slot: string;
    item_id: string;
    item_name: string;
  }>;
  active_effects: Array<{
    effect_id: string;
    name: string;
    remaining_duration?: number;
  }>;
}

export const CharacterPanel: React.FC<CharacterPanelProps> = ({
  isOpen,
  onClose,
  position = 'left',
}) => {
  const { gameState } = useGameStore();
  const [character, setCharacter] = useState<CharacterData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && gameState?.session_id) {
      loadCharacter();
    }
  }, [isOpen, gameState?.session_id]);

  const loadCharacter = async () => {
    if (!gameState?.session_id) return;
    
    setLoading(true);
    try {
      const data = await gameApi.getPlayerCharacter(gameState.session_id);
      setCharacter(data);
    } catch (error) {
      console.error('캐릭터 정보 로드 실패:', error);
      setCharacter(null);
    } finally {
      setLoading(false);
    }
  };

  const panelPosition = position === 'left' 
    ? { left: 0 }
    : { right: 0 };

  const slideDirection = position === 'left' ? -300 : 300;

  const getStatLabel = (stat: string) => {
    const labels: Record<string, string> = {
      strength: '힘',
      dexterity: '민첩',
      intelligence: '지능',
      constitution: '체력',
      wisdom: '지혜',
      charisma: '매력',
    };
    return labels[stat] || stat;
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
          
          {/* 패널 */}
          <motion.div
            className="fixed top-0 bottom-0 z-50 w-80 bg-white shadow-xl flex flex-col"
            style={panelPosition}
            initial={{ x: slideDirection, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: slideDirection, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          >
            {/* 헤더 */}
            <div className="p-4 border-b border-black/10 flex items-center justify-between">
              <h3 className="text-lg font-light text-black/90">캐릭터</h3>
              <button
                onClick={onClose}
                className="text-black/60 hover:text-black/90 transition-colors"
              >
                ✕
              </button>
            </div>

            {/* 컨텐츠 */}
            <div className="flex-1 overflow-y-auto p-4">
              {loading ? (
                <div className="text-center text-black/60 py-8">
                  로딩 중...
                </div>
              ) : !character ? (
                <div className="text-center text-black/60 py-8">
                  캐릭터 정보를 불러올 수 없습니다.
                </div>
              ) : (
                <div className="space-y-6">
                  {/* 이름 */}
                  <div>
                    <h4 className="text-xl font-medium text-black/90">
                      {character.name}
                    </h4>
                    <p className="text-sm text-black/60">{character.entity_type}</p>
                  </div>

                  {/* HP/MP */}
                  <div className="space-y-3">
                    {character.current_stats.max_hp && (
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-black/70">HP</span>
                          <span className="text-black/80">
                            {character.current_stats.hp || 0} / {character.current_stats.max_hp}
                          </span>
                        </div>
                        <div className="h-2 bg-black/10 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-red-500 transition-all"
                            style={{
                              width: `${((character.current_stats.hp || 0) / character.current_stats.max_hp) * 100}%`
                            }}
                          />
                        </div>
                      </div>
                    )}
                    {character.current_stats.max_mp && (
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-black/70">MP</span>
                          <span className="text-black/80">
                            {character.current_stats.mp || 0} / {character.current_stats.max_mp}
                          </span>
                        </div>
                        <div className="h-2 bg-black/10 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500 transition-all"
                            style={{
                              width: `${((character.current_stats.mp || 0) / character.current_stats.max_mp) * 100}%`
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </div>

                  {/* 스탯 */}
                  <div>
                    <h5 className="text-sm font-medium text-black/80 mb-2">능력치</h5>
                    <div className="grid grid-cols-2 gap-2">
                      {['strength', 'dexterity', 'intelligence', 'constitution'].map((stat) => {
                        const value = character.current_stats[stat];
                        if (value === undefined) return null;
                        return (
                          <div key={stat} className="flex justify-between text-sm p-2 bg-black/5 rounded">
                            <span className="text-black/60">{getStatLabel(stat)}</span>
                            <span className="text-black/80 font-medium">{value}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* 장비 */}
                  {character.equipped_items.length > 0 && (
                    <div>
                      <h5 className="text-sm font-medium text-black/80 mb-2">장착 장비</h5>
                      <div className="space-y-1">
                        {character.equipped_items.map((item, index) => (
                          <div key={index} className="flex justify-between text-sm p-2 bg-black/5 rounded">
                            <span className="text-black/50">{item.slot}</span>
                            <span className="text-black/80">{item.item_name}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 활성 효과 */}
                  {character.active_effects.length > 0 && (
                    <div>
                      <h5 className="text-sm font-medium text-black/80 mb-2">활성 효과</h5>
                      <div className="flex flex-wrap gap-2">
                        {character.active_effects.map((effect, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-emerald-100 text-emerald-800 text-xs rounded"
                          >
                            {effect.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

