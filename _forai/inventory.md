# Inventory

## Repository

- Name: `depth-model-survey`
- Path: `/Volumes/data/work/gb_works/depth_model_survey`
- Summary: 단일 이미지에서 픽셀 깊이를 추정해 3D 형상(폴리곤 메시)으로 변환하는 프로젝트의 제안서 작성을 위한 사전 조사 워크스페이스.

## Top-level structure

```
depth_model_survey/
├── .git/                  # 저장소
├── .gitignore             # uv init 기본값
├── .python-version        # 3.11
├── README.md              # (현재 비어 있음)
├── pyproject.toml         # uv init 기본 설정
├── main.py                # uv init 기본 hello-world
├── _forai/                # AI 작업 문맥 (README/inventory/memo/dev_log/plan)
├── examples/              # 데모 예제 모음
│   └── depth_anything_v2_minimal/  (예정)
└── pds/                   # 제안서 자료
    ├── models/            # 모델별 대표 이미지·README
    ├── papers/            # 논문 PDF·abstract·핵심 그림
    └── applications/      # 응용 사례 이미지
```

## Entrypoints and key modules

- `main.py`: `uv init` 기본 hello-world. 실제 작업은 `examples/` 하위에서 진행.
- 최소 데모 예정: `examples/depth_anything_v2_minimal/main.py` — 단일 이미지 → 깊이맵 PNG.

## Build and validation commands

- 의존성 동기화: `uv sync`
- 예제 실행(예정): `uv run python examples/depth_anything_v2_minimal/main.py <image>`
- 모델 가중치 캐시: `/Volumes/data/temp/for_claudeworks/depth_survey/` 아래로 몰아 두고 작업 종료 후 정리.

## Runtime

- Python: 3.11 (`.python-version`)
- 패키지 매니저: uv (pip 직접 사용 금지)
- 디바이스: CUDA GPU 있음 — `torch`는 CUDA 빌드로 설치, 실패 시 CPU 폴백.

## Tests

- 현재 테스트 없음. 데모 예제가 정상 동작하는지 수동 검증.

## Notes

- 본 저장소는 **연구/제안서 사전 조사용**이지 프로덕션 코드가 아니다. 최소 코드 + 문서 중심.
- 이미지·영상·논문 자료는 라이선스를 확인 후 `pds/`에 저장하고, 출처는 `memo.md`에 기록한다.
- 대용량 가중치는 저장소에 커밋하지 않는다 — `.gitignore`에 필요 시 규칙 추가.
