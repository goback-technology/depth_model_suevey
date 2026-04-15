# Marigold

- 공식 저장소: https://github.com/prs-eth/Marigold
- 논문: Ke et al., "Repurposing Diffusion-Based Image Generators for Monocular Depth Estimation" (**CVPR 2024 Oral, Best Paper Award Candidate**)
- 후속: "Marigold: Affordable Adaptation of Diffusion-Based Image Generators for Image Analysis" (2025)
- 라이선스:
  - 코드: Apache-2.0
  - **모델 가중치: RAIL++-M** (사용 목적 제한 조항 존재 — 상용 배포 시 원문 확인 필수)
- 백본: Stable Diffusion v2 U-Net을 depth latent에 fine-tune
- 동작: DDIM 디노이징으로 depth latent 샘플링 → 디코더로 depth map 복원
- 출력: 상대(affine-invariant) 깊이
- 설정 권장값:
  - 실전: `ensemble_size=1`
  - 논문 비교: `denoise_steps=1, ensemble_size=10` (신판) 또는 `denoise_steps=50, ensemble_size=10` (CVPR 오리지널)
  - `--fp16` 플래그로 속도·VRAM 절감
- 특징: 디테일·에지 보존 우수, 단점은 **속도와 VRAM**
- 최근 확장: depth + surface normal + intrinsic 이미지 분해까지 공통 프레임워크로 확장

## 대표 이미지
- `teaser_all.jpg` — 다중 태스크(깊이·노멀·intrinsic) 결과
- `teaser_depth.png` — 깊이 태스크 전용 hero 이미지
