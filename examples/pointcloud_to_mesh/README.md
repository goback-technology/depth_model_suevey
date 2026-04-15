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

## 실행

```bash
cd examples/pointcloud_to_mesh

# 기본 (Poisson):
uv run python main.py samples/depth.png

# BPA 메시:
uv run python main.py samples/depth.png --method bpa

# 컬러 포인트 클라우드 포함:
uv run python main.py samples/depth.png --rgb samples/rgb.jpg

# 카메라 intrinsics 지정 (있는 경우):
uv run python main.py samples/depth.png --fx 525 --fy 525 --cx 320 --cy 240
```

출력:
- `out/<stem>_cloud.ply` — 포인트 클라우드
- `out/<stem>_mesh_poisson.obj` 또는 `out/<stem>_mesh_bpa.obj` — 삼각형 메시

## 파이프라인 두 단계로 분리해서 쓰기

Depth Anything V2 데모와 연결 (전체 파이프라인):

```bash
# 1) 깊이맵 생성
uv run python ../depth_anything_v2_minimal/main.py photo.jpg --out out/

# 2) 깊이맵 → 메시
uv run python main.py out/photo_depth.png --rgb photo.jpg
```

## 주의

- `depth_anything_v2_minimal`의 출력은 **상대 affine-invariant 깊이**다. intrinsics 없는 역투영이므로 시각화용.
- 실측 치수가 필요하면 ZoeDepth나 Metric3D v2 출력을 `--fx/--fy/--cx/--cy`와 함께 사용한다.
- Poisson은 닫힌 표면이지만 뭉개짐, BPA는 열린 표면이지만 디테일 보존. 밀도 희박 구역에선 BPA가 깨질 수 있다.
