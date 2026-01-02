/**
 * 상호작용 가능한 오브젝트/엔티티 레이어 컴포넌트
 * Call of Cthulhu 스타일: 화면에 오브젝트와 엔티티를 표시하고 클릭 가능하게 만듦
 */
import React from 'react';
import { motion } from 'framer-motion';
import { WorldObjectInfo, EntityInfo } from '../../types/game';

interface InteractionLayerProps {
  objects: WorldObjectInfo[];
  entities: EntityInfo[];
  onObjectClick: (object: WorldObjectInfo, event: React.MouseEvent) => void;
  onEntityClick: (entity: EntityInfo, event: React.MouseEvent) => void;
}

export const InteractionLayer: React.FC<InteractionLayerProps> = ({
  objects,
  entities,
  onObjectClick,
  onEntityClick,
}) => {
  // 디버그 로그
  console.log('[InteractionLayer] Rendering with:', { 
    objectsCount: objects.length, 
    entitiesCount: entities.length,
    objects: objects.map(o => ({ id: o.object_id, name: o.object_name, pos: o.position })),
    entities: entities.map(e => ({ id: e.entity_id, name: e.entity_name, pos: e.position }))
  });

  // 위치 기반으로 오브젝트/엔티티 배치 (간단한 그리드 시스템)
  const getPositionStyle = (position: { x: number; y: number; z: number }, index: number) => {
    // 위치가 0-10 범위인 경우 (셀 매트릭스 좌표)
    // 위치가 없거나 이상한 경우 인덱스 기반으로 배치
    let screenX: number;
    let screenY: number;
    
    if (position && typeof position.x === 'number' && typeof position.z === 'number') {
      // x, z 좌표를 화면 좌표로 변환
      // 셀 매트릭스는 보통 10x10이므로 0-10 범위를 10-90% 범위로 매핑
      screenX = (position.x / 10) * 80 + 10; // 0-10을 10-90%로 변환
      screenY = (position.z / 10) * 80 + 10; // z를 y 좌표로 사용
    } else {
      // 위치가 없으면 그리드로 배치
      const cols = 4;
      const col = index % cols;
      const row = Math.floor(index / cols);
      screenX = (col / cols) * 80 + 10;
      screenY = (row / 4) * 60 + 20;
    }
    
    return {
      left: `${Math.max(5, Math.min(95, screenX))}%`,
      top: `${Math.max(10, Math.min(90, screenY))}%`,
      transform: 'translate(-50%, -50%)',
    };
  };

  // 오브젝트와 엔티티가 없으면 아무것도 렌더링하지 않음
  if (objects.length === 0 && entities.length === 0) {
    console.log('[InteractionLayer] No objects or entities to render');
    return null;
  }

  return (
    <div 
      className="absolute inset-0 w-full h-full pointer-events-none" 
      style={{ 
        zIndex: 15,
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        width: '100%',
        height: '100%',
      }}
    >
      {/* 오브젝트 클릭 영역 - 원형 아이콘 */}
      {objects
        .filter((obj) => obj.position)
        .map((obj, index) => (
        <motion.div
          key={obj.object_id}
          className="absolute pointer-events-auto cursor-pointer"
          style={{
            ...getPositionStyle(obj.position!, index),
            width: '80px',
            height: '80px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, delay: index * 0.1 }}
        >
          <motion.div
            className="rounded-full bg-white/40 backdrop-blur-md border-2 border-white/60 shadow-lg"
            onClick={(e) => {
              e.stopPropagation();
              console.log('[InteractionLayer] Object clicked:', obj);
              onObjectClick(obj, e);
            }}
            whileHover={{
              scale: 1.2,
              backgroundColor: 'rgba(255, 255, 255, 0.6)',
              borderColor: 'rgba(255, 255, 255, 0.9)',
            }}
            whileTap={{ scale: 0.9 }}
            style={{
              width: '100%',
              height: '100%',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              color: 'rgba(0, 0, 0, 0.8)',
              cursor: 'pointer',
            }}
          >
            📦
          </motion.div>
        </motion.div>
      ))}

      {/* 엔티티 클릭 영역 */}
      {entities
        .filter((entity) => entity.position)
        .map((entity, index) => (
        <motion.div
          key={entity.entity_id}
          className="absolute pointer-events-auto cursor-pointer"
          style={{
            ...getPositionStyle(entity.position!, objects.length + index),
            width: '80px',
            height: '80px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, delay: (objects.length + index) * 0.1 }}
        >
          <motion.div
            className="rounded-full bg-white/50 backdrop-blur-md border-2 border-white/70 shadow-lg"
            onClick={(e) => {
              e.stopPropagation();
              console.log('[InteractionLayer] Entity clicked:', entity);
              onEntityClick(entity, e);
            }}
            whileHover={{
              scale: 1.2,
              backgroundColor: 'rgba(255, 255, 255, 0.7)',
              borderColor: 'rgba(255, 255, 255, 1)',
            }}
            whileTap={{ scale: 0.9 }}
            style={{
              width: '100%',
              height: '100%',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              color: 'rgba(0, 0, 0, 0.9)',
              cursor: 'pointer',
            }}
          >
            👤
          </motion.div>
        </motion.div>
      ))}
    </div>
  );
};

