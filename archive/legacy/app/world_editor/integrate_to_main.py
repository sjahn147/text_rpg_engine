"""
월드 에디터를 기존 FastAPI 앱에 통합하는 헬퍼
기존 서버가 있다면 이 함수를 사용하여 라우터를 추가할 수 있습니다.
"""
from fastapi import FastAPI
from app.world_editor.routes import (
    regions, locations, cells, roads, pins, map_metadata
)


def integrate_world_editor_routes(app: FastAPI):
    """
    기존 FastAPI 앱에 월드 에디터 라우터 통합
    
    사용 예:
        from app.world_editor.integrate_to_main import integrate_world_editor_routes
        integrate_world_editor_routes(app)
    """
    # 라우터 등록
    app.include_router(regions.router, prefix="/api/regions", tags=["regions"])
    app.include_router(locations.router, prefix="/api/locations", tags=["locations"])
    app.include_router(cells.router, prefix="/api/cells", tags=["cells"])
    app.include_router(roads.router, prefix="/api/roads", tags=["roads"])
    app.include_router(pins.router, prefix="/api/pins", tags=["pins"])
    app.include_router(map_metadata.router, prefix="/api/map", tags=["map"])

