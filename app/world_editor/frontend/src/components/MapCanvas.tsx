/**
 * 지도 캔버스 컴포넌트 (Konva.js)
 */
import React, { useRef, useEffect, useState } from 'react';
import { Stage, Layer, Image, Line, Circle, Group, Text, Rect } from 'react-konva';
// use-image 대신 직접 이미지 로드
import { MapMetadata, PinData, RoadData } from '../types';

interface MapCanvasProps {
  mapState: MapMetadata | null;
  pins: PinData[];
  roads: RoadData[];
  selectedPin: string | null;
  selectedRoad: string | null;
  currentTool: 'select' | 'pin' | 'road' | 'pan' | 'zoom';
  onPinClick: (pinId: string) => void;
  onPinDoubleClick?: (pinId: string) => void;
  onPinDrag: (pinId: string, x: number, y: number) => void;
  onRoadClick: (roadId: string) => void;
  onMapClick?: (x: number, y: number) => void;
  onRoadDraw?: (fromPinId: string, toPinId: string, path: Array<{ x: number; y: number }>) => void;
  onMouseMove?: (x: number, y: number) => void;
  currentMapLevel?: 'world' | 'region' | 'location' | 'cell'; // 현재 맵 레벨
}

export const MapCanvas: React.FC<MapCanvasProps> = ({
  mapState,
  pins,
  roads,
  selectedPin,
  selectedRoad,
  currentTool,
  onPinClick,
  onPinDoubleClick,
  onPinDrag,
  onRoadClick,
  onMapClick,
  onRoadDraw,
  onMouseMove,
  currentMapLevel = 'world', // 기본값은 world
}) => {
  const stageRef = useRef<any>(null);
  const [backgroundImage, setBackgroundImage] = React.useState<HTMLImageElement | null>(null);
  const [imageLoadError, setImageLoadError] = React.useState<boolean>(false);
  
  React.useEffect(() => {
    // 브라우저 환경에서 Image 생성자 사용
    if (typeof window === 'undefined') return;
    
    setImageLoadError(false);
    
    // 이미지가 없으면 빈 이미지로 처리
    if (!mapState?.background_image) {
      setBackgroundImage(null);
      setImageLoadError(true);
      return;
    }
    
    const img = document.createElement('img');
    img.src = mapState.background_image;
    img.onload = () => {
      setBackgroundImage(img);
      setImageLoadError(false);
    };
    img.onerror = () => {
      // 이미지 로드 실패 시 빈 이미지로 처리
      console.warn('이미지 로드 실패:', img.src);
      setBackgroundImage(null);
      setImageLoadError(true);
    };
    
    return () => {
      // 클린업
      img.onload = null;
      img.onerror = null;
    };
  }, [mapState?.background_image]);
  const [zoom, setZoom] = useState(1.0);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  // 줌 핸들러
  const handleWheel = (e: any) => {
    e.evt.preventDefault();
    const stage = e.target.getStage();
    const oldScale = stage.scaleX();
    const pointer = stage.getPointerPosition();

    const mousePointTo = {
      x: (pointer.x - stage.x()) / oldScale,
      y: (pointer.y - stage.y()) / oldScale,
    };

    const newScale = e.evt.deltaY > 0 ? oldScale * 0.9 : oldScale * 1.1;
    const clampedScale = Math.max(0.5, Math.min(3, newScale));

    setZoom(clampedScale);
    setPosition({
      x: pointer.x - mousePointTo.x * clampedScale,
      y: pointer.y - mousePointTo.y * clampedScale,
    });
  };

  // 핀 렌더링
  const renderPin = (pin: PinData, isShadow: boolean = false) => {
    const isSelected = selectedPin === pin.pin_id && !isShadow;
    const isDragging = draggingPinId === pin.pin_id;
    const pinColors: Record<string, string> = {
      region: '#FF6B9D',
      location: '#4ECDC4',
      cell: '#95E1D3',
    };

    // shadow 핀은 드래그 중인 핀만 표시
    if (isShadow && !isDragging) {
      return null;
    }

    return (
      <Group
        key={isShadow ? `shadow-${pin.pin_id}` : pin.pin_id}
        x={isShadow && dragShadowPosition ? dragShadowPosition.x : pin.x}
        y={isShadow && dragShadowPosition ? dragShadowPosition.y : pin.y}
        draggable={false} // 직접 드래그 비활성화
        opacity={isShadow ? 0.5 : 1}
        onMouseDown={(e) => {
          if (isShadow) return;
          
          // 중간 휠 클릭 (button === 1)으로만 드래그 모드 시작
          if (e.evt.button === 1 && currentTool === 'select') {
            e.cancelBubble = true;
            e.evt.preventDefault(); // 브라우저 기본 동작 방지 (스크롤 등)
            setDraggingPinId(pin.pin_id);
            setDragShadowPosition({ x: pin.x, y: pin.y });
          }
        }}
        onClick={(e) => {
          if (isShadow) {
            // shadow 핀 클릭 시 드래그 완료
            if (dragShadowPosition) {
              onPinDrag(pin.pin_id, dragShadowPosition.x, dragShadowPosition.y);
              setDraggingPinId(null);
              setDragShadowPosition(null);
            }
            return;
          }
          e.cancelBubble = true;
          
          // 일반 클릭은 선택만 처리
          onPinClick(pin.pin_id);
        }}
        onDblClick={(e) => {
          if (isShadow) return;
          e.cancelBubble = true;
          if (onPinDoubleClick) {
            onPinDoubleClick(pin.pin_id);
          }
        }}
        onTap={(e) => {
          if (isShadow) return;
          e.cancelBubble = true;
          onPinClick(pin.pin_id);
        }}
      >
        <Circle
          radius={isSelected ? 12 : 10}
          fill={pinColors[pin.pin_type] || pin.color}
          stroke={isSelected ? '#FFFFFF' : '#000000'}
          strokeWidth={isSelected ? 3 : 2}
        />
        <Text
          text={pin.pin_name || `새 핀 ${pin.pin_id.slice(-4)}`}
          fontSize={12}
          fill="#000000"
          x={-20}
          y={15}
        />
      </Group>
    );
  };

  // 도로 렌더링
  const renderRoad = (road: RoadData) => {
    const isSelected = selectedRoad === road.road_id;
    
    // from_pin_id와 to_pin_id를 우선 사용, 없으면 region_id/location_id로 찾기
    let fromPin = road.from_pin_id ? pins.find(p => p.pin_id === road.from_pin_id) : null;
    let toPin = road.to_pin_id ? pins.find(p => p.pin_id === road.to_pin_id) : null;
    
    if (!fromPin) {
      fromPin = pins.find(p => 
        (road.from_region_id && p.game_data_id === road.from_region_id && p.pin_type === 'region') ||
        (road.from_location_id && p.game_data_id === road.from_location_id && p.pin_type === 'location')
      );
    }
    
    if (!toPin) {
      toPin = pins.find(p =>
        (road.to_region_id && p.game_data_id === road.to_region_id && p.pin_type === 'region') ||
        (road.to_location_id && p.game_data_id === road.to_location_id && p.pin_type === 'location')
      );
    }

    if (!fromPin || !toPin) return null;

    const points = road.path_coordinates.length > 0
      ? road.path_coordinates.flatMap(p => [p.x, p.y])
      : [fromPin.x, fromPin.y, toPin.x, toPin.y];

    const roadColors: Record<string, string> = {
      normal: '#8B4513',
      hidden: '#696969',
      river: '#4169E1',
      mountain_pass: '#A0522D',
    };

    return (
      <Line
        key={road.road_id}
        points={points}
        stroke={roadColors[road.road_type] || '#8B4513'}
        strokeWidth={isSelected ? 4 : 2}
        tension={0.5}
        onClick={() => onRoadClick(road.road_id)}
      />
    );
  };

  if (!mapState) {
    return <div>지도를 불러오는 중...</div>;
  }

  // 마우스 위치 추적 (핀 미리보기용)
  const [mousePosition, setMousePosition] = useState<{ x: number; y: number } | null>(null);
  
  // 핀 드래그 shadow 상태
  const [draggingPinId, setDraggingPinId] = useState<string | null>(null);
  const [dragShadowPosition, setDragShadowPosition] = useState<{ x: number; y: number } | null>(null);

  // 맵 클릭 핸들러 (핀 추가, 도로 그리기, 핀 드래그 완료)
  const handleStageClick = (e: any) => {
    const stage = e.target.getStage();
    const targetType = e.target.getType?.();
    
    // 핀 드래그 중이고 배경을 클릭한 경우 - shadow 위치로 핀 이동
    if (draggingPinId && dragShadowPosition && currentTool === 'select') {
      if (targetType === 'Image' || targetType === 'Rect' || targetType === 'Stage') {
        // shadow 위치로 핀 이동
        onPinDrag(draggingPinId, dragShadowPosition.x, dragShadowPosition.y);
        setDraggingPinId(null);
        setDragShadowPosition(null);
        return;
      }
    }
    
    // 핀이나 도로를 클릭한 경우는 무시 (Group, Circle, Line 등)
    if (targetType === 'Group' || targetType === 'Circle' || targetType === 'Line' || targetType === 'Text') {
      return;
    }

    // 배경 이미지나 Stage를 클릭한 경우
    if (currentTool === 'pin' && onMapClick) {
      const pointer = stage.getPointerPosition();
      const scale = stage.scaleX();
      
      // 스테이지 좌표를 맵 좌표로 변환
      const mapX = (pointer.x - stage.x()) / scale;
      const mapY = (pointer.y - stage.y()) / scale;
      
      onMapClick(mapX, mapY);
    } else if (currentTool === 'road') {
      // 도로 그리기는 두 개의 핀을 선택해야 하므로 여기서는 처리하지 않음
    }
  };

  // 마우스 이동 핸들러 (핀 미리보기 및 드래그 shadow)
  const handleStageMouseMove = (e: any) => {
    const stage = e.target.getStage();
    const pointer = stage.getPointerPosition();
    const scale = stage.scaleX();
    
    // 스테이지 좌표를 맵 좌표로 변환
    const mapX = (pointer.x - stage.x()) / scale;
    const mapY = (pointer.y - stage.y()) / scale;
    
    // 상태바에 마우스 위치 전달
    if (onMouseMove) {
      onMouseMove(mapX, mapY);
    }
    
    if (currentTool === 'pin') {
      setMousePosition({ x: mapX, y: mapY });
    } else {
      setMousePosition(null);
    }
    
    // 핀 드래그 중이면 shadow 위치 업데이트
    if (draggingPinId && currentTool === 'select') {
      const maxWidth = mapState?.width || 10000;
      const maxHeight = mapState?.height || 10000;
      
      // 범위 내로 제한
      const clampedX = Math.max(0, Math.min(maxWidth, mapX));
      const clampedY = Math.max(0, Math.min(maxHeight, mapY));
      
      setDragShadowPosition({ x: clampedX, y: clampedY });
    }
  };

  // 마우스가 Stage를 벗어날 때
  const handleStageMouseLeave = () => {
    setMousePosition(null);
    // 드래그 중이면 취소
    if (draggingPinId) {
      setDraggingPinId(null);
      setDragShadowPosition(null);
    }
  };
  
  // ESC 키로 드래그 취소
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && draggingPinId) {
        setDraggingPinId(null);
        setDragShadowPosition(null);
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [draggingPinId]);

  return (
    <Stage
      ref={stageRef}
      width={window.innerWidth - 600}  // 왼쪽 250px + 오른쪽 350px
      height={window.innerHeight - 100}
      scaleX={zoom}
      scaleY={zoom}
      x={position.x}
      y={position.y}
      onWheel={handleWheel}
      onClick={handleStageClick}
      onMouseMove={handleStageMouseMove}
      onMouseLeave={handleStageMouseLeave}
      draggable={(currentTool === 'select' || currentTool === 'pan') && !draggingPinId}
      onDragMove={(e) => {
        const stage = e.target;
        setPosition({ x: stage.x(), y: stage.y() });
      }}
      onDragEnd={(e) => {
        const stage = e.target;
        setPosition({ x: stage.x(), y: stage.y() });
      }}
    >
      <Layer>
        {/* 배경 이미지 */}
        {backgroundImage ? (
          <Image
            image={backgroundImage}
            width={mapState.width}
            height={mapState.height}
            x={0}
            y={0}
          />
        ) : (
          // 이미지가 없을 때 빈 이미지와 안내 메시지 표시
          <Group>
            {/* 빈 배경 (회색) */}
            <Rect
              width={mapState.width}
              height={mapState.height}
              x={0}
              y={0}
              fill="#E0E0E0"
            />
            {/* 안내 메시지 */}
            <Text
              x={mapState.width / 2}
              y={mapState.height / 2 - 20}
              text="이미지가 없습니다"
              fontSize={24}
              fill="#666666"
              align="center"
              offsetX={100}
              offsetY={12}
            />
            <Text
              x={mapState.width / 2}
              y={mapState.height / 2 + 10}
              text="맵 이미지를 업로드하거나 설정해주세요"
              fontSize={14}
              fill="#999999"
              align="center"
              offsetX={150}
              offsetY={7}
            />
          </Group>
        )}

        {/* 그리드 */}
        {mapState.grid_enabled && (
          <Group>
            {Array.from({ length: Math.ceil(mapState.width / mapState.grid_size) }).map((_, i) => (
              <Line
                key={`v-${i}`}
                points={[i * mapState.grid_size, 0, i * mapState.grid_size, mapState.height]}
                stroke="#CCCCCC"
                strokeWidth={1}
              />
            ))}
            {Array.from({ length: Math.ceil(mapState.height / mapState.grid_size) }).map((_, i) => (
              <Line
                key={`h-${i}`}
                points={[0, i * mapState.grid_size, mapState.width, i * mapState.grid_size]}
                stroke="#CCCCCC"
                strokeWidth={1}
              />
            ))}
          </Group>
        )}

        {/* 도로 렌더링 */}
        {roads.map(road => renderRoad(road))}

        {/* 핀 미리보기 (shadow) - 핀 배치 모드 */}
        {currentTool === 'pin' && mousePosition && (
          <Group
            x={mousePosition.x}
            y={mousePosition.y}
            opacity={0.5}
          >
            <Circle
              radius={10}
              fill="#FF6B9D"
              stroke="#000000"
              strokeWidth={2}
            />
            <Text
              text="새 핀"
              fontSize={12}
              fill="#000000"
              x={-20}
              y={15}
            />
          </Group>
        )}

        {/* 핀 드래그 shadow - 핀 이동 모드 */}
        {draggingPinId && dragShadowPosition && currentTool === 'select' && (
          (() => {
            const pin = pins.find(p => p.pin_id === draggingPinId);
            if (!pin) return null;
            return renderPin(pin, true);
          })()
        )}

        {/* 핀 렌더링 - 현재 맵 레벨에 따라 필터링 */}
        {/* World Map: region 핀만 표시 */}
        {currentMapLevel === 'world' && (
          <>
            {pins.filter(pin => pin.pin_type === 'region').map(pin => renderPin(pin))}
          </>
        )}
        
        {/* Region Map: location 핀만 표시 */}
        {currentMapLevel === 'region' && (
          <>
            {pins.filter(pin => pin.pin_type === 'location').map(pin => renderPin(pin))}
          </>
        )}
        
        {/* Location Map: cell 핀만 표시 */}
        {currentMapLevel === 'location' && (
          <>
            {pins.filter(pin => pin.pin_type === 'cell').map(pin => renderPin(pin))}
          </>
        )}
      </Layer>
      
      {/* 기타 핀 Layer - World Map에서만 표시 */}
      {currentMapLevel === 'world' && (
        <Layer>
          {pins.filter(pin => !['region', 'location', 'cell'].includes(pin.pin_type)).map(pin => renderPin(pin))}
        </Layer>
      )}
    </Stage>
  );
};

