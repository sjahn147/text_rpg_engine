"""
MVP 계기판 UI 구현
"""
import sys
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QTabWidget, QGridLayout,
    QMenuBar, QMenu, QAction, QMessageBox, QSplitter, QFrame,
    QFileDialog, QProgressBar, QGroupBox, QListWidget, QListWidgetItem,
    QScrollArea, QFormLayout, QLineEdit, QComboBox, QSpinBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QBrush, QTextCursor
import qasync

from app.core.game_manager import GameManager
from app.managers.entity_manager import EntityManager, EntityType, EntityStatus
from app.managers.cell_manager import CellManager, CellType, CellStatus
from app.game_session import GameSession
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from database.factories.game_data_factory import GameDataFactory
from database.factories.instance_factory import InstanceFactory


class AsyncWorker(QThread):
    """비동기 작업을 처리하는 워커 스레드"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, coro):
        super().__init__()
        self.coro = coro
    
    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.coro)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            loop.close()


class TopBar(QWidget):
    """상단 정보 바"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # 현재 위치 정보
        self.location_label = QLabel("Region: Unknown")
        self.cell_label = QLabel("Cell: Unknown")
        
        # 시간 정보
        self.time_label = QLabel("Time: 12:00")
        self.weather_label = QLabel("Weather: Clear")
        
        # 스타일링
        for label in [self.location_label, self.cell_label, self.time_label, self.weather_label]:
            label.setStyleSheet("QLabel { font-size: 12px; font-weight: bold; }")
        
        layout.addWidget(self.location_label)
        layout.addWidget(self.cell_label)
        layout.addStretch()
        layout.addWidget(self.time_label)
        layout.addWidget(self.weather_label)
        
        self.setLayout(layout)
    
    def update_location(self, region: str, location: str, cell: str):
        """위치 정보 업데이트"""
        self.location_label.setText(f"Region: {region}")
        self.cell_label.setText(f"Cell: {cell}")
    
    def update_time_weather(self, time: str, weather: str):
        """시간과 날씨 정보 업데이트"""
        self.time_label.setText(f"Time: {time}")
        self.weather_label.setText(f"Weather: {weather}")


class ActionPanel(QWidget):
    """좌측 행동 패널"""
    action_requested = pyqtSignal(str)  # 행동 요청 신호
    
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
            btn.setStyleSheet("""
                QPushButton { 
                    font-size: 14px; 
                    font-weight: bold;
                    background-color: #2c3e50;
                    color: white;
                    border: 2px solid #34495e;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
                QPushButton:pressed {
                    background-color: #1abc9c;
                }
            """)
        
        # 버튼 클릭 이벤트 연결
        self.investigate_btn.clicked.connect(lambda: self.action_requested.emit("investigate"))
        self.dialogue_btn.clicked.connect(lambda: self.action_requested.emit("dialogue"))
        self.trade_btn.clicked.connect(lambda: self.action_requested.emit("trade"))
        self.visit_btn.clicked.connect(lambda: self.action_requested.emit("visit"))
        self.wait_btn.clicked.connect(lambda: self.action_requested.emit("wait"))
        
        layout.addWidget(self.investigate_btn)
        layout.addWidget(self.dialogue_btn)
        layout.addWidget(self.trade_btn)
        layout.addWidget(self.visit_btn)
        layout.addWidget(self.wait_btn)
        layout.addStretch()
        
        self.setLayout(layout)


class WorldLogPanel(QWidget):
    """중앙 월드 로그 패널"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 로그 텍스트 영역
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(400)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border: 1px solid #444444;
                border-radius: 5px;
            }
        """)
        
        # 스크롤바 설정
        self.log_text.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        layout.addWidget(QLabel("🌍 월드 로그"))
        layout.addWidget(self.log_text)
        
        self.setLayout(layout)
    
    def add_log(self, message: str, log_type: str = "info"):
        """로그 메시지 추가"""
        timestamp = QTimer().remainingTime()  # 간단한 타임스탬프
        color = {
            "info": "#ffffff",
            "success": "#2ecc71",
            "warning": "#f39c12",
            "error": "#e74c3c"
        }.get(log_type, "#ffffff")
        
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(f'<span style="color: {color};">{formatted_message}</span>')
        
        # 자동 스크롤
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)


