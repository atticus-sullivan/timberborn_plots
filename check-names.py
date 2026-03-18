# SPDX-FileCopyrightText: 2026 Lukas Heindl
#
# SPDX-License-Identifier: GPL-3.0-or-later

game_name = "Plankshire"
game_dir = f"/home/lukas/.local/share/Steam/steamapps/compatdata/1062090/pfx/drive_c/users/steamuser/Documents/Timberborn/Saves/{game_name}/"

import json
import zipfile
import glob
import os

recipes_path = "./recipes.json"
with open(recipes_path) as f:
    recipes = json.load(f)

ignore_path = "./ignore.json"
with open(ignore_path) as f:
    ignore_templates = set(json.load(f))

def latest_save(dir):
    list_of_files = glob.glob(game_dir+"*.timber")
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file
path = latest_save(game_dir)

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
