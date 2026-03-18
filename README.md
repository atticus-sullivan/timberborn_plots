<!--
SPDX-FileCopyrightText: 2026 Lukas Heindl

SPDX-License-Identifier: GPL-3.0-or-later
-->

# timberborn_plots

> [!NOTE]
> The output of this can nicely be used in conjunction with [timberborn_drawing](https://github.com/atticus-sullivan/timberborn_drawing) (a (Lua)LaTeX package)

## Installation
### Option1: via pipx (recommended)
```bash
pipx install git+https://github.com/atticus-sullivan/timberborn-plots.git
```
This installs the tool in an isolated environment (venv specific for this
cli-tool) and makes the commands globally available.

### Option2: via pip
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/atticus-sullivan/timberborn-plots.git
```

## Usage
This installs two commands:

### check-names
```bash
$ timberbornplots-check-names -h
usage: timberbornplots-check-names [-h] savefile_path game_name

positional arguments:
  savefile_path
  game_name

options:
  -h, --help     show this help message and exit
```

### analysis
```bash
$ timberbornplots-analysis -h
usage: timberbornplots-analysis [-h] savefile_path game_name

positional arguments:
  savefile_path
  game_name

options:
  -h, --help     show this help message and e
```

## Output
The output of the analysis is a json file like the following

```json
[
  {
    "template": "LumberMill.Folktails",
    "name": "LumberMill.Folktails",
    "recipe": null,
    "cnt": 5,
    "dur": "1.3h",
    "inputs": {
      "Wood": 1,
      "Power": 50
    },
    "outputs": {
      "Planks": 1
    }
  }
]
```

This is the aggregated, filtered ans enriched data from the savefile.
Also it is more standardized so it is easier to parse.

## Data
There are two or three sources for data:

### Savefile
The savefile is generally specified by
1. the general directory where timberborn places the savefiles, and
2. the name of the game/map specified when creating the new game

The path is then constructed `dir/name/` in this directory the scripts use the
most recent `.timber` file as savefile.

### Recipes
This specifies how a "hut" transforms how many resources into how many other
ones and how long this takes.

```json
{
    "template name as in savefile.entities[].template": {
        "recipes": {
            "default": {
                "duration": "1h",
                "inputs": {"resourceA": 1}
                "outputs": {"resourceB": 1}
            },
            "other recipes": {...}
        }
    }
}
```

If the entity does not specify a recipe, `default` is chosen.

A recipes can also optionally have these keys:
- `needsCuttingArea: boolean`: this recipe is only eligible if the entity is in the area defined for cutting trees.
- `needsPlantingArea: boolean`: this recipe is only eligible if this entity is also defined to be planted at this area.
- `canFallbackTo: bool`: if a previous recipe failed, this one can be used as fallback

The idea here is the following:
- resources like tree -> wood is only counted if it is planted and cut here
- resources like tree -> other (e.g. resin, syrup, etc) is only counted if it is planted here
- trees do not define a recipe, what resource is generated only depends on whether the tree is cut, gathered or tappered. This is the usecase of `canFallbackTo`.

### Ignore
This is only used in `check-names` to silence the output of template/entity
names which should not be reported as missing.

Format:
```json
[
    "template-name"
]
```

## Development
### Setup
1. Clone the repository
2. Create a virtual environment and install the project in editable mode (this
   way the executables are available but still linked to your development
   source so changes are directly applied):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .
    ```
3. Optionally you can install directly via `pipx` as well (also with `-e` in
   edit mode)

The following commands are available:
```bash
timberbornplots-analysis    # main command
timberbornplots-check-names # check if there are unknown names where the lookup failed
```

### Project structure
```bash
timberborn_plots/
  cli/        # CLI entrypoints (argument parsing, user interaction)
  analysis.py # core logic
  utils.py    # shared helpers
data/         # static input files (recipes, ignore lists)
```
