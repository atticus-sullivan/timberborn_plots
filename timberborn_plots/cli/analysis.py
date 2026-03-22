# SPDX-FileCopyrightText: 2026 Lukas Heindl
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentParser
from pathlib import Path
import json
import zipfile

from timberborn_plots.utils import latest_save, coord2tuple, parse_args
from timberborn_plots.analysis import obtain_stats, generate_hut_output

DATA_DIR = Path(__file__).parent.parent.parent / "data"

########
# MAIN #
########
def main():
    # init
    args = parse_args()
    output_path = f"./{args.game_name}.analysis.json"
    path = latest_save(args.savefile_path / args.game_name)
    print(f"Select '{path}' as savefile")

    # read input files
    recipes_path = DATA_DIR / "recipes.json"
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

    active_recipes = obtain_stats(world, recipes, cutting_area, planting_area)
    # artificially added buildings
    active_recipes[("Food", "default")] += 1

    huts = generate_hut_output(recipes, active_recipes)

    # write output
    with open(output_path, "w") as f:
        json.dump(huts, f, indent=2)

    print(f"Wrote {output_path}")

if __name__ == '__main__':
    main()
