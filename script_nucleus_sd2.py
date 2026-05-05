"""
script_nucleus_sd2.py

Generate images with Stable Diffusion 2 and upload them to an
NVIDIA Omniverse Nucleus server.

Usage
-----
    python script_nucleus_sd2.py --prompt "a red sports car on a race track" \
        --nucleus-url omniverse://localhost \
        --nucleus-path /Projects/SD2 \
        --output-dir ./output

Dependencies
------------
    pip install -r requirements.txt

Environment variables (optional – override CLI flags)
------------------------------------------------------
    NUCLEUS_URL       Nucleus server URL  (e.g. omniverse://my-server)
    NUCLEUS_USER      Nucleus username
    NUCLEUS_PASSWORD  Nucleus password
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional imports – fail gracefully so that the module is importable even
# when the heavy dependencies are not installed (e.g. during unit tests).
# ---------------------------------------------------------------------------
try:
    import torch
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    _DIFFUSERS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _DIFFUSERS_AVAILABLE = False

try:
    import omni.client as omni_client  # NVIDIA Omniverse Client Library
    _OMNI_AVAILABLE = True
except ImportError:
    _OMNI_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SD2_MODEL_ID = "stabilityai/stable-diffusion-2-1"
DEFAULT_NUM_INFERENCE_STEPS = 25
DEFAULT_GUIDANCE_SCALE = 7.5
DEFAULT_HEIGHT = 768
DEFAULT_WIDTH = 768


# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------

def build_pipeline(model_id: str = SD2_MODEL_ID, device: str | None = None) -> "StableDiffusionPipeline":
    """Load and return a Stable Diffusion 2 pipeline."""
    if not _DIFFUSERS_AVAILABLE:
        raise RuntimeError(
            "diffusers and torch are required for image generation. "
            "Install them with: pip install -r requirements.txt"
        )

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    logger.info("Loading Stable Diffusion 2 model '%s' on %s …", model_id, device)
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    pipe = pipe.to(device)
    logger.info("Model loaded.")
    return pipe


def generate_image(
    pipe: "StableDiffusionPipeline",
    prompt: str,
    negative_prompt: str = "",
    num_inference_steps: int = DEFAULT_NUM_INFERENCE_STEPS,
    guidance_scale: float = DEFAULT_GUIDANCE_SCALE,
    height: int = DEFAULT_HEIGHT,
    width: int = DEFAULT_WIDTH,
    seed: int | None = None,
):
    """Run inference and return a PIL image."""
    generator = None
    if seed is not None and _DIFFUSERS_AVAILABLE:
        generator = torch.Generator().manual_seed(seed)

    logger.info("Generating image for prompt: %r", prompt)
    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt or None,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        height=height,
        width=width,
        generator=generator,
    )
    image = result.images[0]
    logger.info("Image generated successfully.")
    return image


def save_image_locally(image, output_dir: str | Path, filename: str) -> Path:
    """Save a PIL image to *output_dir/filename* and return the full path."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    image.save(str(path))
    logger.info("Image saved locally: %s", path)
    return path


# ---------------------------------------------------------------------------
# Nucleus upload
# ---------------------------------------------------------------------------

def upload_to_nucleus(local_path: str | Path, nucleus_url: str, nucleus_path: str) -> bool:
    """
    Upload *local_path* to the Nucleus server at *nucleus_url/nucleus_path*.

    Returns True on success, False otherwise.
    """
    if not _OMNI_AVAILABLE:
        logger.warning(
            "omni.client is not available. Skipping Nucleus upload. "
            "Install the NVIDIA Omniverse Client Library to enable uploads."
        )
        return False

    local_path = Path(local_path)
    if not local_path.exists():
        raise FileNotFoundError(f"Local file not found: {local_path}")

    dest_url = f"{nucleus_url.rstrip('/')}/{nucleus_path.strip('/')}/{local_path.name}"
    logger.info("Uploading %s → %s …", local_path, dest_url)

    omni_client.initialize()
    result = omni_client.copy(str(local_path), dest_url)

    if result == omni_client.Result.OK:
        logger.info("Upload successful: %s", dest_url)
        return True

    logger.error("Upload failed (result=%s): %s", result, dest_url)
    return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate an image with Stable Diffusion 2 and upload it to Nucleus.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Generation options
    gen = parser.add_argument_group("generation")
    gen.add_argument("--prompt", required=True, help="Text prompt for image generation.")
    gen.add_argument("--negative-prompt", default="", help="Negative prompt (things to avoid).")
    gen.add_argument("--model-id", default=SD2_MODEL_ID, help="HuggingFace model ID or local path.")
    gen.add_argument("--steps", type=int, default=DEFAULT_NUM_INFERENCE_STEPS, help="Number of inference steps.")
    gen.add_argument("--guidance-scale", type=float, default=DEFAULT_GUIDANCE_SCALE, help="Classifier-free guidance scale.")
    gen.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help="Output image height in pixels.")
    gen.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="Output image width in pixels.")
    gen.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    gen.add_argument("--output-dir", default="./output", help="Local directory to save generated images.")
    gen.add_argument("--filename", default="sd2_output.png", help="Output image filename.")
    gen.add_argument("--device", default=None, help="Torch device override (e.g. 'cpu', 'cuda', 'mps').")

    # Nucleus options
    nuc = parser.add_argument_group("nucleus")
    nuc.add_argument(
        "--nucleus-url",
        default=os.environ.get("NUCLEUS_URL", ""),
        help="Omniverse Nucleus server URL (e.g. omniverse://localhost).",
    )
    nuc.add_argument(
        "--nucleus-path",
        default="/Projects/SD2",
        help="Destination path on the Nucleus server.",
    )
    nuc.add_argument("--skip-upload", action="store_true", help="Skip Nucleus upload; only save locally.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    # --- Generate image ---
    pipe = build_pipeline(model_id=args.model_id, device=args.device)
    image = generate_image(
        pipe=pipe,
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance_scale,
        height=args.height,
        width=args.width,
        seed=args.seed,
    )
    local_path = save_image_locally(image, args.output_dir, args.filename)

    # --- Upload to Nucleus ---
    if not args.skip_upload:
        if not args.nucleus_url:
            logger.warning(
                "No Nucleus URL provided (--nucleus-url or NUCLEUS_URL env var). "
                "Use --skip-upload to suppress this warning."
            )
        else:
            success = upload_to_nucleus(local_path, args.nucleus_url, args.nucleus_path)
            if not success:
                return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
