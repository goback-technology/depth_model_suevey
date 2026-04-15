# Memo

본 프로젝트의 참고 정보를 모으는 곳. 조사가 진행되면 이 파일을 갱신한다.

## 제품 기준선

- 최종 목표: 단일 RGB 이미지 → 픽셀 깊이 → 3D 폴리곤 메시 변환 파이프라인의 기술 타당성 검증 및 제안서 작성
- 기준 모델: **Depth Anything V2** (핵심 5종 중 하나, 가장 최신·품질 SOTA급)
- 플랫폼: Python 3.11 + uv + PyTorch(CUDA)
- 메시화: Open3D 기반 실용 경로 (포인트 클라우드 → 법선 → Poisson)

---

## 모델 비교표

| 모델 | 계열/백본 | 깊이 타입 | 라이선스 | 파라미터 | 추론 속도 | 메트릭 지원 |
|------|----------|----------|----------|----------|-----------|------------|
| **Depth Anything V2** | DINOv2 + DPT | 상대(affine-invariant) | Small=Apache-2.0 / Base·Large·Giant=**CC-BY-NC-4.0** | 25M / 98M / 335M / 1.3B | V1 대비↑, SD 대비 10× | 별도 metric fine-tuned 체크포인트(Small/Base) |
| **MiDaS 3.1 / DPT** | BEiT·Swin·LeViT 등 다양 | 상대 | **MIT** | 42M ~ 345M | BEiT-L 5.7 FPS ~ small 90 FPS | 없음 (상대 전용) |
| **ZoeDepth** | MiDaS 백본 + metric bins | **메트릭** (NYU/KITTI) | **MIT** | MiDaS 수준 | MiDaS 수준 | O (ZoeD_N/ZoeD_K/ZoeD_NK) |
| **Marigold** | Stable Diffusion v2 U-Net | 상대(affine-invariant) | 코드 Apache-2.0 / 모델 **RAIL++-M** | SD v2 기반 (~865M) | 느림 (DDIM 1~50 step, 앙상블 10 권장) | 없음 |
| **Metric3D v2** | DINOv2 reg ViT-S/L/G + RAFT 디코더 | **메트릭** (제로샷) | **BSD-2-Clause** (상업 친화) | ViT-S ~ ViT-Giant2 | 중간 | O, intrinsics 입력 필요 |

### 주요 관찰

- **상업 이용 주의**: Depth Anything V2의 Base/Large/Giant는 CC-BY-NC-4.0이라 상용 제품에 직접 탑재 불가. 상용 제안이라면 **Small(Apache-2.0)** 또는 **MiDaS 3.1 / ZoeDepth / Metric3D v2** 후보가 안전하다.
- **메트릭 깊이 필요 여부**: 단순 시각화·3D 썸네일이면 상대 깊이로 충분. 실제 치수 기반 측정/로보틱스라면 ZoeDepth 또는 Metric3D v2.
- **디테일 품질**: Marigold(디퓨전) ≈ Depth Anything V2 > MiDaS/ZoeDepth. Marigold는 느린 대신 에지·얇은 구조 보존 우수.
- **MiDaS는 2025-08-25 아카이브됨** — 유지보수는 중단되었으나 MIT 라이선스와 생태계는 건재.
- **Metric3D v2는 카메라 intrinsics를 네트워크 입력으로 받아** 제로샷으로 절대 단위(m)를 낸다는 점이 특이점.

---

## 모델별 상세

### 1) Depth Anything V2
- 저장소: https://github.com/DepthAnything/Depth-Anything-V2
- 논문: NeurIPS 2024, arXiv:2406.09414
- 저자: Lihe Yang, Bingyi Kang, Zilong Huang, Zhen Zhao, Xiaogang Xu, Jiashi Feng, Hengshuang Zhao
- 핵심 아이디어:
  1. 라벨된 실제 영상 대신 **합성 영상**으로 교사 모델 학습
  2. 교사 모델 용량을 대폭 확장
  3. 대규모 **pseudo-labeled real images**로 학생 모델 학습
