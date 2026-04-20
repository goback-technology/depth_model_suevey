# 단안 깊이 추정 기반 3D 변환 플랫폼 — 기술 기획 제안서

> 작성일: 2026-04-15  
> 상태: 초안 (검토용)

---

## 1. 제안 요약 (Executive Summary)

**일반 카메라 한 대**로 찍은 2D 사진에서 자동으로 깊이 정보를 추정하고,  
3D 포인트 클라우드·메시로 변환하는 **공통 플랫폼 모듈**을 구축한다.

별도 3D 스캐너나 LiDAR 없이 스마트폰·웹캠 수준의 이미지만으로  
문화재 디지털화, 상품 3D 뷰, 로봇 인식, AR/VR 콘텐츠 등  
사내 여러 사업에 즉시 연결 가능한 공통 인프라를 만드는 것이 목표다.

---

## 2. 배경과 문제 인식

### 기존 3D 취득 방식의 한계

| 방식 | 장비 비용 | 운영 난이도 | 적용 범위 |
|------|---------|-----------|----------|
| 3D 레이저 스캐너 | 수천만 원 이상 | 전문 인력 필요 | 고정 대상 |
| 포토그램메트리(Structure from Motion) | 저비용이나 다중 촬영 필수 | 수십~수백 장 촬영 필요 | 실외·대형 객체 |
| RGBD 카메라(Kinect 등) | 수십만 원 | 근거리 제한, 실외 불가 | 실내 단거리 |
| **단안 깊이 추정 (본 제안)** | **카메라만 있으면 됨** | **사진 1장으로 바로 적용** | **실내외·소품·문화재·상품 모두** |

> AI 기반 단안 깊이 추정 기술은 2024~2025년 들어 품질이 상업 활용 가능 수준에 도달했다.  
> 특히 **Depth Anything V2**(NeurIPS 2024)와 **Metric3D v2**(TPAMI 2024)는  
> 기존 방법 대비 10배 이상 빠르면서 디테일·정밀도도 크게 향상됐다.

---

## 3. 기술 개요

### 3.1 파이프라인

```mermaid
graph LR
    A["🖼 입력 이미지<br/>RGB, 단일"] 
    --> B["🧠 깊이 추정 모델<br/>Depth Anything V2<br/>또는 Metric3D v2"]
    --> C["🗺 깊이맵<br/>H×W float"]
    --> D["☁ 포인트 클라우드<br/>역투영<br/>intrinsics 기반"]
    --> E["📦 3D 메시 생성<br/>Poisson 또는 BPA<br/>폴리곤화"]
    --> F["📤 출력<br/>PNG / PLY / OBJ"]
    
    style A fill:#FFE4B5
    style B fill:#87CEEB
    style C fill:#DDA0DD
    style D fill:#98FB98
    style E fill:#F0E68C
    style F fill:#FFB6C1
```

### 3.2 두 가지 깊이 타입과 선택 기준

```mermaid
graph TD
    A["깊이 추정 모델"]
    
    A --> B["상대 깊이"]
    A --> C["메트릭 깊이"]
    
    B --> B1["특징: 픽셀 간 앞/뒤 순서만 정확"]
    B --> B2["실측 단위: 없음"]
    B --> B3["사용처: 시각화, 3D 효과, AR 콘텐츠"]
    
    C --> C1["특징: 카메라 intrinsics → 미터 단위"]
    C --> C2["실측 단위: 미터(m) ✓"]
    C --> C3["사용처: 치수 측정, 로봇 조작, 정밀 복원"]
    
    style B fill:#FFA07A
    style C fill:#87CEEB
```

---

## 4. 핵심 모델 비교

> 사전 조사한 5종 모델의 핵심 지표. 상세 자료는 [`pds/models/`](pds/models/) 참조.

