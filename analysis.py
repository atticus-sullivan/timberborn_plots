# SPDX-FileCopyrightText: 2026 Lukas Heindl
#
# SPDX-License-Identifier: GPL-3.0-or-later

game_name = "Plankshire"
game_dir = f"/home/lukas/.local/share/Steam/steamapps/compatdata/1062090/pfx/drive_c/users/steamuser/Documents/Timberborn/Saves/{game_name}/"

import json
import zipfile
from collections import Counter
import glob
import os

OUTPUT_PATH = f"./{game_name}.analysis.json"

def coord2tuple(v):
    return (v['X'], v['Y'], v['Z'])

recipes_path = "./recipes.json"
with open(recipes_path) as f:
    recipes = json.load(f)

def latest_save(dir):
    list_of_files = glob.glob(game_dir+"*.timber")
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file
path = latest_save(game_dir)
print(f"Select '{path}' as savefile")

with zipfile.ZipFile(path) as z:
    with z.open("world.json") as f:
        world = json.load(f)

assert world['GameVersion'] == "1.0.12.5-3db367b-sw", f"Unknwon gameversion {world['GameVersion']} seen"

planting_area = {
    t: set(map(coord2tuple, vs))
    for (t,vs) in world['Singletons']['PlantingService']['PlantingMap'].items()
}
cutting_area = set(map(coord2tuple, world['Singletons']['TreeCuttingArea']['CuttingArea']))

# # counter for building types
# template_counts = Counter(
#     e["Template"]
#     for e in world["Entities"]
#     if "Template" in e
# )


# only count active buildings
active_templates = Counter()
active_recipes = Counter()
for e in world["Entities"]:
    template = e.get("Template")
    if not template or template not in recipes:
        continue

    comps = e.get("Components", {})

    finished = comps.get("BlockObjectState", {}).get("Finished", True)
    paused   = comps.get("PausableBuilding", {}).get("Paused", False)

    if not finished or paused:
        continue
    active_templates[template] += 1

    manufactory = comps.get("Manufactory")

    if manufactory:
        recipe_name_init = manufactory.get("CurrentRecipe", "default")
    else:
        recipe_name_init = "default"

    if template in recipes:
        for recipe_name in [recipe_name_init, *map(lambda x: x[0], filter(lambda x: x[1].get("canFallbackTo", False), recipes[template]['recipes'].items()))]:
            recipe = recipes[template]['recipes'][recipe_name]
            coord = coord2tuple(comps.get('BlockObject', {}).get('Coordinates', {"X":0, "Y":0, "Z": 0}))
            skip = False
            if recipe.get('needsCuttingArea', False) and coord not in cutting_area:
                skip = True
            if recipe.get('needsPlantingArea', False) and coord not in planting_area.get(template, {}):
                skip = True
            if (g := recipe.get('needsGrowthProgress', None)) and g and comps.get("Growable", {}).get("GrowthProgress", 0) < g:
                skip = True

            if skip: continue
            break
        else: continue # executed if the for-loop terminates normally (no break)
    else:
        recipe_name = recipe_name_init

    active_recipes[(template, recipe_name)] += 1

# artificially added buildings
active_recipes[("Food", "default")] += 1

# print(active_templates)

# collect huts
huts = []
for template, template_data in recipes.items():
    recipes = template_data['recipes']

    for recipe_name,recipe in recipes.items():
        cnt = active_recipes.get((template, recipe_name), 0)
        if cnt <= 0: continue

        dur = recipe.get("duration", "0s")
        huts.append({
            "template": template,
            "name": template,
            "recipe": recipe_name if recipe_name != "default" else None,
            "cnt": cnt,
            "dur": dur,
            "inputs": recipe.get("inputs", {}),
            "outputs": recipe.get("outputs", {})
        })

# write output
with open(OUTPUT_PATH, "w") as f:
    json.dump(huts, f, indent=2)

print(f"Wrote {OUTPUT_PATH}")