- 주장 성능: V1 대비 fine-grained 디테일과 robustness 개선, SD 기반(Marigold) 대비 10× 빠름
- 체크포인트: Small(25M)/Base(98M)/Large(335M)/Giant(1.3B, coming soon)
- 메트릭 변형: Small/Base 기반 metric-depth 체크포인트 별도 공개(2024-06-22)
- 추론 API:
  ```python
  from depth_anything_v2.dpt import DepthAnythingV2
  model = DepthAnythingV2(**model_configs['vitl'])
  model.load_state_dict(torch.load('checkpoints/depth_anything_v2_vitl.pth'))
  model = model.to(DEVICE).eval()
  depth = model.infer_image(cv2.imread('path/to/image'))
  ```
- 출력: 상대 역깊이(affine-invariant inverse depth), H×W float
- 라이선스: **Small = Apache-2.0, Base/Large/Giant = CC-BY-NC-4.0** ← 상용 시 주의

### 2) MiDaS / DPT (Intel ISL)
- 저장소: https://github.com/isl-org/MiDaS (2025-08-25 archived)
- 논문:
  - "Towards Robust Monocular Depth Estimation: Mixing Datasets for Zero-shot Cross-dataset Transfer" (Ranftl et al., TPAMI 2022)
  - "Vision Transformers for Dense Prediction" (Ranftl, Bochkovskiy, Koltun — DPT)
  - MiDaS v3.1 기술 리포트: arXiv:2307.14460
- 학습 데이터: 12개 데이터셋 혼합(ReDWeb, DIML, Movies, MegaDepth, WSVD, TartanAir, HRWSI, ApolloScape, BlendedMVS, IRS, KITTI, NYU v2)
- 손실: scale/shift-invariant
- 라이선스: **MIT** — 상업 이용 자유
- 배포: PyTorch Hub, Docker, ONNX, 모바일 지원. 상대 깊이 전용, 속도/품질 스펙트럼이 넓어 베이스라인으로 꾸준히 사용됨.

### 3) ZoeDepth
- 저장소: https://github.com/isl-org/ZoeDepth
- 논문: "ZoeDepth: Zero-shot Transfer by Combining Relative and Metric Depth" (Bhat et al., arXiv:2302.12288, 2023)
- 구조: **MiDaS를 상대 깊이 백본으로 사용** + metric bins head 추가
- 변형:
  - `ZoeD_N` — NYU v2 기반, 실내 메트릭
  - `ZoeD_K` — KITTI 기반, 실외 메트릭
  - `ZoeD_NK` — 다중 헤드(실내+실외)
- 추론 API: `zoe.infer_pil(image)` → numpy / 16-bit PIL / tensor 선택 가능
- 라이선스: **MIT**
- 단일 모델로 메트릭 깊이를 얻기 가장 간단한 선택지. 단, 일반 in-the-wild 이미지에 대한 일반화는 NYU/KITTI 분포에 치우침.

### 4) Marigold
- 저장소: https://github.com/prs-eth/Marigold
- 논문: "Repurposing Diffusion-Based Image Generators for Monocular Depth Estimation" (Ke et al., **CVPR 2024 Oral, Best Paper Award Candidate**)
- 후속: "Marigold: Affordable Adaptation of Diffusion-Based Image Generators for Image Analysis" (2025)
- 핵심 아이디어: **Stable Diffusion v2 U-Net**을 depth latent로 fine-tune, DDIM 디노이징으로 depth 샘플링
- 권장 설정:
  - 실전: `ensemble_size=1`
  - 논문 비교: `denoise_steps=1, ensemble_size=10` (신규) 또는 `denoise_steps=50, ensemble_size=10` (CVPR 오리지널)
  - `--fp16` 플래그로 속도/VRAM 절감
- 출력: 상대(affine-invariant) 깊이맵, 옵션으로 컬러 시각화
- 라이선스: **코드 Apache-2.0 / 모델 RAIL++-M** — 모델 라이선스가 제한적이라 배포 시 RAIL 조항 확인 필요
- 특징: 디테일 품질 최상급, 대신 느림(디퓨전 반복) 및 VRAM 요구

