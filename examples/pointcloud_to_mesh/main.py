"""깊이맵 PNG → 포인트 클라우드 → Poisson 메시 파이프라인.

Open3D를 사용해 단일 깊이맵 이미지에서 3D 메시를 생성한다.
카메라 intrinsics가 없을 때는 가상값(fx=fy=0.8*W)을 가정한다.

사용 예:
    uv run python main.py samples/depth.png
    uv run python main.py samples/depth.png --rgb samples/rgb.jpg --method bpa
    uv run python main.py samples/depth.png --fx 525 --fy 525 --cx 320 --cy 240
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import open3d as o3d
from PIL import Image


def depth_to_pcd(
    depth: np.ndarray,
    rgb: np.ndarray | None,
    fx: float,
    fy: float,
    cx: float,
    cy: float,
    depth_scale: float = 1.0,
    depth_trunc: float = 10.0,
) -> o3d.geometry.PointCloud:
    H, W = depth.shape
    intrinsic = o3d.camera.PinholeCameraIntrinsic(W, H, fx, fy, cx, cy)

    depth_o3d = o3d.geometry.Image(depth.astype(np.float32))
    if rgb is not None:
        rgb_o3d = o3d.geometry.Image(rgb.astype(np.uint8))
        rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
            rgb_o3d,
            depth_o3d,
            depth_scale=depth_scale,
            depth_trunc=depth_trunc,
            convert_rgb_to_intensity=False,
        )
        pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd, intrinsic)
    else:
        pcd = o3d.geometry.PointCloud.create_from_depth_image(
            depth_o3d, intrinsic, depth_scale=depth_scale, depth_trunc=depth_trunc
        )
    return pcd


def estimate_normals(pcd: o3d.geometry.PointCloud) -> o3d.geometry.PointCloud:
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30)
    )
    pcd.orient_normals_towards_camera_location(camera_location=np.zeros(3))
    return pcd


def poisson_mesh(pcd: o3d.geometry.PointCloud) -> o3d.geometry.TriangleMesh:
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd, depth=9
    )
    # 저밀도 버텍스 제거 (floating vertices)
    densities_arr = np.asarray(densities)
    vertices_to_remove = densities_arr < np.quantile(densities_arr, 0.05)
    mesh.remove_vertices_by_mask(vertices_to_remove)
    mesh.compute_vertex_normals()
    return mesh


def bpa_mesh(pcd: o3d.geometry.PointCloud) -> o3d.geometry.TriangleMesh:
    distances = pcd.compute_nearest_neighbor_distance()
    avg_dist = float(np.mean(distances))
    radii = [avg_dist, avg_dist * 2, avg_dist * 4]
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
        pcd, o3d.utility.DoubleVector(radii)
    )
    mesh.compute_vertex_normals()
    return mesh


def run(
    depth_path: Path,
    rgb_path: Path | None,
    out_dir: Path,
    fx: float | None,
    fy: float | None,
    cx: float | None,
    cy: float | None,
    method: str,
    depth_trunc: float,
) -> None:
    # 깊이맵 로드 — 8/16bit 모두 허용, 0~1로 정규화 후 역변환
    depth_img = Image.open(depth_path).convert("I")  # 16-bit grayscale
    depth_arr = np.asarray(depth_img, dtype=np.float32)
    if depth_arr.max() > 1.0:
        depth_arr = depth_arr / depth_arr.max()
    # affine-invariant inverse depth → 의사 깊이 변환
    depth_arr = 1.0 / (depth_arr + 1e-6)

    H, W = depth_arr.shape
    _fx = fx if fx is not None else 0.8 * W
    _fy = fy if fy is not None else 0.8 * W
    _cx = cx if cx is not None else W / 2.0
    _cy = cy if cy is not None else H / 2.0

    rgb_arr = None
    if rgb_path is not None:
        rgb_arr = np.asarray(Image.open(rgb_path).convert("RGB"))

    print(f"[info] 깊이맵: {depth_arr.shape}, fx={_fx:.1f}, fy={_fy:.1f}")

    pcd = depth_to_pcd(depth_arr, rgb_arr, _fx, _fy, _cx, _cy, depth_trunc=depth_trunc)
    pcd = estimate_normals(pcd)

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = depth_path.stem

    ply_path = out_dir / f"{stem}_cloud.ply"
    o3d.io.write_point_cloud(str(ply_path), pcd)
    print(f"[ok] 포인트 클라우드 저장: {ply_path}")

    if method == "poisson":
        mesh = poisson_mesh(pcd)
    else:
        mesh = bpa_mesh(pcd)

    obj_path = out_dir / f"{stem}_mesh_{method}.obj"
    o3d.io.write_triangle_mesh(str(obj_path), mesh)
    print(f"[ok] 메시 저장: {obj_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="깊이맵 PNG → 포인트 클라우드 → Poisson/BPA 메시"
    )
    parser.add_argument("depth", type=Path, help="깊이맵 이미지 경로 (PNG)")
    parser.add_argument("--rgb", type=Path, default=None, help="컬러 이미지 경로 (선택)")
    parser.add_argument("--out", type=Path, default=Path("out"), help="출력 폴더")
    parser.add_argument(
        "--method", choices=["poisson", "bpa"], default="poisson", help="메시화 방법"
    )
    parser.add_argument("--fx", type=float, default=None, help="초점 거리 fx (생략 시 가상값)")
    parser.add_argument("--fy", type=float, default=None, help="초점 거리 fy")
    parser.add_argument("--cx", type=float, default=None, help="주점 cx")
    parser.add_argument("--cy", type=float, default=None, help="주점 cy")
    parser.add_argument("--depth_trunc", type=float, default=10.0, help="최대 깊이 절단값")
    args = parser.parse_args()

    if not args.depth.exists():
        raise SystemExit(f"깊이맵 파일이 없음: {args.depth}")

    run(args.depth, args.rgb, args.out, args.fx, args.fy, args.cx, args.cy,
        args.method, args.depth_trunc)


if __name__ == "__main__":
    main()
