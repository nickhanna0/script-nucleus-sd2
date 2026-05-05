# script-nucleus-sd2

Generate images with **Stable Diffusion 2** and upload them to an
**NVIDIA Omniverse Nucleus** server.

## Requirements

- Python 3.10+
- (Optional) CUDA-capable GPU for fast inference
- (Optional) [NVIDIA Omniverse Client Library](https://docs.omniverse.nvidia.com/kit/docs/client_library/) for Nucleus uploads

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python script_nucleus_sd2.py \
  --prompt "a futuristic city at night, neon lights, ultra realistic" \
  --nucleus-url omniverse://my-nucleus-server \
  --nucleus-path /Projects/SD2 \
  --output-dir ./output \
  --filename city_night.png
```

Run locally without uploading to Nucleus:

```bash
python script_nucleus_sd2.py \
  --prompt "a serene mountain lake at sunrise" \
  --skip-upload \
  --output-dir ./output
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--prompt` | *(required)* | Text prompt for image generation |
| `--negative-prompt` | `""` | Things to avoid in the image |
| `--model-id` | `stabilityai/stable-diffusion-2-1` | HuggingFace model ID or local path |
| `--steps` | `25` | Number of inference steps |
| `--guidance-scale` | `7.5` | Classifier-free guidance scale |
| `--height` | `768` | Output image height (px) |
| `--width` | `768` | Output image width (px) |
| `--seed` | `None` | Random seed for reproducibility |
| `--output-dir` | `./output` | Local directory to save images |
| `--filename` | `sd2_output.png` | Output image filename |
| `--device` | auto | Torch device (`cpu`, `cuda`, `mps`) |
| `--nucleus-url` | `$NUCLEUS_URL` | Omniverse Nucleus server URL |
| `--nucleus-path` | `/Projects/SD2` | Destination path on the Nucleus server |
| `--skip-upload` | `false` | Skip Nucleus upload; save locally only |

## Environment variables

| Variable | Description |
|----------|-------------|
| `NUCLEUS_URL` | Nucleus server URL (overridden by `--nucleus-url`) |

## Running tests

```bash
pip install pytest
pytest test_script_nucleus_sd2.py -v
```
