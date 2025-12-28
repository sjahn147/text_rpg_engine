"""
UI 재구조화 완료 스크립트 - 인코딩 보존 및 import 경로 수정
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

def fix_import_paths_for_editor_mode(content: str) -> str:
    """EditorMode.tsx용 import 경로 수정"""
    # './components/X' -> '../components/editor/X'
    content = re.sub(
        r"from ['\"]\.\/components\/([^'\"]+)['\"]",
        r"from '../components/editor/\1'",
        content
    )
    # './services/X' -> '../services/X'
    content = re.sub(
        r"from ['\"]\.\/services\/([^'\"]+)['\"]",
        r"from '../services/\1'",
        content
    )
    # './hooks/X' -> '../hooks/X'
    content = re.sub(
        r"from ['\"]\.\/hooks\/([^'\"]+)['\"]",
        r"from '../hooks/\1'",
        content
    )
    # './types' -> '../types'
    content = re.sub(
        r"from ['\"]\.\/types['\"]",
        r"from '../types'",
        content
    )
    return content

def fix_import_paths_for_components(content: str, component_name: str) -> str:
    """컴포넌트 파일의 import 경로 수정"""
    # './components/ui/X' -> '../common/ui/X'
    content = re.sub(
        r"from ['\"]\.\/components\/ui\/([^'\"]+)['\"]",
        r"from '../../common/ui/\1'",
        content
    )
    # '../components/ui/X' -> '../common/ui/X'
    content = re.sub(
        r"from ['\"]\.\.\/components\/ui\/([^'\"]+)['\"]",
        r"from '../common/ui/\1'",
        content
    )
    # './components/X' -> '../components/editor/X' (같은 디렉토리 내 컴포넌트)
    # 단, ui는 제외
    content = re.sub(
        r"from ['\"]\.\/components\/(?!ui\/)([^'\"]+)['\"]",
        r"from '../components/editor/\1'",
        content
    )
    return content

def main():
    base_dir = Path("app")
    
    # 1. world_editor/frontend의 App.tsx를 EditorMode.tsx로 복사
    print("\n=== Phase 1: App.tsx -> EditorMode.tsx ===")
    src_app = base_dir / "world_editor" / "frontend" / "src" / "App.tsx"
    dst_editor_mode = base_dir / "ui" / "frontend" / "src" / "modes" / "EditorMode.tsx"
    
    if src_app.exists():
        print(f"읽는 중: {src_app}")
        content = read_file_safe(src_app)
        
        # App -> EditorMode로 변경
        content = content.replace("const App: React.FC = () => {", "export const EditorMode: React.FC = () => {")
        content = content.replace("export default App;", "// export default App;")
        
        # import 경로 수정
        content = fix_import_paths_for_editor_mode(content)
        
        # 쓰기
        write_file_safe(dst_editor_mode, content)
        print(f"✅ EditorMode.tsx 생성 완료")
    else:
        print(f"⚠️  {src_app} 없음")
    
    # 2. Editor 컴포넌트들의 import 경로 수정
    print("\n=== Phase 2: Editor 컴포넌트 import 경로 수정 ===")
    editor_components_dir = base_dir / "ui" / "frontend" / "src" / "components" / "editor"
    
    if editor_components_dir.exists():
        for tsx_file in editor_components_dir.glob("*.tsx"):
            print(f"수정 중: {tsx_file.name}")
            content = read_file_safe(tsx_file)
            original_content = content
            
            # import 경로 수정
            content = fix_import_paths_for_components(content, tsx_file.name)
            
            if content != original_content:
                write_file_safe(tsx_file, content)
                print(f"  ✅ {tsx_file.name} 수정 완료")
            else:
                print(f"  ⏭️  {tsx_file.name} 변경 없음")
    
    # 3. common/ui 컴포넌트들의 import 경로 수정
    print("\n=== Phase 3: common/ui 컴포넌트 import 경로 수정 ===")
    common_ui_dir = base_dir / "ui" / "frontend" / "src" / "components" / "common" / "ui"
    
    if common_ui_dir.exists():
        for tsx_file in common_ui_dir.glob("*.tsx"):
            print(f"수정 중: {tsx_file.name}")
            content = read_file_safe(tsx_file)
            original_content = content
            
            # common/ui는 상대 경로만 수정
            # './X' -> 같은 디렉토리이므로 변경 불필요
            # '../X' -> 상위 디렉토리 참조는 그대로 유지
            
            if content != original_content:
                write_file_safe(tsx_file, content)
                print(f"  ✅ {tsx_file.name} 수정 완료")
            else:
                print(f"  ⏭️  {tsx_file.name} 변경 없음")
    
    # 4. App.tsx 생성 (모드 전환용)
    print("\n=== Phase 4: App.tsx 생성 (모드 전환용) ===")
    app_tsx = base_dir / "ui" / "frontend" / "src" / "App.tsx"
    
    app_content = '''/**
 * 통합 UI 메인 앱 - Editor/Game 모드 전환
 */
import React, { useState } from 'react';
import { EditorMode } from './modes/EditorMode';
// import { GameMode } from './modes/GameMode'; // 추후 구현

function App() {
  // URL 파라미터로 모드 확인
  const urlParams = new URLSearchParams(window.location.search);
  const urlMode = urlParams.get('mode') as 'editor' | 'game' | null;
  
  const [mode, setMode] = useState<'editor' | 'game'>(urlMode || 'editor');
  
  return (
    <div className="app-container">
      {/* 모드 전환 버튼 (개발용) */}
      <div className="fixed top-4 left-4 z-50">
        <button
          onClick={() => setMode(mode === 'editor' ? 'game' : 'editor')}
          className="px-4 py-2 bg-white/20 text-black rounded-lg hover:bg-white/30 transition-colors"
        >
          {mode === 'editor' ? '게임 모드' : '에디터 모드'}
        </button>
      </div>
      
      {mode === 'editor' ? <EditorMode /> : <div>Game Mode - 추후 구현</div>}
    </div>
  );
}

export default App;
'''
    
    write_file_safe(app_tsx, app_content)
    print(f"✅ App.tsx 생성 완료")
    
    print("\n=== 완료 ===")

if __name__ == "__main__":
    main()

