"""
월드 에디터 FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Set
import json

from app.api.routes import (
    regions, locations, cells, roads, pins, map_metadata, pin_connections,
    entities, location_management, world_objects, effect_carriers, items,
    search, relationships, map_hierarchy, project
)
from app.api.routes import dialogue, dialogue_knowledge
from common.utils.logger import logger


# WebSocket 연결 관리자
class ConnectionManager:
    """WebSocket 연결 관리"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """연결 수락"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket 연결: {len(self.active_connections)}개 활성 연결")
    
    def disconnect(self, websocket: WebSocket):
        """연결 해제"""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket 연결 해제: {len(self.active_connections)}개 활성 연결")
    
    async def broadcast(self, message: dict):
        """모든 연결에 메시지 브로드캐스트"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"브로드캐스트 실패: {e}")
                disconnected.add(connection)
        
        # 연결 해제된 소켓 제거
        for connection in disconnected:
            self.disconnect(connection)


# FastAPI 앱 생성
app = FastAPI(
    title="World Editor API",
    version="1.0.0",
    description="D&D 타운 스타일 월드 에디터 API"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3000"],  # 프론트엔드 포트
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(regions.router, prefix="/api/regions", tags=["regions"])
app.include_router(locations.router, prefix="/api/locations", tags=["locations"])
app.include_router(cells.router, prefix="/api/cells", tags=["cells"])
app.include_router(roads.router, prefix="/api/roads", tags=["roads"])
app.include_router(pins.router, prefix="/api/pins", tags=["pins"])
app.include_router(pin_connections.router, prefix="/api/pins", tags=["pin-connections"])
app.include_router(map_metadata.router, prefix="/api/map", tags=["map"])
app.include_router(map_hierarchy.router, prefix="/api/maps", tags=["map-hierarchy"])
app.include_router(entities.router, prefix="/api/entities", tags=["entities"])
app.include_router(location_management.router, prefix="/api/manage", tags=["management"])
app.include_router(world_objects.router, prefix="/api/world-objects", tags=["world-objects"])
app.include_router(effect_carriers.router, prefix="/api/effect-carriers", tags=["effect-carriers"])
app.include_router(items.router, prefix="/api/items", tags=["items"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(relationships.router, prefix="/api/relationships", tags=["relationships"])
app.include_router(project.router, prefix="/api/project", tags=["project"])

# Dialogue API
from app.api.routes import dialogue
app.include_router(dialogue.router, prefix="/api/dialogue", tags=["dialogue"])
app.include_router(dialogue_knowledge.router, prefix="/api/dialogue", tags=["dialogue"])

# Behavior Schedule API
from app.api.routes import behavior_schedules
app.include_router(behavior_schedules.router, prefix="/api/behavior-schedules", tags=["behavior-schedules"])

# Gameplay API
from app.ui.backend.routes import gameplay
app.include_router(gameplay.router)

# WebSocket 연결 관리자
manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 엔드포인트 - 실시간 동기화"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            
            # 메시지 타입에 따른 처리
            message_type = data.get("type")
            
            if message_type == "ping":
                # 핑 메시지 응답
                await websocket.send_json({"type": "pong"})
            elif message_type in ["pin_update", "road_update", "map_update"]:
                # 변경사항을 다른 클라이언트에 브로드캐스트
                await manager.broadcast(data)
            else:
                logger.warning(f"알 수 없는 메시지 타입: {message_type}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket 오류: {e}")
        manager.disconnect(websocket)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "World Editor API",
        "version": "1.0.0",
        "endpoints": {
            "regions": "/api/regions",
            "locations": "/api/locations",
            "cells": "/api/cells",
            "roads": "/api/roads",
            "pins": "/api/pins",
            "map": "/api/map",
            "websocket": "/ws"
        }
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "World Editor API"}


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("World Editor API 서버 시작")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("World Editor API 서버 종료")

