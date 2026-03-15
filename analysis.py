game_name = "Plankshire"
path = f"/home/lukas/.local/share/Steam/steamapps/compatdata/1062090/pfx/drive_c/users/steamuser/Documents/Timberborn/Saves/{game_name}/{game_name}.timber"

import json
import zipfile
from collections import Counter

OUTPUT_PATH = f"./{game_name}.analysis.json"

recipes_path = "./recipes.json"
with open(recipes_path) as f:
    recipes = json.load(f)

with zipfile.ZipFile(path) as z:
    with z.open("world.json") as f:
        world = json.load(f)

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

    finished = comps.get("BlockObjectState", {}).get("Finished", False)
    paused   = comps.get("PausableBuilding", {}).get("Paused", False)

    if not finished or paused:
        continue
    active_templates[template] += 1

    manufactory = comps.get("Manufactory")

    if manufactory:
        recipe_name = manufactory.get("CurrentRecipe", "default")
        print(recipe_name)
    else:
        recipe_name = None

    active_recipes[(template, recipe_name)] += 1

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
