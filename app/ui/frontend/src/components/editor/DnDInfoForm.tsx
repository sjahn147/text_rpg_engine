/**
 * D&D 스타일 정보 입력 폼 컴포넌트
 */
import React, { useState, useEffect } from 'react';
import { DnDLocationInfo } from '../../types';

interface DnDInfoFormProps {
  gameDataId: string;
  pinType: 'region' | 'location' | 'cell';
  initialData?: DnDLocationInfo;
  onSave: (data: DnDLocationInfo) => void;
  onCancel: () => void;
}

export const DnDInfoForm: React.FC<DnDInfoFormProps> = ({
  gameDataId,
  pinType,
  initialData,
  onSave,
  onCancel,
}) => {
  const [formData, setFormData] = useState<DnDLocationInfo>(initialData || {
    name: '',
    description: '',
    type: '',
    demographics: {
      population: 0,
      races: {},
      classes: {},
    },
    economy: {
      primary_industry: '',
      trade_goods: [],
      gold_value: 0,
    },
    government: {
      type: '',
      leader: '',
      laws: [],
    },
    culture: {
      religion: [],
      customs: [],
      festivals: [],
    },
    lore: {
      history: '',
      legends: [],
      secrets: [],
    },
    npcs: [],
    quests: [],
    shops: [],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} style={{ padding: '20px' }}>
      <h3>D&D 스타일 정보 입력</h3>
      
      {/* 기본 정보 */}
      <section style={{ marginBottom: '20px' }}>
        <h4>기본 정보</h4>
        <label>
          이름:
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </label>
        <label style={{ display: 'block', marginTop: '10px' }}>
          설명:
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={4}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </label>
        <label style={{ display: 'block', marginTop: '10px' }}>
          타입:
          <input
            type="text"
            value={formData.type}
            onChange={(e) => setFormData({ ...formData, type: e.target.value })}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </label>
      </section>

      {/* 인구 통계 */}
      <section style={{ marginBottom: '20px' }}>
        <h4>인구 통계</h4>
        <label>
          총 인구:
          <input
            type="number"
            value={formData.demographics.population}
            onChange={(e) => setFormData({
              ...formData,
              demographics: {
                ...formData.demographics,
                population: parseInt(e.target.value) || 0,
              },
            })}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </label>
      </section>

      {/* 경제 */}
      <section style={{ marginBottom: '20px' }}>
        <h4>경제</h4>
        <label>
          주요 산업:
          <input
            type="text"
            value={formData.economy.primary_industry}
            onChange={(e) => setFormData({
              ...formData,
              economy: {
                ...formData.economy,
                primary_industry: e.target.value,
              },
            })}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </label>
        <label style={{ display: 'block', marginTop: '10px' }}>
          거래 상품 (쉼표로 구분):
          <input
            type="text"
            value={formData.economy.trade_goods.join(', ')}
            onChange={(e) => setFormData({
              ...formData,
              economy: {
                ...formData.economy,
                trade_goods: e.target.value.split(',').map(s => s.trim()).filter(s => s),
              },
            })}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </label>
      </section>

      {/* 정부 */}
      <section style={{ marginBottom: '20px' }}>
        <h4>정부</h4>
        <label>
          정부 형태:
          <select
            value={formData.government.type}
            onChange={(e) => setFormData({
              ...formData,
              government: {
                ...formData.government,
                type: e.target.value,
              },
            })}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          >
            <option value="">선택하세요</option>
            <option value="democracy">민주주의</option>
            <option value="monarchy">군주제</option>
            <option value="theocracy">신정정치</option>
            <option value="oligarchy">과두정치</option>
          </select>
        </label>
        <label style={{ display: 'block', marginTop: '10px' }}>
          지도자:
          <input
            type="text"
            value={formData.government.leader}
            onChange={(e) => setFormData({
              ...formData,
              government: {
                ...formData.government,
                leader: e.target.value,
              },
            })}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </label>
      </section>

      {/* 로어 */}
      <section style={{ marginBottom: '20px' }}>
        <h4>로어</h4>
        <label>
          역사:
          <textarea
            value={formData.lore.history}
            onChange={(e) => setFormData({
              ...formData,
              lore: {
                ...formData.lore,
                history: e.target.value,
              },
            })}
            rows={6}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </label>
        <label style={{ display: 'block', marginTop: '10px' }}>
          전설 (쉼표로 구분):
          <input
            type="text"
            value={formData.lore.legends.join(', ')}
            onChange={(e) => setFormData({
              ...formData,
              lore: {
                ...formData.lore,
                legends: e.target.value.split(',').map(s => s.trim()).filter(s => s),
              },
            })}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </label>
      </section>

      <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
        <button
          type="submit"
          style={{
            padding: '10px 20px',
            backgroundColor: '#4ECDC4',
            color: 'white',
            border: 'none',
            cursor: 'pointer',
          }}
        >
          저장
        </button>
        <button
          type="button"
          onClick={onCancel}
          style={{
            padding: '10px 20px',
            backgroundColor: '#ccc',
            color: 'white',
            border: 'none',
            cursor: 'pointer',
          }}
        >
          취소
        </button>
      </div>
    </form>
  );
};

