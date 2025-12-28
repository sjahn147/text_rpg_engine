"""
프로젝트 관리 API 라우터
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, Any
import json

from app.api.schemas import ProjectExportResponse, ProjectImportResponse, ValidationResponse
from app.services.world_editor.project_service import ProjectService
from app.services.world_editor.validation_service import ValidationService
from common.utils.logger import logger

router = APIRouter()
project_service = ProjectService()
validation_service = ValidationService()


@router.get("/export", response_model=ProjectExportResponse)
async def export_project():
    """프로젝트 전체 데이터 내보내기"""
    try:
        project_data = await project_service.export_project()
        return {
            'success': True,
            'data': project_data,
            'message': '프로젝트 내보내기 완료'
        }
    except Exception as e:
        logger.error(f"프로젝트 내보내기 실패: {e}")
        raise HTTPException(status_code=500, detail=f"프로젝트 내보내기 실패: {str(e)}")


@router.post("/import", response_model=ProjectImportResponse)
async def import_project(project_data: Dict[str, Any]):
    """프로젝트 데이터 가져오기"""
    try:
        stats = await project_service.import_project(project_data)
        return {
            'success': True,
            'stats': stats,
            'message': '프로젝트 가져오기 완료'
        }
    except Exception as e:
        logger.error(f"프로젝트 가져오기 실패: {e}")
        raise HTTPException(status_code=500, detail=f"프로젝트 가져오기 실패: {str(e)}")


@router.post("/import/file")
async def import_project_file(file: UploadFile = File(...)):
    """프로젝트 파일 가져오기"""
    try:
        content = await file.read()
        project_data = json.loads(content.decode('utf-8'))
        stats = await project_service.import_project(project_data)
        return {
            'success': True,
            'stats': stats,
            'message': '프로젝트 파일 가져오기 완료'
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 JSON 파일: {str(e)}")
    except Exception as e:
        logger.error(f"프로젝트 파일 가져오기 실패: {e}")
        raise HTTPException(status_code=500, detail=f"프로젝트 파일 가져오기 실패: {str(e)}")


@router.post("/import/entities")
async def import_entities(entities: list):
    """엔티티 데이터 가져오기"""
    try:
        from app.api.schemas import EntityCreate
        stats = {'entities': 0}
        for entity_dict in entities:
            try:
                entity_id = entity_dict.get('entity_id')
                if not entity_id:
                    continue
                existing = await project_service.entity_service.get_entity(entity_id)
                if existing:
                    await project_service.entity_service.update_entity(entity_id, entity_dict)
                else:
                    entity_create = EntityCreate(**entity_dict)
                    await project_service.entity_service.create_entity(entity_create)
                stats['entities'] += 1
            except Exception as e:
                logger.warning(f"엔티티 가져오기 실패: {e}")
        return {
            'success': True,
            'stats': stats,
            'message': f"{stats['entities']}개의 엔티티가 가져와졌습니다."
        }
    except Exception as e:
        logger.error(f"엔티티 가져오기 실패: {e}")
        raise HTTPException(status_code=500, detail=f"엔티티 가져오기 실패: {str(e)}")


@router.post("/import/regions")
async def import_regions(regions: list):
    """지역 데이터 가져오기"""
    try:
        from app.api.schemas import RegionCreate
        stats = {'regions': 0}
        for region_dict in regions:
            try:
                region_id = region_dict.get('region_id')
                if not region_id:
                    continue
                existing = await project_service.region_service.get_region(region_id)
                if existing:
                    await project_service.region_service.update_region(region_id, region_dict)
                else:
                    region_create = RegionCreate(**region_dict)
                    await project_service.region_service.create_region(region_create)
                stats['regions'] += 1
            except Exception as e:
                logger.warning(f"지역 가져오기 실패: {e}")
        return {
            'success': True,
            'stats': stats,
            'message': f"{stats['regions']}개의 지역이 가져와졌습니다."
        }
    except Exception as e:
        logger.error(f"지역 가져오기 실패: {e}")
        raise HTTPException(status_code=500, detail=f"지역 가져오기 실패: {str(e)}")


@router.get("/validate/all", response_model=ValidationResponse)
async def validate_all():
    """전체 데이터 검증"""
    try:
        issues = await validation_service.validate_all()
        return {
            'success': True,
            'issues': issues,
            'total_issues': sum(len(v) for v in issues.values()),
            'message': '검증 완료'
        }
    except Exception as e:
        logger.error(f"검증 실패: {e}")
        raise HTTPException(status_code=500, detail=f"검증 실패: {str(e)}")


@router.get("/validate/orphans")
async def validate_orphans():
    """고아 엔티티 검색"""
    try:
        orphans = await validation_service.find_orphans()
        return {
            'success': True,
            'orphans': orphans,
            'count': len(orphans),
            'message': f"{len(orphans)}개의 고아 엔티티를 찾았습니다."
        }
    except Exception as e:
        logger.error(f"고아 엔티티 검색 실패: {e}")
        raise HTTPException(status_code=500, detail=f"고아 엔티티 검색 실패: {str(e)}")


@router.get("/validate/duplicates")
async def validate_duplicates():
    """중복 이름 검색"""
    try:
        duplicates = await validation_service.find_duplicates()
        return {
            'success': True,
            'duplicates': duplicates,
            'count': len(duplicates),
            'message': f"{len(duplicates)}개의 중복을 찾았습니다."
        }
    except Exception as e:
        logger.error(f"중복 검색 실패: {e}")
        raise HTTPException(status_code=500, detail=f"중복 검색 실패: {str(e)}")

