"""
components/editor 내의 ./ui/ import 경로 수정
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

def main():
    editor_dir = Path("app/ui/frontend/src/components/editor")
    
    fixed_count = 0
    for file_path in editor_dir.glob("*.tsx"):
        try:
            content = read_file_safe(file_path)
            original = content
            
            # ./ui/Modal -> ../common/ui/Modal
            content = re.sub(
                r"from ['\"]\.\/ui\/([^'\"]+)['\"]",
                r"from '../common/ui/\1'",
                content
            )
            
            if content != original:
                write_file_safe(file_path, content)
                print(f"✅ 수정: {file_path.name}")
                fixed_count += 1
        except Exception as e:
            print(f"❌ 오류 ({file_path}): {e}")
    
    print(f"\n✅ 총 {fixed_count}개 파일 수정 완료")

if __name__ == "__main__":
    main()