| 모델 | 출시 | 특징 | 라이선스 | 상업 이용 |
|------|------|------|----------|----------|
| **Depth Anything V2-Small** | NeurIPS 2024 | 25M, 가벼움·빠름, 품질 SOTA급 | Apache-2.0 | ✅ 자유 |
| **Depth Anything V2-Large** | NeurIPS 2024 | 335M, 최고 품질 | CC-BY-NC-4.0 | ❌ 비상업 |
| **MiDaS 3.1** | TPAMI 2022 | 성숙한 표준 베이스라인, 다양한 크기 | MIT | ✅ 자유 |
| **ZoeDepth** | arXiv 2023 | MiDaS 기반 + 메트릭 깊이(NYU/KITTI) | MIT | ✅ 자유 |
| **Metric3D v2** | TPAMI 2024 | 카메라 intrinsics 입력 → 제로샷 메트릭, SOTA | BSD-2-Clause | ✅ 자유 |
| Marigold | CVPR 2024 | 디테일 최상, SD 기반으로 느림 | 코드 Apache / 모델 RAIL++-M | ⚠ 검토 필요 |

### 권장 선택 전략

- **기본 채택**: Depth Anything V2-Small — 속도·품질·라이선스 균형 최적
- **메트릭 깊이 필요 시**: Metric3D v2 (BSD-2-Clause) — 카메라 정보만 있으면 제로샷 치수 출력
- **최고 품질 데모 목적**: Depth Anything V2-Large (CC-BY-NC-4.0) — 비상업 환경에서만

---

## 5. 응용 분야 및 사업 가치

```mermaid
graph TD
    A["단안 깊이 추정<br/>플랫폼"]
    
    A --> B["🏛 문화재 디지털화<br/>기존 사진 → 3D 모델<br/>온라인 전시 & 복원"]
    A --> C["🛍 e-커머스 3D 뷰<br/>상품 사진 → 깊이맵<br/>3D 프리뷰, 전환율 ↑"]
    A --> D["🤖 로봇 인식<br/>일반 카메라 + 깊이 추정<br/>저비용 깊이 감지"]
    A --> E["🎮 AR/VR 씬<br/>사진 → 3D 메시<br/>빠른 에셋 프로토타입"]
    
    style B fill:#FFE4B5
    style C fill:#87CEEB
    style D fill:#98FB98
    style E fill:#DDA0DD
```

### 5.1 문화재·유물 디지털 아카이브

![문화재 조각 사진](pds/applications/cultural_heritage/sculpture2.jpg)

- **현황**: 스캐너 장비 없이 보관 중인 유물 사진들이 2D로만 남아있음
- **해결**: 기존 사진 한 장으로 러프 3D 프리뷰 자동 생성
- **활용**: 온라인 전시, 복원 참고, VR/AR 연동
- **참고 연구**: 보로부두르 은닉 부조 사진(1890년 흑백)에서 단안 깊이 추정으로 3D 포인트 클라우드 복원 성공 (Hu et al., 2021)

### 5.2 e-커머스 3D 상품 뷰

![상품 사진](pds/applications/ecommerce/product_pottery.jpg)

- **현황**: 상품 촬영 후 2D 사진만 제공, 3D 뷰는 별도 장비·비용 필요
- **해결**: 기존 상품 사진 → 깊이맵 → PLY → 간단한 3D 미리보기
- **기대 효과**: 별도 3D 촬영 없이 기존 스튜디오 컷 재활용, 구매 전환율 향상
- **주의**: 실측 치수가 필요하면 촬영 시 카메라 정보(intrinsics) 병기 필요

### 5.3 로봇·자동화 장면 인식

![로봇 팔](pds/applications/robotics/robot_arm.jpg)

- **현황**: 로봇 팔 작업 영역 인식에 RGBD 카메라 또는 LiDAR 사용 중 → 비용·세팅 부담
- **해결**: 일반 산업용 카메라 + 단안 깊이 추정으로 저비용 깊이 인식 추가
- **활용**: 물체 위치 추정 보조, 조작 경로 계획 초기 가설 생성
- **권장 모델**: Metric3D v2 (카메라 intrinsics → 미터 단위 출력)

### 5.4 AR/VR 콘텐츠 프로토타이핑

![VR 헤드셋](pds/applications/ar_vr/vr_headset.jpg)

