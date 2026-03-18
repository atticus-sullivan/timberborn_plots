# SPDX-FileCopyrightText: 2026 Lukas Heindl
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from argparse import ArgumentParser
import os

def latest_save(dir: Path) -> Path:
    files = list(dir.glob("*.timber"))
    if not files:
        raise FileNotFoundError(f"No .timber files in {dir}")
    return max(files, key=os.path.getctime)

def coord2tuple(v: dict) -> tuple[int, int, int]:
    return (v["X"], v["Y"], v["Z"])

#######
# CLI #
#######

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("savefile_path", type=Path)
    parser.add_argument("game_name")
    return parser.parse_args()
