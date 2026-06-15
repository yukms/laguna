#!/usr/bin/env python3
"""Example: dual Canon DSLR timelapse via Laguna YAML configuration."""

import logging
import sys
from pathlib import Path

from laguna import FlumeLab

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "cameras.yaml"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    lab = FlumeLab(config_file=str(CONFIG_PATH))

    if lab.dslr_cameras is None:
        print("No 'cameras' section found in config.")
        return 1

    print("Configured cameras:", lab.dslr_cameras.camera_names)

    # Named callable API
    lab.dslr_cameras.connect_all()
    lab.dslr_cameras.apply_settings_all()

    print("Capturing Hangang...")
    lab.dslr_cameras.capture("Hangang")

    print("Capturing both cameras in parallel...")
    lab.dslr_cameras.capture_all_parallel()

    print("Running timelapse...")
    success = lab.dslr_cameras.run_timelapse()

    lab.dslr_cameras.disconnect_all()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