- **현황**: AR/VR 씬 제작에 3D 에셋 필요 → 외주 모델링 또는 3D 스캐너 사용
- **해결**: 사진 → 깊이 → 3D 메시 → AR 씬에 바로 삽입 (러프 에셋 빠른 프로토타이핑)
- **활용**: 프로토타입 제작, 배경 씬 빠른 구성

---

## 6. 모델 결과 예시

> 아래 이미지는 Depth Anything V2 공식 프로젝트 페이지(NeurIPS 2024) 자료.

### V1 → V2 품질 개선 (자전거 — 스포크 디테일)

| 원본 | V1 깊이맵 | **V2 깊이맵** |
|------|---------|------------|
| ![](pds/applications/depth_results/bicycle_img.jpg) | ![](pds/applications/depth_results/bicycle_v1.jpg) | ![](pds/applications/depth_results/bicycle_v2.jpg) |

### 실내 공간 — V1 vs V2

| 원본 | V1 | **V2** |
|------|----|--------|
| ![](pds/applications/depth_results/demo5_img.jpg) | ![](pds/applications/depth_results/demo5_v1.jpg) | ![](pds/applications/depth_results/demo5_v2.jpg) |

### V2 vs Marigold vs GeoWizard (실내)

| 원본 | **V2** | Marigold | GeoWizard |
|------|--------|---------|-----------|
| ![](pds/applications/depth_results/room_img.jpg) | ![](pds/applications/depth_results/room_v2.jpg) | ![](pds/applications/depth_results/room_marigold.jpg) | ![](pds/applications/depth_results/room_geowizard.jpg) |

### 도메인 외 일반화 — 스케치 이미지

| 원본(스케치) | **V2** | Marigold |
|---------|--------|---------|
| ![](pds/applications/depth_results/sketch_img.jpg) | ![](pds/applications/depth_results/sketch_v2.jpg) | ![](pds/applications/depth_results/sketch_marigold.jpg) |

---

## 7. 직접 구동 데모 결과

> Depth Anything V2-Small (Apache-2.0)을 **M1 Max MPS** 환경에서 실제 구동한 결과.  
> 모델 추론 → 포인트 클라우드 → 3D 메시까지 전체 파이프라인을 검증했다.

### 주차장 (Parking Lot)

| 입력 | 깊이맵 (컬러) |
|------|-------------|
| ![입력](examples/pointcloud_to_mesh/samples/parking.jpg) | ![깊이맵](examples/pointcloud_to_mesh/samples/parking_depth_color.png) |

- 산출물: `parking_depth_cloud.ply` (3.4MB, 7만 점), `parking_depth_mesh_poisson.obj` (6.9MB)
- 근거리 차량 = 주황/빨강, 배경 건물 = 파랑. Poisson 메시 생성 성공.

### 도심 도로 (Urban Road)

| 입력 | 깊이맵 (컬러) |
|------|-------------|
| ![입력](examples/pointcloud_to_mesh/samples/road.jpg) | ![깊이맵](examples/pointcloud_to_mesh/samples/road_depth_color.png) |

- 산출물: `road_depth_cloud.ply` (6.4MB, 13만 점), `road_depth_mesh_bpa.obj` (18MB)
- 도로 원근감이 앞→뒤 빨강→파랑 그라디언트로 명확하게 표현. BPA 메시 생성 성공.

**컬러맵 기준**: 붉은색=근거리, 파란색=원거리.

```bash
# 단계 1 — 깊이맵 생성
uv run python examples/depth_anything_v2_minimal/main.py <이미지> --out tmp/

# 단계 2 — 포인트 클라우드 + 메시 생성
uv run python examples/pointcloud_to_mesh/main.py tmp/<stem>_depth.png --rgb <이미지> --depth_trunc 2.2
```

---

## 8. 로드맵

