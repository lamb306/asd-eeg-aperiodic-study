#!/usr/bin/env python
"""删除 data/external_hbn_eeg 下 Mac 残留 ._* 与 .DS_Store。"""

from __future__ import annotations

import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--root",
        type=Path,
        default=PROJECT_ROOT / "data/external_hbn_eeg",
    )
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    root = Path(args.root)
    removed = 0
    for path in root.rglob("*"):
        if path.name == ".DS_Store" or path.name.startswith("._"):
            print(("would remove " if args.dry_run else "removed "), path)
            if not args.dry_run:
                path.unlink(missing_ok=True)
            removed += 1
    print(f"{'would remove' if args.dry_run else 'removed'} {removed} junk files")


if __name__ == "__main__":
    main()
