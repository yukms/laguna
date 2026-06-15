"""Canon DSLR control via libgphoto2 for Laguna experiments."""

from __future__ import annotations

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import gphoto2 as gp

logger = logging.getLogger(__name__)


@dataclass
class DSLRSettings:
    iso: str = "800"
    aperture: str = "8"
    shutter: str = "1/500"
    output_dir: str = "./data"
    port: Optional[str] = None


class DSLRCamera:
    """Controls a single Canon DSLR over USB via gphoto2."""

    def __init__(self, name: str, settings: DSLRSettings, context: Optional[gp.Context] = None):
        self.name = name
        self.settings = settings
        self.context = context or gp.Context()
        self._camera: Optional[gp.Camera] = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self, port: Optional[str] = None) -> None:
        if self._connected:
            return

        port = port if port is not None else self.settings.port
        camera = gp.Camera()

        if port:
            port_info_list = gp.PortInfoList()
            port_info_list.load()
            idx = port_info_list.lookup_path(port)
            camera.set_port_info(port_info_list[idx])
            logger.info("[%s] Connecting via port %s", self.name, port)
        else:
            logger.info("[%s] Connecting via auto-detect", self.name)

        camera.init(self.context)
        self._camera = camera
        self._connected = True
        self._flush_event_queue()
        logger.info("[%s] Connected successfully", self.name)

    def _flush_event_queue(self) -> None:
        if not self._camera:
            return
        try:
            self._camera.wait_for_event(500, self.context)
        except Exception:
            pass

    def apply_settings(
        self,
        iso: Optional[str] = None,
        aperture: Optional[str] = None,
        shutter: Optional[str] = None,
    ) -> None:
        iso = iso if iso is not None else self.settings.iso
        aperture = aperture if aperture is not None else self.settings.aperture
        shutter = shutter if shutter is not None else self.settings.shutter

        self._set_config("iso", iso)
        self._set_config("aperture", aperture)
        self._set_config("shutterspeed", shutter)
        time.sleep(3.0)

    def _set_config(self, key: str, value: str) -> bool:
        if not self._camera:
            raise RuntimeError(f"[{self.name}] Camera not connected")

        try:
            config = self._camera.get_config(self.context)
            setting_widget = config.get_child_by_name(key)
            if setting_widget.get_value() != value:
                setting_widget.set_value(value)
                self._camera.set_config(config, self.context)
            return True
        except Exception:
            logger.warning("[%s] Skipping setting change for '%s'", self.name, key)
            return False

    def capture_to(self, output_dir: Optional[str] = None, prefix: Optional[str] = None) -> Path:
        if not self._camera:
            raise RuntimeError(f"[{self.name}] Camera not connected")

        output_dir = output_dir or self.settings.output_dir
        prefix = prefix or self.name
        local_dir = Path(os.path.expanduser(output_dir))
        local_dir.mkdir(parents=True, exist_ok=True)

        file_path = self._camera.capture(gp.GP_CAPTURE_IMAGE, self.context)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.jpg"
        target = local_dir / filename

        camera_file = self._camera.file_get(
            file_path.folder,
            file_path.name,
            gp.GP_FILE_TYPE_NORMAL,
        )
        camera_file.save(str(target))
        return target

    def disconnect(self) -> None:
        if self._camera and self._connected:
            try:
                self._camera.exit(self.context)
            except Exception as exc:
                logger.warning("[%s] Error during disconnect: %s", self.name, exc)
            finally:
                self._camera = None
                self._connected = False


class DSLRCameraManager:
    """Manages named Canon DSLRs loaded from Laguna YAML configuration."""

    def __init__(
        self,
        cameras: Dict[str, DSLRCamera],
        timelapse_config: Optional[Dict[str, Any]] = None,
        context: Optional[gp.Context] = None,
    ):
        self._cameras = cameras
        self._timelapse_config = timelapse_config or {}
        self._context = context or gp.Context()

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "DSLRCameraManager":
        cameras_config = config.get("cameras", {})
        if not cameras_config:
            raise ValueError("Config must contain a non-empty 'cameras' section")

        context = gp.Context()
        cameras: Dict[str, DSLRCamera] = {}
        for name, cam_config in cameras_config.items():
            settings = DSLRSettings(
                iso=str(cam_config.get("iso", "800")),
                aperture=str(cam_config.get("aperture", "8")),
                shutter=str(cam_config.get("shutter", "1/500")),
                output_dir=cam_config.get("output_dir", "./data"),
                port=cam_config.get("port"),
            )
            cameras[name] = DSLRCamera(name=name, settings=settings, context=context)

        return cls(
            cameras=cameras,
            timelapse_config=config.get("timelapse", {}),
            context=context,
        )

    @property
    def camera_names(self) -> List[str]:
        return list(self._cameras.keys())

    def get(self, name: str) -> DSLRCamera:
        if name not in self._cameras:
            raise KeyError(f"Unknown camera '{name}'. Available: {self.camera_names}")
        return self._cameras[name]

    def connect_all(self) -> Dict[str, bool]:
        results: Dict[str, bool] = {}
        for name, camera in self._cameras.items():
            try:
                camera.connect()
                results[name] = True
            except Exception as exc:
                logger.error("[%s] Connection failed: %s", name, exc)
                results[name] = False
        return results

    def disconnect_all(self) -> None:
        for camera in self._cameras.values():
            camera.disconnect()

    def apply_settings_all(self) -> None:
        for camera in self._cameras.values():
            if camera.is_connected:
                camera.apply_settings()

    def capture(self, name: str) -> Optional[Path]:
        camera = self.get(name)
        if not camera.is_connected:
            camera.connect()
            camera.apply_settings()
        try:
            return camera.capture_to()
        except Exception as exc:
            logger.error("[%s] Capture failed: %s", name, exc)
            return None

    def _capture_worker(self, name: str) -> tuple[str, Optional[Path], Optional[str]]:
        camera = self.get(name)
        try:
            if not camera.is_connected:
                camera.connect()
            path = camera.capture_to()
            return name, path, None
        except Exception as exc:
            return name, None, str(exc)

    def capture_all_parallel(self) -> Dict[str, Optional[Path]]:
        results: Dict[str, Optional[Path]] = {}
        names = self.camera_names

        with ThreadPoolExecutor(max_workers=len(names)) as pool:
            futures = {pool.submit(self._capture_worker, name): name for name in names}
            for future in as_completed(futures):
                name, path, error = future.result()
                if error:
                    logger.error("[%s] Parallel capture failed: %s", name, error)
                results[name] = path

        return results

    def run_timelapse(
        self,
        interval_seconds: Optional[int] = None,
        total_photos: Optional[int] = None,
    ) -> bool:
        interval = interval_seconds or self._timelapse_config.get("interval_seconds", 10)
        total = total_photos or self._timelapse_config.get("total_photos", 3)

        connect_results = self.connect_all()
        if not any(connect_results.values()):
            logger.error("No DSLR cameras connected; aborting timelapse")
            return False

        self.apply_settings_all()

        try:
            for frame in range(1, total + 1):
                start_time = time.time()
                logger.info("[%d/%d] Triggering parallel DSLR capture", frame, total)
                self.capture_all_parallel()

                elapsed = time.time() - start_time
                sleep_needed = max(0, interval - elapsed)
                if frame < total:
                    time.sleep(sleep_needed)

            return True
        finally:
            self.disconnect_all()

    def get_status(self) -> Dict[str, Any]:
        return {
            name: {"connected": camera.is_connected, "output_dir": camera.settings.output_dir}
            for name, camera in self._cameras.items()
        }
