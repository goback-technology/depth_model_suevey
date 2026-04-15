from __future__ import annotations

import asyncio
import json
from pathlib import Path

import numpy as np
import open3d as o3d
import torch
from PIL import Image
from transformers import pipeline

from app.schemas.job import JobArtifacts, JobStatus
from app.services.store import job_store

MODEL_IDS = {
    "Small": "depth-anything/Depth-Anything-V2-Small-hf",
    "Base": "depth-anything/Depth-Anything-V2-Base-hf",
    "Large": "depth-anything/Depth-Anything-V2-Large-hf",
}


def _select_device() -> tuple[str, int]:
    if torch.cuda.is_available():
        return "cuda", 0
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps", 0
    return "cpu", -1


def _infer_depth(image_path: Path, out_dir: Path, model_key: str) -> tuple[Path, Path]:
    _, pipe_device = _select_device()

    pipe = pipeline(
        task="depth-estimation",
        model=MODEL_IDS[model_key],
        device=pipe_device,
    )

    image = Image.open(image_path).convert("RGB")
    result = pipe(image)
    depth_pil: Image.Image = result["depth"]

    out_dir.mkdir(parents=True, exist_ok=True)
    gray_path = out_dir / "depth.png"
    color_path = out_dir / "depth_color.png"

    depth_pil.save(gray_path)

    depth = np.array(depth_pil, dtype=np.float32)
    depth_norm = (depth - depth.min()) / max(depth.max() - depth.min(), 1e-6)
    turbo = _apply_turbo(depth_norm)
    Image.fromarray(turbo).save(color_path)

    return gray_path, color_path


def _apply_turbo(depth_norm: np.ndarray) -> np.ndarray:
    import matplotlib

    cmap = matplotlib.colormaps.get_cmap("turbo")
    rgba = (cmap(depth_norm) * 255).astype(np.uint8)
    return rgba[..., :3]


def _load_depth_for_geometry(depth_path: Path) -> np.ndarray:
    raw = Image.open(depth_path)
    depth_img = raw.convert("I") if raw.mode not in ("L", "I") else raw
    depth_arr = np.asarray(depth_img, dtype=np.float32)

    d_min, d_max = depth_arr.min(), depth_arr.max()
    if d_max > d_min:
        depth_arr = (depth_arr - d_min) / (d_max - d_min)

    depth_arr = 1.0 - depth_arr
    depth_arr = depth_arr * 2.0 + 0.1
    return depth_arr


def _depth_to_point_cloud(
    depth: np.ndarray,
    rgb: np.ndarray,
    depth_trunc: float,
) -> o3d.geometry.PointCloud:
    h, w = depth.shape
    fx = 0.8 * w
    fy = 0.8 * w
    cx = w / 2.0
    cy = h / 2.0

    intrinsic = o3d.camera.PinholeCameraIntrinsic(w, h, fx, fy, cx, cy)
    depth_o3d = o3d.geometry.Image(depth.astype(np.float32))
    rgb_o3d = o3d.geometry.Image(rgb.astype(np.uint8))

    rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
        rgb_o3d,
        depth_o3d,
        depth_scale=1.0,
        depth_trunc=depth_trunc,
        convert_rgb_to_intensity=False,
    )
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd, intrinsic)
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30)
    )
    pcd.orient_normals_towards_camera_location(camera_location=np.zeros(3))
    return pcd


def _voxelize(pcd: o3d.geometry.PointCloud, voxel_size: float) -> list[list[float]]:
    voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size=voxel_size)
    centers: list[list[float]] = []
    for voxel in voxel_grid.get_voxels():
        center = voxel_grid.get_voxel_center_coordinate(voxel.grid_index)
        centers.append([float(center[0]), float(center[1]), float(center[2])])
    return centers


def _mesh_from_pcd(pcd: o3d.geometry.PointCloud, method: str) -> o3d.geometry.TriangleMesh:
    if method == "bpa":
        distances = pcd.compute_nearest_neighbor_distance()
        avg_dist = float(np.mean(distances)) if distances else 0.01
        radii = [avg_dist, avg_dist * 2.0, avg_dist * 4.0]
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
            pcd, o3d.utility.DoubleVector(radii)
        )
    else:
        mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            pcd, depth=8
        )
        densities_arr = np.asarray(densities)
        vertices_to_remove = densities_arr < np.quantile(densities_arr, 0.05)
        mesh.remove_vertices_by_mask(vertices_to_remove)

    mesh.compute_vertex_normals()
    return mesh


def _serialize_mesh(mesh: o3d.geometry.TriangleMesh) -> dict[str, list[list[float]] | list[list[int]]]:
    vertices = np.asarray(mesh.vertices, dtype=np.float32).tolist()
    faces = np.asarray(mesh.triangles, dtype=np.int32).tolist()
    return {"vertices": vertices, "faces": faces}


def _save_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


async def run_job(
    job_id: str,
    image_path: Path,
    artifact_dir: Path,
    *,
    model: str,
    mesh_method: str,
    voxel_size: float,
    depth_trunc: float,
) -> None:
    try:
        await job_store.update(job_id, status=JobStatus.running, message="depth estimation")

        depth_path, depth_color_path = await asyncio.to_thread(
            _infer_depth, image_path, artifact_dir, model
        )

        await job_store.update(job_id, status=JobStatus.running, message="geometry reconstruction")

        rgb = np.asarray(Image.open(image_path).convert("RGB"))
        depth = _load_depth_for_geometry(depth_path)
        h, w = depth.shape
        if (rgb.shape[1], rgb.shape[0]) != (w, h):
            rgb_img = Image.fromarray(rgb).resize((w, h), Image.LANCZOS)
            rgb = np.asarray(rgb_img)

        pcd = await asyncio.to_thread(_depth_to_point_cloud, depth, rgb, depth_trunc)
        voxels = await asyncio.to_thread(_voxelize, pcd, voxel_size)
        mesh = await asyncio.to_thread(_mesh_from_pcd, pcd, mesh_method)
        mesh_json = await asyncio.to_thread(_serialize_mesh, mesh)

        voxels_path = artifact_dir / "voxels.json"
        point_cloud_path = artifact_dir / "cloud.ply"
        mesh_path = artifact_dir / "mesh.json"
        mesh_obj_path = artifact_dir / "mesh.obj"

        await asyncio.to_thread(o3d.io.write_point_cloud, str(point_cloud_path), pcd)
        await asyncio.to_thread(o3d.io.write_triangle_mesh, str(mesh_obj_path), mesh)
        await asyncio.to_thread(_save_json, voxels_path, {"points": voxels, "voxel_size": voxel_size})
        await asyncio.to_thread(_save_json, mesh_path, mesh_json)

        artifacts = JobArtifacts(
            depth_color_url=f"/artifacts/{job_id}/depth_color.png",
            voxels_url=f"/artifacts/{job_id}/voxels.json",
            mesh_url=f"/artifacts/{job_id}/mesh.json",
            point_cloud_url=f"/artifacts/{job_id}/cloud.ply",
            mesh_obj_url=f"/artifacts/{job_id}/mesh.obj",
        )
        await job_store.update(job_id, status=JobStatus.done, message="completed", artifacts=artifacts)
    except Exception as exc:  # pragma: no cover
        await job_store.update(job_id, status=JobStatus.failed, message=str(exc))
