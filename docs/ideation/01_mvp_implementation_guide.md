# MVP 구현 가이드

> **문서 버전**: v1.0  
> **작성일**: 2025-10-18  
> **최종 수정**: 2025-10-18

## 🎯 **MVP 구현 개요**

이 문서는 RPG Engine의 MVP(Minimum Viable Product) 구현을 위한 상세 가이드입니다. 계기판 UI와 코어 루프 구현에 중점을 둡니다.

### **MVP 목표**
- **계기판 UI**: 텍스트 기반 UI, 월드맵(리스트), Region→Location→Cell 전환
- **핵심 행동**: 조사/대화/거래/방문/대기
- **최소 데이터**: 도시 1(레크로스타), Location ≥3, NPC ≥2, 이벤트 ≥1
- **Dev Mode**: 엔티티/로어 추가, **promote** 1‑click
- **로그/저장**: 세션 저장·복구, 행동/세계 이벤트 기록

---

## 🎨 **계기판 UI 구현**

### **레이아웃 설계**

#### **상단 바**
```python
class TopBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # 현재 위치 정보
        self.location_label = QLabel("Region: Forest Village")
        self.cell_label = QLabel("Cell: Village Square")
        
        # 시간 정보
        self.time_label = QLabel("Time: 14:30")
        self.weather_label = QLabel("Weather: Clear")
        
        layout.addWidget(self.location_label)
        layout.addWidget(self.cell_label)
        layout.addStretch()
        layout.addWidget(self.time_label)
        layout.addWidget(self.weather_label)
        
        self.setLayout(layout)
```

#### **좌측 패널 (행동)**
```python
class ActionPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 행동 버튼들
        self.investigate_btn = QPushButton("🔍 조사")
        self.dialogue_btn = QPushButton("💬 대화")
        self.trade_btn = QPushButton("💰 거래")
        self.visit_btn = QPushButton("🚶 방문")
        self.wait_btn = QPushButton("⏰ 대기")
        
        # 버튼 스타일링
        for btn in [self.investigate_btn, self.dialogue_btn, self.trade_btn, 
                   self.visit_btn, self.wait_btn]:
            btn.setMinimumHeight(40)
            btn.setStyleSheet("QPushButton { font-size: 14px; }")
        
        layout.addWidget(self.investigate_btn)
        layout.addWidget(self.dialogue_btn)
        layout.addWidget(self.trade_btn)
        layout.addWidget(self.visit_btn)
        layout.addWidget(self.wait_btn)
        
        self.setLayout(layout)
```

#### **중앙 패널 (월드 로그)**
```python
class WorldLogPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 로그 텍스트 영역
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(400)
        
        # 스크롤바 설정
        self.log_text.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        layout.addWidget(QLabel("🌍 월드 로그"))
        layout.addWidget(self.log_text)
        
        self.setLayout(layout)
    
    def add_log_entry(self, message: str, log_type: str = "info"):
        """로그 엔트리 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if log_type == "action":
            prefix = "🎯"
        elif log_type == "result":
            prefix = "📝"
        elif log_type == "event":
            prefix = "⚡"
        else:
            prefix = "ℹ️"
        
        formatted_message = f"[{timestamp}] {prefix} {message}"
        self.log_text.append(formatted_message)
        
        # 자동 스크롤
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
```

#### **우측 패널 (정보)**
```python
class InfoPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 탭 위젯
        self.tab_widget = QTabWidget()
        
        # 인벤토리 탭
        self.inventory_tab = QWidget()
        self.inventory_list = QListWidget()
        inventory_layout = QVBoxLayout()
        inventory_layout.addWidget(self.inventory_list)
        self.inventory_tab.setLayout(inventory_layout)
        
        # 자산 탭
        self.assets_tab = QWidget()
        self.assets_label = QLabel("Gold: 100\nItems: 5")
        assets_layout = QVBoxLayout()
        assets_layout.addWidget(self.assets_label)
        self.assets_tab.setLayout(assets_layout)
        
        # 관계/기록 탭
        self.relations_tab = QWidget()
        self.relations_list = QListWidget()
        relations_layout = QVBoxLayout()
        relations_layout.addWidget(self.relations_list)
        self.relations_tab.setLayout(relations_layout)
        
        # 로어/지도 탭
        self.lore_tab = QWidget()
        self.lore_list = QListWidget()
        lore_layout = QVBoxLayout()
        lore_layout.addWidget(self.lore_list)
        self.lore_tab.setLayout(lore_layout)
        
        # 탭 추가
        self.tab_widget.addTab(self.inventory_tab, "🎒 인벤토리")
        self.tab_widget.addTab(self.assets_tab, "💰 자산")
        self.tab_widget.addTab(self.relations_tab, "👥 관계")
        self.tab_widget.addTab(self.lore_tab, "📚 로어")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
```

