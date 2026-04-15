# Metric3D v2

- 공식 저장소: https://github.com/YvanYin/Metric3D
- 논문: Hu et al., "Metric3D v2: A Versatile Monocular Geometric Foundation Model..." (TPAMI 2024)
- 라이선스: **BSD-2-Clause** (코드·가중치 상업 친화). 별도 상업 문의 연락처 명시.
- 백본 (v2): **DINOv2-reg ViT-S / ViT-L / ViT-Giant2** + RAFT 디코더 (4~8 iterations)
- 기능:
  - **제로샷 metric depth** (카메라 intrinsics를 네트워크 입력으로 받음)
  - **surface normal** 동시 예측 — "geometric foundation model" 지향
- 성능 (ViT-Giant2):
  - KITTI δ1 = 0.989
  - NYU δ1 = 0.987
- 배포: `torch.hub` 지원
- 약점:
  - chandelier, drone 등 저빈도 객체
  - aerial / bird's-eye 관점
- 제안서 관점 포인트: **카메라 intrinsics만 알면 단일 이미지로 실측 단위(m) 3D 복원**이 가능하다는 점이 핵심 셀링 포인트.

## 대표 이미지

- `depth_normal.jpg` — depth + surface normal 동시 출력 예시
- `metrology.jpg` — 실측 metrology 응용 예시 (제안서의 "측정 가능성" 스토리에 적합)
