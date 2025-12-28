"""
Framework Manager - 프레임워크 중앙 관리 시스템
아키텍처 리팩토링, 성능 최적화, 모듈 통합 관리
"""
import asyncio
import sys
import os
from typing import Dict, Any, List, Optional, Type, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import uuid
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.connection import DatabaseConnection
from common.utils.logger import logger
from common.error_handling.error_types import (
    ErrorContext, SystemError, BusinessLogicError
)

class ModuleStatus(str, Enum):
    """모듈 상태"""
    INITIALIZED = "initialized"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class ModuleInfo:
    """모듈 정보"""
    module_name: str
    module_type: str
    status: ModuleStatus
    dependencies: List[str]
    performance_metrics: Dict[str, Any]
    last_updated: datetime

class FrameworkManager:
    """프레임워크 중앙 관리 시스템"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.modules: Dict[str, Any] = {}
        self.module_info: Dict[str, ModuleInfo] = {}
        self.is_initialized = False
        self.performance_cache: Dict[str, Any] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        
    async def initialize(self):
        """프레임워크 초기화"""
        try:
            await self.db.initialize()
            await self._load_module_dependencies()
            await self._initialize_core_modules()
            self.is_initialized = True
            logger.info("FrameworkManager 초기화 완료")
        except Exception as e:
            logger.error(f"FrameworkManager 초기화 실패: {e}")
            raise SystemError(
                message=f"프레임워크 초기화 실패: {str(e)}",
                error_code="FRAMEWORK_INIT_FAILED"
            )
    
    async def cleanup(self):
        """프레임워크 정리"""
        try:
            await self._stop_all_modules()
            await self.db.close()
            self.is_initialized = False
            logger.info("FrameworkManager 정리 완료")
        except Exception as e:
            logger.error(f"FrameworkManager 정리 실패: {e}")
    
    async def _load_module_dependencies(self):
        """모듈 의존성 로드"""
        # 핵심 모듈 의존성 정의
        self.dependency_graph = {
            "DatabaseConnection": [],
            "ErrorHandler": ["DatabaseConnection"],
            "TimeSystem": ["DatabaseConnection", "ErrorHandler"],
            "EntityManager": ["DatabaseConnection", "ErrorHandler"],
            "CellManager": ["DatabaseConnection", "ErrorHandler", "EntityManager"],
            "DialogueManager": ["DatabaseConnection", "ErrorHandler", "EntityManager"],
            "ActionHandler": ["DatabaseConnection", "ErrorHandler", "EntityManager", "CellManager"]
        }
        
        logger.info(f"모듈 의존성 로드: {len(self.dependency_graph)}개 모듈")
    
    async def _initialize_core_modules(self):
        """핵심 모듈 초기화"""
        # 의존성 순서대로 모듈 초기화
        initialization_order = self._get_initialization_order()
        
        for module_name in initialization_order:
            try:
                await self._initialize_module(module_name)
                logger.info(f"모듈 초기화 완료: {module_name}")
            except Exception as e:
                logger.error(f"모듈 초기화 실패: {module_name} - {e}")
                raise
    
    def _get_initialization_order(self) -> List[str]:
        """초기화 순서 계산 (의존성 기반)"""
        visited = set()
        temp_visited = set()
        result = []
        
        def dfs(node):
            if node in temp_visited:
                raise ValueError(f"순환 의존성 발견: {node}")
            if node in visited:
                return
            
            temp_visited.add(node)
            for dependency in self.dependency_graph.get(node, []):
                dfs(dependency)
            temp_visited.remove(node)
            visited.add(node)
            result.append(node)
        
        for module in self.dependency_graph:
            if module not in visited:
                dfs(module)
        
        return result
    
    async def _initialize_module(self, module_name: str):
        """개별 모듈 초기화"""
        if module_name == "DatabaseConnection":
            self.modules["DatabaseConnection"] = self.db
            self.module_info["DatabaseConnection"] = ModuleInfo(
                module_name="DatabaseConnection",
                module_type="infrastructure",
                status=ModuleStatus.INITIALIZED,
                dependencies=[],
                performance_metrics={},
                last_updated=datetime.now()
            )
        
        elif module_name == "ErrorHandler":
            from common.error_handling.error_handler import error_handler
            self.modules["ErrorHandler"] = error_handler
            self.module_info["ErrorHandler"] = ModuleInfo(
                module_name="ErrorHandler",
                module_type="infrastructure",
                status=ModuleStatus.INITIALIZED,
                dependencies=["DatabaseConnection"],
                performance_metrics={},
                last_updated=datetime.now()
            )
        
        elif module_name == "TimeSystem":
            from app.systems.time_system import time_system
            await time_system.initialize()
            self.modules["TimeSystem"] = time_system
            self.module_info["TimeSystem"] = ModuleInfo(
                module_name="TimeSystem",
                module_type="system",
                status=ModuleStatus.INITIALIZED,
                dependencies=["DatabaseConnection", "ErrorHandler"],
                performance_metrics={},
                last_updated=datetime.now()
            )
        
        elif module_name == "EntityManager":
            from app.managers.entity_manager import EntityManager
            from database.repositories.game_data import GameDataRepository
            from database.repositories.runtime_data import RuntimeDataRepository
            from database.repositories.reference_layer import ReferenceLayerRepository
            
            # Repository 인스턴스 생성
            game_data_repo = GameDataRepository(self.modules["DatabaseConnection"])
            runtime_data_repo = RuntimeDataRepository(self.modules["DatabaseConnection"])
            reference_layer_repo = ReferenceLayerRepository(self.modules["DatabaseConnection"])
            
            entity_manager = EntityManager(
                self.modules["DatabaseConnection"],
                game_data_repo,
                runtime_data_repo,
                reference_layer_repo
            )
            self.modules["EntityManager"] = entity_manager
            self.module_info["EntityManager"] = ModuleInfo(
                module_name="EntityManager",
                module_type="manager",
                status=ModuleStatus.INITIALIZED,
                dependencies=["DatabaseConnection", "ErrorHandler"],
                performance_metrics={},
                last_updated=datetime.now()
            )
        
        elif module_name == "CellManager":
            from app.managers.cell_manager import CellManager
            from database.repositories.game_data import GameDataRepository
            from database.repositories.runtime_data import RuntimeDataRepository
            from database.repositories.reference_layer import ReferenceLayerRepository
            
            # Repository 인스턴스 생성
            game_data_repo = GameDataRepository(self.modules["DatabaseConnection"])
            runtime_data_repo = RuntimeDataRepository(self.modules["DatabaseConnection"])
            reference_layer_repo = ReferenceLayerRepository(self.modules["DatabaseConnection"])
            
            cell_manager = CellManager(
                self.modules["DatabaseConnection"],
                game_data_repo,
                runtime_data_repo,
                reference_layer_repo,
                self.modules["EntityManager"]
            )
            self.modules["CellManager"] = cell_manager
            self.module_info["CellManager"] = ModuleInfo(
                module_name="CellManager",
                module_type="manager",
                status=ModuleStatus.INITIALIZED,
                dependencies=["DatabaseConnection", "ErrorHandler", "EntityManager"],
                performance_metrics={},
                last_updated=datetime.now()
            )
        
        elif module_name == "DialogueManager":
            from app.managers.dialogue_manager import DialogueManager
            from database.repositories.game_data import GameDataRepository
            from database.repositories.runtime_data import RuntimeDataRepository
            from database.repositories.reference_layer import ReferenceLayerRepository
            
            # Repository 인스턴스 생성
            game_data_repo = GameDataRepository(self.modules["DatabaseConnection"])
            runtime_data_repo = RuntimeDataRepository(self.modules["DatabaseConnection"])
            reference_layer_repo = ReferenceLayerRepository(self.modules["DatabaseConnection"])
            
            dialogue_manager = DialogueManager(
                self.modules["DatabaseConnection"],
                game_data_repo,
                runtime_data_repo,
                reference_layer_repo,
                self.modules["EntityManager"]
            )
            self.modules["DialogueManager"] = dialogue_manager
            self.module_info["DialogueManager"] = ModuleInfo(
                module_name="DialogueManager",
                module_type="manager",
                status=ModuleStatus.INITIALIZED,
                dependencies=["DatabaseConnection", "ErrorHandler", "EntityManager"],
                performance_metrics={},
                last_updated=datetime.now()
            )
        
        elif module_name == "ActionHandler":
            from app.handlers.action_handler import ActionHandler
            from database.repositories.game_data import GameDataRepository
            from database.repositories.runtime_data import RuntimeDataRepository
            from database.repositories.reference_layer import ReferenceLayerRepository
            
            # Repository 인스턴스 생성
            game_data_repo = GameDataRepository(self.modules["DatabaseConnection"])
            runtime_data_repo = RuntimeDataRepository(self.modules["DatabaseConnection"])
            reference_layer_repo = ReferenceLayerRepository(self.modules["DatabaseConnection"])
            
            action_handler = ActionHandler(
                self.modules["DatabaseConnection"],
                game_data_repo,
                runtime_data_repo,
                reference_layer_repo,
                self.modules["EntityManager"],
                self.modules["CellManager"]
            )
            self.modules["ActionHandler"] = action_handler
            self.module_info["ActionHandler"] = ModuleInfo(
                module_name="ActionHandler",
                module_type="manager",
                status=ModuleStatus.INITIALIZED,
                dependencies=["DatabaseConnection", "ErrorHandler", "EntityManager", "CellManager"],
                performance_metrics={},
                last_updated=datetime.now()
            )
    
    async def _stop_all_modules(self):
        """모든 모듈 중지"""
        # 역순으로 모듈 중지
        stop_order = list(reversed(self._get_initialization_order()))
        
        for module_name in stop_order:
            try:
                await self._stop_module(module_name)
                logger.info(f"모듈 중지 완료: {module_name}")
            except Exception as e:
                logger.error(f"모듈 중지 실패: {module_name} - {e}")
    
    async def _stop_module(self, module_name: str):
        """개별 모듈 중지"""
        if module_name in self.modules:
            module = self.modules[module_name]
            
            # 모듈별 정리 메서드 호출
            if hasattr(module, 'cleanup'):
                await module.cleanup()
            elif hasattr(module, 'close'):
                await module.close()
            
            # 상태 업데이트
            if module_name in self.module_info:
                self.module_info[module_name].status = ModuleStatus.STOPPED
                self.module_info[module_name].last_updated = datetime.now()
    
    async def get_module(self, module_name: str) -> Optional[Any]:
        """모듈 조회"""
        return self.modules.get(module_name)
    
    async def get_module_status(self, module_name: str) -> Optional[ModuleStatus]:
        """모듈 상태 조회"""
        if module_name in self.module_info:
            return self.module_info[module_name].status
        return None
    
    async def get_all_module_status(self) -> Dict[str, ModuleStatus]:
        """모든 모듈 상태 조회"""
        return {
            name: info.status 
            for name, info in self.module_info.items()
        }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        metrics = {
            "total_modules": len(self.modules),
            "initialized_modules": sum(
                1 for info in self.module_info.values() 
                if info.status == ModuleStatus.INITIALIZED
            ),
            "running_modules": sum(
                1 for info in self.module_info.values() 
                if info.status == ModuleStatus.RUNNING
            ),
            "error_modules": sum(
                1 for info in self.module_info.values() 
                if info.status == ModuleStatus.ERROR
            ),
            "module_details": {
                name: {
                    "status": info.status.value,
                    "dependencies": info.dependencies,
                    "performance_metrics": info.performance_metrics,
                    "last_updated": info.last_updated.isoformat()
                }
                for name, info in self.module_info.items()
            }
        }
        
        return metrics
    
    async def optimize_performance(self):
        """성능 최적화"""
        try:
            # DB 연결 풀 최적화
            if "DatabaseConnection" in self.modules:
                db = self.modules["DatabaseConnection"]
                if hasattr(db, 'optimize_connection_pool'):
                    await db.optimize_connection_pool()
            
            # 캐시 최적화
            await self._optimize_caches()
            
            # 메모리 최적화
            await self._optimize_memory()
            
            logger.info("성능 최적화 완료")
            
        except Exception as e:
            logger.error(f"성능 최적화 실패: {e}")
            raise SystemError(
                message=f"성능 최적화 실패: {str(e)}",
                error_code="PERFORMANCE_OPTIMIZATION_FAILED"
            )
    
    async def _optimize_caches(self):
        """캐시 최적화"""
        # 모듈별 캐시 최적화
        for module_name, module in self.modules.items():
            if hasattr(module, 'optimize_cache'):
                await module.optimize_cache()
                logger.info(f"📈 캐시 최적화: {module_name}")
    
    async def _optimize_memory(self):
        """메모리 최적화"""
        # 가비지 컬렉션 강제 실행
        import gc
        gc.collect()
        
        # 메모리 사용량 모니터링
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        self.performance_cache["memory_usage"] = {
            "rss": memory_info.rss,
            "vms": memory_info.vms,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"메모리 사용량: {memory_info.rss / 1024 / 1024:.2f} MB")
    
    async def health_check(self) -> Dict[str, Any]:
        """헬스 체크"""
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "modules": {},
            "issues": []
        }
        
        # 모듈별 헬스 체크
        for module_name, module in self.modules.items():
            try:
                if hasattr(module, 'health_check'):
                    module_health = await module.health_check()
                    health_status["modules"][module_name] = module_health
                else:
                    health_status["modules"][module_name] = {
                        "status": "unknown",
                        "message": "health_check method not implemented"
                    }
            except Exception as e:
                health_status["modules"][module_name] = {
                    "status": "error",
                    "message": str(e)
                }
                health_status["issues"].append(f"{module_name}: {str(e)}")
        
        # 전체 상태 결정
        if health_status["issues"]:
            health_status["overall_status"] = "degraded"
        
        return health_status
    
    async def export_framework_report(self, file_path: str):
        """프레임워크 보고서 내보내기"""
        report = {
            "export_timestamp": datetime.now().isoformat(),
            "framework_status": {
                "is_initialized": self.is_initialized,
                "total_modules": len(self.modules),
                "dependency_graph": self.dependency_graph
            },
            "module_status": await self.get_all_module_status(),
            "performance_metrics": await self.get_performance_metrics(),
            "health_check": await self.health_check()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"프레임워크 보고서 저장: {file_path}")

# 전역 FrameworkManager 인스턴스
framework_manager = FrameworkManager()

# 편의 함수들
async def initialize_framework():
    """프레임워크 초기화 편의 함수"""
    await framework_manager.initialize()

async def cleanup_framework():
    """프레임워크 정리 편의 함수"""
    await framework_manager.cleanup()

async def get_module(module_name: str) -> Optional[Any]:
    """모듈 조회 편의 함수"""
    return await framework_manager.get_module(module_name)

async def get_framework_status() -> Dict[str, Any]:
    """프레임워크 상태 조회 편의 함수"""
    return {
        "module_status": await framework_manager.get_all_module_status(),
        "performance_metrics": await framework_manager.get_performance_metrics(),
        "health_check": await framework_manager.health_check()
    }
