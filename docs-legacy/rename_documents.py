#!/usr/bin/env python3
"""
문서 이름을 논리적이고 시간순서대로 정리하는 스크립트
같은 종류 안에서의 시간 순서를 표현하는 넘버링 적용
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_file_modification_time(file_path):
    """파일의 수정 시간을 반환"""
    try:
        return os.path.getmtime(file_path)
    except OSError:
        return 0

def rename_documents():
    """문서들을 논리적이고 시간순서대로 이름 변경"""
    
    # 현재 작업 디렉토리를 docs로 설정
    docs_path = Path(".")
    if not docs_path.exists():
        logger.error("docs 디렉토리를 찾을 수 없습니다.")
        return
    
    # 파일 매핑 정의 (기존 이름 -> 새 이름)
    # 같은 종류 안에서 시간 순서로 넘버링
    file_mappings = {
        # 01. 초기 설계 및 아키텍처 (2025-06-15)
        "architecture/db_schema/00_README.md": "01_ARCH_DB_SCHEMA_README.md",
        "architecture/db_schema/00_extensions.sql": "01_ARCH_DB_EXTENSIONS.sql",
        "architecture/db_schema/01_recreate_tables.sql": "01_ARCH_DB_TABLES.sql",
        "architecture/db_schema/02_fix_triggers.sql": "01_ARCH_DB_TRIGGERS.sql",
        
        # 데이터 일관성 및 문제점 (시간순)
        "architecture/db_schema/data_consistency_issues.md": "01_ARCH_DATA_CONSISTENCY_ISSUES.md",
        "architecture/db_schema/dialogue_simulation.md": "01_ARCH_DIALOGUE_SIMULATION.md",
        "architecture/db_schema/dialogue_sync_issues.md": "01_ARCH_DIALOGUE_SYNC_ISSUES.md",
        "architecture/db_schema/json_schemas.md": "01_ARCH_JSON_SCHEMAS.md",
        
        # 게임 데이터 스키마 (시간순)
        "architecture/db_schema/data_consistency_issues.md": "01_ARCH_DATA_CONSISTENCY_ISSUES.md",
        "architecture/db_schema/dialogue_simulation.md": "01_ARCH_DIALOGUE_SIMULATION.md",
        "architecture/db_schema/dialogue_sync_issues.md": "01_ARCH_DIALOGUE_SYNC_ISSUES.md",
        "architecture/db_schema/json_schemas.md": "01_ARCH_JSON_SCHEMAS.md",
        
        # 게임 데이터 엔티티 (시간순)
        "architecture/db_schema/game_data/entities/entities.sql": "01_ARCH_GAME_DATA_ENTITIES.sql",
        "architecture/db_schema/game_data/entities/abilities.sql": "01_ARCH_GAME_DATA_ABILITIES.sql",
        "architecture/db_schema/game_data/entities/effects.sql": "01_ARCH_GAME_DATA_EFFECTS.sql",
        "architecture/db_schema/game_data/entities/items.sql": "01_ARCH_GAME_DATA_ITEMS.sql",
        "architecture/db_schema/game_data/entities/equipment.sql": "01_ARCH_GAME_DATA_EQUIPMENT.sql",
        "architecture/db_schema/game_data/entities/base_properties.sql": "01_ARCH_GAME_DATA_BASE_PROPERTIES.sql",
        "architecture/db_schema/game_data/world/locations.sql": "01_ARCH_GAME_DATA_LOCATIONS.sql",
        "architecture/db_schema/game_data/world/regions.sql": "01_ARCH_GAME_DATA_REGIONS.sql",
        "architecture/db_schema/game_data/world/cells.sql": "01_ARCH_GAME_DATA_CELLS.sql",
        "architecture/db_schema/game_data/objects/world_objects.sql": "01_ARCH_GAME_DATA_WORLD_OBJECTS.sql",
        
        # 런타임 데이터 스키마 (시간순)
        "architecture/db_schema/runtime_data/dialogue/contexts.sql": "01_ARCH_RUNTIME_DIALOGUE_CONTEXTS.sql",
        "architecture/db_schema/runtime_data/dialogue/knowledge.sql": "01_ARCH_RUNTIME_DIALOGUE_KNOWLEDGE.sql",
        "architecture/db_schema/runtime_data/dialogue/history.sql": "01_ARCH_RUNTIME_DIALOGUE_HISTORY.sql",
        "architecture/db_schema/runtime_data/dialogue/states.sql": "01_ARCH_RUNTIME_DIALOGUE_STATES.sql",
        "architecture/db_schema/runtime_data/dialogue/procedures.sql": "01_ARCH_RUNTIME_DIALOGUE_PROCEDURES.sql",
        "architecture/db_schema/runtime_data/events/triggered_events.sql": "01_ARCH_RUNTIME_EVENTS_TRIGGERED.sql",
        "architecture/db_schema/runtime_data/events/player_choices.sql": "01_ARCH_RUNTIME_EVENTS_PLAYER_CHOICES.sql",
        "architecture/db_schema/runtime_data/events/event_consequences.sql": "01_ARCH_RUNTIME_EVENTS_CONSEQUENCES.sql",
        "architecture/db_schema/runtime_data/sessions/active_sessions.sql": "01_ARCH_RUNTIME_SESSIONS_ACTIVE.sql",
        "architecture/db_schema/runtime_data/states/entity_states.sql": "01_ARCH_RUNTIME_STATES_ENTITY.sql",
        "architecture/db_schema/runtime_data/states/object_states.sql": "01_ARCH_RUNTIME_STATES_OBJECT.sql",
        "architecture/db_schema/runtime_data/states/entity_state_history.sql": "01_ARCH_RUNTIME_STATES_ENTITY_HISTORY.sql",
        
        # 참조 레이어 (시간순)
        "architecture/db_schema/reference_layer/cell_references.sql": "01_ARCH_REFERENCES_CELL.sql",
        "architecture/db_schema/reference_layer/entity_references.sql": "01_ARCH_REFERENCES_ENTITY.sql",
        "architecture/db_schema/reference_layer/object_references.sql": "01_ARCH_REFERENCES_OBJECT.sql",
        
        # 인프라 설정 (시간순)
        "guides/postgresql_5431_setup_guide.md": "01_GUIDE_POSTGRESQL_SETUP.md",
        "guides/postgres_setting.py": "01_GUIDE_POSTGRESQL_CONFIG.py",
        
        # 02. MVP 개발 및 구현 (2025-10-18) - 시간순
        "ideation/mvp_implementation_guide.md": "02_GUIDE_MVP_IMPLEMENTATION_CORE.md",
        "ideation/dev_mode_guide.md": "02_GUIDE_DEVELOPMENT_MODE.md",
        "ideation/world_tick_guide.md": "02_GUIDE_WORLD_TICK_SYSTEM.md",
        "ideation/deployment_guide.md": "02_GUIDE_DEPLOYMENT.md",
        "ideation/security_guide.md": "02_GUIDE_SECURITY.md",
        "ideation/testing_guide.md": "02_GUIDE_TESTING.md",
        "ideation/api_reference.md": "02_GUIDE_API_REFERENCE.md",
        "ideation/architecture_guide.md": "02_GUIDE_ARCHITECTURE.md",
        
        # 게임 디자인 (시간순)
        "ideation/game_design_document.md": "02_DESIGN_GAME_DOCUMENT.md",
        "ideation/effect_carrier_design.md": "02_DESIGN_EFFECT_CARRIER.md",
        "ideation/village_simulation_design.md": "02_DESIGN_VILLAGE_SIMULATION.md",
        
        # 개발 로그 (시간순)
        "project-management/phase1_development_log.md": "02_DEV_LOG_PHASE1.md",
        "project-management/phase2_development_log.md": "02_DEV_LOG_PHASE2.md",
        "project-management/phase3_development_log.md": "02_DEV_LOG_PHASE3.md",
        "project-management/phase4_development_log.md": "02_DEV_LOG_PHASE4.md",
        "project-management/phase5_development_log.md": "02_DEV_LOG_PHASE5.md",
        
        # 개발 계획 (시간순)
        "project-management/phase3_development_plan.md": "02_DEV_PLAN_PHASE3.md",
        "project-management/mvp_development_plan.md": "02_DEV_PLAN_MVP_V1.md",
        "project-management/mvp_development_plan_v2.md": "02_DEV_PLAN_MVP_V2.md",
        "project-management/immediate_development_plan.md": "02_DEV_PLAN_IMMEDIATE.md",
        "project-management/next_development_plan.md": "02_DEV_PLAN_NEXT.md",
        "project-management/village_simulation_plan.md": "02_DEV_PLAN_VILLAGE_SIMULATION.md",
        
        # 스키마 분석 (시간순)
        "project-management/schema_compatibility_report.md": "02_AUDIT_SCHEMA_COMPATIBILITY.md",
        "project-management/schema_comparison_report.md": "02_AUDIT_SCHEMA_COMPARISON.md",
        
        # MVP 검토 (시간순)
        "project-management/mvp_critical_review.md": "02_AUDIT_MVP_CRITICAL_REVIEW.md",
        "project-management/known_issues.md": "02_AUDIT_KNOWN_ISSUES.md",
        
        # 인프라 개발 (시간순)
        "infrastructure/database_infrastructure_guide.md": "02_INFRA_DATABASE_GUIDE.md",
        "infrastructure/database_infrastructure_completion_report.md": "02_INFRA_DATABASE_COMPLETION.md",
        
        # 03. 개발 완료 및 최종 검토 (2025-10-19) - 시간순
        "audit/manager_schema_compliance_audit.md": "03_AUDIT_MANAGER_SCHEMA_COMPLIANCE.md",
        "audit/abstraction_principle_audit.md": "03_AUDIT_ABSTRACTION_PRINCIPLE.md",
        "project-management/project_audit_report.md": "03_AUDIT_PROJECT.md",
        "project-management/critical_development_review.md": "03_AUDIT_CRITICAL_DEVELOPMENT_REVIEW.md",
        
        # 최종 개발 계획 및 보고서 (시간순)
        "project-management/phase6_development_plan.md": "03_DEV_PLAN_PHASE6.md",
        "project-management/final_phase_development_plan.md": "03_DEV_PLAN_FINAL_PHASE.md",
        "project-management/db_infrastructure_development_plan.md": "03_DEV_PLAN_DB_INFRASTRUCTURE.md",
        "project-management/jsonb_properties_and_unused_tables_plan.md": "03_DEV_PLAN_JSONB_PROPERTIES.md",
        "project-management/development_fix_plan.md": "03_DEV_PLAN_DEVELOPMENT_FIX.md",
        
        # 최종 보고서 (시간순)
        "project-management/phase6_completion_report.md": "03_REPORT_PHASE6_COMPLETION.md",
        "project-management/final_development_report.md": "03_REPORT_FINAL_DEVELOPMENT.md",
        
        # 개발 메모 (시간순)
        "ideation/dev_memo.md": "03_DEV_MEMO.md",
        "guides/game_design_memo.md": "03_DEV_MEMO_GAME_DESIGN.md",
        
        # 코딩 표준
        "rules/코딩 컨벤션 및 품질 가이드.md": "03_RULES_CODING_CONVENTIONS.md",
    }
    
    # 파일 이름 변경 실행
    success_count = 0
    error_count = 0
    
    for old_path, new_name in file_mappings.items():
        try:
            old_file_path = Path(old_path)
            new_file_path = Path(new_name)
            
            # 기존 파일이 존재하는지 확인
            if old_file_path.exists():
                # 새 파일이 이미 존재하는지 확인
                if new_file_path.exists():
                    logger.warning(f"새 파일이 이미 존재합니다: {new_name}")
                    continue
                
                # 파일 이동
                shutil.move(str(old_file_path), str(new_file_path))
                logger.info(f"성공: {old_path} -> {new_name}")
                success_count += 1
            else:
                logger.warning(f"기존 파일을 찾을 수 없습니다: {old_path}")
                
        except Exception as e:
            logger.error(f"오류 발생 {old_path} -> {new_name}: {str(e)}")
            error_count += 1
    
    logger.info(f"변경 완료: 성공 {success_count}개, 오류 {error_count}개")

if __name__ == "__main__":
    logger.info("문서 이름 변경을 시작합니다...")
    rename_documents()
    logger.info("문서 이름 변경이 완료되었습니다.")
