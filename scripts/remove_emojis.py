"""
파일에서 이모지 제거 스크립트
"""
import re
import os
import sys

def remove_emojis_from_file(file_path: str):
    """파일에서 이모지를 제거합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 이모지 패턴 (유니코드 이모지 범위)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"  # Enclosed characters
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002600-\U000026FF"  # Miscellaneous Symbols
            "\U00002700-\U000027BF"  # Dingbats
            "]+",
            flags=re.UNICODE
        )
        
        original_content = content
        content = emoji_pattern.sub('', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"제거 완료: {file_path}")
            return True
        else:
            print(f"이모지 없음: {file_path}")
            return False
    except Exception as e:
        print(f"오류 발생 ({file_path}): {str(e)}")
        return False

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법: python scripts/remove_emojis.py <파일경로> [파일경로2] ...")
        print("또는: python scripts/remove_emojis.py --all")
        sys.exit(1)
    
    if sys.argv[1] == '--all':
        # 모든 Python 파일에서 이모지 제거
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for root, dirs, files in os.walk(base_dir):
            # 특정 디렉토리 제외
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv', 'venv']]
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    remove_emojis_from_file(file_path)
    else:
        # 지정된 파일들에서 이모지 제거
        for file_path in sys.argv[1:]:
            if os.path.exists(file_path):
                remove_emojis_from_file(file_path)
            else:
                print(f"파일을 찾을 수 없습니다: {file_path}")

if __name__ == "__main__":
    main()

