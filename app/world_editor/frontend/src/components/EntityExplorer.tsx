/**
 * 통합 엔티티 탐색기 컴포넌트
 * 스카이림 Creation Kit 스타일의 트리 구조 탐색기
 */
import React, { useState, useEffect, useCallback } from 'react';
import { 
  regionsApi, locationsApi, cellsApi, entitiesApi, 
  worldObjectsApi, effectCarriersApi, itemsApi 
} from '../services/api';

export type EntityType = 'region' | 'location' | 'cell' | 'entity' | 'world_object' | 'effect_carrier' | 'item' | 'road' | 'folder';

export interface TreeNode {
  id: string;
  type: EntityType;
  label: string;
  icon: string;
  children?: TreeNode[];
  data?: any;
  expanded?: boolean;
  selected?: boolean;
  parentId?: string;
}

interface EntityExplorerProps {
  onEntitySelect: (entityType: EntityType, entityId: string) => void;
  selectedEntityType?: EntityType;
  selectedEntityId?: string | null;
  searchQuery?: string;
  onSearchQueryChange?: (query: string) => void;
  onAddPinToMap?: (entityType: EntityType, entityId: string, entityName: string) => void;
}

const getEntityIcon = (type: EntityType): string => {
  const icons: Record<EntityType, string> = {
    folder: '📁',
    region: '📍',
    location: '📍',
    cell: '📍',
    entity: '👤',
    world_object: '📦',
    effect_carrier: '⚡',
    item: '⚔️',
    road: '🛣️',
  };
  return icons[type] || '📄';
};