### 5) Metric3D v2
- 저장소: https://github.com/YvanYin/Metric3D
- 논문: "Metric3D v2: A Versatile Monocular Geometric Foundation Model..." (Hu et al., TPAMI 2024)
- 핵심 아이디어: 카메라 **intrinsics(fx,fy,cx,cy)를 네트워크 입력**으로 받아 제로샷 metric depth
- 백본: v1=ConvNeXt-T/L + Hourglass, **v2=DINOv2-reg ViT-S/L/Giant2 + RAFT 디코더(4~8 iters)**
- v2 추가 기능: **surface normal**도 함께 예측 (geometric foundation model 지향)
- 성능: ViT-giant2 기준 KITTI δ1=0.989, NYU δ1=0.987 (SOTA)
- 약점: chandelier/drone 같은 저빈도 객체, aerial/bird's-eye 뷰에서 성능 저하
- 라이선스: **BSD-2-Clause** (상업 친화). 별도 상업 문의 연락처 명시.

---

## 폴리곤화 파이프라인 (Open3D 기반)

### 1) 깊이 → 포인트 클라우드

카메라 intrinsics가 있으면 그대로 사용, 없으면 가상값을 가정한다.

```python
import open3d as o3d
import numpy as np

H, W = depth.shape
fx = fy = 0.8 * W           # 가상 초점 거리
cx, cy = W / 2, H / 2
intrinsic = o3d.camera.PinholeCameraIntrinsic(W, H, fx, fy, cx, cy)

# 상대 깊이(0~1)는 역변환 + 스케일 필요
depth_m = (1.0 / (depth + 1e-6)).astype(np.float32)  # 역깊이 → 깊이 proxy
depth_o3d = o3d.geometry.Image(depth_m)
pcd = o3d.geometry.PointCloud.create_from_depth_image(
    depth_o3d, intrinsic, depth_scale=1.0, depth_trunc=50.0
)
```

> 주의: affine-invariant inverse depth는 실측 단위가 없으므로 위 결과는 "시각화용"이다. 실제 치수가 필요하면 ZoeDepth 또는 Metric3D v2 출력을 써야 한다.

### 2) 법선 추정

```python
pcd.estimate_normals(
    search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30)
)
pcd.orient_normals_towards_camera_location(camera_location=np.zeros(3))
```

### 3) Poisson Surface Reconstruction

```python
mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
    pcd, depth=9
)
densities = np.asarray(densities)
vertices_to_remove = densities < np.quantile(densities, 0.05)
mesh.remove_vertices_by_mask(vertices_to_remove)
mesh.compute_vertex_normals()
o3d.io.write_triangle_mesh("out/mesh_poisson.obj", mesh)
```

부드러운 표면, 닫힌 메시. 얇은 구조는 뭉개질 수 있음.

### 4) Ball Pivoting 대안

```python
radii = [0.005, 0.01, 0.02, 0.04]
mesh_bpa = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
    pcd, o3d.utility.DoubleVector(radii)
)
```

디테일 보존 우수, 열린 표면 가능, 반지름에 민감.

### 5) 참고 개념 (제안서용 짧은 설명)

- **Marching Cubes**: 3D 스칼라 필드(TSDF/SDF)의 등위면(iso-surface)을 격자별로 삼각형 메시로 추출하는 표준 알고리즘.
- **TSDF Fusion**: Truncated Signed Distance Function을 복셀 그리드에 누적해 다중 프레임을 하나의 표면으로 융합(KinectFusion 계열). 단일 깊이맵보다 **다중 뷰**에 적합.
- **Delaunay 기반**: 포인트 밀도가 균일할 때 유리, 단일 깊이맵엔 Poisson이 무난.

### 6) 대안 파이프라인

- `o3d.geometry.TriangleMesh.create_from_depth_image` 직접 사용 — 빠르지만 카메라 왜곡 보정이 안 되어 품질은 떨어짐.
- MeshLab의 Poisson / Screened Poisson — 오프라인 배치 처리에 좋음.
- Blender Displacement modifier — 아티스트 친화 루트, 텍스처와 결합해 러프 모델링에 쓰임.

---

## 제안서 응용 사례 아이디어

