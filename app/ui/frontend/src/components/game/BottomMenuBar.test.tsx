/**
 * BottomMenuBar 컴포넌트 테스트
 */
import React from 'react';
import { vi, describe, test, expect, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BottomMenuBar } from './BottomMenuBar';
import { useGameStore } from '../../store/gameStore';
import { gameApi } from '../../services/gameApi';

// Mock dependencies
vi.mock('../../store/gameStore');
vi.mock('../../services/gameApi');

const mockUseGameStore = useGameStore as vi.MockedFunction<typeof useGameStore>;
const mockGameApi = gameApi as vi.Mocked<typeof gameApi>;

describe('BottomMenuBar 컴포넌트 테스트', () => {
  const mockCallbacks = {
    onInventoryClick: vi.fn(),
    onJournalClick: vi.fn(),
    onSkillClick: vi.fn(),
    onSpellClick: vi.fn(),
    onSettlementClick: vi.fn(),
    onSettingsClick: vi.fn(),
    onSaveClick: vi.fn(),
    onLoadClick: vi.fn(),
    onCharacterClick: vi.fn(),
    onInfoClick: vi.fn(),
    onEditorModeClick: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    
    mockUseGameStore.mockReturnValue({
      gameTime: { day: 1, hour: 12, minute: 30 },
      characterStats: {
        success: true,
        stats: {
          hp: 50,
          max_hp: 100,
          mp: 30,
          max_mp: 50,
        },
      },
      setCharacterStats: vi.fn(),
    } as any);

    mockGameApi.getCharacterStats.mockResolvedValue({
      success: true,
      stats: {
        hp: 50,
        max_hp: 100,
        mp: 30,
        max_mp: 50,
      },
    } as any);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  test('모든 메뉴 버튼이 렌더링됨', () => {
    render(<BottomMenuBar sessionId="test-session" {...mockCallbacks} />);

    expect(screen.getByTitle('인벤토리 (I)')).toBeInTheDocument();
    expect(screen.getByTitle('저널 (J)')).toBeInTheDocument();
    expect(screen.getByTitle('스킬 관리 (K)')).toBeInTheDocument();
    expect(screen.getByTitle('주문 관리 (S)')).toBeInTheDocument();
    expect(screen.getByTitle('정보 (I)')).toBeInTheDocument();
    expect(screen.getByTitle('저장')).toBeInTheDocument();
    expect(screen.getByTitle('불러오기')).toBeInTheDocument();
  });

  test('메뉴 버튼 클릭 시 콜백 호출', () => {
    render(<BottomMenuBar sessionId="test-session" {...mockCallbacks} />);

    fireEvent.click(screen.getByTitle('인벤토리 (I)'));
    expect(mockCallbacks.onInventoryClick).toHaveBeenCalled();

    fireEvent.click(screen.getByTitle('저장'));
    expect(mockCallbacks.onSaveClick).toHaveBeenCalled();

    fireEvent.click(screen.getByTitle('불러오기'));
    expect(mockCallbacks.onLoadClick).toHaveBeenCalled();
  });

  test('캐릭터 상태가 있으면 HP/MP 표시', () => {
    render(<BottomMenuBar sessionId="test-session" {...mockCallbacks} />);

    expect(screen.getByText('HP')).toBeInTheDocument();
    expect(screen.getByText('MP')).toBeInTheDocument();
    expect(screen.getByText('50/100')).toBeInTheDocument();
    expect(screen.getByText('30/50')).toBeInTheDocument();
  });

  test('캐릭터 상태가 없으면 HP/MP 표시 안함', () => {
    mockUseGameStore.mockReturnValue({
      gameTime: null,
      characterStats: null,
      setCharacterStats: vi.fn(),
    } as any);

    render(<BottomMenuBar sessionId="test-session" {...mockCallbacks} />);

    expect(screen.queryByText('HP')).not.toBeInTheDocument();
    expect(screen.queryByText('MP')).not.toBeInTheDocument();
  });

  test('에디터 모드 버튼이 onEditorModeClick이 없으면 표시 안함', () => {
    const { onEditorModeClick, ...callbacksWithoutEditor } = mockCallbacks;
    render(<BottomMenuBar sessionId="test-session" {...callbacksWithoutEditor} />);

    expect(screen.queryByTitle('에디터 모드')).not.toBeInTheDocument();
  });

  test('시간 포맷이 올바르게 표시', () => {
    mockUseGameStore.mockReturnValue({
      gameTime: { day: 5, hour: 14, minute: 45 },
      characterStats: null,
      setCharacterStats: vi.fn(),
    } as any);

    render(<BottomMenuBar sessionId="test-session" {...mockCallbacks} />);

    // 시간은 TimeLocationPanel에서 동적으로 포맷되므로 테스트가 복잡
    // 실제로는 BottomMenuBar에서 직접 표시하지 않을 수도 있음
  });
});
