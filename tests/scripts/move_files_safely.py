"""
파일 이동 시 인코딩 보존 및 import 경로 수정
"""
import os
import shutil
from pathlib import Path
import re

def read_file_safe(file_path: Path) -> str:
    """안전하게 파일 읽기 (인코딩 자동 감지)"""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return content
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"파일을 읽을 수 없습니다: {file_path}")

def write_file_safe(file_path: Path, content: str):
    """안전하게 파일 쓰기 (UTF-8)"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_import_paths(content: str, old_path: str, new_path: str) -> str:
    """import 경로 수정"""
    # 상대 경로 변환
    old_parts = Path(old_path).parts
    new_parts = Path(new_path).parts
    
    # components/editor/로 이동한 경우
    if 'components/editor' in new_path:
        # from '../components/X' -> from './X' 또는 절대 경로로
        content = re.sub(
            r"from ['\"]\.\.\/components\/([^'\"]+)['\"]",
            r"from './\1'",
            content
        )
        # from '../components/ui/X' -> from '../common/ui/X'
        content = re.sub(
            r"from ['\"]\.\.\/components\/ui\/([^'\"]+)['\"]",
            r"from '../common/ui/\1'",
            content
        )
    
    return content

def move_file_safely(src: Path, dst: Path, fix_imports: bool = True):
    """파일을 안전하게 이동 (인코딩 보존)"""
    if not src.exists():
        print(f"⚠️  파일 없음: {src}")
        return False
    
    try:
        # 파일 읽기
        content = read_file_safe(src)
        
        # import 경로 수정
        if fix_imports:
            content = fix_import_paths(content, str(src), str(dst))
        
        # 대상 디렉토리 생성
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        # 파일 쓰기
        write_file_safe(dst, content)
        
        # 원본 삭제
        src.unlink()
        
        print(f"✅ 이동 완료: {src.name} -> {dst}")
        return True
    except Exception as e:
        print(f"❌ 오류 ({src.name}): {e}")
        return False

def main():
    base_dir = Path("app")
    
    # 1. world_editor/frontend -> ui/frontend (복사 후 삭제)
    print("\n=== Phase 1: world_editor/frontend -> ui/frontend ===")
    src_frontend = base_dir / "world_editor" / "frontend"
    dst_frontend = base_dir / "ui" / "frontend"
    
    if src_frontend.exists() and not dst_frontend.exists():
        print(f"복사 중: {src_frontend} -> {dst_frontend}")
        shutil.copytree(src_frontend, dst_frontend, dirs_exist_ok=True)
        print(f"✅ 복사 완료")
        
        # node_modules 제외하고 나머지 파일들 인코딩 확인 및 재작성
        for file_path in dst_frontend.rglob("*.tsx"):
            if "node_modules" in str(file_path):
                continue
            try:
                content = read_file_safe(file_path)
                write_file_safe(file_path, content)
            except Exception as e:
                print(f"⚠️  {file_path}: {e}")
        
        for file_path in dst_frontend.rglob("*.ts"):
            if "node_modules" in str(file_path):
                continue
            try:
                content = read_file_safe(file_path)
                write_file_safe(file_path, content)
            except Exception as e:
                print(f"⚠️  {file_path}: {e}")
    
    # 2. Editor 컴포넌트들을 components/editor/로 이동
    print("\n=== Phase 2: Editor 컴포넌트 이동 ===")
    editor_components = [
        "MapCanvas.tsx",
        "PinEditorNew.tsx",
        "EntityExplorer.tsx",
        "EntityEditor.tsx",
        "HierarchicalMapView.tsx",
        "CellEntityManager.tsx",
        "PinTreeView.tsx",
        "InfoPanel.tsx",
        "MenuBar.tsx",
        "StatusBar.tsx",
        "Toolbar.tsx",
    ]
    
    components_src = dst_frontend / "src" / "components"
    components_editor_dst = dst_frontend / "src" / "components" / "editor"
    
    for comp_name in editor_components:
        src_file = components_src / comp_name
        if src_file.exists():
            dst_file = components_editor_dst / comp_name
            move_file_safely(src_file, dst_file, fix_imports=True)
    
    # 3. ui 폴더를 common/ui로 이동
    print("\n=== Phase 3: ui 폴더 이동 ===")
    ui_src = components_src / "ui"
    ui_dst = components_src / "common" / "ui"
    
    if ui_src.exists():
        for file_path in ui_src.rglob("*.tsx"):
            relative = file_path.relative_to(ui_src)
            dst_file = ui_dst / relative
            move_file_safely(file_path, dst_file, fix_imports=True)
        
        # 빈 디렉토리 삭제
        try:
            ui_src.rmdir()
        except:
            pass
    
    # 4. 기존 App.tsx를 EditorMode.tsx로 복사
    print("\n=== Phase 4: App.tsx -> EditorMode.tsx ===")
    app_tsx_src = dst_frontend / "src" / "App.tsx"
    editor_mode_dst = dst_frontend / "src" / "modes" / "EditorMode.tsx"
    
    if app_tsx_src.exists() and not editor_mode_dst.exists():
        content = read_file_safe(app_tsx_src)
        # EditorMode로 export 변경
        content = content.replace("function App()", "export function EditorMode()")
        content = content.replace("export default App", "// export default App")
        write_file_safe(editor_mode_dst, content)
        print(f"✅ EditorMode.tsx 생성 완료")
    
    print("\n=== 완료 ===")

if __name__ == "__main__":
    main()

