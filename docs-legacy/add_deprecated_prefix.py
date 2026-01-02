#!/usr/bin/env python3
"""
문서 내용에 [deprecated] 태그와 날짜가 있으면 파일명 앞에 [deprecated] 접두어를 추가하는 스크립트
"""

import os
import re
from pathlib import Path

def has_deprecated_tag(file_path: Path) -> bool:
    """파일 내용에 deprecated 태그가 있는지 확인"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 제목에 [deprecated] 태그가 있는지 확인
            if re.search(r'^#\s*\[deprecated\]', content, re.MULTILINE | re.IGNORECASE):
                return True
            
            # Deprecated 날짜 문구가 있는지 확인
            if re.search(r'Deprecated 날짜|Deprecated 날짜|deprecated 날짜', content, re.IGNORECASE):
                return True
                
            return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def add_deprecated_prefix(file_path: Path) -> bool:
    """파일명 앞에 [deprecated] 접두어 추가"""
    if file_path.name.startswith('[deprecated]'):
        return False  # 이미 접두어가 있음
    
    new_name = f'[deprecated]{file_path.name}'
    new_path = file_path.parent / new_name
    
    try:
        file_path.rename(new_path)
        print(f"Renamed: {file_path.name} -> {new_name}")
        return True
    except Exception as e:
        print(f"Error renaming {file_path}: {e}")
        return False

def process_directory(directory: Path):
    """디렉토리 내의 모든 .md 파일을 처리"""
    count = 0
    
    for file_path in directory.rglob('*.md'):
        # changelog 디렉토리는 제외
        if 'changelog' in str(file_path):
            continue
            
        if has_deprecated_tag(file_path):
            if add_deprecated_prefix(file_path):
                count += 1
    
    return count

def main():
    """메인 함수"""
    docs_dir = Path(__file__).parent
    
    print(f"Processing directory: {docs_dir}")
    print("=" * 60)
    
    count = process_directory(docs_dir)
    
    print("=" * 60)
    print(f"Total files renamed: {count}")

if __name__ == '__main__':
    main()