class InfoPanel(QWidget):
    """우측 정보 패널"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 탭 위젯
        self.tab_widget = QTabWidget()
        
        # 인벤토리 탭
        self.inventory_tab = QWidget()
        inventory_layout = QVBoxLayout()
        self.inventory_list = QListWidget()
        inventory_layout.addWidget(QLabel("🎒 인벤토리"))
        inventory_layout.addWidget(self.inventory_list)
        self.inventory_tab.setLayout(inventory_layout)
        
        # 자산 탭
        self.assets_tab = QWidget()
        assets_layout = QVBoxLayout()
        self.gold_label = QLabel("💰 골드: 0")
        self.items_label = QLabel("📦 아이템: 0")
        assets_layout.addWidget(self.gold_label)
        assets_layout.addWidget(self.items_label)
        assets_layout.addStretch()
        self.assets_tab.setLayout(assets_layout)
        
        # 관계 탭
        self.relationships_tab = QWidget()
        relationships_layout = QVBoxLayout()
        self.relationships_list = QListWidget()
        relationships_layout.addWidget(QLabel("👥 관계"))
        relationships_layout.addWidget(self.relationships_list)
        self.relationships_tab.setLayout(relationships_layout)
        
        # 로어 탭
        self.lore_tab = QWidget()
        lore_layout = QVBoxLayout()
        self.lore_list = QListWidget()
        lore_layout.addWidget(QLabel("📚 로어"))
        lore_layout.addWidget(self.lore_list)
        self.lore_tab.setLayout(lore_layout)
        
        # 탭 추가
        self.tab_widget.addTab(self.inventory_tab, "인벤토리")
        self.tab_widget.addTab(self.assets_tab, "자산")
        self.tab_widget.addTab(self.relationships_tab, "관계")
        self.tab_widget.addTab(self.lore_tab, "로어")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def update_inventory(self, items: List[Dict[str, Any]]):
        """인벤토리 업데이트"""
        self.inventory_list.clear()
        for item in items:
            self.inventory_list.addItem(f"{item.get('name', 'Unknown')} x{item.get('quantity', 1)}")
    
    def update_assets(self, gold: int, items: int):
        """자산 업데이트"""
        self.gold_label.setText(f"💰 골드: {gold}")
        self.items_label.setText(f"📦 아이템: {items}")
    
    def update_relationships(self, relationships: List[Dict[str, Any]]):
        """관계 업데이트"""
        self.relationships_list.clear()
        for rel in relationships:
            self.relationships_list.addItem(f"{rel.get('name', 'Unknown')}: {rel.get('status', 'Neutral')}")
    
    def update_lore(self, lore_entries: List[Dict[str, Any]]):
        """로어 업데이트"""
        self.lore_list.clear()
        for lore in lore_entries:
            self.lore_list.addItem(f"{lore.get('title', 'Unknown')}")


class CommandPanel(QWidget):
    """하단 명령 패널"""
    command_entered = pyqtSignal(str)  # 명령 입력 신호
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # 명령 입력 필드
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("명령을 입력하세요...")
        self.command_input.returnPressed.connect(self.on_command_entered)
        
        # 명령 버튼
        self.execute_btn = QPushButton("실행")
        self.execute_btn.clicked.connect(self.on_command_entered)
        
        layout.addWidget(QLabel("💬 명령:"))
        layout.addWidget(self.command_input)
        layout.addWidget(self.execute_btn)
        
        self.setLayout(layout)
    
    def on_command_entered(self):
        """명령 입력 처리"""
        command = self.command_input.text().strip()
        if command:
            self.command_entered.emit(command)
            self.command_input.clear()


class DashboardUI(QMainWindow):
    """MVP 계기판 UI 메인 윈도우"""
    
    def __init__(self):
        super().__init__()
        self.game_manager: Optional[GameManager] = None
        self.entity_manager: Optional[EntityManager] = None
        self.cell_manager: Optional[CellManager] = None
        self.current_session: Optional[GameSession] = None
        self.workers = []
        
        self.setup_ui()
        self.setup_connections()
        self.initialize_game()
    
    def setup_ui(self):
        """UI 설정"""
        self.setWindowTitle("RPG Engine - MVP Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        
        # 상단 바
        self.top_bar = TopBar()
        main_layout.addWidget(self.top_bar)
        
        # 중앙 분할 영역
        central_splitter = QSplitter(Qt.Horizontal)
        
        # 좌측 행동 패널
        self.action_panel = ActionPanel()
        self.action_panel.setMaximumWidth(200)
        central_splitter.addWidget(self.action_panel)
        
        # 중앙 월드 로그 패널
        self.world_log_panel = WorldLogPanel()
        central_splitter.addWidget(self.world_log_panel)
        
        # 우측 정보 패널
        self.info_panel = InfoPanel()
        self.info_panel.setMaximumWidth(300)
        central_splitter.addWidget(self.info_panel)
        
        # 분할 비율 설정
        central_splitter.setSizes([200, 700, 300])
        
        main_layout.addWidget(central_splitter)
        
        # 하단 명령 패널
        self.command_panel = CommandPanel()
        main_layout.addWidget(self.command_panel)
        
        central_widget.setLayout(main_layout)
        
        # 메뉴바 설정
        self.setup_menu_bar()
    
    def setup_menu_bar(self):
        """메뉴바 설정"""
        menubar = self.menuBar()
        
        # 게임 메뉴
        game_menu = menubar.addMenu('게임')
        
        new_game_action = QAction('새 게임', self)
        new_game_action.triggered.connect(self.new_game)
        game_menu.addAction(new_game_action)
        
        load_game_action = QAction('게임 로드', self)
        load_game_action.triggered.connect(self.load_game)
        game_menu.addAction(load_game_action)
        
        save_game_action = QAction('게임 저장', self)
        save_game_action.triggered.connect(self.save_game)
        game_menu.addAction(save_game_action)
        
        # 개발자 모드 메뉴
        dev_menu = menubar.addMenu('개발자 모드')
        
        dev_mode_action = QAction('Dev Mode 열기', self)
        dev_mode_action.triggered.connect(self.open_dev_mode)
        dev_menu.addAction(dev_mode_action)
        
        # 도움말 메뉴
        help_menu = menubar.addMenu('도움말')
        
        about_action = QAction('정보', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_connections(self):
        """신호 연결"""
        self.action_panel.action_requested.connect(self.handle_action)
        self.command_panel.command_entered.connect(self.handle_command)
    
    async def initialize_game(self):
        """게임 초기화"""
        try:
            # 데이터베이스 연결
            db_connection = DatabaseConnection()
            await db_connection.initialize()
            
            # Repository 생성
            game_data_repo = GameDataRepository(db_connection)
            runtime_data_repo = RuntimeDataRepository(db_connection)
            reference_layer_repo = ReferenceLayerRepository(db_connection)
            
            # Factory 생성
            game_data_factory = GameDataFactory()
            instance_factory = InstanceFactory()
            
            # Manager 생성
            self.game_manager = GameManager(
                db_connection, game_data_repo, runtime_data_repo,
                reference_layer_repo, game_data_factory, instance_factory
            )
            
            self.entity_manager = EntityManager(db_connection, game_data_repo, runtime_data_repo)
            self.cell_manager = CellManager(db_connection, game_data_repo, runtime_data_repo)
            
            # 초기 로그
            self.world_log_panel.add_log("게임 엔진이 초기화되었습니다.", "success")
            self.world_log_panel.add_log("새 게임을 시작하거나 기존 게임을 로드하세요.", "info")
            
        except Exception as e:
            self.world_log_panel.add_log(f"게임 초기화 실패: {str(e)}", "error")
            QMessageBox.critical(self, "오류", f"게임 초기화에 실패했습니다: {str(e)}")
    
    def handle_action(self, action: str):
        """행동 처리"""
        if not self.current_session:
            self.world_log_panel.add_log("게임이 시작되지 않았습니다. 새 게임을 시작하세요.", "warning")
            return
        
        # 비동기 행동 처리
        worker = AsyncWorker(self.process_action(action))
        worker.finished.connect(lambda result: self.on_action_completed(action, result))
        worker.error.connect(lambda error: self.world_log_panel.add_log(f"행동 실패: {error}", "error"))
        worker.start()
        self.workers.append(worker)
    
    async def process_action(self, action: str):
        """비동기 행동 처리"""
        if action == "investigate":
            return await self.action_investigate()
        elif action == "dialogue":
            return await self.action_dialogue()
        elif action == "trade":
            return await self.action_trade()
        elif action == "visit":
            return await self.action_visit()
        elif action == "wait":
            return await self.action_wait()
        else:
            return {"success": False, "message": f"알 수 없는 행동: {action}"}
    
    async def action_investigate(self):
        """조사 행동"""
        if not self.current_session:
            return {"success": False, "message": "세션이 없습니다."}
        
        # 현재 셀 조사
        cell_result = await self.cell_manager.get_cell(self.current_session.current_cell_id)
        if not cell_result.success:
            return {"success": False, "message": "셀을 찾을 수 없습니다."}
        
        # 셀 컨텐츠 로드
        content_result = await self.cell_manager.load_cell_content(self.current_session.current_cell_id)
        if not content_result.success:
            return {"success": False, "message": "셀 컨텐츠를 로드할 수 없습니다."}
        
        # 조사 결과 생성
        entities = content_result.content.entities
        objects = content_result.content.objects
        events = content_result.content.events
        
        result_text = f"조사 결과:\n"
        result_text += f"셀: {cell_result.cell.name}\n"
        result_text += f"설명: {cell_result.cell.description}\n"
        
        if entities:
            result_text += f"\n엔티티: {len(entities)}개\n"
            for entity in entities:
                result_text += f"- {entity.get('name', 'Unknown')}\n"
        
        if objects:
            result_text += f"\n오브젝트: {len(objects)}개\n"
            for obj in objects:
                result_text += f"- {obj.get('name', 'Unknown')}\n"
        
        if events:
            result_text += f"\n이벤트: {len(events)}개\n"
            for event in events:
                result_text += f"- {event.get('title', 'Unknown')}\n"
        
        return {"success": True, "message": result_text}
    
    async def action_dialogue(self):
        """대화 행동"""
        return {"success": True, "message": "대화 기능은 아직 구현되지 않았습니다."}
    
    async def action_trade(self):
        """거래 행동"""
        return {"success": True, "message": "거래 기능은 아직 구현되지 않았습니다."}
    
    async def action_visit(self):
        """방문 행동"""
        return {"success": True, "message": "방문 기능은 아직 구현되지 않았습니다."}
    
    async def action_wait(self):
        """대기 행동"""
        return {"success": True, "message": "대기했습니다. 시간이 흘렀습니다."}
    
    def on_action_completed(self, action: str, result: Dict[str, Any]):
        """행동 완료 처리"""
        if result.get("success", False):
            self.world_log_panel.add_log(result.get("message", "행동이 완료되었습니다."), "success")
        else:
            self.world_log_panel.add_log(result.get("message", "행동이 실패했습니다."), "error")
    
    def handle_command(self, command: str):
        """명령 처리"""
        self.world_log_panel.add_log(f"명령 실행: {command}", "info")
        # TODO: 명령 처리 로직 구현
    
    def new_game(self):
        """새 게임 시작"""
        worker = AsyncWorker(self.start_new_game())
        worker.finished.connect(self.on_new_game_started)
        worker.error.connect(lambda error: self.world_log_panel.add_log(f"새 게임 시작 실패: {error}", "error"))
        worker.start()
        self.workers.append(worker)
    
    async def start_new_game(self):
        """비동기 새 게임 시작"""
        if not self.game_manager:
            return {"success": False, "message": "게임 매니저가 초기화되지 않았습니다."}
        
        # 기본 플레이어 템플릿과 시작 셀 사용
        player_template_id = "player_template_001"
        start_cell_id = "cell_village_001"
        
        session_id = await self.game_manager.start_new_game(player_template_id, start_cell_id)
        if session_id:
            return {"success": True, "message": f"새 게임이 시작되었습니다. 세션 ID: {session_id}"}
        else:
            return {"success": False, "message": "새 게임 시작에 실패했습니다."}
    
    def on_new_game_started(self, result: Dict[str, Any]):
        """새 게임 시작 완료"""
        if result.get("success", False):
            self.world_log_panel.add_log(result.get("message", "새 게임이 시작되었습니다."), "success")
            # TODO: 세션 정보 업데이트
        else:
            self.world_log_panel.add_log(result.get("message", "새 게임 시작에 실패했습니다."), "error")
    
    def load_game(self):
        """게임 로드"""
        self.world_log_panel.add_log("게임 로드 기능은 아직 구현되지 않았습니다.", "warning")
    
    def save_game(self):
        """게임 저장"""
        self.world_log_panel.add_log("게임 저장 기능은 아직 구현되지 않았습니다.", "warning")
    
    def open_dev_mode(self):
        """개발자 모드 열기"""
        self.world_log_panel.add_log("개발자 모드는 아직 구현되지 않았습니다.", "warning")
    
    def show_about(self):
        """정보 표시"""
        QMessageBox.about(self, "정보", 
                         "RPG Engine MVP Dashboard\n"
                         "버전: 0.3.0\n"
                         "개발: RPG Engine Team")
    
    def closeEvent(self, event):
        """윈도우 종료 이벤트"""
        # 워커 스레드 정리
        for worker in self.workers:
            if worker.isRunning():
                worker.terminate()
                worker.wait()
        
        event.accept()


def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    
    # qasync 설정
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # 대시보드 UI 생성
    dashboard = DashboardUI()
    dashboard.show()
    
    # 이벤트 루프 실행
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
