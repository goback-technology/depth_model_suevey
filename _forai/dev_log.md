# Dev Log

## 2026-04-15

### _forAI 문서 세트 초기 생성
- `forai-scaffold` 지침에 따라 `README.md`, `inventory.md`, `memo.md`, `dev_log.md`를 신규 생성.
- 기존 `plan.md`(사용자 요구사항 원본)는 그대로 보존.
- 저장소는 직전에 `uv init`으로 초기화된 상태(Python 3.11, 기본 `main.py`/`pyproject.toml`)임을 확인.

### 사전 조사 1차 완료
- 조사 대상 모델 5종 모두 공식 저장소 확인 완료: Depth Anything V2, MiDaS/DPT, ZoeDepth, Marigold, Metric3D v2.
- `memo.md`에 모델 비교표·상세·폴리곤화 파이프라인(Open3D)·BibTeX·라이선스 치트시트 작성.
- `pds/models/<각모델>/`에 대표 이미지와 `NOTE.md` 저장 완료.
  - depth_anything_v2/teaser.png (프로젝트 페이지 hero)
  - midas/Improvement_vs_FPS.png, Comparison.png (v3.1 모델 zoo 비교)
  - zoedepth/teaser.png
  - marigold/teaser_all.jpg, teaser_depth.png
  - metric3d_v2/depth_normal.jpg, metrology.jpg
- `pds/papers/README.md`에 5편 논문 요약·인용 정보 정리 (BibTeX 본문은 `memo.md` 중앙 관리).
- **중요 발견**: Depth Anything V2 Base/Large/Giant는 CC-BY-NC-4.0 — 상용 시 Small(Apache-2.0)이나 MiDaS/ZoeDepth/Metric3D v2로 대체 필요. 라이선스 치트시트를 memo.md에 추가.
- **중요 발견**: MiDaS repo는 2025-08-25 아카이브됨(유지보수 중단).

### 최소 데모 예제 스캐폴딩
- 경로: `examples/depth_anything_v2_minimal/`
- 파이프라인: HuggingFace `transformers.pipeline("depth-estimation", ...)` — 공식 repo clone 불필요, 가장 짧은 경로
- 기능: 단일 이미지 → `out/<stem>_depth.png` (회색조) + `out/<stem>_depth_color.png` (turbo 컬러맵)
- 체크포인트 선택: Small/Base/Large (기본 Small — 상용 안전)
- 디바이스: `cuda` 자동 감지, 실패 시 CPU 폴백
- `py_compile` 구문 검증 통과
- `samples/test.jpg` (unsplash 거실 사진 1280×853) 배치 완료
- **아직 실제 추론 검증은 수행하지 않음** (torch/transformers 의존성 설치와 가중치 다운로드가 커서 사용자 확인 후 진행 권장)

### 응용 사례 이미지 수집 완료 (2026-04-15)
- `pds/applications/depth_results/` — Depth Anything V2 공식 비교 이미지 15장 (V1 vs V2 디테일, V2 vs Marigold vs GeoWizard, 항공/스케치): depth-anything-v2.github.io
- `pds/applications/cultural_heritage/` — 신전 유적·조각 사진 2장 (Unsplash CC0)
- `pds/applications/ar_vr/` — VR 헤드셋 1장 (Unsplash CC0)
- `pds/applications/ecommerce/` — 공예품 상품 사진 1장 (Unsplash CC0)
- `pds/applications/robotics/` — 산업용 로봇 팔·자율주행 도시 2장 (Unsplash CC0)
- `pds/applications/NOTE.md` — 폴더 구성·라이선스·제안서 응용 스토리 연결 가이드

### 폴리곤화 예제 분리 완료 (2026-04-15)
- `examples/pointcloud_to_mesh/main.py` — 깊이맵 PNG → 포인트 클라우드(.ply) → Poisson/BPA 메시(.obj) 완성 예제
- `examples/pointcloud_to_mesh/README.md` — 설치·실행·두 단계 파이프라인 설명
- memo.md의 스니펫을 실행 가능한 독립 패키지로 분리. 인자: `--method poisson/bpa`, `--rgb`, `--fx/fy/cx/cy`, `--depth_trunc`
- 구문 검증(`py_compile`) 통과

### 현재 상태 (2026-04-15 기준)
- **완료**: _forAI 문서 세트, 5종 모델 조사, 폴리곤화 정리, pds/models, pds/papers, pds/applications, 데모 예제 2종 스캐폴딩
- **보류**: 실제 추론 검증 (torch/transformers 설치 후 사용자와 함께)
- **다음 단계 후보**: 제안서 내용 보강(수치/사례), 추론 검증, PPT 아웃라인

### 제안서 초안 완성 (2026-04-15)
- `readme.md` — 사내 의사결정자 대상 범용 플랫폼 제안서 초안 작성
- 구성: Executive Summary → 배경·문제 → 기술 개요 → 모델 비교표 → 응용 4종(문화재·e-커머스·로봇·AR/VR) → 결과 이미지(V1 vs V2, 모델 비교) → 로드맵 3단계 → 리스크 테이블 → 필요 자원 → 참고
- Phase 1(타당성·데모 2개월) → Phase 2(API 모듈화 +2개월) → Phase 3(사업 연결) 3단계 로드맵
- 라이선스 권장 명시: 상업 배포 = DA V2 Small(Apache-2.0) 또는 Metric3D v2(BSD-2-Clause)

### 추론 검증 완료 (2026-04-15)
- 환경: Apple M1 Max / MPS (CUDA 없음, MPS 자동 감지로 수정)
- 실행: `uv run python examples/depth_anything_v2_minimal/main.py samples/test.jpg`
- 결과: `out/test_depth.png` (회색조 1280×853), `out/test_depth_color.png` (turbo 컬러맵) 정상 생성
- matplotlib `get_cmap` deprecation 경고 수정 (`matplotlib.colormaps.get_cmap`)
- 데모 결과 이미지를 `pds/applications/depth_results_demo/`에 복사, 제안서 §7에 삽입
- 의존성: torch 2.11.0, transformers 5.5.4 — `uv add` 완료, `pyproject.toml` 갱신됨

### pointcloud_to_mesh 검증 완료 (2026-04-15)
- 샘플: DA V2 출력 깊이맵(`test_depth.png`) + 원본 RGB → `samples/depth.png`, `samples/rgb.jpg`
- 수정 사항:
  - 8-bit PNG 입력 처리 (`raw.mode` 분기)
  - inverse depth → 선형 깊이 변환 (`1.0 - norm`) + 0.1~2.1m 범위 클리핑
  - `remove_statistical_outlier` 전처리 추가 (107만 점 → 노이즈 제거)
- 결과 (all OK): `depth_cloud.ply` 52MB, `depth_mesh_poisson.obj` 31MB, `depth_mesh_bpa.obj` 149MB
- open3d 0.19.0 설치됨
- 전체 파이프라인 확정: `depth_anything_v2_minimal` → `pointcloud_to_mesh` 직결 가능
