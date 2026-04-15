# ZoeDepth

- 공식 저장소: https://github.com/isl-org/ZoeDepth
- 논문: Bhat et al., "ZoeDepth: Zero-shot Transfer by Combining Relative and Metric Depth" (arXiv:2302.12288, 2023)
- 저자: Bhat, Birkl, Wofk, Wonka, Müller
- 라이선스: **MIT**
- 구조: MiDaS를 상대 깊이 백본으로 사용하고, metric bins head를 얹은 구조
- 변형:
  - `ZoeD_N` — NYU v2 학습 (실내 metric)
  - `ZoeD_K` — KITTI 학습 (실외 metric)
  - `ZoeD_NK` — 멀티 헤드 (실내+실외)
- 출력: 절대 깊이(미터 단위). numpy / 16-bit PIL / tensor 선택 가능.
- 의존성: `torch.hub`로 MiDaS 최신 fetch 필요

## 최소 추론 코드

```python
from PIL import Image
import torch

zoe = torch.hub.load("isl-org/ZoeDepth", "ZoeD_NK", pretrained=True).to("cuda")
image = Image.open("img.jpg").convert("RGB")
depth_numpy = zoe.infer_pil(image)               # float, 미터
depth_pil   = zoe.infer_pil(image, output_type="pil")  # 16-bit PIL
```

## 대표 이미지
- `teaser.png` — 공식 repo teaser