- 문화재·공예품 디지털 아카이브 (단일 사진 → 러프 3D 프리뷰)
- e-커머스 상품 3D 썸네일 생성 파이프라인
- 로봇 조작을 위한 단안 장면 재구성 초기 가설
- AR/VR 콘텐츠·게임 에셋 빠른 프로토타이핑
- 건축/인테리어 사진의 깊이 인지 증강

## BibTeX

```bibtex
@article{Yang2024DepthAnythingV2,
  title   = {Depth Anything V2},
  author  = {Yang, Lihe and Kang, Bingyi and Huang, Zilong and Zhao, Zhen and
             Xu, Xiaogang and Feng, Jiashi and Zhao, Hengshuang},
  journal = {arXiv preprint arXiv:2406.09414},
  year    = {2024},
  note    = {NeurIPS 2024}
}

@article{Ranftl2022MiDaS,
  title   = {Towards Robust Monocular Depth Estimation: Mixing Datasets for
             Zero-shot Cross-dataset Transfer},
  author  = {Ranftl, Ren{\'e} and Lasinger, Katrin and Hafner, David and
             Schindler, Konrad and Koltun, Vladlen},
  journal = {IEEE TPAMI},
  year    = {2022}
}

@inproceedings{Ranftl2021DPT,
  title     = {Vision Transformers for Dense Prediction},
  author    = {Ranftl, Ren{\'e} and Bochkovskiy, Alexey and Koltun, Vladlen},
  booktitle = {ICCV},
  year      = {2021}
}

@article{Birkl2023MiDaS31,
  title   = {MiDaS v3.1 -- A Model Zoo for Robust Monocular Relative Depth Estimation},
  author  = {Birkl, Reiner and Wofk, Diana and M{\"u}ller, Matthias},
  journal = {arXiv preprint arXiv:2307.14460},
  year    = {2023}
}

@article{Bhat2023ZoeDepth,
  title   = {ZoeDepth: Zero-shot Transfer by Combining Relative and Metric Depth},
  author  = {Bhat, Shariq Farooq and Birkl, Reiner and Wofk, Diana and
             Wonka, Peter and M{\"u}ller, Matthias},
  journal = {arXiv preprint arXiv:2302.12288},
  year    = {2023}
}

@inproceedings{Ke2024Marigold,
  title     = {Repurposing Diffusion-Based Image Generators for Monocular Depth Estimation},
  author    = {Ke, Bingxin and Obukhov, Anton and Huang, Shengyu and
               Metzger, Nando and Daudt, Rodrigo Caye and Schindler, Konrad},
  booktitle = {CVPR},
  year      = {2024},
  note      = {Oral, Best Paper Award Candidate}
}

@article{Hu2024Metric3Dv2,
  title   = {Metric3D v2: A Versatile Monocular Geometric Foundation Model for
             Zero-shot Metric Depth and Surface Normal Estimation},
  author  = {Hu, Mu and Yin, Wei and others},
  journal = {IEEE TPAMI},
  year    = {2024}
}
```

## 라이선스 요약 치트시트

| 모델 | 코드 | 가중치 | 상용 가능? |
|------|------|--------|-----------|
| Depth Anything V2 (Small) | Apache-2.0 | Apache-2.0 | ✅ |
| Depth Anything V2 (Base/Large/Giant) | Apache-2.0 | **CC-BY-NC-4.0** | ❌ (비상업 전용) |
| MiDaS / DPT | MIT | MIT | ✅ |
| ZoeDepth | MIT | MIT | ✅ (백본 MiDaS 조건 확인) |
| Marigold | Apache-2.0 | **RAIL++-M** | ⚠ RAIL 조항 검토 필요 |
| Metric3D v2 | BSD-2-Clause | BSD-2-Clause | ✅ |

## 반복 금지 (조사 시 주의점)

- 상대 깊이를 메트릭으로 오해하지 말 것 — scale/shift 미지수
- intrinsics 없는 역투영은 시각화용이며 제안서에도 그 한계를 명시할 것
- "Apache-2.0 코드"라고 해서 **가중치까지 같은 라이선스는 아님** (Depth Anything V2 대형 모델, Marigold 사례)
- Metric3D의 성능 숫자는 KITTI/NYU에서 측정된 것 — 일반 in-the-wild 영상에도 동일하게 보장되지 않음
