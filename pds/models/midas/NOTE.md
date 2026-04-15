# MiDaS / DPT

- 공식 저장소: https://github.com/isl-org/MiDaS (2025-08-25 아카이브)
- 논문:
  - Ranftl et al., "Towards Robust Monocular Depth Estimation" (TPAMI 2022)
  - Ranftl, Bochkovskiy, Koltun, "Vision Transformers for Dense Prediction" (ICCV 2021, DPT)
  - Birkl, Wofk, Müller, "MiDaS v3.1" (arXiv:2307.14460)
- 라이선스: **MIT** (코드·가중치 모두)
- 모델 변형 (v3.1): BEiT-L 345M / Swin2-L 213M / LeViT 51M / v21-small 21M 등 다양
- 출력: 상대 깊이(affine-invariant)
- 속도: BEiT-L 5.7 FPS ~ small 90 FPS
- 특징: 12개 데이터셋 혼합 학습, PyTorch Hub/Docker/ONNX/모바일 지원
- 상태: 유지보수 중단이나 생태계는 살아있음. 상용 베이스라인으로 안전한 선택.

## 참고 이미지

- `Improvement_vs_FPS.png` — v3.1 모델 zoo의 속도·정확도 trade-off
- `Comparison.png` — 모델 간 결과 비교
