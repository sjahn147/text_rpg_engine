# 월드 에디터 에셋 디렉토리

이 디렉토리는 월드 에디터에서 사용하는 에셋 파일들을 저장합니다.

## 파일 구조

```
assets/world_editor/
├── worldmap.png          # 기본 지도 이미지
└── README.md            # 이 파일
```

## 지도 이미지

### worldmap.png

- **용도**: 월드 에디터의 기본 배경 지도
- **형식**: PNG
- **설명**: 프로젝트의 메인 월드맵 이미지
  - 지역, 도시, 산맥, 바다 등이 표시된 판타지 스타일 지도
  - 그리드 오버레이 지원
  - 핀 배치 및 도로 그리기 작업의 기준이 됨

## 사용 방법

월드 에디터에서 지도 이미지를 로드하려면:

```typescript
// React 컴포넌트에서
import worldmapImage from '../../assets/world_editor/worldmap.png';

// 또는 상대 경로 사용
const imagePath = '/assets/world_editor/worldmap.png';
```

## 향후 확장

- 핀 아이콘 이미지
- 도로 스타일 이미지
- 지역 타입별 아이콘
- 지형 오버레이 이미지

