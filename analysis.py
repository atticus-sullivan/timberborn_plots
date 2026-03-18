# SPDX-FileCopyrightText: 2026 Lukas Heindl
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from argparse import ArgumentParser
import json
import zipfile
from collections import Counter
import glob
from pathlib import Path

#######
# CLI #
#######

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("savefile_path", type=Path)
    parser.add_argument("game_name")
    return parser.parse_args()

#########
# UTILS #
#########

def coord2tuple(v):
    return (v['X'], v['Y'], v['Z'])

def latest_save(dir: Path):
    list_of_files = dir.glob("*.timber")
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

#########
# LOGIC #
#########

def obtain_stats(world):
    # count active buildings
    # active_templates = Counter()

    # count the active recipes
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
        # active_templates[template] += 1

        manufactory = comps.get("Manufactory")

        if manufactory:
            recipe_name_init = manufactory.get("CurrentRecipe", "default")
        else:
            recipe_name_init = "default"

        if template in recipes:
            # logic to obtain the correct recipe, especially if the entity does not specify the recipe explicitly
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
                # use the first recipe which is not skipped
                break
            else: continue # executed if the for-loop terminates normally (no break)
        else:
            # use the initial recipe to avoid crashes
            recipe_name = recipe_name_init

        active_recipes[(template, recipe_name)] += 1
    return active_recipes

def generate_hut_output(recipes, active_recipes):
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
    return huts

########
# MAIN #
########
if __name__ == '__main__':
    # init
    args = parse_args()
    output_path = f"./{args.game_name}.analysis.json"
    path = latest_save(args.savefile_path / args.game_name)
    print(f"Select '{path}' as savefile")

    # read input files
    recipes_path = "./recipes.json"
    with open(recipes_path) as f:
        recipes = json.load(f)

    with zipfile.ZipFile(path) as z:
        with z.open("world.json") as f:
            world = json.load(f)

    # ensure the recipes match the version of the game
    # TODO: make this work with more recent versions / matrix with version -> recipe
    assert world['GameVersion'] == "1.0.12.5-3db367b-sw", f"Unknwon gameversion {world['GameVersion']} seen"

    # obtain the coordinates of the planting-/cutting-area
    planting_area = {
        t: set(map(coord2tuple, vs))
        for (t,vs) in world['Singletons']['PlantingService']['PlantingMap'].items()
    }
    cutting_area = set(map(coord2tuple, world['Singletons']['TreeCuttingArea']['CuttingArea']))

    active_recipes = obtain_stats(world)
    # artificially added buildings
    active_recipes[("Food", "default")] += 1

    huts = generate_hut_output(recipes, active_recipes)

    # write output
    with open(output_path, "w") as f:
        json.dump(huts, f, indent=2)

    print(f"Wrote {output_path}")
