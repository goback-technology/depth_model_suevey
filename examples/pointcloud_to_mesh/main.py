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
        pcd, depth=8
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
    # 깊이맵 로드 — 8/16bit 모두 허용
    raw = Image.open(depth_path)
    depth_img = raw.convert("I") if raw.mode not in ("L", "I") else raw
    depth_arr = np.asarray(depth_img, dtype=np.float32)

    # 0~1 정규화
    d_min, d_max = depth_arr.min(), depth_arr.max()
    if d_max > d_min:
        depth_arr = (depth_arr - d_min) / (d_max - d_min)

    # DA V2 출력은 "밝을수록 가까움"(inverse depth).
    # 역변환해서 "밝을수록 멀다"(실제 깊이 방향)로 바꾼다.
    depth_arr = 1.0 - depth_arr  # 0=가까움, 1=멀음

    # 포인트 클라우드의 절대 스케일을 2m 범위로 제한해 메시화 안정성 확보
    depth_arr = depth_arr * 2.0 + 0.1  # 0.1m ~ 2.1m

    H, W = depth_arr.shape
    _fx = fx if fx is not None else 0.8 * W
    _fy = fy if fy is not None else 0.8 * W
    _cx = cx if cx is not None else W / 2.0
    _cy = cy if cy is not None else H / 2.0

    rgb_arr = None
    if rgb_path is not None:
        rgb_img = Image.open(rgb_path).convert("RGB")
        # 깊이맵 해상도에 맞춰 리사이즈
        if rgb_img.size != (W, H):
            rgb_img = rgb_img.resize((W, H), Image.LANCZOS)
        rgb_arr = np.asarray(rgb_img)

    print(f"[info] 깊이맵: {depth_arr.shape}, depth: [{depth_arr.min():.2f}, {depth_arr.max():.2f}]m")
    print(f"[info] intrinsics: fx={_fx:.1f}, fy={_fy:.1f}, cx={_cx:.1f}, cy={_cy:.1f}")

    pcd = depth_to_pcd(depth_arr, rgb_arr, _fx, _fy, _cx, _cy,
                       depth_scale=1.0, depth_trunc=depth_trunc)

    # 노이즈 제거: 통계적 outlier 제거
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    print(f"[info] 포인트 수 (노이즈 제거 후): {len(pcd.points):,}")

    # 메시화 안정성을 위해 voxel 다운샘플링 (목표: ~50만 점 이하)
    n_pts = len(pcd.points)
    if n_pts > 500_000:
        voxel_size = 0.005 * (n_pts / 500_000) ** (1 / 3)
        pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
        print(f"[info] 포인트 수 (다운샘플 후): {len(pcd.points):,}  (voxel={voxel_size:.4f})")

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
