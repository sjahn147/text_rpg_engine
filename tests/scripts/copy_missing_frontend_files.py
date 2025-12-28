"""
프론트엔드 누락 파일 복사 (인코딩 보존)
"""
from pathlib import Path

def read_file_safe(file_path: Path) -> str:
    """안전하게 파일 읽기"""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except:
            continue
    raise ValueError(f"파일을 읽을 수 없습니다: {file_path}")

def write_file_safe(file_path: Path, content: str):
    """안전하게 파일 쓰기 (UTF-8)"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    src_base = Path("app/world_editor/frontend")
    dst_base = Path("app/ui/frontend")
    
    files_to_copy = [
        ("src/main.tsx", "src/main.tsx"),
        ("src/index.css", "src/index.css"),
        ("index.html", "index.html"),
        ("vite.config.ts", "vite.config.ts"),
    ]
    
    for src_rel, dst_rel in files_to_copy:
        src_file = src_base / src_rel
        dst_file = dst_base / dst_rel
        
        if not src_file.exists():
            print(f"⚠️  {src_rel} 없음")
            continue
        
        if dst_file.exists():
            print(f"⏭️  {dst_rel} 이미 존재")
            continue
        
        try:
            content = read_file_safe(src_file)
            
            # main.tsx의 경우 App import 경로 확인
            if "main.tsx" in src_rel:
                # 이미 올바른 경로인지 확인
                if "./App" not in content and "../App" not in content:
                    # 변경 불필요
                    pass
            
            write_file_safe(dst_file, content)
            print(f"✅ {dst_rel} 복사 완료")
        except Exception as e:
            print(f"❌ {dst_rel} 복사 실패: {e}")

if __name__ == "__main__":
    main()

