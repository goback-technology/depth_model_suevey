# Dev Log

## 2026-04-15

### _forai 문서 정리 + 구현 확인 반영 (2026-04-15)
- `_forai/README.md` 스냅샷을 현재 저장소 기준으로 갱신:
  - 실제 경로(`/home/agent01/works/depth_model_suevey`)
  - 웹 데모/배포 상태 포함
- `_forai/inventory.md` 전면 갱신:
  - `web_demo` 구조, 엔트리포인트, 실행/배포 명령, PM2/Nginx 운영 정보 반영
- `_forai/memo.md`에 "구현 확인 상태" 섹션 추가:
  - MVP 구현/운영/아티팩트/빌드 경고 해석/버전 배지 반영 상태 요약
- 구현 확인 중 경로 버그 수정:
  - `web_demo/backend/app/core/settings.py`의 아티팩트 경로를
    `web_demo/backend/data/jobs` 기준으로 수정 (`web_demo/web_demo/...` 중첩 제거)

### 프론트 버전 표시 추가 및 빌드 검증 (2026-04-15)
- `frontend` 상단 헤더에 앱 버전 배지(`v0.1.0`) 표시 추가.
- Vite `define`으로 `__APP_VERSION__` 주입, npm 스크립트에서 `VITE_APP_VERSION=$npm_package_version` 설정.
- `npm run build` 재검증 완료(성공).
- 빌드 로그의 `"use client" ignored` 및 chunk size 메시지는 경고이며, 빌드 실패 아님을 확인.

### PM2 ecosystem 파일 추가 (2026-04-15)
- `web_demo/ecosystem.config.cjs` 신규 생성.
- 앱명: `dap3d-backend`, 포트: `21031`.
- 실행 명령을 `uv run uvicorn --app-dir web_demo/backend app.main:app --port 21031`로 고정.
- `web_demo/README.md`의 PM2 섹션을 ecosystem 기반 실행/리로드 명령으로 갱신.

### 웹 데모 다음 단계 반영 (2026-04-15)
- 백엔드 API 입력 검증 강화:
  - 이미지 업로드 크기 제한 10MB
  - `voxel_size`/`depth_trunc` 범위 검증
- 아티팩트 확장:
  - `cloud.ply`, `mesh.obj` 추가 생성
  - Job 응답 아티팩트에 `point_cloud_url`, `mesh_obj_url` 추가
- 프론트 UI 확장:
  - 모델/메시 방식/파라미터 입력 UI 추가
  - 복셀/메시 표시 토글 추가
  - 깊이맵 프리뷰 및 아티팩트 다운로드 버튼 추가
- 문서:
  - `web_demo/README.md` 실행/엔드포인트 가이드 추가

### 웹 데모 MVP 코드 구현 (2026-04-15)
- 경로: `web_demo/backend`, `web_demo/frontend`.
- 백엔드(FastAPI):
  - `POST /api/v1/jobs` 업로드 + 비동기 처리 시작
  - `GET /api/v1/jobs/{job_id}` 상태 조회
  - `/artifacts/{job_id}/...` 정적 파일 제공
- 파이프라인:
  - Depth Anything V2 추론
  - 포인트클라우드 생성 후 복셀화(`VoxelGrid`)
  - Poisson/BPA 메시 생성
  - `voxels.json`, `mesh.json`, `depth_color.png` 아티팩트 생성
- 프론트엔드(React + Three.js):
  - 이미지 업로드/상태 폴링 UI
  - 복셀(인스턴스 박스) + 메시 동시 렌더링 뷰어
  - 모바일 대응 기본 레이아웃 포함

### 웹 데모 기획 반영 (2026-04-15)
- 사용자 요청으로 `_forai` 문서에 웹 데모 설계 초안 추가.
- 반영 위치: `memo.md`.
- 핵심 결정:
  - 스택: FastAPI(REST) + React(Vite/TS) + Three.js.
  - 처리 방식: v1은 Job API 기반(`POST /jobs`, `GET /jobs/{id}`) 권장.
  - 렌더링 포맷: JSON(vertices/faces)보다 GLB 우선.
  - 기존 `examples/` 파이프라인을 서비스 레이어에서 재사용.

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
