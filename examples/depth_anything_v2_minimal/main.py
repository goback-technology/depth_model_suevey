"""Depth Anything V2 최소 데모.

단일 RGB 이미지를 입력받아 Depth Anything V2로 상대 깊이를 추정하고,
회색조 PNG와 컬러맵 PNG를 out/ 폴더에 저장한다.

사용 예:
    uv run python main.py samples/test.jpg
    uv run python main.py samples/test.jpg --model Small --out out/
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from transformers import pipeline

MODEL_IDS = {
    "Small": "depth-anything/Depth-Anything-V2-Small-hf",
    "Base": "depth-anything/Depth-Anything-V2-Base-hf",
    "Large": "depth-anything/Depth-Anything-V2-Large-hf",
}


def _select_device() -> tuple[str, int]:
    """사용 가능한 최선의 디바이스를 반환한다. (device_str, pipeline_device_id)"""
    if torch.cuda.is_available():
        return "cuda", 0
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps", 0
    return "cpu", -1


def infer(image_path: Path, model_key: str, out_dir: Path) -> None:
    device, pipe_device = _select_device()
    print(f"[info] device = {device}, model = {model_key}")

    pipe = pipeline(
        task="depth-estimation",
        model=MODEL_IDS[model_key],
        device=pipe_device,
    )

    image = Image.open(image_path).convert("RGB")
    result = pipe(image)
    depth_pil: Image.Image = result["depth"]

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = image_path.stem

    gray_path = out_dir / f"{stem}_depth.png"
    depth_pil.save(gray_path)
    print(f"[ok] saved {gray_path}")

    depth = np.array(depth_pil, dtype=np.float32)
    depth_norm = (depth - depth.min()) / max(depth.max() - depth.min(), 1e-6)
    color = _apply_turbo(depth_norm)
    color_path = out_dir / f"{stem}_depth_color.png"
    Image.fromarray(color).save(color_path)
    print(f"[ok] saved {color_path}")


def _apply_turbo(depth_norm: np.ndarray) -> np.ndarray:
    """matplotlib 없이 쓰기 위한 간이 turbo 컬러맵."""
    try:
        import matplotlib
        cmap = matplotlib.colormaps.get_cmap("turbo")
        rgba = (cmap(depth_norm) * 255).astype(np.uint8)
        return rgba[..., :3]
    except ImportError:
        gray = (depth_norm * 255).astype(np.uint8)
        return np.stack([gray, gray, gray], axis=-1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Depth Anything V2 minimal demo")
    parser.add_argument("image", type=Path, help="입력 이미지 경로")
    parser.add_argument(
        "--model",
        choices=list(MODEL_IDS),
        default="Small",
        help="체크포인트 선택 (Small=Apache-2.0, Base/Large=CC-BY-NC-4.0)",
    )
    parser.add_argument("--out", type=Path, default=Path("out"), help="출력 폴더")
    args = parser.parse_args()

    if not args.image.exists():
        raise SystemExit(f"입력 이미지가 없음: {args.image}")

    infer(args.image, args.model, args.out)


if __name__ == "__main__":
    main()
