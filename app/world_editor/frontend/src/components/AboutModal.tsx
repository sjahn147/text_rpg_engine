/**
 * About 모달 컴포넌트
 */
import React from 'react';
import { Modal } from './ui/Modal';

interface AboutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AboutModal: React.FC<AboutModalProps> = ({
  isOpen,
  onClose,
}) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="About World Editor" width="500px" height="400px">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '20px' }}>
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ margin: '0 0 8px 0', fontSize: '24px', fontWeight: 'bold' }}>
            World Editor
          </h2>
          <p style={{ margin: 0, fontSize: '16px', color: '#666' }}>
            v1.0.0
          </p>
        </div>
        
        <div style={{ borderTop: '1px solid #ddd', paddingTop: '16px' }}>
          <p style={{ margin: '0 0 12px 0', fontSize: '14px', lineHeight: '1.6' }}>
            전문 게임 개발 도구 수준의 월드 에디터입니다.
          </p>
          <p style={{ margin: '0 0 12px 0', fontSize: '14px', lineHeight: '1.6' }}>
            D&D 스타일의 RPG 게임을 위한 월드, 지역, 위치, 셀, 인물, 오브젝트 등을
            시각적으로 편집하고 관리할 수 있습니다.
          </p>
        </div>

        <div style={{ borderTop: '1px solid #ddd', paddingTop: '16px' }}>
          <h3 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: 'bold' }}>
            주요 기능
          </h3>
          <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', lineHeight: '1.8', color: '#666' }}>
            <li>계층적 맵 구조 (World → Region → Location → Cell)</li>
            <li>핀 기반 지도 편집</li>
            <li>도로 연결 및 경로 관리</li>
            <li>엔티티 (인물, 오브젝트, 아이템) 관리</li>
            <li>대화 시스템 및 행동 스케줄</li>
            <li>실시간 동기화 (WebSocket)</li>
            <li>프로젝트 저장/로드</li>
            <li>데이터 가져오기/내보내기</li>
          </ul>
        </div>

        <div style={{ borderTop: '1px solid #ddd', paddingTop: '16px', textAlign: 'center' }}>
          <p style={{ margin: 0, fontSize: '12px', color: '#999' }}>
            © 2024 RPG Engine Project
          </p>
        </div>
      </div>
    </Modal>
  );
};