```mermaid
graph LR
    A["🎯 Phase 1<br/>타당성 검증<br/>1~2개월"]
    --> B["✅ DA V2-Small 파이프라인<br/>✅ 3~5건 콘텐츠 테스트<br/>✅ 벤치마크<br/>✅ 라이선스 확정"]
    
    A --> A1["⏱️ 2~4개월"]
    A1 --> C["📡 Phase 2<br/>API 모듈화"]
    
    C --> C1["✅ REST API/gRPC<br/>✅ PNG/PLY/OBJ 출력<br/>✅ 모델 플러그인<br/>✅ 캐시·큐 처리"]
    
    C --> C2["⏱️ 4개월 이후"]
    C2 --> D["🚀 Phase 3<br/>사업 연결"]
    
    D --> D1["✅ e-커머스 파일럿<br/>✅ 문화재 자동화<br/>✅ 로봇 적용<br/>✅ A/B 테스트"]
    
    style A fill:#FFE4B5
    style C fill:#87CEEB
    style D fill:#98FB98
```

---

## 9. 리스크 및 한계

```mermaid
graph TD
    A["리스크 & 한계"]
    
    A --> B["⚠ 상대 깊이 한계"]
    B --> B1["실측 치수 없음<br/> → 메트릭 모델 교체/병행"]
    
    A --> C["⚠ 라이선스 제약"]
    C --> C1["CC-BY-NC-4.0 상업 불가<br/> → Small/Metric3D v2로 고정"]
    
    A --> D["⚠ 복잡한 형태"]
    D --> D1["얇은 구조물·투명 객체<br/> → Marigold 병행"]
    
    A --> E["⚠ 표면 복원 품질"]
    E --> E1["배면 불완전<br/> → '러프 프리뷰' 기대치 관리"]
    
    A --> F["⚠ Intrinsics 미지수"]
    F --> F1["카메라 정보 필요<br/> → EXIF 활용 또는 가상값"]
    
    style B fill:#FFB6C1
    style C fill:#FFB6C1
    style D fill:#FFB6C1
    style E fill:#FFB6C1
    style F fill:#FFB6C1
```

---

## 10. 필요 자원 (추정)

| 항목 | 스펙 | 비고 |
|------|------|------|
| GPU 서버 | NVIDIA VRAM 8GB 이상 | V2-Small: ~2GB VRAM, Metric3D v2-Large: ~8GB |
| Python 환경 | 3.11 + uv + PyTorch(CUDA) + Open3D + transformers | 의존성 목록 별도 관리 |
| 개발 인력 | 1명 (Phase 1~2 기준) | ML 엔지니어 또는 백엔드 + ML 경험자 |
| 기간 | Phase 1: ~2개월, Phase 2: ~2개월 추가 | Phase 3는 사업 일정에 따라 조정 |

---

## 11. 참고 자료

### 논문

- Yang et al., **"Depth Anything V2"**, NeurIPS 2024. [arXiv:2406.09414](https://arxiv.org/abs/2406.09414)
- Ranftl et al., **"Towards Robust Monocular Depth Estimation"**, TPAMI 2022.
- Bhat et al., **"ZoeDepth"**, arXiv:2302.12288, 2023.
- Ke et al., **"Repurposing Diffusion-Based Image Generators for Monocular Depth Estimation"**, CVPR 2024 (Oral).
- Hu et al., **"Metric3D v2"**, TPAMI 2024.

### 코드 및 자료

- [Depth Anything V2 GitHub](https://github.com/DepthAnything/Depth-Anything-V2)
- [Metric3D GitHub](https://github.com/YvanYin/Metric3D)
- [MiDaS GitHub](https://github.com/isl-org/MiDaS) (아카이브)
- [Marigold GitHub](https://github.com/prs-eth/Marigold)
- 본 저장소 사전 조사 문서: [`_forAI/memo.md`](_forAI/memo.md)
- 모델별 상세: [`pds/models/`](pds/models/)
- 응용 사례 이미지: [`pds/applications/`](pds/applications/)

---

*본 제안서는 사전 조사(2026-04-15) 기준 초안입니다. 실제 추론 검증 및 내부 파일럿 결과에 따라 모델 선택·로드맵이 수정될 수 있습니다.*
