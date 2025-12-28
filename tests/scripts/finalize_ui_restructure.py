"""
UI 재구조화 최종 정리 - 남은 파일들 처리 및 import 경로 최종 수정
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

def fix_all_import_paths(content: str, file_path: Path) -> str:
    """파일의 모든 import 경로 수정"""
    original = content
    
    # EditorMode.tsx에서 사용하는 경로들
    if 'modes/EditorMode.tsx' in str(file_path) or 'EditorMode' in str(file_path):
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
    
    # components/editor 내부 파일들
    if 'components/editor' in str(file_path):
        # './components/ui/X' -> '../../common/ui/X'
        content = re.sub(
            r"from ['\"]\.\/components\/ui\/([^'\"]+)['\"]",
            r"from '../../common/ui/\1'",
            content
        )
        # '../components/ui/X' -> '../../common/ui/X'
        content = re.sub(
            r"from ['\"]\.\.\/components\/ui\/([^'\"]+)['\"]",
            r"from '../../common/ui/\1'",
            content
        )
        # './components/X' -> '../components/editor/X' (같은 editor 폴더 내)
        # 단, ui는 제외하고, 이미 editor가 아닌 경우만
        content = re.sub(
            r"from ['\"]\.\/components\/(?!ui\/)(?!editor\/)([^'\"]+)['\"]",
            r"from '../components/editor/\1'",
            content
        )
        # '../components/X' -> '../components/editor/X' (상위에서 editor로)
        content = re.sub(
            r"from ['\"]\.\.\/components\/(?!ui\/)(?!editor\/)([^'\"]+)['\"]",
            r"from '../components/editor/\1'",
            content
        )
    
    # components/common/ui 내부 파일들
    if 'components/common/ui' in str(file_path):
        # 같은 디렉토리 내 파일 참조는 그대로 유지
        pass
    
    return content

def copy_missing_files():
    """world_editor/frontend에서 ui/frontend로 누락된 파일 복사"""
    src_base = Path("app/world_editor/frontend/src")
    dst_base = Path("app/ui/frontend/src")
    
    if not src_base.exists():
        print("✅ world_editor/frontend/src 없음 (이미 정리됨)")
        return
    
    # 복사할 파일 패턴
    patterns = [
        ("components/**/*.tsx", "components/editor"),
        ("components/**/*.ts", "components/editor"),
        ("hooks/**/*.ts", "hooks"),
        ("services/**/*.ts", "services"),
        ("types/**/*.ts", "types"),
        ("*.css", ""),
        ("*.json", ""),
    ]
    
    copied_count = 0
    for pattern, subdir in patterns:
        src_files = list(src_base.glob(pattern))
        for src_file in src_files:
            # node_modules 제외
            if "node_modules" in str(src_file):
                continue
            
            # 상대 경로 계산
            rel_path = src_file.relative_to(src_base)
            
            # components는 editor로, 나머지는 그대로
            if subdir == "components/editor":
                # 이미 editor에 있는 파일은 스킵
                if (dst_base / "components" / "editor" / rel_path.name).exists():
                    continue
                dst_file = dst_base / "components" / "editor" / rel_path.name
            elif subdir:
                dst_file = dst_base / subdir / rel_path.name
            else:
                dst_file = dst_base / rel_path.name
            
            # 이미 존재하면 스킵
            if dst_file.exists():
                continue
            
            try:
                content = read_file_safe(src_file)
                # import 경로 수정
                content = fix_all_import_paths(content, dst_file)
                write_file_safe(dst_file, content)
                copied_count += 1
                print(f"  ✅ 복사: {rel_path.name}")
            except Exception as e:
                print(f"  ⚠️  복사 실패 ({rel_path.name}): {e}")
    
    print(f"✅ 총 {copied_count}개 파일 복사 완료")

def fix_existing_imports():
    """기존 파일들의 import 경로 수정"""
    print("\n=== 기존 파일 import 경로 수정 ===")
    
    base_dir = Path("app/ui/frontend/src")
    
    # 모든 .tsx, .ts 파일 검색
    for file_path in base_dir.rglob("*.tsx"):
        if "node_modules" in str(file_path):
            continue
        
        try:
            content = read_file_safe(file_path)
            original = content
            
            # import 경로 수정
            content = fix_all_import_paths(content, file_path)
            
            if content != original:
                write_file_safe(file_path, content)
                print(f"  ✅ 수정: {file_path.relative_to(base_dir)}")
        except Exception as e:
            print(f"  ⚠️  수정 실패 ({file_path}): {e}")
    
    for file_path in base_dir.rglob("*.ts"):
        if "node_modules" in str(file_path):
            continue
        
        try:
            content = read_file_safe(file_path)
            original = content
            
            # import 경로 수정
            content = fix_all_import_paths(content, file_path)
            
            if content != original:
                write_file_safe(file_path, content)
                print(f"  ✅ 수정: {file_path.relative_to(base_dir)}")
        except Exception as e:
            print(f"  ⚠️  수정 실패 ({file_path}): {e}")

def main():
    print("=== UI 재구조화 최종 정리 ===")
    
    # 1. 누락된 파일 복사
    print("\n=== Phase 1: 누락된 파일 복사 ===")
    copy_missing_files()
    
    # 2. 기존 파일 import 경로 수정
    print("\n=== Phase 2: 기존 파일 import 경로 수정 ===")
    fix_existing_imports()
    
    print("\n=== 완료 ===")

if __name__ == "__main__":
    main()

