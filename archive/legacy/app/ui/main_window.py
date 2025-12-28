import sys
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QTabWidget, QGridLayout,
    QMenuBar, QMenu, QAction, QMessageBox, QSplitter, QFrame,
    QFileDialog, QProgressBar, QGroupBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QBrush, QTextCursor
import qasync

from app.core.game_manager import GameManager
from app.core.scenario_loader import ScenarioLoader
from app.core.scenario_executor import ScenarioExecutor
from app.game_session import GameSession
from app.ui.screens.map_screen import MapScreen
from app.ui.screens.dialogue_screen import DialogueScreen
from app.ui.screens.inventory_screen import InventoryScreen
from app.ui.screens.status_screen import StatusScreen

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game_manager = GameManager()
        self.current_session: Optional[GameSession] = None
        self.current_session_id: Optional[str] = None
        self.workers = []  # AsyncWorker 스레드 보관용 리스트
        
        # 시나리오 관련
        self.scenario_loader = ScenarioLoader()
        self.scenario_executor = ScenarioExecutor()
        self.current_scenario: Optional[Dict[str, Any]] = None
        
        self.init_ui()
        self.setup_menu()
        self.setup_scenario_callbacks()
        
        # 상태 업데이트 타이머
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_game_state)
        self.update_timer.start(1000)  # 1초마다 업데이트
    
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle('RPG Engine GUI')
        self.setGeometry(100, 100, 1600, 1000)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QHBoxLayout(central_widget)
        
        # 왼쪽 패널 (맵/게임 화면)
        left_panel = QFrame()
        left_panel.setFrameStyle(QFrame.Box)
        left_panel.setMinimumWidth(800)
        left_layout = QVBoxLayout(left_panel)
        
        # 맵 화면
        self.map_screen = MapScreen()
        left_layout.addWidget(self.map_screen)
        
        # 하단 대화창
        self.dialogue_screen = DialogueScreen()
        left_layout.addWidget(self.dialogue_screen)
        
        # 중앙 패널 (시나리오 제어)
        center_panel = QFrame()
        center_panel.setFrameStyle(QFrame.Box)
        center_panel.setMaximumWidth(300)
        center_layout = QVBoxLayout(center_panel)
        
        # 시나리오 그룹
        scenario_group = QGroupBox("시나리오 제어")
        scenario_layout = QVBoxLayout(scenario_group)
        
        # 시나리오 로드 버튼
        self.load_scenario_btn = QPushButton("시나리오 로드")
        self.load_scenario_btn.clicked.connect(self.load_scenario_file)
        scenario_layout.addWidget(self.load_scenario_btn)
        
        # 시나리오 정보
        self.scenario_info_label = QLabel("로드된 시나리오: 없음")
        self.scenario_info_label.setWordWrap(True)
        scenario_layout.addWidget(self.scenario_info_label)
        
        # 시나리오 실행 버튼들
        self.run_scenario_btn = QPushButton("시나리오 실행")
        self.run_scenario_btn.clicked.connect(self.run_scenario)
        self.run_scenario_btn.setEnabled(False)
        scenario_layout.addWidget(self.run_scenario_btn)
        
        self.pause_scenario_btn = QPushButton("일시정지")
        self.pause_scenario_btn.clicked.connect(self.pause_scenario)
        self.pause_scenario_btn.setEnabled(False)
        scenario_layout.addWidget(self.pause_scenario_btn)
        
        self.stop_scenario_btn = QPushButton("중지")
        self.stop_scenario_btn.clicked.connect(self.stop_scenario)
        self.stop_scenario_btn.setEnabled(False)
        scenario_layout.addWidget(self.stop_scenario_btn)
        
        # 진행률 표시
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        scenario_layout.addWidget(self.progress_bar)
        
        # 실행 상태
        self.execution_status_label = QLabel("대기 중")
        scenario_layout.addWidget(self.execution_status_label)
        
        center_layout.addWidget(scenario_group)
        center_layout.addStretch()
        
        # 오른쪽 패널 (탭 위젯)
        right_panel = QFrame()
        right_panel.setFrameStyle(QFrame.Box)
        right_panel.setMaximumWidth(400)
        right_layout = QVBoxLayout(right_panel)
        
        # 탭 위젯
        self.tab_widget = QTabWidget()
        
        # 상태 탭
        self.status_screen = StatusScreen()
        self.tab_widget.addTab(self.status_screen, "상태")
        
        # 인벤토리 탭
        self.inventory_screen = InventoryScreen()
        self.tab_widget.addTab(self.inventory_screen, "인벤토리")
        
        # 로그 탭
        self.log_screen = QTextEdit()
        self.log_screen.setReadOnly(True)
        self.tab_widget.addTab(self.log_screen, "로그")
        
        right_layout.addWidget(self.tab_widget)
        
        # 스플리터로 분할
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([800, 300, 400])
        
        main_layout.addWidget(splitter)
        
        # 시그널 연결
        self.map_screen.entity_clicked.connect(self.on_entity_clicked)
        self.dialogue_screen.dialogue_choice.connect(self.on_dialogue_choice)
    
    def setup_menu(self):
        """메뉴바 설정"""
        menubar = self.menuBar()
        
        # 게임 메뉴
        game_menu = menubar.addMenu('게임')
        
        new_game_action = QAction('새 게임', self)
        new_game_action.triggered.connect(self.start_new_game)
        game_menu.addAction(new_game_action)
        
        load_game_action = QAction('게임 불러오기', self)
        load_game_action.triggered.connect(self.load_game)
        game_menu.addAction(load_game_action)
        
        save_game_action = QAction('게임 저장', self)
        save_game_action.triggered.connect(self.save_game)
        game_menu.addAction(save_game_action)
        
        game_menu.addSeparator()
        
        exit_action = QAction('종료', self)
        exit_action.triggered.connect(self.close)
        game_menu.addAction(exit_action)
        
        # 시나리오 메뉴
        scenario_menu = menubar.addMenu('시나리오')
        
        load_scenario_action = QAction('시나리오 로드', self)
        load_scenario_action.triggered.connect(self.load_scenario_file)
        scenario_menu.addAction(load_scenario_action)
        
        run_scenario_action = QAction('시나리오 실행', self)
        run_scenario_action.triggered.connect(self.run_scenario)
        scenario_menu.addAction(run_scenario_action)
        
        scenario_menu.addSeparator()
        
        list_scenarios_action = QAction('시나리오 목록', self)
        list_scenarios_action.triggered.connect(self.show_scenario_list)
        scenario_menu.addAction(list_scenarios_action)
        
        # 도구 메뉴
        tools_menu = menubar.addMenu('도구')
        
        debug_action = QAction('디버그 정보', self)
        debug_action.triggered.connect(self.show_debug_info)
        tools_menu.addAction(debug_action)
    
    def setup_scenario_callbacks(self):
        """시나리오 실행기 콜백 설정"""
        self.scenario_executor.set_callbacks(
            on_step_start=self.on_scenario_step_start,
            on_step_complete=self.on_scenario_step_complete,
            on_scenario_complete=self.on_scenario_complete,
            on_error=self.on_scenario_error,
            on_log=self.on_scenario_log
        )
    
    def load_scenario_file(self):
        """시나리오 파일 로드"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "시나리오 파일 선택", 
            "", 
            "시나리오 파일 (*.json *.yaml *.yml);;모든 파일 (*)"
        )
        
        if file_path:
            self.log_message(f"시나리오 파일 로드 중: {file_path}")
            
            async def load_scenario():
                try:
                    scenario_data = self.scenario_loader.load_scenario(file_path)
                    return scenario_data
                except Exception as e:
                    raise Exception(f"시나리오 로드 실패: {str(e)}")
            
            worker = AsyncWorker(load_scenario())
            self.workers.append(worker)
            worker.finished.connect(self.on_scenario_loaded)
            worker.error.connect(self.on_scenario_error)
            worker.finished.connect(lambda _: self.cleanup_worker(worker))
            worker.error.connect(lambda _: self.cleanup_worker(worker))
            worker.start()
    
    def on_scenario_loaded(self, scenario_data: Dict[str, Any]):
        """시나리오 로드 완료"""
        self.current_scenario = scenario_data
        
        # UI 업데이트
        scenario_name = scenario_data.get('name', 'Unknown')
        step_count = len(scenario_data.get('steps', []))
        description = scenario_data.get('description', '설명 없음')
        
        info_text = f"로드된 시나리오: {scenario_name}\n"
        info_text += f"단계 수: {step_count}\n"
        info_text += f"설명: {description}"
        
        self.scenario_info_label.setText(info_text)
        self.run_scenario_btn.setEnabled(True)
        
        self.log_message(f"시나리오 로드 완료: {scenario_name}")
    
    def run_scenario(self):
        """시나리오 실행"""
        if not self.current_scenario:
            QMessageBox.warning(self, "경고", "먼저 시나리오를 로드해주세요.")
            return
        
        self.log_message("시나리오 실행을 시작합니다...")
        
        async def execute():
            try:
                success = await self.scenario_executor.execute_scenario(self.current_scenario)
                return success
            except Exception as e:
                raise Exception(f"시나리오 실행 실패: {str(e)}")
        
        worker = AsyncWorker(execute())
        self.workers.append(worker)
        worker.finished.connect(self.on_scenario_execution_finished)
        worker.error.connect(self.on_scenario_error)
        worker.finished.connect(lambda _: self.cleanup_worker(worker))
        worker.error.connect(lambda _: self.cleanup_worker(worker))
        worker.start()
        
        # UI 상태 업데이트
        self.run_scenario_btn.setEnabled(False)
        self.pause_scenario_btn.setEnabled(True)
        self.stop_scenario_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.current_scenario.get('steps', [])))
        self.progress_bar.setValue(0)
    
    def pause_scenario(self):
        """시나리오 일시정지"""
        self.scenario_executor.pause_scenario()
        self.pause_scenario_btn.setText("재개")
        self.pause_scenario_btn.clicked.disconnect()
        self.pause_scenario_btn.clicked.connect(self.resume_scenario)
    
    def resume_scenario(self):
        """시나리오 재개"""
        self.scenario_executor.resume_scenario()
        self.pause_scenario_btn.setText("일시정지")
        self.pause_scenario_btn.clicked.disconnect()
        self.pause_scenario_btn.clicked.connect(self.pause_scenario)
    
    def stop_scenario(self):
        """시나리오 중지"""
        self.scenario_executor.stop_scenario()
        self.reset_scenario_ui()
    
    def on_scenario_step_start(self, step_index: int, step: Dict[str, Any]):
        """시나리오 단계 시작"""
        self.execution_status_label.setText(f"Step {step_index + 1} 실행 중...")
        self.progress_bar.setValue(step_index)
    
    def on_scenario_step_complete(self, step_index: int, step: Dict[str, Any], execution_time: float):
        """시나리오 단계 완료"""
        self.progress_bar.setValue(step_index + 1)
        self.execution_status_label.setText(f"Step {step_index + 1} 완료 ({execution_time:.2f}초)")
    
    def on_scenario_complete(self):
        """시나리오 완료"""
        self.log_message("시나리오 실행이 완료되었습니다.")
        self.reset_scenario_ui()
        QMessageBox.information(self, "완료", "시나리오 실행이 완료되었습니다.")
    
    def on_scenario_error(self, error_msg: str):
        """시나리오 오류"""
        self.log_message(f"시나리오 오류: {error_msg}")
        self.reset_scenario_ui()
        QMessageBox.critical(self, "오류", f"시나리오 실행 중 오류가 발생했습니다:\n{error_msg}")
    
    def on_scenario_log(self, log_msg: str):
        """시나리오 로그"""
        self.log_message(log_msg)
    
    def reset_scenario_ui(self):
        """시나리오 UI 초기화"""
        self.run_scenario_btn.setEnabled(True)
        self.pause_scenario_btn.setEnabled(False)
        self.stop_scenario_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.execution_status_label.setText("대기 중")
        
        # 일시정지 버튼 텍스트 복원
        self.pause_scenario_btn.setText("일시정지")
        self.pause_scenario_btn.clicked.disconnect()
        self.pause_scenario_btn.clicked.connect(self.pause_scenario)
    
    def show_scenario_list(self):
        """시나리오 목록 표시"""
        # tests/scenarios 디렉토리에서 시나리오 파일들 찾기
        scenario_dir = "tests/scenarios"
        scenario_files = self.scenario_loader.list_scenarios(scenario_dir)
        
        if not scenario_files:
            QMessageBox.information(self, "정보", "사용 가능한 시나리오 파일이 없습니다.")
            return
        
        # 시나리오 목록 다이얼로그
        dialog = QMessageBox(self)
        dialog.setWindowTitle("사용 가능한 시나리오")
        
        scenario_list = "\n".join([f"• {Path(f).name}" for f in scenario_files])
        dialog.setText(f"다음 시나리오 파일들을 사용할 수 있습니다:\n\n{scenario_list}")
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec_()
    
    def start_new_game(self):
        """새 게임 시작"""
        self.log_message("새 게임을 시작합니다...")
        
        async def create_game():
            try:
                # 플레이어 엔티티 ID (실제로는 선택 UI 필요)
                player_entity_id = "TEST_PLAYER_001"
                
                # 게임 매니저로 새 세션 생성
                session_id = await self.game_manager.start_new_game(player_entity_id)
                self.current_session_id = session_id
                
                # 게임 세션 생성
                self.current_session = GameSession(session_id)
                await self.current_session.initialize_session()
                
                # 초기 셀 생성 및 입장
                await self.setup_initial_cell()
                
                return session_id
            except Exception as e:
                raise Exception(f"게임 시작 실패: {str(e)}")
        
        worker = AsyncWorker(create_game())
        self.workers.append(worker)
        worker.finished.connect(self.on_game_started)
        worker.error.connect(self.on_game_error)
        worker.finished.connect(lambda _: self.cleanup_worker(worker))
        worker.error.connect(lambda _: self.cleanup_worker(worker))
        worker.start()
    
    async def setup_initial_cell(self):
        """초기 셀 설정"""
        if not self.current_session:
            return
        
        # 테스트 셀 생성 (실제로는 시작 셀 설정 필요)
        from app.managers.instance_manager import InstanceManager
        instance_manager = InstanceManager()
        
        # 테스트 셀 인스턴스 생성
        cell_data = await instance_manager.instantiate_world_cell(
            self.current_session_id, 
            "CELL_VILLAGE_CENTER_001"
        )
        
        # 플레이어를 셀에 입장
        player_entities = await self.current_session.get_player_entities()
        if player_entities:
            player_id = player_entities[0]['runtime_entity_id']
            await self.current_session.move_player(
                player_id, 
                cell_data['runtime_cell_id'],
                {"x": 50, "y": 0, "z": 50}
            )
    
    def on_game_started(self, session_id: str):
        """게임 시작 완료"""
        self.log_message(f"게임이 시작되었습니다. 세션 ID: {session_id}")
        self.update_game_state()
    
    def on_game_error(self, error_msg: str):
        """게임 오류 처리"""
        QMessageBox.critical(self, "오류", f"게임 시작 중 오류가 발생했습니다:\n{error_msg}")
        self.log_message(f"오류: {error_msg}")
    
    def load_game(self):
        """게임 불러오기"""
        QMessageBox.information(self, "알림", "게임 불러오기 기능은 아직 구현되지 않았습니다.")
    
    def save_game(self):
        """게임 저장"""
        QMessageBox.information(self, "알림", "게임 저장 기능은 아직 구현되지 않았습니다.")
    
    def show_debug_info(self):
        """디버그 정보 표시"""
        if self.current_session:
            info = f"현재 세션: {self.current_session_id}\n"
            info += f"세션 상태: 활성"
        else:
            info = "현재 활성 세션이 없습니다."
        
        QMessageBox.information(self, "디버그 정보", info)
    
    def update_game_state(self):
        """게임 상태 업데이트"""
        if not self.current_session:
            return
        
        async def update():
            try:
                # 세션 정보 업데이트
                session_info = await self.current_session.get_session_info()
                
                # 플레이어 엔티티 정보 업데이트
                player_entities = await self.current_session.get_player_entities()
                if player_entities:
                    player = player_entities[0]
                    self.status_screen.update_player_status(player)
                
                # 맵 정보 업데이트
                await self.map_screen.update_map(self.current_session)
                
                return session_info
            except Exception as e:
                self.log_message(f"상태 업데이트 오류: {str(e)}")
        
        worker = AsyncWorker(update())
        self.workers.append(worker)
        worker.finished.connect(lambda result: self.log_message("상태 업데이트 완료"))
        worker.error.connect(lambda error: self.log_message(f"상태 업데이트 오류: {error}"))
        worker.finished.connect(lambda _: self.cleanup_worker(worker))
        worker.error.connect(lambda _: self.cleanup_worker(worker))
        worker.start()
    
    def on_entity_clicked(self, entity_id: str, entity_type: str):
        """엔티티 클릭 처리"""
        self.log_message(f"엔티티 클릭: {entity_type} (ID: {entity_id})")
        
        if entity_type == 'npc':
            self.start_dialogue(entity_id)
    
    def start_dialogue(self, npc_id: str):
        """NPC와 대화 시작"""
        if not self.current_session:
            return
        
        async def dialogue():
            try:
                player_entities = await self.current_session.get_player_entities()
                if not player_entities:
                    return
                
                player_id = player_entities[0]['runtime_entity_id']
                dialogue_id = await self.current_session.start_npc_dialogue(player_id, npc_id)
                
                if dialogue_id:
                    self.dialogue_screen.start_dialogue(dialogue_id, npc_id)
                    self.log_message(f"대화 시작: {dialogue_id}")
                else:
                    self.log_message("대화를 시작할 수 없습니다.")
            except Exception as e:
                self.log_message(f"대화 시작 오류: {str(e)}")
        
        worker = AsyncWorker(dialogue())
        self.workers.append(worker)
        worker.error.connect(lambda error: self.log_message(f"대화 오류: {error}"))
        worker.finished.connect(lambda _: self.cleanup_worker(worker))
        worker.error.connect(lambda _: self.cleanup_worker(worker))
        worker.start()
    
    def on_dialogue_choice(self, choice: str):
        """대화 선택 처리"""
        self.log_message(f"대화 선택: {choice}")
        
        if not self.current_session:
            return
        
        async def process_choice():
            try:
                response = await self.current_session.handle_dialogue_input(choice, "npc_id")
                self.dialogue_screen.add_message("플레이어", choice)
                self.dialogue_screen.add_message("NPC", response)
            except Exception as e:
                self.log_message(f"대화 처리 오류: {str(e)}")
        
        worker = AsyncWorker(process_choice())
        self.workers.append(worker)
        worker.error.connect(lambda error: self.log_message(f"대화 처리 오류: {error}"))
        worker.finished.connect(lambda _: self.cleanup_worker(worker))
        worker.error.connect(lambda _: self.cleanup_worker(worker))
        worker.start()
    
    def log_message(self, message: str):
        """로그 메시지 추가"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_screen.append(f"[{timestamp}] {message}")
    
    def closeEvent(self, event):
        """윈도우 종료 시 처리"""
        if self.current_session:
            async def cleanup():
                await self.current_session.end_session()
            
            worker = AsyncWorker(cleanup())
            worker.start()
            worker.wait()
        
        event.accept()

    def cleanup_worker(self, worker):
        if worker in self.workers:
            self.workers.remove(worker)
            worker.deleteLater()

    def on_scenario_execution_finished(self, success: bool):
        """시나리오 실행 완료"""
        if success:
            self.log_message("시나리오 실행이 성공적으로 완료되었습니다.")
        else:
            self.log_message("시나리오 실행이 실패했습니다.")
        self.reset_scenario_ui()

def main():
    app = QApplication(sys.argv)
    
    # 폰트 설정
    font = QFont("Malgun Gothic", 9)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 