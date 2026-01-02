#!/usr/bin/env python3
"""
이미 변경된 문서들을 원래 폴더 구조로 복원하고
각 폴더 내에서 시간순으로 넘버링하는 스크립트
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

def organize_documents():
    """문서들을 원래 폴더 구조로 복원하고 시간순으로 정리"""
    
    # 현재 작업 디렉토리를 docs로 설정
    docs_path = Path(".")
    if not docs_path.exists():
        logger.error("docs 디렉토리를 찾을 수 없습니다.")
        return
    
    # 각 폴더별로 파일 매핑 정의 (새 이름 -> 원래 위치 + 시간순 넘버링)
    
    # 1. architecture/db_schema/ 폴더 정리
    arch_db_schema_files = {
        "01_ARCH_DB_SCHEMA_README.md": "architecture/db_schema/01_README.md",
        "01_ARCH_DB_EXTENSIONS.sql": "architecture/db_schema/01_extensions.sql", 
        "01_ARCH_DB_TABLES.sql": "architecture/db_schema/02_recreate_tables.sql",
        "01_ARCH_DB_TRIGGERS.sql": "architecture/db_schema/03_fix_triggers.sql",
        "01_ARCH_DATA_CONSISTENCY_ISSUES.md": "architecture/db_schema/04_data_consistency_issues.md",
        "01_ARCH_DIALOGUE_SIMULATION.md": "architecture/db_schema/05_dialogue_simulation.md",
        "01_ARCH_DIALOGUE_SYNC_ISSUES.md": "architecture/db_schema/06_dialogue_sync_issues.md",
        "01_ARCH_JSON_SCHEMAS.md": "architecture/db_schema/07_json_schemas.md",
    }
    
    # 2. architecture/db_schema/game_data/ 폴더 정리
    arch_game_data_files = {
        "01_ARCH_GAME_DATA_ENTITIES.sql": "architecture/db_schema/game_data/entities/01_entities.sql",
        "01_ARCH_GAME_DATA_ABILITIES.sql": "architecture/db_schema/game_data/entities/02_abilities.sql",
        "01_ARCH_GAME_DATA_EFFECTS.sql": "architecture/db_schema/game_data/entities/03_effects.sql",
        "01_ARCH_GAME_DATA_ITEMS.sql": "architecture/db_schema/game_data/entities/04_items.sql",
        "01_ARCH_GAME_DATA_EQUIPMENT.sql": "architecture/db_schema/game_data/entities/05_equipment.sql",
        "01_ARCH_GAME_DATA_BASE_PROPERTIES.sql": "architecture/db_schema/game_data/entities/06_base_properties.sql",
        "01_ARCH_GAME_DATA_LOCATIONS.sql": "architecture/db_schema/game_data/world/01_locations.sql",
        "01_ARCH_GAME_DATA_REGIONS.sql": "architecture/db_schema/game_data/world/02_regions.sql",
        "01_ARCH_GAME_DATA_CELLS.sql": "architecture/db_schema/game_data/world/03_cells.sql",
        "01_ARCH_GAME_DATA_WORLD_OBJECTS.sql": "architecture/db_schema/game_data/objects/01_world_objects.sql",
    }
    
    # 3. architecture/db_schema/runtime_data/ 폴더 정리
    arch_runtime_data_files = {
        "01_ARCH_RUNTIME_DIALOGUE_CONTEXTS.sql": "architecture/db_schema/runtime_data/dialogue/01_contexts.sql",
        "01_ARCH_RUNTIME_DIALOGUE_KNOWLEDGE.sql": "architecture/db_schema/runtime_data/dialogue/02_knowledge.sql",
        "01_ARCH_RUNTIME_DIALOGUE_HISTORY.sql": "architecture/db_schema/runtime_data/dialogue/03_history.sql",
        "01_ARCH_RUNTIME_DIALOGUE_STATES.sql": "architecture/db_schema/runtime_data/dialogue/04_states.sql",
        "01_ARCH_RUNTIME_DIALOGUE_PROCEDURES.sql": "architecture/db_schema/runtime_data/dialogue/05_procedures.sql",
        "01_ARCH_RUNTIME_EVENTS_TRIGGERED.sql": "architecture/db_schema/runtime_data/events/01_triggered_events.sql",
        "01_ARCH_RUNTIME_EVENTS_PLAYER_CHOICES.sql": "architecture/db_schema/runtime_data/events/02_player_choices.sql",
        "01_ARCH_RUNTIME_EVENTS_CONSEQUENCES.sql": "architecture/db_schema/runtime_data/events/03_event_consequences.sql",
        "01_ARCH_RUNTIME_SESSIONS_ACTIVE.sql": "architecture/db_schema/runtime_data/sessions/01_active_sessions.sql",
        "01_ARCH_RUNTIME_STATES_ENTITY.sql": "architecture/db_schema/runtime_data/states/01_entity_states.sql",
        "01_ARCH_RUNTIME_STATES_OBJECT.sql": "architecture/db_schema/runtime_data/states/02_object_states.sql",
        "01_ARCH_RUNTIME_STATES_ENTITY_HISTORY.sql": "architecture/db_schema/runtime_data/states/03_entity_state_history.sql",
    }
    
    # 4. architecture/db_schema/reference_layer/ 폴더 정리
    arch_reference_files = {
        "01_ARCH_REFERENCES_CELL.sql": "architecture/db_schema/reference_layer/01_cell_references.sql",
        "01_ARCH_REFERENCES_ENTITY.sql": "architecture/db_schema/reference_layer/02_entity_references.sql",
        "01_ARCH_REFERENCES_OBJECT.sql": "architecture/db_schema/reference_layer/03_object_references.sql",
    }
    
    # 5. guides/ 폴더 정리
    guides_files = {
        "01_GUIDE_POSTGRESQL_SETUP.md": "guides/01_postgresql_5431_setup_guide.md",
        "01_GUIDE_POSTGRESQL_CONFIG.py": "guides/02_postgres_setting.py",
        "03_DEV_MEMO_GAME_DESIGN.md": "guides/03_game_design_memo.md",
    }
    
    # 6. ideation/ 폴더 정리 (시간순으로 정렬)
    ideation_files = {
        "02_GUIDE_MVP_IMPLEMENTATION_CORE.md": "ideation/01_mvp_implementation_guide.md",
        "02_GUIDE_DEVELOPMENT_MODE.md": "ideation/02_dev_mode_guide.md", 
        "02_GUIDE_WORLD_TICK_SYSTEM.md": "ideation/03_world_tick_guide.md",
        "02_GUIDE_DEPLOYMENT.md": "ideation/04_deployment_guide.md",
        "02_GUIDE_SECURITY.md": "ideation/05_security_guide.md",
        "02_GUIDE_TESTING.md": "ideation/06_testing_guide.md",
        "02_GUIDE_API_REFERENCE.md": "ideation/07_api_reference.md",
        "02_GUIDE_ARCHITECTURE.md": "ideation/08_architecture_guide.md",
        "02_DESIGN_GAME_DOCUMENT.md": "ideation/09_game_design_document.md",
        "02_DESIGN_EFFECT_CARRIER.md": "ideation/10_effect_carrier_design.md",
        "02_DESIGN_VILLAGE_SIMULATION.md": "ideation/11_village_simulation_design.md",
        "03_DEV_MEMO.md": "ideation/12_dev_memo.md",
    }
    
    # 7. project-management/ 폴더 정리 (시간순으로 정렬)
    project_management_files = {
        "02_DEV_LOG_PHASE1.md": "project-management/01_phase1_development_log.md",
        "02_DEV_LOG_PHASE2.md": "project-management/02_phase2_development_log.md",
        "02_DEV_LOG_PHASE3.md": "project-management/03_phase3_development_log.md",
        "02_DEV_LOG_PHASE4.md": "project-management/04_phase4_development_log.md",
        "02_DEV_LOG_PHASE5.md": "project-management/05_phase5_development_log.md",
        "02_DEV_PLAN_PHASE3.md": "project-management/06_phase3_development_plan.md",
        "02_DEV_PLAN_MVP_V1.md": "project-management/07_mvp_development_plan.md",
        "02_DEV_PLAN_MVP_V2.md": "project-management/08_mvp_development_plan_v2.md",
        "02_DEV_PLAN_IMMEDIATE.md": "project-management/09_immediate_development_plan.md",
        "02_DEV_PLAN_NEXT.md": "project-management/10_next_development_plan.md",
        "02_DEV_PLAN_VILLAGE_SIMULATION.md": "project-management/11_village_simulation_plan.md",
        "02_AUDIT_SCHEMA_COMPATIBILITY.md": "project-management/12_schema_compatibility_report.md",
        "02_AUDIT_SCHEMA_COMPARISON.md": "project-management/13_schema_comparison_report.md",
        "02_AUDIT_MVP_CRITICAL_REVIEW.md": "project-management/14_mvp_critical_review.md",
        "02_AUDIT_KNOWN_ISSUES.md": "project-management/15_known_issues.md",
        "03_AUDIT_PROJECT.md": "project-management/16_project_audit_report.md",
        "03_AUDIT_CRITICAL_DEVELOPMENT_REVIEW.md": "project-management/17_critical_development_review.md",
        "03_DEV_PLAN_PHASE6.md": "project-management/18_phase6_development_plan.md",
        "03_DEV_PLAN_FINAL_PHASE.md": "project-management/19_final_phase_development_plan.md",
        "03_DEV_PLAN_DB_INFRASTRUCTURE.md": "project-management/20_db_infrastructure_development_plan.md",
        "03_DEV_PLAN_JSONB_PROPERTIES.md": "project-management/21_jsonb_properties_and_unused_tables_plan.md",
        "03_DEV_PLAN_DEVELOPMENT_FIX.md": "project-management/22_development_fix_plan.md",
        "03_REPORT_PHASE6_COMPLETION.md": "project-management/23_phase6_completion_report.md",
        "03_REPORT_FINAL_DEVELOPMENT.md": "project-management/24_final_development_report.md",
    }
    
    # 8. infrastructure/ 폴더 정리
    infrastructure_files = {
        "02_INFRA_DATABASE_GUIDE.md": "infrastructure/01_database_infrastructure_guide.md",
        "02_INFRA_DATABASE_COMPLETION.md": "infrastructure/02_database_infrastructure_completion_report.md",
    }
    
    # 9. audit/ 폴더 정리
    audit_files = {
        "03_AUDIT_MANAGER_SCHEMA_COMPLIANCE.md": "audit/01_manager_schema_compliance_audit.md",
        "03_AUDIT_ABSTRACTION_PRINCIPLE.md": "audit/02_abstraction_principle_audit.md",
    }
    
    # 10. rules/ 폴더 정리
    rules_files = {
        "03_RULES_CODING_CONVENTIONS.md": "rules/01_코딩_컨벤션_및_품질_가이드.md",
    }
    
    # 모든 파일 매핑을 하나로 합치기
    all_file_mappings = {
        **arch_db_schema_files,
        **arch_game_data_files,
        **arch_runtime_data_files,
        **arch_reference_files,
        **guides_files,
        **ideation_files,
        **project_management_files,
        **infrastructure_files,
        **audit_files,
        **rules_files,
    }
    
    # 파일 이름 변경 실행
    success_count = 0
    error_count = 0
    
    for current_name, new_path in all_file_mappings.items():
        try:
            current_file_path = Path(current_name)
            new_file_path = Path(new_path)
            
            # 기존 파일이 존재하는지 확인
            if current_file_path.exists():
                # 새 디렉토리가 존재하지 않으면 생성
                new_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 새 파일이 이미 존재하는지 확인
                if new_file_path.exists():
                    logger.warning(f"새 파일이 이미 존재합니다: {new_path}")
                    continue
                
                # 파일 이동
                shutil.move(str(current_file_path), str(new_file_path))
                logger.info(f"성공: {current_name} -> {new_path}")
                success_count += 1
            else:
                logger.warning(f"기존 파일을 찾을 수 없습니다: {current_name}")
                
        except Exception as e:
            logger.error(f"오류 발생 {current_name} -> {new_path}: {str(e)}")
            error_count += 1
    
    logger.info(f"정리 완료: 성공 {success_count}개, 오류 {error_count}개")

if __name__ == "__main__":
    logger.info("문서 구조 복원 및 시간순 정리를 시작합니다...")
    organize_documents()
    logger.info("문서 구조 복원 및 시간순 정리가 완료되었습니다.")
