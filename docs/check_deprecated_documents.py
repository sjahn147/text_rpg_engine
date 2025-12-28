#!/usr/bin/env python3
"""
문서 내용을 확인하여 deprecated 처리가 필요한 문서를 찾는 스크립트
"""

import re
from pathlib import Path
from datetime import datetime

def check_document(file_path: Path) -> dict:
    """문서 내용을 확인하여 deprecated 여부 판단"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = {
            'path': str(file_path),
            'has_deprecated_tag': False,
            'has_deprecated_date': False,
            'has_updated_date': False,
            'mentions_completed': False,
            'mentions_old_phase': False,
            'suggestions': []
        }
        
        # 제목에 [deprecated] 태그가 있는지 확인
        if re.search(r'^#\s*\[deprecated\]', content, re.MULTILINE | re.IGNORECASE):
            result['has_deprecated_tag'] = True
            result['suggestions'].append("제목에 [deprecated] 태그가 있음")
        
        # Deprecated 날짜 문구가 있는지 확인
        if re.search(r'Deprecated 날짜|deprecated 날짜', content, re.IGNORECASE):
            result['has_deprecated_date'] = True
            result['suggestions'].append("Deprecated 날짜가 명시됨")
        
        # 최신화 날짜가 있는지 확인
        if re.search(r'최신화 날짜|Updated.*date|Last updated', content, re.IGNORECASE):
            result['has_updated_date'] = True
        
        # 완료된 Phase 언급 확인
        if re.search(r'Phase\s*[1-6]\s*(완료|완성|종료)', content, re.IGNORECASE):
            result['mentions_completed'] = True
            result['suggestions'].append("완료된 Phase 언급")
        
        # 오래된 Phase 언급 확인
        if re.search(r'Phase\s*[1-3]', content, re.IGNORECASE):
            result['mentions_old_phase'] = True
            result['suggestions'].append("오래된 Phase 언급")
        
        # "구식", "대체됨", "더 이상 사용" 등의 키워드 확인
        deprecated_keywords = [
            r'구식', r'대체됨', r'더 이상 사용', r'사용하지 않음',
            r'obsolete', r'superseded', r'replaced', r'outdated'
        ]
        for keyword in deprecated_keywords:
            if re.search(keyword, content, re.IGNORECASE):
                result['suggestions'].append(f"deprecated 관련 키워드 발견: {keyword}")
        
        return result
        
    except Exception as e:
        return {
            'path': str(file_path),
            'error': str(e)
        }

def main():
    """메인 함수"""
    docs_dir = Path(__file__).parent
    
    print(f"Checking documents in: {docs_dir}")
    print("=" * 80)
    
    candidates = []
    
    # docs 디렉토리 내의 모든 .md 파일 확인
    for file_path in docs_dir.rglob("*.md"):
        # archive와 changelog 디렉토리는 제외
        if "archive" in str(file_path) or "changelog" in str(file_path):
            continue
        
        # 이미 [deprecated] 접두어가 있는 파일은 제외
        if file_path.name.startswith("[deprecated]"):
            continue
        
        result = check_document(file_path)
        
        # deprecated 처리가 필요한 후보 문서
        if (result.get('has_deprecated_tag') or 
            result.get('has_deprecated_date') or
            (result.get('mentions_completed') and result.get('mentions_old_phase')) or
            len(result.get('suggestions', [])) > 0):
            candidates.append(result)
    
    # 결과 출력
    if candidates:
        print(f"\n⚠️  Deprecated 처리가 필요한 문서 후보: {len(candidates)}개\n")
        for candidate in candidates:
            print(f"📄 {candidate['path']}")
            if candidate.get('suggestions'):
                for suggestion in candidate['suggestions']:
                    print(f"   - {suggestion}")
            print()
    else:
        print("\n✅ Deprecated 처리가 필요한 문서를 찾지 못했습니다.\n")
    
    print("=" * 80)

if __name__ == '__main__':
    main()

