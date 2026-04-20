# Inventory

## Repository

- Name: `depth-model-survey`
- Path: `/home/agent01/works/depth_model_suevey`
- Summary: 단일 이미지 깊이 추정/메시화 사전 조사 + 웹 데모 구현/배포 워크스페이스.

## Top-level structure

```
depth_model_suevey/
├── .git/                  # 저장소
├── .gitignore             # uv init 기본값
├── .python-version        # 3.11
├── README.md              # 제안서 문서(mermaid 일부 반영)
├── pyproject.toml         # Python 의존성 (fastapi/uvicorn 포함)
├── main.py                # 기본 엔트리(실사용도 낮음)
├── _forAI/                # AI 작업 문맥 (README/inventory/memo/dev_log/plan)
├── examples/              # 데모 예제 모음
│   ├── depth_anything_v2_minimal/
│   └── pointcloud_to_mesh/
├── web_demo/
│   ├── backend/           # FastAPI Job API
│   ├── frontend/          # React + Vite + Three.js
│   ├── ecosystem.config.cjs
│   └── README.md
└── pds/                   # 제안서 자료
    ├── models/            # 모델별 대표 이미지·README
    ├── papers/            # 논문 PDF·abstract·핵심 그림
    └── applications/      # 응용 사례 이미지
```

## Entrypoints and key modules

- `examples/depth_anything_v2_minimal/main.py`: 단일 이미지 → 깊이맵/컬러맵 생성.
- `examples/pointcloud_to_mesh/main.py`: 깊이맵 → 포인트클라우드/메시 생성.
- `web_demo/backend/app/main.py`: FastAPI 서버 (`/api/v1/jobs`, `/artifacts`).
- `web_demo/frontend/src/App.tsx`: 업로드/상태/3D 뷰어 UI.
- `web_demo/ecosystem.config.cjs`: PM2 운영 설정(`dap3d-backend`, 21031).

## Build and validation commands

- 의존성 동기화: `uv sync`
- 예제 실행:
    - `uv run python examples/depth_anything_v2_minimal/main.py <image>`
    - `uv run python examples/pointcloud_to_mesh/main.py <depth_png> --rgb <image>`
- 웹 데모 백엔드:
    - `uv run uvicorn --app-dir web_demo/backend app.main:app --port 21031`
- 웹 데모 프론트:
    - `cd web_demo/frontend && npm run dev`
    - `cd web_demo/frontend && npm run build`
- PM2:
    - `pm2 start web_demo/ecosystem.config.cjs --only dap3d-backend`

## Runtime

- Python: 3.11 (`.python-version`)
- 패키지 매니저: uv (Python), npm (frontend)
- 디바이스: CUDA GPU 환경 지원, 실패 시 CPU 폴백
- 서비스 URL: `http://gobackdev.iptime.org:21038/dap3d`

## Tests

- 자동 테스트는 없음. 현재는 빌드/헬스체크/수동 UI 검증 중심.

## Notes

- 사전 조사 문서(`pds`, 루트 `README.md`)와 데모 구현(`web_demo`)이 공존한다.
- `_forAI/` 디렉터리를 기준 문서 허브로 사용한다.
- 배포는 Nginx(21038) + backend proxy(`/api`, `/artifacts`) 구성을 사용한다.
- 아티팩트 저장 경로는 `web_demo/backend/data/jobs` 기준.
