# Depth Web Demo

FastAPI + React + Three.js 기반 단안 깊이 추정 웹 데모.

## 기능

- 이미지 업로드 후 비동기 Job 처리
- Depth Anything V2 모델 선택 (Small/Base/Large)
- 메시 생성 방식 선택 (Poisson/BPA)
- 복셀 크기/깊이 절단값 조절
- 3D 뷰어에서 복셀/메시 토글 렌더링
- 결과 다운로드: Depth PNG, Voxels JSON, Mesh JSON, Cloud PLY, Mesh OBJ

## 실행

### 1) 백엔드

```bash
cd /home/agent01/works/depth_model_suevey
uv sync
cd web_demo/backend
uv run uvicorn app.main:app --reload --port 8000
```

루트 경로에서 바로 실행하려면 아래처럼 `--app-dir`를 지정해야 한다.

```bash
cd /home/agent01/works/depth_model_suevey
uv run uvicorn --app-dir web_demo/backend app.main:app --reload --port 8000
```

헬스체크:

```bash
curl -sS http://127.0.0.1:8000/health
```

### 1-1) 백엔드 PM2 실행 (권장: 서비스 운영용)

`21031` 포트 기준, ecosystem 파일 사용:

```bash
cd /home/agent01/works/depth_model_suevey
pm2 start web_demo/ecosystem.config.cjs --only dap3d-backend
pm2 save
pm2 startup
```

운영 명령:

```bash
pm2 status
pm2 logs dap3d-backend
pm2 restart dap3d-backend
pm2 stop dap3d-backend
pm2 delete dap3d-backend
```

ecosystem 파일 수정 후 반영:

```bash
cd /home/agent01/works/depth_model_suevey
pm2 reload web_demo/ecosystem.config.cjs --only dap3d-backend --update-env
```

헬스체크:

```bash
curl -sS http://127.0.0.1:21031/health
```

### 2) 프론트엔드

```bash
cd /home/agent01/works/depth_model_suevey/web_demo/frontend
npm install
VITE_BACKEND_URL=http://127.0.0.1:8000 npm run dev
```

백엔드를 다른 포트(예: `21031`)로 띄웠다면:

```bash
cd /home/agent01/works/depth_model_suevey/web_demo/frontend
VITE_BACKEND_URL=http://127.0.0.1:21031 npm run dev
```

또는 `.env.local` 파일을 만들어 고정할 수 있다:

```bash
cd /home/agent01/works/depth_model_suevey/web_demo/frontend
cat > .env.local << 'EOF'
VITE_BACKEND_URL=http://127.0.0.1:21031
EOF
npm run dev
```

브라우저: http://localhost:5173

## 배포 (Nginx + 서브패스)

운영 URL: `http://gobackdev.iptime.org:21038/dap3d/`

- Nginx 설정: `/etc/nginx/sites-available/web_pub`
  - `location /dap3d/` → `/home/agent01/works/web_pub/dap3d/` 정적 서빙
  - `location /api/`, `/artifacts/` → `proxy_pass http://127.0.0.1:21031`
- 프론트엔드 base path: [vite.config.ts](frontend/vite.config.ts)에 `base: "/dap3d/"` 고정. `npm run build`만 하면 서브패스 빌드 결과가 나옴.
- 배포 경로는 **심볼릭 링크**:
  ```
  /home/agent01/works/web_pub/dap3d -> /home/agent01/works/depth_model_suevey/web_demo/frontend/dist
  ```
  따라서 빌드만 하면 자동 반영. 별도 복사 단계 없음.
- 백엔드: PM2 `dap3d-backend` (포트 21031). 코드 수정 후에는 `pm2 restart dap3d-backend` 필수.

### 빌드 & 배포 절차

```bash
# 프론트엔드 변경 → 빌드만 하면 nginx에 즉시 반영 (심볼릭 링크)
cd /home/agent01/works/depth_model_suevey/web_demo/frontend
npm run build

# 백엔드 변경이 있었다면
pm2 restart dap3d-backend

# 검증
curl -s http://gobackdev.iptime.org:21038/api/v1/version
curl -sI http://gobackdev.iptime.org:21038/dap3d/ | head -5
```

브라우저에서는 캐시된 구 번들이 남아 있을 수 있으므로 **Ctrl+Shift+R**로 하드 리로드.

링크가 사라졌다면 재생성:
```bash
ln -s /home/agent01/works/depth_model_suevey/web_demo/frontend/dist /home/agent01/works/web_pub/dap3d
```

## API

- `POST /api/v1/jobs` : 이미지 업로드 + 옵션 전달
- `GET /api/v1/jobs/{job_id}` : 상태/아티팩트 조회
- `GET /artifacts/{job_id}/...` : 생성 파일 접근

### POST form fields

- `image` : 입력 이미지 파일 (최대 10MB)
- `model` : `Small | Base | Large`
- `mesh_method` : `poisson | bpa`
- `voxel_size` : `0.005 ~ 0.2`
- `depth_trunc` : `0.3 ~ 20.0`
