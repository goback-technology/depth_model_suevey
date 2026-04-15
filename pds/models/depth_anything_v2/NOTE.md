# Depth Anything V2

- 공식 저장소: https://github.com/DepthAnything/Depth-Anything-V2
- 논문: https://arxiv.org/abs/2406.09414 (NeurIPS 2024)
- 저자: Yang, Kang, Huang, Zhao, Xu, Feng, Zhao
- 체크포인트: Small(25M) / Base(98M) / Large(335M) / Giant(1.3B, 예정)
- 라이선스:
  - **Small**: Apache-2.0 (상업 이용 가능)
  - **Base/Large/Giant**: CC-BY-NC-4.0 (비상업 한정)
- 출력: affine-invariant inverse depth (상대 깊이)
- metric 변형: Small/Base 기반 metric-depth 체크포인트 별도 공개(2024-06-22)
- 대표 이미지: `teaser.png` (공식 프로젝트 페이지 teaser)

## 최소 추론 코드

```python
import cv2, torch
from depth_anything_v2.dpt import DepthAnythingV2

model = DepthAnythingV2(**model_configs['vitl'])
model.load_state_dict(torch.load('checkpoints/depth_anything_v2_vitl.pth'))
model = model.to('cuda').eval()
depth = model.infer_image(cv2.imread('image.jpg'))
```
