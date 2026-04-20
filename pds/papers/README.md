# Papers

핵심 5종 모델의 논문 메타데이터와 인용 정보. 전체 BibTeX와 라이선스 요약은 `_forAI/memo.md`에 통합되어 있다.

## 1) Depth Anything V2 (NeurIPS 2024)

- arXiv: https://arxiv.org/abs/2406.09414
- 저자: Lihe Yang, Bingyi Kang, Zilong Huang, Zhen Zhao, Xiaogang Xu, Jiashi Feng, Hengshuang Zhao
- 요지: 라벨된 실제 이미지 대신 **합성 이미지 + 교사 용량 확장 + pseudo-labeled real image**의 3단계 전략으로 V1 대비 디테일·robustness를 개선. SD 기반(Marigold) 대비 10× 빠르고, 25M~1.3B 규모로 공개.

## 2) MiDaS (TPAMI 2022) + DPT (ICCV 2021) + MiDaS v3.1 (arXiv 2023)

- 저자: René Ranftl 외 (Intel ISL)
- TPAMI: "Towards Robust Monocular Depth Estimation: Mixing Datasets for Zero-shot Cross-dataset Transfer"
- DPT: "Vision Transformers for Dense Prediction" (ICCV 2021)
- v3.1: arXiv:2307.14460 — BEiT/Swin/LeViT 등 다양한 ViT 백본을 통합한 모델 zoo
- 요지: **12개 서로 다른 데이터셋을 혼합**하고 scale/shift-invariant 손실로 학습해 제로샷 cross-dataset 전이를 달성. 상대 깊이 추정의 사실상 표준 베이스라인.

## 3) ZoeDepth (arXiv 2023)

- arXiv: https://arxiv.org/abs/2302.12288
- 저자: Shariq Farooq Bhat, Reiner Birkl, Diana Wofk, Peter Wonka, Matthias Müller
- 요지: MiDaS 상대 깊이 백본 + metric bins head를 결합해 단일 모델로 **실내(NYU)·실외(KITTI) 메트릭 깊이**를 모두 처리. ZoeD_N / ZoeD_K / ZoeD_NK 3종.

## 4) Marigold (CVPR 2024 Oral)

- 제목: "Repurposing Diffusion-Based Image Generators for Monocular Depth Estimation"
- 저자: Bingxin Ke, Anton Obukhov, Shengyu Huang, Nando Metzger, Rodrigo Caye Daudt, Konrad Schindler
- 수상: CVPR 2024 Oral, Best Paper Award Candidate
- 요지: **Stable Diffusion v2 U-Net을 fine-tune**해 depth latent를 샘플링. 적은 학습 데이터로 디테일·에지 품질이 탁월하며, 앙상블과 디노이즈 스텝 수로 품질-속도 균형 조절.

## 5) Metric3D v2 (TPAMI 2024)

- 저자: Mu Hu, Wei Yin 외
- 요지: **카메라 intrinsics를 네트워크 입력**으로 제공해 제로샷 metric depth 달성. v2는 DINOv2-reg ViT + RAFT 디코더 구조이며, surface normal까지 예측하는 기하 기반 모델.

## 인용(BibTeX)

전체 BibTeX는 `../../_forAI/memo.md`의 "BibTeX" 섹션에서 관리한다.
