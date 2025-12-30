/**
 * 캐릭터 정보 화면 - 스탯, HP/MP, 장비
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';
import { gameApi } from '../../services/gameApi';

interface CharacterScreenProps {
  onClose: () => void;
}

interface CharacterStats {
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
}

interface EquippedItem {
  slot: string;
  item_id: string;
  name: string;
}

interface ActiveEffect {
  effect_id: string;
  name: string;
  description?: string;
  duration?: number;
}

interface CharacterInfo {
  name: string;
  entity_type: string;
  level: number;
  occupation: string;
  stats: CharacterStats;
  current_hp: number;
  max_hp: number;
  current_mp: number;
  max_mp: number;
  equipped_items: EquippedItem[];
  active_effects: ActiveEffect[];
}

export const CharacterScreen: React.FC<CharacterScreenProps> = ({ onClose }) => {
  const { gameState } = useGameStore();
  const [character, setCharacter] = useState<CharacterInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (gameState?.session_id) {
      loadCharacterInfo();
    }
  }, [gameState?.session_id]);

  const loadCharacterInfo = async () => {
    if (!gameState?.session_id) return;
    
    try {
      setLoading(true);
      setError(null);
      const response = await gameApi.getPlayerCharacter(gameState.session_id);
      
      if (response.success && response.character) {
        setCharacter(response.character);
      } else {
        setError('캐릭터 정보를 불러올 수 없습니다.');
      }
    } catch (err) {
      console.error('캐릭터 정보 로드 실패:', err);
      setError('캐릭터 정보를 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  const getHpColor = (current: number, max: number) => {
    const ratio = current / max;
    if (ratio > 0.6) return 'bg-green-500';
    if (ratio > 0.3) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getMpColor = () => 'bg-blue-500';

  const getStatLabel = (stat: string) => {
    const labels: { [key: string]: string } = {
      strength: '힘',
      dexterity: '민첩',
      constitution: '체력',
      intelligence: '지능',
      wisdom: '지혜',
      charisma: '매력',
    };
    return labels[stat] || stat;
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
          className="bg-white p-8 rounded-lg shadow-xl w-full max-w-lg max-h-[80vh] overflow-y-auto"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 50, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* 헤더 */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-light text-black/90">캐릭터 정보</h2>
            <button
              onClick={onClose}
              className="text-black/60 hover:text-black/90 transition-colors text-2xl"
            >
              ✕
            </button>
          </div>

          {/* 에러 메시지 */}
          {error && (
            <div className="mb-4 p-3 bg-red-100 text-red-800 rounded text-sm">
              {error}
            </div>
          )}

          {/* 로딩 */}
          {loading && (
            <div className="text-center py-8 text-black/60">로딩 중...</div>
          )}

          {/* 캐릭터 정보 */}
          {!loading && character && (
            <div className="space-y-6">
              {/* 기본 정보 */}
              <div className="text-center">
                <h3 className="text-xl font-medium text-black/90">{character.name}</h3>
                <p className="text-sm text-black/60">
                  Lv.{character.level} {character.occupation || character.entity_type}
                </p>
              </div>

              {/* HP/MP 바 */}
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-black/70">HP</span>
                    <span className="text-black/60">{character.current_hp} / {character.max_hp}</span>
                  </div>
                  <div className="h-3 bg-black/10 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getHpColor(character.current_hp, character.max_hp)} transition-all`}
                      style={{ width: `${(character.current_hp / character.max_hp) * 100}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-black/70">MP</span>
                    <span className="text-black/60">{character.current_mp} / {character.max_mp}</span>
                  </div>
                  <div className="h-3 bg-black/10 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getMpColor()} transition-all`}
                      style={{ width: `${(character.current_mp / character.max_mp) * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* 능력치 */}
              <div>
                <h4 className="text-lg font-light text-black/90 mb-3">능력치</h4>
                <div className="grid grid-cols-3 gap-3">
                  {Object.entries(character.stats).map(([stat, value]) => (
                    <div
                      key={stat}
                      className="p-3 bg-black/5 rounded text-center"
                    >
                      <div className="text-xs text-black/60 mb-1">{getStatLabel(stat)}</div>
                      <div className="text-lg font-medium text-black/90">{value}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 장착 장비 */}
              <div>
                <h4 className="text-lg font-light text-black/90 mb-3">장착 장비</h4>
                {character.equipped_items.length > 0 ? (
                  <div className="space-y-2">
                    {character.equipped_items.map((item) => (
                      <div
                        key={item.slot}
                        className="p-3 bg-black/5 rounded flex justify-between items-center"
                      >
                        <span className="text-xs text-black/60">{item.slot}</span>
                        <span className="text-sm text-black/80">{item.name}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-sm text-black/60 text-center py-4">
                    장착된 장비가 없습니다.
                  </div>
                )}
              </div>

              {/* 활성 효과 */}
              <div>
                <h4 className="text-lg font-light text-black/90 mb-3">활성 효과</h4>
                {character.active_effects.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {character.active_effects.map((effect, index) => (
                      <div
                        key={effect.effect_id || index}
                        className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm"
                        title={effect.description}
                      >
                        {effect.name}
                        {effect.duration && (
                          <span className="ml-1 text-xs text-purple-600">
                            ({effect.duration}턴)
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-sm text-black/60 text-center py-4">
                    활성화된 효과가 없습니다.
                  </div>
                )}
              </div>
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};


