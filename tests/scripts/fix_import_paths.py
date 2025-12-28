"""
import 경로 일괄 수정
"""
from pathlib import Path
import re

def read_file_safe(file_path: Path) -> str:
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except:
            continue
    raise ValueError(f"파일을 읽을 수 없습니다: {file_path}")

def write_file_safe(file_path: Path, content: str):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_imports(content: str, file_path: Path) -> str:
    original = content
    
    # EditorMode.tsx: ./services/api -> ../services/api
    if 'modes/EditorMode.tsx' in str(file_path):
        content = re.sub(
            r"from ['\"]\.\/services\/api['\"]",
            r"from '../services/api'",
            content
        )
        content = re.sub(
            r"import\(['\"]\.\/services\/api['\"]\)",
            r"import('../services/api')",
            content
        )
    
    # components/editor: ../services/api는 이미 맞음, 하지만 확인
    if 'components/editor' in str(file_path):
        # ./services/api -> ../../services/api
        content = re.sub(
            r"from ['\"]\.\/services\/api['\"]",
            r"from '../../services/api'",
            content
        )
        content = re.sub(
            r"import\(['\"]\.\/services\/api['\"]\)",
            r"import('../../services/api')",
            content
        )
    
    return content

def main():
    base_dir = Path("app/ui/frontend/src")
    
    # 모든 .tsx 파일 수정
    files_to_fix = list(base_dir.rglob("*.tsx"))
    
    fixed_count = 0
    for file_path in files_to_fix:
        if "node_modules" in str(file_path):
            continue
        
        try:
            content = read_file_safe(file_path)
            original = content
            
            content = fix_imports(content, file_path)
            
            if content != original:
                write_file_safe(file_path, content)
                print(f"✅ 수정: {file_path.relative_to(base_dir)}")
                fixed_count += 1
        except Exception as e:
            print(f"❌ 오류 ({file_path}): {e}")
    
    print(f"\n✅ 총 {fixed_count}개 파일 수정 완료")

if __name__ == "__main__":
    main()

