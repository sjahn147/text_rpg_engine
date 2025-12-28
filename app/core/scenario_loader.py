import json
import yaml
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

class ScenarioLoader:
    """시나리오 파일을 로드하고 검증하는 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['.json', '.yaml', '.yml']
    
    def load_scenario(self, file_path: str) -> Dict[str, Any]:
        """
        시나리오 파일을 로드합니다.
        
        Args:
            file_path: 시나리오 파일 경로
            
        Returns:
            로드된 시나리오 데이터
            
        Raises:
            FileNotFoundError: 파일이 존재하지 않는 경우
            ValueError: 지원하지 않는 파일 형식인 경우
            json.JSONDecodeError: JSON 파싱 오류
            yaml.YAMLError: YAML 파싱 오류
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"시나리오 파일을 찾을 수 없습니다: {file_path}")
        
        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {file_path.suffix}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    scenario_data = json.load(f)
                else:  # .yaml or .yml
                    scenario_data = yaml.safe_load(f)
            
            self.logger.info(f"시나리오 파일 로드 완료: {file_path}")
            
            # 시나리오 검증
            self.validate_scenario(scenario_data)
            
            return scenario_data
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"시나리오 파일 파싱 오류: {str(e)}")
    
    def validate_scenario(self, scenario_data: Dict[str, Any]) -> None:
        """
        시나리오 데이터를 검증합니다.
        
        Args:
            scenario_data: 검증할 시나리오 데이터
            
        Raises:
            ValueError: 검증 실패 시
        """
        required_fields = ['name', 'version', 'steps']
        
        for field in required_fields:
            if field not in scenario_data:
                raise ValueError(f"필수 필드가 누락되었습니다: {field}")
        
        if not isinstance(scenario_data['steps'], list):
            raise ValueError("steps는 리스트여야 합니다.")
        
        if len(scenario_data['steps']) == 0:
            raise ValueError("최소 하나의 step이 필요합니다.")
        
        # 각 step 검증
        for i, step in enumerate(scenario_data['steps']):
            self.validate_step(step, i)
        
        self.logger.info(f"시나리오 검증 완료: {scenario_data.get('name', 'Unknown')}")
    
    def validate_step(self, step: Dict[str, Any], step_index: int) -> None:
        """
        개별 step을 검증합니다.
        
        Args:
            step: 검증할 step 데이터
            step_index: step 인덱스
            
        Raises:
            ValueError: 검증 실패 시
        """
        required_fields = ['type', 'description']
        
        for field in required_fields:
            if field not in step:
                raise ValueError(f"Step {step_index}: 필수 필드가 누락되었습니다: {field}")
        
        step_type = step['type']
        supported_types = [
            'setup_data', 'create_session', 'create_entity', 
            'move_entity', 'start_dialogue', 'interact', 
            'update_stats', 'complete_event', 'cleanup'
        ]
        
        if step_type not in supported_types:
            raise ValueError(f"Step {step_index}: 지원하지 않는 step 타입입니다: {step_type}")
    
    def list_scenarios(self, directory: str) -> List[str]:
        """
        디렉토리에서 사용 가능한 시나리오 파일들을 나열합니다.
        
        Args:
            directory: 검색할 디렉토리 경로
            
        Returns:
            시나리오 파일 경로 리스트
        """
        scenario_files = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return scenario_files
        
        for file_path in dir_path.rglob('*'):
            if file_path.suffix.lower() in self.supported_formats:
                scenario_files.append(str(file_path))
        
        return sorted(scenario_files)
    
    def get_scenario_info(self, file_path: str) -> Dict[str, Any]:
        """
        시나리오 파일의 기본 정보를 조회합니다.
        
        Args:
            file_path: 시나리오 파일 경로
            
        Returns:
            시나리오 기본 정보
        """
        try:
            scenario_data = self.load_scenario(file_path)
            
            return {
                'name': scenario_data.get('name', 'Unknown'),
                'version': scenario_data.get('version', '1.0'),
                'description': scenario_data.get('description', ''),
                'author': scenario_data.get('author', 'Unknown'),
                'step_count': len(scenario_data.get('steps', [])),
                'file_path': file_path,
                'file_size': os.path.getsize(file_path)
            }
        except Exception as e:
            return {
                'name': 'Error',
                'error': str(e),
                'file_path': file_path
            } 