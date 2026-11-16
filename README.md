# D4 dev starter (proof of concept)

A voxel dragon on a grid, snake rules: Godot and Blender, driven from text, with the same task
habits as D3. The dragon moves and turns; food, growth, and collisions are yours to add,
in `core/session.gd`.

| You want to | Run | What happens |
| --- | --- | --- |
| Get the tools | `deno task setup` | Downloads pinned Godot 4.7.2 and only its web export template into `.tools/` |
| Make the art | `deno task art` | Runs `tools/build_art.py` with Blender as a Python library (`bpy`), writes `art/*.glb` |
| Make the art on an Intel Mac | `deno task art:lts` | Same script, Blender 4.5 LTS |
| Check this computer | `deno task doctor` | Tries every step and prints a report to paste into Canvas |
| See the kit in the game's lighting | `deno task kit` | Every piece in a row, plus a sample dragon bending through turns |
| Play it | `deno task dev` | Runs the game in a native window |
| Open the editor | `deno task edit` | The graphical editor is still there when you want it |
| Check before commit | `deno task ci` | Format check, lint, import, tests, web export into `dist/` |
| See the web build | `deno task preview` | Serves `dist/` locally |

Push to `main` and `.github/workflows/deploy.yml` runs the same `deno task ci`
on GitHub and deploys `dist/` to Pages. The optional review bot
(`.github/workflows/review-bot.yml`, guided by `REVIEWBOT.md`) comments on each push
once you set it up; until then it shows a red X that says nothing about your code.

## Editor

Open this folder in VS Code and accept the recommended extensions
(`.vscode/extensions.json`):

- **godot-tools:** GDScript completion, hover docs, and go-to-definition. It starts a
  windowless Godot from `.tools/godot` (made by `deno task setup`), so no editor needs
  to be open. Format GDScript with `deno task fmt`, not this extension.
- **Python:** completion for `bpy` and `bmesh` in `tools/build_art.py`, from Blender 5.2
  stubs that `deno task setup` installs into `.tools/python-stubs`.
- **GLB Viewer:** click `art/dragon_kit.glb` to orbit the kit. `build_art.py` lays the
  pieces out in rows (dragon pieces, then tile kinds) just for viewers like this; the
  game uses only each piece's mesh, so the layout never affects play.
- **Deno:** for the TypeScript in `scripts/`.

`Cmd/Ctrl+Shift+B` runs `deno task ci`.

## Layout

- `DESIGN.md`: your target, your two menu choices, and the words your project uses. Your
  partner and the optional review bot read it to learn where you are headed.

- `project.godot`, `main.tscn`, `export_presets.cfg`: Godot's own config, plain text, editable by hand.
- `core/session.gd`: one run at the game. It owns the board and the dragon and ticks them; rules that
  involve more than the dragon (food, score, collisions) go here. No Nodes; tested headless.
- `core/dragon.gd`: the dragon's movement on the grid (heading, a turn queue). No Nodes; tested headless.
- `core/kit.gd`: which piece (head, straight, turn, tail) goes in each cell and how far to rotate it.
- `core/board.gd`: the tile vocabulary: which kind of tile is in each cell, and what each kind
  means to the rules (`Board.TILES`).
- `app/main.gd`: the engine adapter. Keeps the clock, ticks the session, draws the dragon with four
  shared meshes, and follows it with the camera.
- `app/stage.gd`: sky, sun, glow, fog, and one instanced mesh per tile kind.
- `tools/build_art.py`: Blender as code. The dragon kit is drawn as ASCII voxel layers; edit, run
  `deno task art`, replay.
- `tests/`: `*_test.gd` files, run by `tests/run_tests.gd` (a tiny runner, no plugin).
- `scripts/godot.ts`: finds Godot, and fails the task when Godot prints script errors.

## Where this can go

The voxel art and plain rules are a starting point. The course staff keep a fully
realized version with every optional requirement implemented, glowing PBR art from
the same `build_art.py` structure, and effects driven by game events:
https://github.com/rndmcnlly/ember-dragon. Read it for ideas; AGENTS.md says more.

## Why `scripts/godot.ts` is strict

Godot exits with code 0 even when a script fails to parse, so a plain
`godot --headless ...` would let a broken commit pass CI. The wrapper watches
Godot's output for script errors and fails instead, and the test runner treats
an unloadable test file or zero tests run as failure.

## Requirements

Deno and uv. The first `deno task art` downloads Blender's `bpy` package
(a few hundred MB; minutes on slow networks), so run it once before you need it.
Set `GODOT=/path/to/godot` to use your own Godot 4.7.2 instead of `.tools/`.

| Platform | Godot tasks | `deno task art` |
| --- | --- | --- |
| Mac (Apple Silicon), Windows (x64 or ARM) | yes | yes |
| Mac (Intel) | yes | use `deno task art:lts` (Blender 5 dropped Intel Macs) |
| Linux x86_64, including x86 Chromebooks | yes | yes, after installing the libraries below |
| Linux ARM, including ARM Chromebooks | yes | no: Blender's Python package has no ARM Linux build |

On Linux (Debian, Ubuntu, Chromebook), install what minimal systems lack:

    sudo apt install libfontconfig1                       # quiets harmless Godot font errors
    sudo apt install libx11-6 libxrender1 libxfixes3 libxi6 libxkbcommon0 libsm6 libgl1   # for art

Run `deno task doctor` to try every step and print a report of what works on your computer.
