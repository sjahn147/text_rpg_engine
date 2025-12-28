/**
 * 단축키 가이드 모달 컴포넌트
 */
import React from 'react';
import { Modal } from './ui/Modal';

interface KeyboardShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const KeyboardShortcutsModal: React.FC<KeyboardShortcutsModalProps> = ({
  isOpen,
  onClose,
}) => {
  const shortcuts = [
    { category: '파일', items: [
      { key: 'Ctrl+N', description: '새 프로젝트' },
      { key: 'Ctrl+O', description: '프로젝트 열기' },
      { key: 'Ctrl+S', description: '프로젝트 저장' },
      { key: 'Ctrl+Shift+S', description: '다른 이름으로 저장' },
    ]},
    { category: '편집', items: [
      { key: 'Ctrl+Z', description: '실행 취소' },
      { key: 'Ctrl+Y', description: '다시 실행' },
      { key: 'Ctrl+X', description: '잘라내기' },
      { key: 'Ctrl+C', description: '복사' },
      { key: 'Ctrl+V', description: '붙여넣기' },
      { key: 'Ctrl+D', description: '복제' },
      { key: 'Del', description: '삭제' },
      { key: 'Ctrl+A', description: '전체 선택' },
      { key: 'Ctrl+Shift+A', description: '선택 해제' },
      { key: 'Ctrl+F', description: '찾기' },
      { key: 'Ctrl+Shift+F', description: '파일에서 찾기' },
      { key: 'Ctrl+H', description: '바꾸기' },
    ]},
    { category: '보기', items: [
      { key: 'Ctrl+Shift+E', description: '탐색기 패널 토글' },
      { key: 'Ctrl+Shift+P', description: '속성 패널 토글' },
      { key: 'Ctrl+1', description: '맵 뷰' },
      { key: 'Ctrl+2', description: '리스트 뷰' },
      { key: 'Ctrl+3', description: '트리 뷰' },
    ]},
    { category: '줌', items: [
      { key: 'Ctrl++', description: '확대' },
      { key: 'Ctrl+-', description: '축소' },
      { key: 'Ctrl+0', description: '맞춤' },
    ]},
    { category: '기타', items: [
      { key: 'F11', description: '전체 화면' },
      { key: 'F1', description: '도움말' },
      { key: 'Ctrl+,', description: '설정' },
    ]},
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="키보드 단축키" width="500px" height="70vh">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxHeight: 'calc(70vh - 100px)', overflowY: 'auto' }}>
        {shortcuts.map((category) => (
          <div key={category.category}>
            <h3 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: 'bold', color: '#333' }}>
              {category.category}
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {category.items.map((item, index) => (
                <div
                  key={index}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '6px 8px',
                    backgroundColor: '#f9f9f9',
                    borderRadius: '4px',
                  }}
                >
                  <span style={{ fontSize: '12px', color: '#666' }}>{item.description}</span>
                  <kbd style={{
                    fontSize: '11px',
                    padding: '4px 8px',
                    backgroundColor: '#fff',
                    border: '1px solid #ddd',
                    borderRadius: '3px',
                    fontFamily: 'monospace',
                    color: '#333',
                  }}>
                    {item.key}
                  </kbd>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </Modal>
  );
};

