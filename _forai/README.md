# _forAI Guide

## 한 줄 요약

이 디렉터리는 `depth_model_suevey` 작업을 이어받을 때 필요한 AI 작업 문맥을 정리해 두는 곳이다. 현재는 사전 조사뿐 아니라 **웹 데모(FastAPI + React + Three.js) 구현/배포 상태**까지 포함해 관리한다.

## 읽는 순서

1. `README.md` (이 파일)
2. `inventory.md` — 저장소 구조와 실행 환경
3. `memo.md` — 모델 비교표·폴리곤화 방법·라이선스·BibTeX
4. `dev_log.md` — 날짜별 작업 이력
5. `plan.md` — 사용자가 작성한 원본 요구사항 메모

## 문서 역할

- `plan.md`: 사용자가 직접 적어둔 원본 요구사항(보존). 새 작업 지시를 여기에 섞지 말 것.
- `inventory.md`: 저장소에 실제로 존재하는 구조, 엔트리포인트, 실행 명령.
- `memo.md`: 모델 비교·폴리곤화·논문·라이선스 등 참고 정보 모음.
- `dev_log.md`: 날짜별 작업 이력과 `_forAI` 정비 내역.

## 현재 스냅샷

- 저장소 경로: `/home/agent01/works/depth_model_suevey`
- 프로젝트 타입: Python(uv) + 웹 데모(React/Vite)
- 목표: 깊이 추정 모델 + 메시화 파이프라인 조사 및 웹 데모 운영
- 기준 모델: Depth Anything V2
- 자료 저장소: `./pds/` (models/papers/applications 하위 분류)
- 데모 예제: `./examples/depth_anything_v2_minimal/`, `./examples/pointcloud_to_mesh/`
- 웹 데모: `./web_demo/backend`, `./web_demo/frontend`
- 배포 경로: `/home/agent01/works/web_pub/dap3d` (Nginx 21038)

## 유지 규칙

- 계획이 아닌 참고 정보는 `plan.md`가 아니라 `memo.md`에 둔다.
- 저장소 구조나 실행 명령이 바뀌면 `inventory.md`를 먼저 갱신한다.
- 작업 이력은 날짜를 붙여 `dev_log.md`에만 남긴다.
- 새 작업을 시작할 때는 `inventory.md`와 `memo.md`를 먼저 읽고, 사용자가 남긴 요구사항은 `plan.md`에서 확인한다.
