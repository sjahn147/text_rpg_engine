/**
 * Cell 내 Entity 관리 컴포넌트
 * 2D 그리드 기반 Entity 위치 편집
 */
import React, { useState, useEffect } from 'react';
import { entitiesApi, worldObjectsApi } from '../../services/api';

interface CellEntityManagerProps {
  cellId: string;
  onBack: () => void;
}

interface EntityData {
  entity_id: string;
  entity_name: string;
  entity_type: string;
  default_position_3d: {
    x: number;
    y: number;
    z: number;
    rotation_y?: number;
    cell_id: string;
  } | null;
  entity_size: string;
}

interface WorldObjectData {
  object_id: string;
  object_name: string;
  object_type: string;
  default_position: {
    x: number;
    y: number;
  } | null;
  object_width: number;
  object_height: number;
  object_depth: number;
  passable: boolean;
  movable: boolean;
  wall_mounted: boolean;
}

export const CellEntityManager: React.FC<CellEntityManagerProps> = ({
  cellId,
  onBack,
}) => {
  const [entities, setEntities] = useState<EntityData[]>([]);
  const [worldObjects, setWorldObjects] = useState<WorldObjectData[]>([]);
  const [selectedEntity, setSelectedEntity] = useState<string | null>(null);
  const [gridSize, setGridSize] = useState(20);
  const [zoom, setZoom] = useState(1.0);
  const [loading, setLoading] = useState(true);

  // Entity 및 World Object 로드
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [entitiesRes, objectsRes] = await Promise.all([
          entitiesApi.getByCell(cellId),
          worldObjectsApi.getByCell(cellId),
        ]);

        setEntities(entitiesRes.data);
        setWorldObjects(objectsRes.data);
      } catch (error) {
        console.error('데이터 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [cellId]);

  // Entity 위치 업데이트
  const handleEntityPositionUpdate = async (
    entityId: string,
    position: { x: number; y: number; z: number }
  ) => {
    try {
      await entitiesApi.update(entityId, {
        default_position_3d: {
          ...position,
          cell_id: cellId,
        },
      });

      // 로컬 상태 업데이트
      setEntities(prevEntities =>
        prevEntities.map(e =>
          e.entity_id === entityId
            ? {
                ...e,
                default_position_3d: {
                  ...position,
                  cell_id: cellId,
                },
              }
            : e
        )
      );
    } catch (error) {
      console.error('Entity 위치 업데이트 실패:', error);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>로딩 중...</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', height: '100%' }}>
      {/* 왼쪽 사이드바 - Entity 목록 */}
      <div style={{
        width: '300px',
        borderRight: '1px solid #ddd',
        padding: '10px',
        overflowY: 'auto',
      }}>
        <div style={{ marginBottom: '20px' }}>
          <button
            onClick={onBack}
            style={{ padding: '5px 15px', marginBottom: '10px', cursor: 'pointer' }}
          >
            ← 뒤로
          </button>
          <h3>Entity 목록</h3>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h4>Entities ({entities.length})</h4>
          {entities.map(entity => (
            <div
              key={entity.entity_id}
              onClick={() => setSelectedEntity(entity.entity_id)}
              style={{
                padding: '10px',
                marginBottom: '5px',
                backgroundColor: selectedEntity === entity.entity_id ? '#e3f2fd' : '#f5f5f5',
                cursor: 'pointer',
                border: '1px solid #ddd',
                borderRadius: '4px',
              }}
            >
              <div style={{ fontWeight: 'bold' }}>{entity.entity_name}</div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                {entity.entity_type} ({entity.entity_size})
              </div>
              {entity.default_position_3d && (
                <div style={{ fontSize: '11px', color: '#999' }}>
                  위치: ({entity.default_position_3d.x.toFixed(1)}, {entity.default_position_3d.y.toFixed(1)}, {entity.default_position_3d.z.toFixed(1)})
                </div>
              )}
            </div>
          ))}
        </div>

        <div>
          <h4>World Objects ({worldObjects.length})</h4>
          {worldObjects.map(obj => (
            <div
              key={obj.object_id}
              style={{
                padding: '10px',
                marginBottom: '5px',
                backgroundColor: '#f5f5f5',
                border: '1px solid #ddd',
                borderRadius: '4px',
              }}
            >
              <div style={{ fontWeight: 'bold' }}>{obj.object_name}</div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                {obj.object_type}
              </div>
              {obj.default_position && (
                <div style={{ fontSize: '11px', color: '#999' }}>
                  위치: ({obj.default_position.x.toFixed(1)}, {obj.default_position.y.toFixed(1)})
                </div>
              )}
              <div style={{ fontSize: '11px', color: '#999' }}>
                {obj.passable && '통과 가능'} {obj.movable && '이동 가능'} {obj.wall_mounted && '벽 부착'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 중앙 - 2D 그리드 뷰 */}
      <div style={{ flex: 1, position: 'relative', overflow: 'auto' }}>
        <div style={{
          padding: '20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid #ddd',
        }}>
          <h3>Cell Entity 배치</h3>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <label>
              그리드 크기:
              <input
                type="number"
                value={gridSize}
                onChange={(e) => setGridSize(Number(e.target.value))}
                min={10}
                max={50}
                style={{ width: '60px', marginLeft: '5px' }}
              />
            </label>
            <label>
              줌:
              <input
                type="range"
                min={0.5}
                max={2}
                step="0.1"
                value={zoom}
                onChange={(e) => setZoom(Number(e.target.value))}
                style={{ marginLeft: '5px' }}
              />
              {zoom.toFixed(1)}x
            </label>
          </div>
        </div>

        {/* 그리드 캔버스 영역 */}
        <div style={{
          padding: '20px',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '500px',
        }}>
          <div style={{
            position: 'relative',
            transform: `scale(${zoom})`,
            transformOrigin: 'top left',
          }}>
            {/* 그리드 배경 */}
            <svg
              width={gridSize * 20}
              height={gridSize * 20}
              style={{
                border: '1px solid #ddd',
                backgroundColor: '#fff',
              }}
            >
              {/* 그리드 라인 */}
              {Array.from({ length: 21 }).map((_, i) => (
                <g key={i}>
                  <line
                    x1={i * gridSize}
                    y1={0}
                    x2={i * gridSize}
                    y2={gridSize * 20}
                    stroke="#e0e0e0"
                    strokeWidth="1"
                  />
                  <line
                    x1={0}
                    y1={i * gridSize}
                    x2={gridSize * 20}
                    y2={i * gridSize}
                    stroke="#e0e0e0"
                    strokeWidth="1"
                  />
                </g>
              ))}

              {/* World Objects 렌더링 */}
              {worldObjects
                .filter(obj => obj.default_position)
                .map(obj => (
                  <rect
                    key={obj.object_id}
                    x={(obj.default_position!.x - obj.object_width / 2) * gridSize}
                    y={(obj.default_position!.y - obj.object_depth / 2) * gridSize}
                    width={obj.object_width * gridSize}
                    height={obj.object_depth * gridSize}
                    fill={obj.passable ? 'rgba(76, 175, 80, 0.3)' : 'rgba(244, 67, 54, 0.3)'}
                    stroke={obj.passable ? '#4CAF50' : '#F44336'}
                    strokeWidth="2"
                  />
                ))}

              {/* Entities 렌더링 */}
              {entities
                .filter(e => e.default_position_3d)
                .map(entity => {
                  const pos = entity.default_position_3d!;
                  const sizeMap: { [key: string]: number } = {
                    tiny: 0.25,
                    small: 0.5,
                    medium: 0.5,
                    large: 1.0,
                    huge: 1.5,
                    gargantuan: 2.0,
                  };
                  const radius = (sizeMap[entity.entity_size] || 0.5) * gridSize;

                  return (
                    <circle
                      key={entity.entity_id}
                      cx={pos.x * gridSize}
                      cy={pos.y * gridSize}
                      r={radius}
                      fill={selectedEntity === entity.entity_id ? '#2196F3' : '#4CAF50'}
                      stroke="#000"
                      strokeWidth="2"
                      style={{ cursor: 'pointer' }}
                      onClick={() => setSelectedEntity(entity.entity_id)}
                    />
                  );
                })}
            </svg>
          </div>
        </div>
      </div>

      {/* 오른쪽 사이드바 - 선택된 Entity 편집 */}
      {selectedEntity && (
        <div style={{
          width: '300px',
          borderLeft: '1px solid #ddd',
          padding: '10px',
        }}>
          <h3>Entity 편집</h3>
          {(() => {
            const entity = entities.find(e => e.entity_id === selectedEntity);
            if (!entity) return null;

            return (
              <div>
                <div style={{ marginBottom: '15px' }}>
                  <strong>{entity.entity_name}</strong>
                </div>
                {entity.default_position_3d && (
                  <div>
                    <h4>위치</h4>
                    <div style={{ marginBottom: '10px' }}>
                      <label>
                        X:
                        <input
                          type="number"
                          value={entity.default_position_3d.x}
                          onChange={(e) => {
                            const newPos = {
                              ...entity.default_position_3d!,
                              x: Number(e.target.value),
                            };
                            handleEntityPositionUpdate(selectedEntity, newPos);
                          }}
                          step="0.1"
                          style={{ width: '100%', marginTop: '5px' }}
                        />
                      </label>
                    </div>
                    <div style={{ marginBottom: '10px' }}>
                      <label>
                        Y:
                        <input
                          type="number"
                          value={entity.default_position_3d.y}
                          onChange={(e) => {
                            const newPos = {
                              ...entity.default_position_3d!,
                              y: Number(e.target.value),
                            };
                            handleEntityPositionUpdate(selectedEntity, newPos);
                          }}
                          step="0.1"
                          style={{ width: '100%', marginTop: '5px' }}
                        />
                      </label>
                    </div>
                    <div style={{ marginBottom: '10px' }}>
                      <label>
                        Z:
                        <input
                          type="number"
                          value={entity.default_position_3d.z}
                          onChange={(e) => {
                            const newPos = {
                              ...entity.default_position_3d!,
                              z: Number(e.target.value),
                            };
                            handleEntityPositionUpdate(selectedEntity, newPos);
                          }}
                          step="0.1"
                          style={{ width: '100%', marginTop: '5px' }}
                        />
                      </label>
                    </div>
                  </div>
                )}
                <div>
                  <h4>크기</h4>
                  <select
                    value={entity.entity_size || 'medium'}
                    onChange={async (e) => {
                      const newSize = e.target.value;
                      try {
                        await entitiesApi.update(entity.entity_id, { entity_size: newSize });
                        // 로컬 상태 업데이트
                        setEntities(prev => prev.map(e => 
                          e.entity_id === entity.entity_id 
                            ? { ...e, entity_size: newSize }
                            : e
                        ));
                      } catch (error) {
                        console.error('Entity 크기 업데이트 실패:', error);
                        alert('크기 업데이트에 실패했습니다.');
                      }
                    }}
                    style={{ width: '100%', marginTop: '5px' }}
                  >
                    <option value="tiny">Tiny</option>
                    <option value="small">Small</option>
                    <option value="medium">Medium</option>
                    <option value="large">Large</option>
                    <option value="huge">Huge</option>
                    <option value="gargantuan">Gargantuan</option>
                  </select>
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
};

