# 메뉴바 기능 상태 문서

## ✅ 실제로 작동하는 기능들

### File 메뉴
- **Save Project** (Ctrl+S): 데이터 새로고침 (실제 저장)
- **Export > Entities**: 엔티티 JSON 다운로드 ✅
- **Export > Regions**: 지역 JSON 다운로드 ✅
- **Export > Full**: 전체 데이터 JSON 다운로드 ✅

### Edit 메뉴
- **Undo** (Ctrl+Z): 실행 취소 ✅
- **Redo** (Ctrl+Y): 다시 실행 ✅
- **Cut** (Ctrl+X): 핀 잘라내기 (클립보드 복사 + 삭제) ✅
- **Copy** (Ctrl+C): 핀 복사 (클립보드에 JSON 저장) ✅
- **Paste** (Ctrl+V): 핀 붙여넣기 (클립보드에서 읽어서 새 핀 생성) ✅
- **Duplicate** (Ctrl+D): 핀 복제 ✅
- **Delete** (Del): 핀 삭제 ✅
- **Select All** (Ctrl+A): 첫 번째 핀 선택 (다중 선택은 추후 구현) ✅
- **Deselect All** (Ctrl+Shift+A): 선택 해제 ✅
- **Find** (Ctrl+F): 검색 API 호출 (alert로 결과 표시) ✅
- **Find in Files** (Ctrl+Shift+F): 검색 API 호출 ✅
- **Preferences** (Ctrl+,): 설정 모달 열기 ✅

### View 메뉴
- **View Mode > Map/Explorer**: 모드 전환 ✅
- **Zoom In** (Ctrl+=): 확대 ✅
- **Zoom Out** (Ctrl+-): 축소 ✅
- **Zoom to Fit**: 맵에 맞춤 ✅
- **Zoom to Selection**: 선택된 핀에 맞춤 ✅
- **Grid Toggle**: 그리드 표시/숨김 ✅
- **Fullscreen** (F11): 전체화면 ✅

### Entity 메뉴
- **New > Region**: 지역 생성 ✅
- **New > Location**: 위치 생성 ✅
- **New > Cell**: 셀 생성 ✅
- **New > Entity**: 인물 생성 ✅
- **Entity Relationships**: 관계 조회 (alert로 표시) ✅

### Tools 메뉴
- **Select Tool**: 선택 도구 ✅
- **Pin Tool**: 핀 추가 도구 ✅
- **Road Tool**: 도로 그리기 도구 ✅

### Help 메뉴
- **Keyboard Shortcuts**: 단축키 안내 (alert) ✅
- **About**: 정보 표시 (alert) ✅

## ⚠️ 부분적으로 작동하는 기능들

### File 메뉴
- **New Project**: 데이터 새로고침만 (실제 초기화 없음)
- **Open Project**: alert만 표시
- **Save Project As**: alert만 표시
- **Import > Map**: 파일 선택은 하지만 실제 업로드 없음
- **Import > Entities**: alert만 표시
- **Import > Regions**: alert만 표시

### Edit 메뉴
- **Replace**: alert만 표시

### View 메뉴
- **Grid Settings**: console.log만

### Entity 메뉴
- **Entity Properties**: 이미 편집기가 열려있으면 아무것도 안함

### Tools 메뉴
- **Validate > All**: alert만 표시
- **Validate > Orphans**: alert만 표시
- **Validate > Duplicates**: alert만 표시
- **Batch Operations**: alert만 표시

### Window 메뉴
- **Layout**: console.log만
- **Toggle Panel**: console.log만

## 📝 구현 개선 사항

1. **Cut/Copy/Paste/Duplicate**: 핀에 대해서는 구현 완료, 엔티티는 추후 구현 필요
2. **Select All**: 현재는 첫 번째 핀만 선택, 다중 선택 기능 필요
3. **Zoom to Fit/Selection**: 구현 완료
4. **Import 기능**: 실제 파일 업로드 및 파싱 로직 필요
5. **Validate 기능**: 실제 검증 로직 구현 필요
6. **검색 결과 표시**: 현재는 alert만, 검색 결과 패널 필요

## 사용 방법

### 핀 복사/붙여넣기
1. 핀 선택
2. Edit > Copy (Ctrl+C) 또는 Cut (Ctrl+X)
3. Edit > Paste (Ctrl+V)로 붙여넣기

### 핀 복제
1. 핀 선택
2. Edit > Duplicate (Ctrl+D)

### 줌 기능
- **Zoom to Fit**: View > Zoom > Fit - 맵 전체를 화면에 맞춤
- **Zoom to Selection**: 핀 선택 후 View > Zoom > Selection - 선택된 핀 중심으로 확대

