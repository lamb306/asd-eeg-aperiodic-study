#!/usr/bin/env python
"""打包 HBN 外部静息预处理运行包（代码 + participants，不含 EEG 原始数据）。"""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "transfer_packages" / "hbn_external_resting_run"
ZIP_PATH = PROJECT_ROOT / "transfer_packages" / "hbn_external_resting_run.zip"

COPY_FILES = [
    "config/config_external_hbn_resting_60x60.yaml",
    "scripts/78_clean_external_hbn_mac_junk.py",
    "scripts/79_build_external_hbn_participants.py",
    "scripts/80_preprocess_external_hbn_resting.py",
    "src/__init__.py",
    "src/config.py",
    "src/io_utils.py",
    "src/eeg_preprocessing.py",
    "src/external_hbn.py",
    "data/participants/participants_external_hbn_60x60.csv",
    "data/participants/participants_external_hbn_60x60_resting.csv",
    "data/participants/external_hbn_60x60_availability_summary.csv",
    "data/participants/external_validation_subjects_hbn_eeg_balanced_60x60.csv",
    "data/participants/external_hbn_eeg_download_audit_60x60.csv",
]


def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    for rel in COPY_FILES:
        src = PROJECT_ROOT / rel
        dst = OUT_DIR / rel
        if not src.exists():
            raise FileNotFoundError(src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    # 运行说明与依赖
    shutil.copy2(
        PROJECT_ROOT / "transfer_packages" / "hbn_external_resting_run_README_template.md",
        OUT_DIR / "README_运行说明.md",
    )
    shutil.copy2(
        PROJECT_ROOT / "transfer_packages" / "requirements_hbn_resting_preprocess.txt",
        OUT_DIR / "requirements-resting.txt",
    )
    shutil.copy2(
        PROJECT_ROOT / "transfer_packages" / "run_resting_preprocess.ps1",
        OUT_DIR / "run_resting_preprocess.ps1",
    )
    shutil.copy2(
        PROJECT_ROOT / "transfer_packages" / "run_resting_preprocess.bat",
        OUT_DIR / "run_resting_preprocess.bat",
    )

    # EEG 数据清单（路径列表，便于核对是否拷全）
    manifest_lines = [
        "# 需另行拷贝的 EEG 目录（约 17 GB，223 个 .set）",
        "data/external_hbn_eeg/",
        "",
        "# 目录结构示例",
        "data/external_hbn_eeg/R1/sub-NDARxxxx/eeg/sub-NDARxxxx_task-RestingState_eeg.set",
        "",
    ]
    eeg_root = PROJECT_ROOT / "data" / "external_hbn_eeg"
    if eeg_root.is_dir():
        sets = sorted(
            p for p in eeg_root.rglob("*RestingState_eeg.set")
            if not p.name.startswith("._")
        )
        manifest_lines.append(f"# 本机 RestingState .set 数量: {len(sets)}")
        manifest_lines.append("")
        for p in sets:
            try:
                manifest_lines.append(str(p.relative_to(PROJECT_ROOT)).replace("\\", "/"))
            except ValueError:
                manifest_lines.append(str(p))
    (OUT_DIR / "MANIFEST_eeg_paths_to_copy.txt").write_text(
        "\n".join(manifest_lines), encoding="utf-8"
    )

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(OUT_DIR.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(OUT_DIR.parent))

    print(f"Package folder: {OUT_DIR}")
    print(f"Zip archive:    {ZIP_PATH}")
    print(f"Zip size MB:    {ZIP_PATH.stat().st_size / 1e6:.1f}")


if __name__ == "__main__":
    main()