#### **하단 패널 (명령 입력)**
```python
class CommandPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # 명령 입력
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("명령을 입력하세요...")
        self.command_input.returnPressed.connect(self.execute_command)
        
        # 최근 로그 5개
        self.recent_logs = QLabel("최근 로그: 조사 → 대화 → 거래")
        
        layout.addWidget(QLabel("💬 명령:"))
        layout.addWidget(self.command_input)
        layout.addWidget(self.recent_logs)
        
        self.setLayout(layout)
    
    def execute_command(self):
        """명령 실행"""
        command = self.command_input.text().strip()
        if command:
            # 명령 처리 로직
            self.command_input.clear()
```

### **메인 윈도우 통합**
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        self.setWindowTitle("RPG Engine - 계기판")
        self.setGeometry(100, 100, 1200, 800)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QHBoxLayout()
        
        # 좌측 패널
        self.action_panel = ActionPanel()
        main_layout.addWidget(self.action_panel, 1)
        
        # 중앙 패널
        self.world_log_panel = WorldLogPanel()
        main_layout.addWidget(self.world_log_panel, 3)
        
        # 우측 패널
        self.info_panel = InfoPanel()
        main_layout.addWidget(self.info_panel, 2)
        
        # 하단 패널
        bottom_layout = QVBoxLayout()
        self.command_panel = CommandPanel()
        bottom_layout.addWidget(self.command_panel)
        
        # 전체 레이아웃
        full_layout = QVBoxLayout()
        full_layout.addLayout(main_layout)
        full_layout.addLayout(bottom_layout)
        
        central_widget.setLayout(full_layout)
    
    def setup_connections(self):
        """이벤트 연결"""
        self.action_panel.investigate_btn.clicked.connect(self.investigate)
        self.action_panel.dialogue_btn.clicked.connect(self.dialogue)
        self.action_panel.trade_btn.clicked.connect(self.trade)
        self.action_panel.visit_btn.clicked.connect(self.visit)
        self.action_panel.wait_btn.clicked.connect(self.wait)
```

---

## 🔄 **코어 루프 구현**

### **플레이 경험 & 코어 루프**

#### **1. 월드맵에서 Region 선택**
```python
class RegionSelector:
    def __init__(self):
        self.regions = {
            "forest_village": {
                "name": "Forest Village",
                "description": "평화로운 숲 마을",
                "entry_cost": 0,
                "travel_time": 0
            }
        }
    
    async def select_region(self, region_id: str, player_id: str):
        """지역 선택 및 입장"""
        region = self.regions.get(region_id)
        if not region:
            raise ValueError(f"Unknown region: {region_id}")
        
        # 입장 비용 확인
        if region["entry_cost"] > 0:
            # 플레이어 자산 확인
            player_assets = await self.get_player_assets(player_id)
            if player_assets["gold"] < region["entry_cost"]:
                return {"success": False, "message": "자금이 부족합니다."}
        
        # 이동 시간 처리
        if region["travel_time"] > 0:
            await self.process_travel_time(region["travel_time"])
        
        # 지역 입장
        await self.enter_region(player_id, region_id)
        return {"success": True, "message": f"{region['name']}에 입장했습니다."}
```

#### **2. Location 진입**
```python
class LocationManager:
    def __init__(self):
        self.locations = {
            "village_square": {
                "name": "Village Square",
                "type": "public",
                "description": "마을의 중심 광장"
            },
            "weapon_shop": {
                "name": "Weapon Shop",
                "type": "shop",
                "description": "무기 상점"
            },
            "tavern": {
                "name": "Tavern",
                "type": "social",
                "description": "여관"
            }
        }
    
    async def enter_location(self, location_id: str, player_id: str):
        """장소 진입"""
        location = self.locations.get(location_id)
        if not location:
            raise ValueError(f"Unknown location: {location_id}")
        
        # 장소별 진입 처리
        if location["type"] == "shop":
            await self.enter_shop(location_id, player_id)
        elif location["type"] == "social":
            await self.enter_social_area(location_id, player_id)
        else:
            await self.enter_public_area(location_id, player_id)
        
        return {"success": True, "location": location}
