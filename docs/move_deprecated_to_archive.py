#!/usr/bin/env python3
"""
deprecated 문서들을 docs/archive/deprecated/ 디렉토리로 이동하는 스크립트
"""

import os
import shutil
from pathlib import Path

def move_deprecated_files(docs_dir: Path):
    """deprecated 파일들을 archive로 이동"""
    archive_dir = docs_dir / "archive" / "deprecated"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    error_count = 0
    skipped_count = 0
    
    # docs 디렉토리 내의 모든 .md 파일 찾기
    for file_path in docs_dir.rglob("*.md"):
        # archive와 changelog 디렉토리는 제외
        if "archive" in str(file_path) or "changelog" in str(file_path):
            continue
        
        # 파일명이 [deprecated]로 시작하는지 확인
        if not file_path.name.startswith("[deprecated]"):
            continue
        
        try:
            # 원본 파일의 상대 경로 계산
            relative_path = file_path.relative_to(docs_dir)
            
            # 대상 경로 생성
            target_path = archive_dir / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 파일 이동
            if target_path.exists():
                print(f"Target exists, removing source: {relative_path}")
                file_path.unlink()
                skipped_count += 1
            else:
                shutil.move(str(file_path), str(target_path))
                print(f"Moved: {relative_path} -> archive/deprecated/{relative_path}")
            
            moved_count += 1
            
        except Exception as e:
            print(f"Error moving {file_path}: {e}")
            error_count += 1
    
    return moved_count, error_count, skipped_count

def main():
    """메인 함수"""
    docs_dir = Path(__file__).parent
    
    print(f"Processing directory: {docs_dir}")
    print("=" * 60)
    
    moved_count, error_count, skipped_count = move_deprecated_files(docs_dir)
    
    print("=" * 60)
    print(f"Total files processed: {moved_count}")
    print(f"Files moved: {moved_count - skipped_count}")
    print(f"Files skipped (already in archive): {skipped_count}")
    if error_count > 0:
        print(f"Errors: {error_count}")

if __name__ == '__main__':
    main()

