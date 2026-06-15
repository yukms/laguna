"""Test suite for DSLR camera configuration and manager."""

import sys
from unittest.mock import MagicMock

import pytest

# Mock gphoto2 before importing DSLR modules (hardware not required for tests).
mock_gp = MagicMock()
mock_gp.Context = MagicMock
mock_gp.Camera = MagicMock
mock_gp.PortInfoList = MagicMock
mock_gp.GP_CAPTURE_IMAGE = 0
mock_gp.GP_FILE_TYPE_NORMAL = 0
sys.modules.setdefault("gphoto2", mock_gp)

from laguna.camera.dslr import DSLRCameraManager


SAMPLE_CONFIG = {
    "cameras": {
        "Hangang": {
            "port": None,
            "iso": "800",
            "aperture": "8",
            "shutter": "1/500",
            "output_dir": "./data/Hangang",
        },
        "Nakdong": {
            "port": "usb:001,003",
            "iso": "400",
            "aperture": "5.6",
            "shutter": "1/250",
            "output_dir": "./data/Nakdong",
        },
    },
    "timelapse": {
        "interval_seconds": 15,
        "total_photos": 5,
    },
}


class TestDSLRCameraManager:
    """Test cases for YAML-driven DSLR camera management."""

    @pytest.fixture
    def manager(self):
        return DSLRCameraManager.from_config(SAMPLE_CONFIG)

    def test_from_config_resolves_named_cameras(self, manager):
        assert manager.camera_names == ["Hangang", "Nakdong"]
        hangang = manager.get("Hangang")
        nakdong = manager.get("Nakdong")

        assert hangang.name == "Hangang"
        assert hangang.settings.iso == "800"
        assert nakdong.name == "Nakdong"
        assert nakdong.settings.port == "usb:001,003"
        assert nakdong.settings.aperture == "5.6"

    def test_get_unknown_camera_raises_key_error(self, manager):
        with pytest.raises(KeyError, match="Unknown camera"):
            manager.get("Seoul")

    def test_empty_cameras_raises_value_error(self):
        with pytest.raises(ValueError, match="cameras"):
            DSLRCameraManager.from_config({"cameras": {}})

    def test_capture_all_parallel_submits_per_camera(self, manager, monkeypatch):
        calls = []

        def fake_worker(name):
            calls.append(name)
            return name, None, None

        monkeypatch.setattr(manager, "_capture_worker", fake_worker)

        results = manager.capture_all_parallel()

        assert set(calls) == {"Hangang", "Nakdong"}
        assert set(results.keys()) == {"Hangang", "Nakdong"}

    def test_get_status_reports_camera_names(self, manager):
        status = manager.get_status()
        assert "Hangang" in status
        assert "Nakdong" in status
        assert status["Hangang"]["output_dir"] == "./data/Hangang"