```

#### **3. Cell 단위 상호작용**
```python
class CellManager:
    def __init__(self):
        self.cells = {}
    
    async def enter_cell(self, cell_id: str, player_id: str):
        """셀 진입 및 컨텐츠 로딩"""
        # 셀 정보 로드
        cell_data = await self.load_cell_data(cell_id)
        
        # 엔티티 로드
        entities = await self.load_cell_entities(cell_id)
        
        # 오브젝트 로드
        objects = await self.load_cell_objects(cell_id)
        
        # 이벤트 확인
        events = await self.check_cell_events(cell_id, player_id)
        
        return {
            "cell": cell_data,
            "entities": entities,
            "objects": objects,
            "events": events
        }
```

#### **4. 행동 버튼 처리**
```python
class ActionHandler:
    def __init__(self):
        self.actions = {
            "investigate": self.investigate,
            "dialogue": self.dialogue,
            "trade": self.trade,
            "visit": self.visit,
            "wait": self.wait
        }
    
    async def investigate(self, player_id: str, cell_id: str):
        """조사 행동"""
        # 셀 정보 수집
        cell_info = await self.get_cell_information(cell_id)
        
        # 숨겨진 정보 확인
        hidden_info = await self.check_hidden_information(cell_id, player_id)
        
        # 결과 생성
        result = {
            "visible": cell_info,
            "hidden": hidden_info,
            "success": True
        }
        
        return result
    
    async def dialogue(self, player_id: str, target_id: str):
        """대화 행동"""
        # 대화 상대 확인
        target = await self.get_entity(target_id)
        if not target:
            return {"success": False, "message": "대화 상대를 찾을 수 없습니다."}
        
        # 대화 컨텍스트 생성
        context = await self.build_dialogue_context(player_id, target_id)
        
        # 대화 시작
        dialogue_result = await self.start_dialogue(context)
        
        return dialogue_result
    
    async def trade(self, player_id: str, target_id: str):
        """거래 행동"""
        # 거래 상대 확인
        target = await self.get_entity(target_id)
        if not target or target.get("type") != "merchant":
            return {"success": False, "message": "거래할 수 없는 상대입니다."}
        
        # 거래 시작
        trade_result = await self.start_trade(player_id, target_id)
        
        return trade_result
    
    async def visit(self, player_id: str, destination_id: str):
        """방문/이동 행동"""
        # 목적지 확인
        destination = await self.get_location(destination_id)
        if not destination:
            return {"success": False, "message": "목적지를 찾을 수 없습니다."}
        
        # 이동 처리
        move_result = await self.move_player(player_id, destination_id)
        
        return move_result
    
    async def wait(self, player_id: str, duration: int = 1):
        """대기 행동"""
        # 시간 경과 처리
        await self.pass_time(duration)
        
        # 대기 중 이벤트 확인
        events = await self.check_waiting_events(player_id, duration)
        
        return {"success": True, "events": events}
```

#### **5. 로그 & 상태 업데이트**
```python
class GameLogger:
    def __init__(self):
        self.logs = []
    
    async def log_action(self, player_id: str, action: str, result: dict):
        """행동 로그 기록"""
        log_entry = {
            "timestamp": datetime.now(),
            "player_id": player_id,
            "action": action,
            "result": result,
            "success": result.get("success", False)
        }
        
        self.logs.append(log_entry)
        
        # 데이터베이스에 저장
        await self.save_log_to_db(log_entry)
        
        # UI 업데이트
        await self.update_ui_log(log_entry)
    
    async def update_player_state(self, player_id: str, changes: dict):
        """플레이어 상태 업데이트"""
        # 상태 변경사항 적용
        await self.apply_state_changes(player_id, changes)
        
        # UI 상태 업데이트
        await self.update_ui_state(player_id, changes)
```

#### **6. Dev Mode 승격**
```python
class DevModeManager:
    def __init__(self):
        self.pending_promotions = []
    
    async def promote_to_game_data(self, runtime_id: str, target_table: str, reason: str):
        """Runtime → Game Data 승격"""
        # 승격 대상 확인
        runtime_data = await self.get_runtime_data(runtime_id)
        if not runtime_data:
            return {"success": False, "message": "승격할 데이터를 찾을 수 없습니다."}
        
        # 승격 검증
        validation_result = await self.validate_promotion(runtime_data, target_table)
        if not validation_result["valid"]:
            return {"success": False, "message": validation_result["error"]}
        
        # 승격 실행
        promotion_result = await self.execute_promotion(runtime_data, target_table, reason)
        
        return promotion_result
