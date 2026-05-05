"""
Tests for script_nucleus_sd2.py

These tests use mocks so they run without GPU, diffusers, or omni.client.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# ---------------------------------------------------------------------------
# Patch heavy optional dependencies before importing the module under test
# ---------------------------------------------------------------------------

# Fake torch
torch_mock = MagicMock()
torch_mock.cuda.is_available.return_value = False
torch_mock.float32 = "float32"
torch_mock.float16 = "float16"
sys.modules.setdefault("torch", torch_mock)

# Fake diffusers
diffusers_mock = MagicMock()
sys.modules.setdefault("diffusers", diffusers_mock)

# Fake omni.client
omni_mock = MagicMock()
omni_client_mock = MagicMock()
sys.modules.setdefault("omni", omni_mock)
sys.modules.setdefault("omni.client", omni_client_mock)

import script_nucleus_sd2 as sn2  # noqa: E402 – must come after mock setup


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fake_image() -> MagicMock:
    """Return a MagicMock that acts like a PIL Image."""
    img = MagicMock()
    saved_path: list[str] = []
    img.save.side_effect = lambda p: saved_path.append(p)  # record save calls
    return img


# ---------------------------------------------------------------------------
# build_arg_parser
# ---------------------------------------------------------------------------

class TestBuildArgParser:
    def test_required_prompt(self):
        parser = sn2.build_arg_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_defaults(self):
        parser = sn2.build_arg_parser()
        args = parser.parse_args(["--prompt", "hello"])
        assert args.prompt == "hello"
        assert args.steps == sn2.DEFAULT_NUM_INFERENCE_STEPS
        assert args.guidance_scale == sn2.DEFAULT_GUIDANCE_SCALE
        assert args.height == sn2.DEFAULT_HEIGHT
        assert args.width == sn2.DEFAULT_WIDTH
        assert args.seed is None
        assert args.skip_upload is False
        assert args.nucleus_path == "/Projects/SD2"

    def test_custom_args(self):
        parser = sn2.build_arg_parser()
        args = parser.parse_args([
            "--prompt", "sunset",
            "--steps", "10",
            "--guidance-scale", "5.0",
            "--seed", "42",
            "--skip-upload",
            "--nucleus-url", "omniverse://my-server",
            "--nucleus-path", "/MyProject",
        ])
        assert args.steps == 10
        assert args.guidance_scale == 5.0
        assert args.seed == 42
        assert args.skip_upload is True
        assert args.nucleus_url == "omniverse://my-server"
        assert args.nucleus_path == "/MyProject"


# ---------------------------------------------------------------------------
# save_image_locally
# ---------------------------------------------------------------------------

class TestSaveImageLocally:
    def test_creates_directory_and_saves(self, tmp_path):
        image = MagicMock()
        out_dir = tmp_path / "images"
        result = sn2.save_image_locally(image, out_dir, "test.png")
        assert result == out_dir / "test.png"
        image.save.assert_called_once_with(str(out_dir / "test.png"))
        assert out_dir.is_dir()

    def test_returns_path_object(self, tmp_path):
        image = MagicMock()
        result = sn2.save_image_locally(image, tmp_path, "out.png")
        assert isinstance(result, Path)


# ---------------------------------------------------------------------------
# upload_to_nucleus
# ---------------------------------------------------------------------------

class TestUploadToNucleus:
    def test_skips_when_omni_unavailable(self, tmp_path):
        """When omni.client is not importable, upload returns False with a warning."""
        fake_file = tmp_path / "img.png"
        fake_file.write_bytes(b"fake")

        with patch.object(sn2, "_OMNI_AVAILABLE", False):
            result = sn2.upload_to_nucleus(fake_file, "omniverse://localhost", "/Projects/SD2")
        assert result is False

    def test_raises_on_missing_file(self, tmp_path):
        with patch.object(sn2, "_OMNI_AVAILABLE", True):
            with pytest.raises(FileNotFoundError):
                sn2.upload_to_nucleus(tmp_path / "nonexistent.png", "omniverse://localhost", "/P")

    def test_returns_true_on_success(self, tmp_path):
        fake_file = tmp_path / "img.png"
        fake_file.write_bytes(b"fake")

        with patch.object(sn2, "_OMNI_AVAILABLE", True):
            with patch.object(sn2, "omni_client") as mock_oc:
                mock_oc.Result.OK = "OK"
                mock_oc.copy.return_value = "OK"
                result = sn2.upload_to_nucleus(fake_file, "omniverse://localhost", "/Projects/SD2")
        assert result is True

    def test_returns_false_on_failure(self, tmp_path):
        fake_file = tmp_path / "img.png"
        fake_file.write_bytes(b"fake")

        with patch.object(sn2, "_OMNI_AVAILABLE", True):
            with patch.object(sn2, "omni_client") as mock_oc:
                mock_oc.Result.OK = "OK"
                mock_oc.copy.return_value = "ERROR"
                result = sn2.upload_to_nucleus(fake_file, "omniverse://localhost", "/Projects/SD2")
        assert result is False


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

class TestMain:
    def test_skip_upload_returns_zero(self, tmp_path):
        fake_image = MagicMock()
        fake_image.save = MagicMock()

        with patch.object(sn2, "_DIFFUSERS_AVAILABLE", True), \
             patch.object(sn2, "build_pipeline", return_value=MagicMock()), \
             patch.object(sn2, "generate_image", return_value=fake_image), \
             patch.object(sn2, "save_image_locally", return_value=tmp_path / "out.png"):
            rc = sn2.main([
                "--prompt", "test",
                "--skip-upload",
                "--output-dir", str(tmp_path),
            ])
        assert rc == 0

    def test_no_nucleus_url_warns_and_returns_zero(self, tmp_path):
        fake_image = MagicMock()

        with patch.object(sn2, "_DIFFUSERS_AVAILABLE", True), \
             patch.object(sn2, "build_pipeline", return_value=MagicMock()), \
             patch.object(sn2, "generate_image", return_value=fake_image), \
             patch.object(sn2, "save_image_locally", return_value=tmp_path / "out.png"), \
             patch.dict("os.environ", {}, clear=False):
            rc = sn2.main([
                "--prompt", "test",
                "--nucleus-url", "",
                "--output-dir", str(tmp_path),
            ])
        assert rc == 0

    def test_upload_failure_returns_nonzero(self, tmp_path):
        fake_image = MagicMock()

        with patch.object(sn2, "_DIFFUSERS_AVAILABLE", True), \
             patch.object(sn2, "build_pipeline", return_value=MagicMock()), \
             patch.object(sn2, "generate_image", return_value=fake_image), \
             patch.object(sn2, "save_image_locally", return_value=tmp_path / "out.png"), \
             patch.object(sn2, "upload_to_nucleus", return_value=False):
            rc = sn2.main([
                "--prompt", "test",
                "--nucleus-url", "omniverse://localhost",
                "--output-dir", str(tmp_path),
            ])
        assert rc == 1
