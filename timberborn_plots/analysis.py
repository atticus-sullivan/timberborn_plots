# SPDX-FileCopyrightText: 2026 Lukas Heindl
#
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import Counter

from timberborn_plots.utils import coord2tuple

def obtain_stats(world: dict, recipes: dict, cutting_area: set[tuple[int,int,int]], planting_area: dict[str,set[tuple[int,int,int]]]):
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
