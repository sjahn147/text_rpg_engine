/**
 * 통합 엔티티 편집기 컴포넌트
 * 모든 엔티티 타입을 하나의 편집기에서 관리
 */
import React, { useState, useEffect } from 'react';
import { EntityType } from './EntityExplorer';
import { LocationEditorModal } from './LocationEditorModal';
import { CellEditorModal } from './CellEditorModal';
import { EntityEditorModal } from './EntityEditorModal';
import { WorldObjectEditorModal } from './WorldObjectEditorModal';
import { EffectCarrierEditorModal } from './EffectCarrierEditorModal';
import { ItemEditorModal } from './ItemEditorModal';
import { 
  regionsApi, locationsApi, cellsApi, entitiesApi,
  worldObjectsApi, effectCarriersApi, itemsApi, roadsApi
} from '../services/api';

interface EntityEditorProps {
  entityType: EntityType;
  entityId: string | null | undefined;
  onSave: (entityType: EntityType, entityId: string, data: any) => Promise<void>;
  onDelete: (entityType: EntityType, entityId: string) => Promise<void>;
  onClose: () => void;
}

export const EntityEditor: React.FC<EntityEditorProps> = ({
  entityType,
  entityId,
  onSave,
  onDelete,
  onClose,
}) => {
  const [entityData, setEntityData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // 엔티티 데이터 로드
  useEffect(() => {
    const loadEntity = async () => {
      if (!entityId) {
        setEntityData(null);
        return;
      }

      setLoading(true);
      try {
        let response: any;
        
        switch (entityType) {
          case 'region':
            response = await regionsApi.getById(entityId);
            break;
          case 'location':
            response = await locationsApi.getById(entityId);
            break;
          case 'cell':
            response = await cellsApi.getById(entityId);
            break;
          case 'entity':
            response = await entitiesApi.getById(entityId);
            break;
          case 'world_object':
            response = await worldObjectsApi.getById(entityId);
            break;
          case 'effect_carrier':
            response = await effectCarriersApi.getById(entityId);
            break;
          case 'item':
            response = await itemsApi.getById(entityId);
            break;
          case 'road':
            response = await roadsApi.getById(entityId);
            break;
          default:
            return;
        }
        
        setEntityData(response.data);
      } catch (error) {
        console.error('엔티티 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadEntity();
  }, [entityType, entityId]);

  if (!entityId) {
    return (
      <div style={{ 
        padding: '16px', 
        textAlign: 'center', 
        color: '#666',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        엔티티를 선택하세요
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ 
        padding: '16px', 
        textAlign: 'center', 
        color: '#666' 
      }}>
        로딩 중...
      </div>
    );
  }

  // 엔티티 타입별로 기존 모달 재사용
  if (entityType === 'location' && entityData) {
    return (
      <LocationEditorModal
        isOpen={true}
        onClose={onClose}
        locationId={entityId}
        regionId={entityData.region_id}
        embedded={true}
        onSave={async () => {
          const response = await locationsApi.getById(entityId);
          await onSave(entityType, entityId, response.data);
        }}
      />
    );
  }

  if (entityType === 'cell') {
    return (
      <CellEditorModal
        isOpen={true}
        onClose={onClose}
        cellId={entityId}
        embedded={true}
        onSave={async () => {
          const response = await cellsApi.getById(entityId);
          await onSave(entityType, entityId, response.data);
        }}
      />
    );
  }

  if (entityType === 'entity') {
    return (
      <EntityEditorModal
        isOpen={true}
        onClose={onClose}
        entityId={entityId}
        embedded={true}
        onSave={async () => {
          const response = await entitiesApi.getById(entityId);
          await onSave(entityType, entityId, response.data);
        }}
      />
    );
  }

  // World Objects 편집
  if (entityType === 'world_object') {
    return (
      <WorldObjectEditorModal
        isOpen={true}
        onClose={onClose}
        objectId={entityId}
        onSave={async () => {
          const response = await worldObjectsApi.getById(entityId);
          await onSave(entityType, entityId, response.data);
        }}
      />
    );
  }

  // Effect Carriers 편집
  if (entityType === 'effect_carrier') {
    return (
      <EffectCarrierEditorModal
        isOpen={true}
        onClose={onClose}
        effectId={entityId}
        onSave={async () => {
          const response = await effectCarriersApi.getById(entityId);
          await onSave(entityType, entityId, response.data);
        }}
      />
    );
  }

  // Items 편집
  if (entityType === 'item') {
    return (
      <ItemEditorModal
        isOpen={true}
        onClose={onClose}
        itemId={entityId}
        onSave={async () => {
          const response = await itemsApi.getById(entityId);
          await onSave(entityType, entityId, response.data);
        }}
      />
    );
  }

  // 기타 엔티티 타입은 기본 편집 폼 표시
  return (
    <div style={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      <div style={{ 
        padding: '12px', 
        borderBottom: '1px solid #ddd',
        backgroundColor: '#f5f5f5',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 'bold' }}>
            {entityType}: {entityData?.name || entityData?.entity_name || entityData?.object_name || entityId}
          </h3>
        </div>
        <button
          onClick={onClose}
          style={{
            padding: '4px 8px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px',
          }}
        >
          닫기
        </button>
      </div>
      <div style={{ 
        flex: 1, 
        overflowY: 'auto',
        padding: '16px',
      }}>
        <pre style={{ 
          fontSize: '12px', 
          fontFamily: 'monospace',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}>
          {JSON.stringify(entityData, null, 2)}
        </pre>
      </div>
    </div>
  );
};

