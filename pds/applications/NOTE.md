# Applications — 제안서용 이미지 자료

## 폴더 구성

| 폴더 | 내용 | 출처 / 라이선스 |
|------|------|---------------|
| `depth_results/` | Depth Anything V2 공식 비교 이미지 (V1 vs V2, V2 vs Marigold vs GeoWizard) | depth-anything-v2.github.io — 학술/비상업 발표 자료, NeurIPS 2024 |
| `cultural_heritage/` | 신전 유적·조각 사진 (입력 이미지 예시용) | Unsplash — CC0 (저작권 없음) |
| `ar_vr/` | VR 헤드셋 착용 사진 (AR/VR 응용 스토리용) | Unsplash — CC0 |
| `ecommerce/` | 도자기·공예품 상품 사진 (e-커머스 3D 썸네일 스토리용) | Unsplash — CC0 |
| `robotics/` | 산업용 로봇 팔·자율주행 도시 거리 사진 | Unsplash — CC0 |

## depth_results 이미지 설명

### V1 vs V2 디테일 비교
- `bicycle_img/v1/v2.jpg` — 자전거: 스포크·프레임 디테일 차이가 명확
- `demo5_img/v1/v2.jpg` — 실내 공간: 가구 에지와 원거리 객체 품질 비교

### V2 vs Marigold vs GeoWizard 비교
- `room_*` — 실내방: 모델별 벽/가구/조명 표현 비교
- `sketch_*` — 스케치 그림: in-domain 외 데이터 일반화 비교

### 항공/도시 뷰
- `aerial_img/v2.jpg` — 항공 사진에서 V2 적용 결과

## 응용 사례 스토리 연결 가이드

| 응용 분야 | 사용 이미지 | 제안서 포인트 |
|----------|------------|------------|
| 문화재 디지털 아카이브 | `cultural_heritage/` 입력 → `depth_results/` 깊이맵 | 단일 사진 → 러프 3D 프리뷰, 비전문가도 가능 |
| e-커머스 3D 썸네일 | `ecommerce/product_pottery.jpg` | 제품 사진 → 깊이맵 → PLY로 3D 확인 |
| 로봇 조작 | `robotics/robot_arm.jpg` | 환경 깊이 인식 → 물체 파지 경로 계획 |
| 자율주행 | `robotics/autonomous_car_street.jpg` | 카메라만으로 거리 추정 보조 |
| AR/VR 콘텐츠 | `ar_vr/vr_headset.jpg` + depth 결과 | 2D 사진 → 깊이 → 3D 씬 삽입 |
| 그림/스케치 3D화 | `depth_results/sketch_*` | 도메인 외(회화·일러스트)에서도 동작 확인 |
