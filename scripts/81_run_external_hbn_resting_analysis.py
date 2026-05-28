#!/usr/bin/env python
"""HBN 外部验证静息队列：PSD → specparam → 统计（03–09）。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "config/config_external_hbn_resting_60x60.yaml"

STEPS = [
    ("03_compute_psd.py", "PSD"),
    ("04_run_specparam.py", "specparam"),
    ("05_specparam_qc.py", "specparam QC"),
    ("06_compute_roi_metrics.py", "ROI"),
    ("07_demographic_and_qc_stats.py", "demographics"),
    ("08_main_group_analysis.py", "main group"),
    ("09_roi_mixed_model.py", "ROI mixed model"),
    ("10_channel_level_analysis.py", "channel level"),
]


def main() -> int:
    config = DEFAULT_CONFIG
    if len(sys.argv) > 1:
        config = Path(sys.argv[1])

    for script, label in STEPS:
        cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / script), "--config", str(config)]
        print(f"\n=== {label}: {script} ===")
        rc = subprocess.call(cmd, cwd=PROJECT_ROOT)
        if rc != 0:
            print(f"FAILED: {script} (exit {rc})")
            return rc
    print("\n[DONE] external HBN resting analysis pipeline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
