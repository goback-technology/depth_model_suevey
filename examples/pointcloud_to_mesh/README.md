# 깊이맵 → 포인트 클라우드 → 3D 메시 (Open3D 기반)

단일 깊이맵 PNG에서 포인트 클라우드(.ply)와 메시(.obj)를 생성하는 예제.  
Depth Anything V2 등의 출력을 그대로 입력으로 쓸 수 있다.

## 파이프라인

```
깊이맵 PNG
  └─ 역변환(inverse depth → 의사 깊이)
      └─ 포인트 클라우드 역투영 (PinholeCameraIntrinsic)
          └─ 법선 추정 (KDTree Hybrid)
              ├─ Poisson Surface Reconstruction → mesh.obj
              └─ Ball Pivoting Algorithm → mesh.obj
```

> 카메라 intrinsics가 없으면 `fx = fy = 0.8 × W`를 가정한다.  
> 이 경우 포인트 클라우드는 **시각화 용도**이며 실측 단위가 없다.

## 설치

```bash
cd /Volumes/data/work/gb_works/depth_model_survey
uv add open3d pillow numpy
```

## 샘플 준비 (DA V2 출력 이용)

```bash
# Depth Anything V2 데모를 먼저 실행해 깊이맵 생성
uv run python examples/depth_anything_v2_minimal/main.py \
  examples/depth_anything_v2_minimal/samples/test.jpg

# 결과를 pointcloud_to_mesh 샘플로 복사
cp examples/depth_anything_v2_minimal/out/test_depth.png \
   examples/pointcloud_to_mesh/samples/depth.png
cp examples/depth_anything_v2_minimal/samples/test.jpg \
   examples/pointcloud_to_mesh/samples/rgb.jpg
```

## 실행

```bash
cd examples/pointcloud_to_mesh

# Poisson 메시 (부드러운 닫힌 표면):
uv run python main.py samples/depth.png --rgb samples/rgb.jpg \
  --method poisson --depth_trunc 2.2

# BPA 메시 (에지 보존):
uv run python main.py samples/depth.png --rgb samples/rgb.jpg \
  --method bpa --depth_trunc 2.2

# 카메라 intrinsics 지정 (실측 치수 필요 시):
uv run python main.py samples/depth.png --fx 525 --fy 525 --cx 320 --cy 240
```

출력 (검증 완료 2026-04-15):
- `out/depth_cloud.ply` — 컬러 포인트 클라우드 ~107만 점 (52MB)
- `out/depth_mesh_poisson.obj` — Poisson 삼각형 메시 (31MB)
- `out/depth_mesh_bpa.obj` — BPA 삼각형 메시 (149MB)

## 전체 파이프라인 (DA V2 → 메시)

```bash
# 1) 깊이맵 생성
uv run python examples/depth_anything_v2_minimal/main.py photo.jpg --out tmp/

# 2) 깊이맵 → 메시 (--depth_trunc는 스케일에 맞게 조정)
uv run python examples/pointcloud_to_mesh/main.py \
  tmp/photo_depth.png --rgb photo.jpg --depth_trunc 2.2
```

## 주의

- `depth_anything_v2_minimal`의 출력은 **상대 affine-invariant 깊이**다. intrinsics 없는 역투영이므로 시각화용.
- 실측 치수가 필요하면 ZoeDepth나 Metric3D v2 출력을 `--fx/--fy/--cx/--cy`와 함께 사용한다.
- Poisson은 닫힌 표면이지만 뭉개짐, BPA는 열린 표면이지만 디테일 보존. 밀도 희박 구역에선 BPA가 깨질 수 있다.
