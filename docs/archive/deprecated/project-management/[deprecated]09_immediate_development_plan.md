# [deprecated] 즉각적인 개발 계획

> **Deprecated 날짜**: 2025-12-28  
> **Deprecated 이유**: 즉각적인 개발 계획이 완료되어 더 이상 진행 중인 작업이 아님. 현재는 Phase 4+ 개발이 진행 중이며, 이 계획의 목표들은 대부분 달성되었음.  
> **계획 수립일**: 2025-10-18  
> **목표**: 3-5일 내 MVP 완전 구현  
> **우선순위**: 실행 가능성 확보 → 게임 플로우 완성 → MVP 완성

## 🚨 **Phase 3.5: 실행 가능성 확보 (1-2일)**

### **우선순위 1: Python 경로 문제 해결 (즉시)**

#### **해결 방안 A: 실행 스크립트 생성**
```python
# run_dashboard.py
import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from app.ui.dashboard import main

if __name__ == "__main__":
    main()
```

#### **해결 방안 B: PYTHONPATH 환경변수 설정**
```bash
# Windows PowerShell
$env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)"

# Linux/Mac
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### **해결 방안 C: setup.py 생성**
```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="rpg_engine",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.0",
        "qasync>=0.24.0",
        "asyncpg>=0.28.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0"
    ]
)
```

### **우선순위 2: 게임 플로우 완성 (1일)**

#### **2.1 GameManager 연동**
- **세션 생성**: `start_new_game()` 메서드 실제 동작
- **플레이어 생성**: 런타임 플레이어 엔티티 자동 생성
- **시작 셀 설정**: 플레이어를 시작 셀에 배치

#### **2.2 UI 연동**
- **"새 게임" 버튼**: 실제 게임 시작 기능
- **게임 상태 표시**: 현재 셀, 플레이어 정보 표시
- **행동 버튼**: 조사/대화/거래/방문/대기 실제 동작

#### **2.3 데이터 영속성**
- **게임 저장**: 세션 상태 데이터베이스 저장
- **게임 로드**: 저장된 세션 복구
- **자동 저장**: 중요한 행동 후 자동 저장

### **우선순위 3: 통합 테스트 (0.5일)**

#### **3.1 실제 플레이 테스트**
```python
# test_full_game_flow.py
async def test_complete_game_flow():
    # 1. 새 게임 시작
    session_id = await game_manager.start_new_game("player_template_001", "CELL_VILLAGE_CENTER_001")
    
    # 2. 플레이어가 셀에 진입
    enter_result = await cell_manager.enter_cell("CELL_VILLAGE_CENTER_001", player_id)
    
    # 3. 조사 행동
    investigate_result = await action_handler.handle_action(player_id, ActionType.INVESTIGATE, cell_id)
    
    # 4. NPC와 대화
    dialogue_result = await dialogue_manager.start_dialogue(player_id, npc_id, cell_id)
    
    # 5. 게임 저장
    save_result = await game_manager.save_game(session_id)
```

#### **3.2 UI 연동 테스트**
- **모든 버튼 동작**: 조사/대화/거래/방문/대기 버튼 테스트
- **실시간 피드백**: 월드 로그 업데이트 확인
- **정보 패널**: 인벤토리/자산/관계/로어 탭 동작 확인

## 🎯 **Phase 4: MVP 완성 (2-3일)**

### **우선순위 4: Dev Mode 구현 (1일)**

#### **4.1 Runtime → Game Data 승격**
```python
# app/core/dev_mode.py
class DevModeManager:
    async def promote_entity_to_game_data(self, entity_id: str) -> bool:
        """런타임 엔티티를 게임 데이터로 승격"""
        # 1. 런타임 엔티티 조회
        runtime_entity = await self.entity_manager.get_entity(entity_id, is_runtime=True)
        
        # 2. 게임 데이터로 변환
        game_entity = self._convert_to_game_data(runtime_entity)
        
        # 3. 게임 데이터 저장
        await self.game_data_repo.create_entity(game_entity)
        
        # 4. 참조 레이어 업데이트
        await self.reference_layer_repo.create_entity_reference(entity_id, game_entity.entity_id)
        
        return True
```

#### **4.2 Dev Mode UI**
- **승격 버튼**: 1-click promote 기능
- **실시간 편집**: 게임 데이터 실시간 수정
- **데이터 검증**: 승격 시 무결성 검증

### **우선순위 5: 최종 통합 테스트 (1일)**

#### **5.1 MVP 수용 기준 달성**
- **100회 연속 무오류 플레이**: 자동화된 테스트
- **DevMode 승격**: 생성한 NPC가 다음 세션에서 템플릿으로 노출
- **룰 기반 플레이**: LLM 비활성 시에도 플레이 가능

#### **5.2 성능 최적화**
- **DB 쿼리 최적화**: 인덱스 활용 확인
- **캐시 효율성**: Manager 캐시 동작 확인
- **메모리 사용량**: 장시간 플레이 시 메모리 누수 방지

### **우선순위 6: 사용자 경험 개선 (1일)**

#### **6.1 UI/UX 개선**
- **직관적 인터페이스**: 버튼 배치 및 색상 최적화
- **반응성**: 버튼 클릭 시 즉시 피드백
- **접근성**: 키보드 단축키 지원

#### **6.2 게임 밸런스**
- **행동 결과**: 각 행동의 의미 있는 결과
- **NPC 반응**: 다양한 NPC 성격과 대화
- **이벤트 시스템**: 예측 가능한 이벤트 발생

## 📅 **상세 일정표**

### **Day 1 (2025-10-18)**
- **오전**: Python 경로 문제 해결
- **오후**: 게임 플로우 완성 (GameManager 연동)

### **Day 2 (2025-10-19)**
- **오전**: UI 연동 및 데이터 영속성
- **오후**: 통합 테스트 및 버그 수정

### **Day 3 (2025-10-20)**
- **오전**: Dev Mode 구현
- **오후**: Runtime → Game Data 승격 기능

### **Day 4 (2025-10-21)**
- **오전**: 최종 통합 테스트
- **오후**: 성능 최적화 및 사용자 경험 개선

### **Day 5 (2025-10-22)**
- **오전**: MVP 수용 기준 달성 확인
- **오후**: 최종 버그 수정 및 문서화

## 🎯 **성공 지표**

### **Phase 3.5 완료 기준**
- ✅ `python run_dashboard.py` 실행 성공
- ✅ "새 게임" 버튼으로 실제 게임 시작 가능
- ✅ 조사/대화/거래/방문/대기 행동 모두 동작
- ✅ 게임 상태 저장/로드 가능

### **Phase 4 완료 기준**
- ✅ 100회 연속 무오류 플레이 달성
- ✅ DevMode에서 생성한 NPC가 다음 세션에서 템플릿으로 노출
- ✅ LLM 비활성 시에도 룰 기반 플레이 가능
- ✅ 모든 MVP 수용 기준 달성

## 🚀 **즉시 시작할 작업**

### **1. Python 경로 문제 해결 (30분)**
```bash
# run_dashboard.py 생성
# 실행 테스트
python run_dashboard.py
```

### **2. 게임 플로우 완성 (2시간)**
```python
# GameManager.start_new_game() 실제 구현
# 플레이어 엔티티 생성 로직
# 시작 셀 배치 로직
```

### **3. UI 연동 (1시간)**
```python
# "새 게임" 버튼 실제 동작
# 행동 버튼 실제 동작
# 월드 로그 실시간 업데이트
```

**예상 완성 시점**: 2025-10-22 (5일 후)  
**현재 완성도**: 60% → **목표 완성도**: 100%