export const EntityExplorer: React.FC<EntityExplorerProps> = ({
  onEntitySelect,
  selectedEntityType,
  selectedEntityId,
  searchQuery = '',
  onSearchQueryChange,
  onAddPinToMap,
}) => {
  const [treeData, setTreeData] = useState<TreeNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; node: TreeNode } | null>(null);

  // 트리 데이터 로드
  const loadTreeData = useCallback(async () => {
    setLoading(true);
    try {
      const rootNodes: TreeNode[] = [
        {
          id: 'folder_regions',
          type: 'folder',
          label: '지역 (Regions)',
          icon: getEntityIcon('folder'),
          children: [],
          expanded: expandedNodes.has('folder_regions'),
        },
        {
          id: 'folder_entities',
          type: 'folder',
          label: '인물 (Entities)',
          icon: getEntityIcon('folder'),
          children: [],
          expanded: expandedNodes.has('folder_entities'),
        },
        {
          id: 'folder_world_objects',
          type: 'folder',
          label: '오브젝트 (World Objects)',
          icon: getEntityIcon('folder'),
          children: [],
          expanded: expandedNodes.has('folder_world_objects'),
        },
        {
          id: 'folder_effect_carriers',
          type: 'folder',
          label: '이펙트 (Effect Carriers)',
          icon: getEntityIcon('folder'),
          children: [],
          expanded: expandedNodes.has('folder_effect_carriers'),
        },
        {
          id: 'folder_items',
          type: 'folder',
          label: '장비 (Items)',
          icon: getEntityIcon('folder'),
          children: [],
          expanded: expandedNodes.has('folder_items'),
        },
      ];

      // Regions 로드 (계층 구조)
      try {
        const regionsRes = await regionsApi.getAll();
        const regions = regionsRes.data || [];
        
        const regionNodes: TreeNode[] = await Promise.all(
          regions.map(async (region: any) => {
            const locationRes = await locationsApi.getByRegion(region.region_id);
            const locations = locationRes.data || [];
            
            const locationNodes: TreeNode[] = await Promise.all(
              locations.map(async (location: any) => {
                const cellRes = await cellsApi.getByLocation(location.location_id);
                const cells = cellRes.data || [];
                
                const cellNodes: TreeNode[] = cells.map((cell: any) => ({
                  id: cell.cell_id,
                  type: 'cell' as EntityType,
                  label: cell.cell_name || cell.cell_id,
                  icon: getEntityIcon('cell'),
                  children: [], // 지연 로딩 - 확장 시 로드
                  data: cell,
                  parentId: location.location_id,
                  expanded: false,
                }));
                
                return {
                  id: location.location_id,
                  type: 'location' as EntityType,
                  label: location.location_name,
                  icon: getEntityIcon('location'),
                  children: cellNodes,
                  data: location,
                  parentId: region.region_id,
                };
              })
            );
            
            return {
              id: region.region_id,
              type: 'region' as EntityType,
              label: region.region_name,
              icon: getEntityIcon('region'),
              children: locationNodes,
              data: region,
            };
          })
        );
        
        rootNodes[0].children = regionNodes;
      } catch (error) {
        console.error('Regions 로드 실패:', error);
      }

      // Entities 전체 목록
      try {
        const entitiesRes = await entitiesApi.getAll();
        const entities = entitiesRes.data || [];
        rootNodes[1].children = entities.map((entity: any) => ({
          id: entity.entity_id,
          type: 'entity' as EntityType,
          label: entity.entity_name,
          icon: getEntityIcon('entity'),
          data: entity,
        }));
      } catch (error) {
        console.error('Entities 로드 실패:', error);
      }

      // World Objects 전체 목록
      try {
        const objectsRes = await worldObjectsApi.getAll();
        const objects = objectsRes.data || [];
        rootNodes[2].children = objects.map((obj: any) => ({
          id: obj.object_id,
          type: 'world_object' as EntityType,
          label: obj.object_name,
          icon: getEntityIcon('world_object'),
          data: obj,
        }));
      } catch (error) {
        console.error('World Objects 로드 실패:', error);
      }

      // Effect Carriers 전체 목록
      try {
        const effectsRes = await effectCarriersApi.getAll();
        const effects = effectsRes.data || [];
        rootNodes[3].children = effects.map((effect: any) => ({
          id: effect.effect_id,
          type: 'effect_carrier' as EntityType,
          label: effect.name,
          icon: getEntityIcon('effect_carrier'),
          data: effect,
        }));
      } catch (error) {
        console.error('Effect Carriers 로드 실패:', error);
      }

      // Items 전체 목록
      try {
        const itemsRes = await itemsApi.getAll();
        const items = itemsRes.data || [];
        rootNodes[4].children = items.map((item: any) => ({
          id: item.item_id,
          type: 'item' as EntityType,
          label: item.base_property_name || item.item_id,
          icon: getEntityIcon('item'),
          data: item,
        }));
      } catch (error) {
        console.error('Items 로드 실패:', error);
      }

      setTreeData(rootNodes);
    } catch (error) {
      console.error('트리 데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  }, [expandedNodes]);

  useEffect(() => {
    loadTreeData();
  }, []);

  // Cell의 자식 데이터 로드 (Entities, World Objects)
  const loadCellChildren = async (cellId: string): Promise<TreeNode[]> => {
    const children: TreeNode[] = [];
    
    try {
      // Entities 로드
      const entitiesRes = await entitiesApi.getByCell(cellId);
      const entities = entitiesRes.data || [];
      console.log(`Cell ${cellId}의 Entities:`, entities.length, '개');
      entities.forEach((entity: any) => {
        children.push({
          id: entity.entity_id,
          type: 'entity' as EntityType,
          label: entity.entity_name,
          icon: getEntityIcon('entity'),
          data: entity,
          parentId: cellId,
        });
      });
    } catch (error) {
      console.error('Cell Entities 로드 실패:', error);
      console.error('Error details:', error);
    }
    
    try {
      // World Objects 로드
      const objectsRes = await worldObjectsApi.getByCell(cellId);
      const objects = objectsRes.data || [];
      objects.forEach((obj: any) => {
        children.push({
          id: obj.object_id,
          type: 'world_object' as EntityType,
          label: obj.object_name,
          icon: getEntityIcon('world_object'),
          data: obj,
          parentId: cellId,
        });
      });
    } catch (error) {
      console.error('Cell World Objects 로드 실패:', error);
    }
    
    return children;
  };

  // 노드 확장/축소
  const toggleNode = async (nodeId: string) => {
    const newExpanded = new Set(expandedNodes);
    const wasExpanded = newExpanded.has(nodeId);
    
    if (wasExpanded) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
    
    // 노드 확장 시 자식 데이터 로드 (지연 로딩)
    const updateNodeExpansion = async (nodes: TreeNode[]): Promise<TreeNode[]> => {
      const updatedNodes: TreeNode[] = [];
      
      for (const node of nodes) {
        if (node.id === nodeId && !wasExpanded) {
          // Cell 노드인 경우 자식 데이터 로드
          if (node.type === 'cell' && (!node.children || node.children.length === 0)) {
            const children = await loadCellChildren(nodeId);
            updatedNodes.push({ ...node, expanded: true, children });
          } else {
            updatedNodes.push({ ...node, expanded: true });
          }
        } else if (node.id === nodeId && wasExpanded) {
          updatedNodes.push({ ...node, expanded: false });
        } else if (node.children) {
          const updatedChildren = await updateNodeExpansion(node.children);
          updatedNodes.push({ ...node, children: updatedChildren });
        } else {
          updatedNodes.push(node);
        }
      }
      
      return updatedNodes;
    };
    
    const updatedTree = await updateNodeExpansion(treeData);
    setTreeData(updatedTree);
  };

  // 노드 선택
  const handleNodeClick = (node: TreeNode) => {
    if (node.type === 'folder') {
      toggleNode(node.id);
    } else {
      onEntitySelect(node.type, node.id);
    }
  };

  // 컨텍스트 메뉴 핸들러
  const handleContextMenu = (e: React.MouseEvent, node: TreeNode) => {
    e.preventDefault();
    e.stopPropagation();
    
    // folder 타입이 아니고, region/location/cell인 경우에만 메뉴 표시
    if (node.type !== 'folder' && ['region', 'location', 'cell'].includes(node.type)) {
      setContextMenu({ x: e.clientX, y: e.clientY, node });
    }
  };

  // 컨텍스트 메뉴 닫기
  const closeContextMenu = () => {
    setContextMenu(null);
  };

  // 맵에 핀 추가
  const handleAddPinToMap = () => {
    if (contextMenu && onAddPinToMap) {
      const { node } = contextMenu;
      onAddPinToMap(node.type, node.id, node.label);
      closeContextMenu();
    }
  };

  // 트리 노드 렌더링
  const renderTreeNode = (node: TreeNode, level: number = 0): React.ReactNode => {
    const isExpanded = expandedNodes.has(node.id);
    const isSelected = selectedEntityType === node.type && selectedEntityId === node.id;
    const hasChildren = node.children && node.children.length > 0;

    return (
      <div key={node.id}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            padding: '4px 8px',
            paddingLeft: `${level * 16 + 8}px`,
            cursor: 'pointer',
            backgroundColor: isSelected ? '#e3f2fd' : 'transparent',
            fontSize: '13px',
            userSelect: 'none',
          }}
          onClick={() => handleNodeClick(node)}
          onDoubleClick={() => {
            if (hasChildren) {
              toggleNode(node.id);
            }
          }}
          onContextMenu={(e) => handleContextMenu(e, node)}
        >
          <span style={{ marginRight: '4px', fontSize: '14px' }}>
            {hasChildren ? (isExpanded ? '▼' : '▶') : ' '}
          </span>
          <span style={{ marginRight: '6px', fontSize: '16px' }}>{node.icon}</span>
          <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {node.label}
          </span>
        </div>
        {hasChildren && isExpanded && (
          <div>
            {node.children!.map(child => renderTreeNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  // 검색 필터링
  const filterTree = (nodes: TreeNode[], query: string): TreeNode[] => {
    if (!query) return nodes;
    
    const filtered: TreeNode[] = [];
    for (const node of nodes) {
      const matchesQuery = node.label.toLowerCase().includes(query.toLowerCase());
      const filteredChildren = node.children ? filterTree(node.children, query) : [];
      
      if (matchesQuery || filteredChildren.length > 0) {
        filtered.push({
          ...node,
          children: filteredChildren.length > 0 ? filteredChildren : node.children,
        });
      }
    }
    return filtered;
  };

  const filteredTree = searchQuery ? filterTree(treeData, searchQuery) : treeData;

  return (
    <div 
      style={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        backgroundColor: '#fff',
        borderRight: '1px solid #ddd',
        position: 'relative',
      }}
      onClick={closeContextMenu}
      onContextMenu={closeContextMenu}
    >
      <div style={{ 
        padding: '8px', 
        borderBottom: '1px solid #ddd',
        backgroundColor: '#f5f5f5',
      }}>
          <input
          type="text"
          placeholder="검색..."
          value={searchQuery}
          onChange={(e) => {
            if (onSearchQueryChange) {
              onSearchQueryChange(e.target.value);
            }
          }}
          style={{
            width: '100%',
            padding: '6px 8px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '12px',
          }}
        />
      </div>
      <div style={{ 
        flex: 1, 
        overflowY: 'auto',
        padding: '4px 0',
      }}>
        {loading ? (
          <div style={{ padding: '16px', textAlign: 'center', color: '#666' }}>
            로딩 중...
          </div>
        ) : (
          filteredTree.map(node => renderTreeNode(node))
        )}
      </div>
      
      {/* 컨텍스트 메뉴 */}
      {contextMenu && (
        <div
          style={{
            position: 'fixed',
            left: contextMenu.x,
            top: contextMenu.y,
            backgroundColor: '#fff',
            border: '1px solid #ddd',
            borderRadius: '4px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            zIndex: 1000,
            minWidth: '150px',
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <div
            style={{
              padding: '8px 12px',
              cursor: 'pointer',
              fontSize: '13px',
              borderBottom: '1px solid #eee',
            }}
            onClick={handleAddPinToMap}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#f0f0f0';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            📍 맵에 핀 추가
          </div>
        </div>
      )}
    </div>
  );
};

