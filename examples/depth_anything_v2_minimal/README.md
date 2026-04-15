# Depth Anything V2 — Minimal Demo

단일 이미지를 넣으면 Depth Anything V2로 상대 깊이맵을 뽑아 `out/`에 저장하는 **최소 예제**. transformers 파이프라인만 쓰므로 공식 repo를 clone할 필요가 없다.

## 구성

```
depth_anything_v2_minimal/
├── main.py        # 데모 스크립트
├── README.md      # 이 문서
├── samples/       # 테스트 이미지 두기 (git ignore 권장)
└── out/           # 추론 결과 (git ignore 권장)
```

## 설치

상위 저장소 루트에서 의존성 추가:

```bash
cd /Volumes/data/work/gb_works/depth_model_survey
uv add torch transformers pillow numpy matplotlib
# CUDA 빌드가 필요하면 torch를 먼저 CUDA wheel로 설치:
# uv add --index-url https://download.pytorch.org/whl/cu124 torch
```

## 실행

```bash
cd examples/depth_anything_v2_minimal
# 가볍게 (Small, Apache-2.0):
uv run python main.py samples/test.jpg

# 품질 우선 (Large, 비상업 전용):
uv run python main.py samples/test.jpg --model Large
```

출력:
- `out/<stem>_depth.png` — 16-bit 회색조 상대 깊이
- `out/<stem>_depth_color.png` — turbo 컬러맵 시각화

## 주의

- `Base/Large`는 **CC-BY-NC-4.0**. 상용 파이프라인 검증이면 `Small`을 쓴다.
- 출력은 **상대 깊이**다. 실측 단위가 필요하면 ZoeDepth나 Metric3D v2를 붙여야 한다.
- 모델 가중치는 Hugging Face 캐시에 저장된다. 디스크가 부족하면 환경변수 `HF_HOME`으로 옮긴다.
