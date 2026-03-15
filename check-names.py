path = "/home/lukas/.local/share/Steam/steamapps/compatdata/1062090/pfx/drive_c/users/steamuser/Documents/Timberborn/Saves/Biberhausen/Biberhausen.timber"

import json
import zipfile

recipes_path = "./recipies.json"
with open(recipes_path) as f:
    recipes = json.load(f)

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
recipes_not_in_save = sorted(recipe_templates - save_templates)
save_not_in_recipes = sorted(save_templates - recipe_templates)

# --- output ---
print("=== Recipes referencing templates NOT found in save ===")
for r in recipes_not_in_save:
    print(r)

print("\n=== Save entities without recipe definitions ===")
for s in save_not_in_recipes:
    print(s)