```

---

## 🎮 **게임 상태 관리**

### **세션 관리**
```python
class GameSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.player_id = None
        self.current_region = None
        self.current_location = None
        self.current_cell = None
        self.game_state = {}
        self.logs = []
    
    async def save_session(self):
        """세션 저장"""
        session_data = {
            "session_id": self.session_id,
            "player_id": self.player_id,
            "current_region": self.current_region,
            "current_location": self.current_location,
            "current_cell": self.current_cell,
            "game_state": self.game_state,
            "logs": self.logs,
            "saved_at": datetime.now()
        }
        
        await self.save_to_database(session_data)
    
    async def load_session(self, session_id: str):
        """세션 로드"""
        session_data = await self.load_from_database(session_id)
        
        if session_data:
            self.session_id = session_data["session_id"]
            self.player_id = session_data["player_id"]
            self.current_region = session_data["current_region"]
            self.current_location = session_data["current_location"]
            self.current_cell = session_data["current_cell"]
            self.game_state = session_data["game_state"]
            self.logs = session_data["logs"]
            
            return True
        
        return False
```

### **상태 동기화**
```python
class StateSynchronizer:
    def __init__(self):
        self.state_cache = {}
    
    async def sync_state(self, player_id: str, state_changes: dict):
        """상태 동기화"""
        # 로컬 상태 업데이트
        self.state_cache[player_id] = state_changes
        
        # 데이터베이스 상태 업데이트
        await self.update_database_state(player_id, state_changes)
        
        # UI 상태 업데이트
        await self.update_ui_state(player_id, state_changes)
    
    async def get_current_state(self, player_id: str):
        """현재 상태 조회"""
        # 캐시에서 조회
        if player_id in self.state_cache:
            return self.state_cache[player_id]
        
        # 데이터베이스에서 조회
        state = await self.load_state_from_database(player_id)
        self.state_cache[player_id] = state
        
        return state
```

---

## 🧪 **테스트 및 검증**

### **MVP 수용 기준 테스트**
```python
class MVPAcceptanceTest:
    def __init__(self):
        self.test_results = []
    
    async def test_100_consecutive_actions(self):
        """100회 연속 무오류 테스트"""
        success_count = 0
        
        for i in range(100):
            try:
                # 행동 실행
                result = await self.execute_random_action()
                
                if result["success"]:
                    success_count += 1
                else:
                    self.test_results.append({
                        "test": "100_consecutive_actions",
                        "iteration": i,
                        "result": "FAIL",
                        "error": result.get("error")
                    })
                    break
                    
            except Exception as e:
                self.test_results.append({
                    "test": "100_consecutive_actions",
                    "iteration": i,
                    "result": "ERROR",
                    "error": str(e)
                })
                break
        
        return success_count == 100
    
    async def test_devmode_persistence(self):
        """DevMode 생성 지속성 테스트"""
        # DevMode에서 NPC 생성
        npc = await self.create_npc_in_devmode()
        
        # 세션 저장
        await self.save_session()
        
        # 새 세션에서 로드
        await self.load_session()
        
        # 생성된 NPC가 템플릿으로 노출되는지 확인
        template = await self.get_entity_template(npc["id"])
        
        return template is not None
    
    async def test_rule_based_play(self):
        """룰기반 플레이 테스트"""
        # LLM 비활성화
        await self.disable_llm()
        
        # 룰기반 대화 테스트
        dialogue_result = await self.test_rule_based_dialogue()
        
        # 룰기반 묘사 테스트
        description_result = await self.test_rule_based_description()
        
        return dialogue_result["success"] and description_result["success"]
```

---

## 📋 **구현 체크리스트**

### **계기판 UI**
- [ ] 상단 바 (Region/Location/Cell, 시간, 날씨)
- [ ] 좌측 패널 (행동 버튼)
- [ ] 중앙 패널 (월드 로그)
- [ ] 우측 패널 (정보 탭)
- [ ] 하단 패널 (명령 입력)

### **코어 루프**
- [ ] Region 선택 및 입장
- [ ] Location 진입
- [ ] Cell 단위 상호작용
- [ ] 행동 버튼 처리 (조사/대화/거래/방문/대기)
- [ ] 로그 & 상태 업데이트
- [ ] Dev Mode 승격

### **게임 상태 관리**
- [ ] 세션 저장/로드
- [ ] 상태 동기화
- [ ] 이벤트 처리

### **테스트**
- [ ] 100회 연속 무오류 테스트
- [ ] DevMode 지속성 테스트
- [ ] 룰기반 플레이 테스트

---

## 🚀 **다음 단계**

1. **계기판 UI 구현**: PyQt5 기반 UI 컴포넌트 개발
2. **코어 루프 구현**: 게임 로직 및 상태 관리
3. **테스트 구현**: MVP 수용 기준 테스트
4. **통합 테스트**: 전체 시스템 통합 테스트
5. **성능 최적화**: 캐시 및 성능 튜닝

---

**문서 작성자**: RPG Engine Development Team  
**최종 검토**: 2025-10-18  
**다음 검토 예정**: 2025-11-18
