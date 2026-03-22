# SPDX-FileCopyrightText: 2026 Lukas Heindl
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import zipfile
import os
from pathlib import Path
from argparse import ArgumentParser

from timberborn_plots.utils import latest_save, parse_args

DATA_DIR = Path(__file__).parent.parent.parent / "data"

########
# MAIN #
########
def main():
    # init
    args = parse_args()
    path = latest_save(args.savefile_path / args.game_name)
    print(f"Select '{path}' as savefile")

    # read input files
    recipes_path = DATA_DIR / "recipes.json"
    with open(recipes_path) as f:
        recipes = json.load(f)
    ignore_path = DATA_DIR / "ignore.json"
    with open(ignore_path) as f:
        ignore_templates = set(json.load(f))

    with zipfile.ZipFile(path) as z:
        with z.open("world.json") as f:
            world = json.load(f)

    save_templates = {
        e["Template"]
        for e in world["Entities"]
        if "Template" in e
    }

    recipe_templates = set(recipes.keys())

    # --- comparisons ---
    recipes_not_in_save = sorted(recipe_templates - save_templates - ignore_templates)
    save_not_in_recipes = sorted(save_templates - recipe_templates - ignore_templates)

    # --- output ---
    print("=== Recipes referencing templates NOT found in save ===")
    for r in recipes_not_in_save:
        print(r)

    print("\n=== Save entities without recipe definitions ===")
    for s in save_not_in_recipes:
        print(s)

if __name__ == '__main__':
    main()
