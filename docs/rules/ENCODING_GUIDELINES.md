# 인코딩 가이드라인

## 문제 진단

### 인코딩 문제 발생 원인

1. **PowerShell 기본 인코딩 불일치**
   - Windows PowerShell의 기본 인코딩은 UTF-8이 아닐 수 있음
   - 파일을 읽고 쓸 때 인코딩이 일치하지 않으면 한글이 깨짐
   - 깨진 한글 문자열은 "Unterminated string literal" 파싱 오류를 발생시킴

2. **파일 처리 시 인코딩 미지정**
   - 파일을 읽고 쓸 때 인코딩을 명시하지 않으면 시스템 기본값 사용
   - 여러 환경(Windows, Linux, CI/CD)에서 다른 인코딩 사용 가능

3. **일괄 처리 스크립트의 인코딩 문제**
   - PowerShell 스크립트로 파일을 일괄 수정할 때 인코딩을 명시하지 않음
   - 정규식으로 한글을 치환할 때 인코딩 불일치로 추가 손상 발생

## 금지 규칙

### 절대 금지 사항

1. **DO NOT**: 파일을 읽고 쓸 때 인코딩을 명시하지 않고 처리
   ```powershell
   # 금지: 인코딩 미지정
   $content = Get-Content $file.FullName -Raw
   Set-Content $file.FullName $content
   
   # 필수: UTF-8 명시
   $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
   [System.IO.File]::WriteAllText($file.FullName, $content, [System.Text.Encoding]::UTF8)
   ```

2. **DO NOT**: 한글이 포함된 파일을 정규식으로 일괄 치환
   - 깨진 한글을 패턴 매칭으로 복원하려고 시도하면 추가 손상 발생
   - 인코딩이 다른 상태에서 문자열 치환은 위험함

3. **DO NOT**: 인코딩 변환 없이 파일 내용 수정
   - 깨진 파일을 그대로 수정하면 손상이 누적됨
   - 반드시 원본 파일을 UTF-8로 읽고 UTF-8로 저장해야 함

4. **DO NOT**: 테스트 파일에 한글 주석/문자열을 작성한 후 인코딩 확인 없이 커밋
   - 파일 저장 시 UTF-8 인코딩 확인 필수
   - IDE 설정에서 파일 인코딩을 UTF-8로 고정

## 필수 사항

### 파일 처리 시

1. **DO**: 항상 UTF-8 인코딩 명시
   ```typescript
   // TypeScript/JavaScript 파일은 항상 UTF-8로 저장
   // .editorconfig 또는 IDE 설정에서 강제
   ```

2. **DO**: 파일을 수정하기 전에 인코딩 확인
   ```bash
   # 파일 인코딩 확인
   file -bi filename.ts
   # 또는
   chardet filename.ts
   ```

3. **DO**: 한글이 포함된 파일은 수동으로 직접 수정
   - 자동화 스크립트보다는 직접 수정이 안전
   - 각 파일의 내용을 확인하고 올바른 한글로 복원

4. **DO**: .editorconfig에 인코딩 설정 추가
   ```ini
   [*]
   charset = utf-8
   ```

### IDE 설정

1. **VS Code**: `files.encoding` 설정을 `utf8`로 고정
2. **IntelliJ/WebStorm**: File Encoding을 UTF-8로 설정
3. **Git**: `core.autocrlf` 설정 확인 (Windows에서 `false` 권장)

## 복구 방법

### 깨진 파일 복구 절차

1. **원본 파일 확인**: Git 히스토리에서 마지막 정상 상태 확인
2. **수동 복구**: 각 파일을 열어서 올바른 한글로 직접 수정
3. **인코딩 확인**: 저장 전 UTF-8 인코딩 확인
4. **테스트 실행**: 수정 후 테스트가 정상 실행되는지 확인

### 예방 방법

1. **.editorconfig 파일 생성**
   ```ini
   root = true
   
   [*]
   charset = utf-8
   end_of_line = lf
   insert_final_newline = true
   ```

2. **Git 설정**
   ```bash
   git config --global core.autocrlf false
   git config --global core.quotepath false
   ```

3. **IDE 설정 확인**
   - 파일 저장 시 UTF-8 인코딩 강제
   - 한글 주석/문자열 작성 후 인코딩 확인

## 참고

- [UTF-8 Everywhere](https://utf8everywhere.org/)
- [EditorConfig](https://editorconfig.org/)
- [Git Encoding](https://git-scm.com/docs/git-config#Documentation/git-config.txt-coreautocrlf)

