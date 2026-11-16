# /// script
# requires-python = "==3.13.*"
# dependencies = ["bpy==5.2.*"]
# ///
"""Blender as a library: build the kit, art/dragon_kit.glb.

deno task art      uses Blender 5.2 (the header above)
deno task art:lts  uses Blender 4.5 LTS, for Intel Macs, which Blender 5 dropped

Every piece fills one 1x1 grid cell and is made by a builder function listed in
PIECES (the dragon) or TILES (the ground). The starter's builders all use voxels(),
but a builder can make any geometry: swap one out and the game picks it up by name.

Conventions the game relies on (Blender coordinates, Z up):
  - A cell spans x and y from -0.5 to 0.5. +Y is the direction of travel.
  - Openings must match Kit.OPENINGS in core/kit.gd: the head and tail join the
    body at the back and front, the turn joins the back and the right side.
  - Floors lie with their top at z = 0; everything else stands on z = 0.
"""

import bpy  # first: importing bpy is what makes bmesh and mathutils available
import bmesh
from mathutils import Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)  # start from an empty scene

VOXELS = 4  # voxels per cell edge

MATERIALS = []  # every material, in order; a face's material_index points into this list


def pbr_material(name, color, metallic=0.0, roughness=0.5, emission=None, strength=1.0):
    """A Principled BSDF using only inputs glTF keeps. Returns its index in MATERIALS.
    Emission above about 1 blooms in the game, because the stage has glow switched on."""
    material = bpy.data.materials.new(name)
    if not material.use_nodes:  # Blender 4.x starts without nodes; 5.x always has them
        material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = srgb(color)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:  # glTF keeps a color up to 1 plus a strength (KHR_materials_emissive_strength)
        bsdf.inputs["Emission Color"].default_value = srgb(emission)
        bsdf.inputs["Emission Strength"].default_value = strength
    material.diffuse_color = srgb(color)  # the viewport's solid color, for the GUI
    MATERIALS.append(material)
    return len(MATERIALS) - 1


def srgb(hex_code):
    """A hex color as Blender wants it: linear RGBA."""
    channels = [int(hex_code.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels) + (1.0,)


SCALES = pbr_material("Scales", "#2f9e5b", metallic=0.2, roughness=0.45)
GOLD = pbr_material("Gold", "#f2bf3a", metallic=1.0, roughness=0.3)
EYE = pbr_material("Eye", "#ffb22e", emission="#ffa21a", strength=4.0)
EMBER = pbr_material("Ember", "#ff6a1a", emission="#ff4a08", strength=3.0)
STONE = pbr_material("Stone", "#9e9883", roughness=0.85)
MOSS = pbr_material("Moss", "#6f8558", roughness=0.9)
BRICK = pbr_material("Brick", "#6b4d3d", roughness=0.9)

PALETTE = {"#": SCALES, "*": GOLD, "e": EYE, "o": EMBER, "s": STONE, "t": MOSS, "w": BRICK}


def voxels(bm, layers, below_ground=0):
    """Add one cube per palette character. Each layer is a top-down view of the cell,
    from the ground up: the top row is the front (+Y), the bottom row is the back."""
    for z, layer in enumerate(layers):
        for row, line in enumerate(layer.split()):
            for column, char in enumerate(line):
                if char not in PALETTE:
                    continue
                center = (
                    (column + 0.5) / VOXELS - 0.5,
                    0.5 - (row + 0.5) / VOXELS,
                    (z - below_ground + 0.5) / VOXELS,
                )
                cube = bmesh.ops.create_cube(bm, size=1 / VOXELS, matrix=Matrix.Translation(center))
                for face in {f for v in cube["verts"] for f in v.link_faces}:
                    face.material_index = PALETTE[char]


def build_head(bm):
    voxels(bm, ["""
        .##.
        ####
        ####
        .##.
        """, """
        ....
        e##e
        .##.
        .##.
        """, """
        ....
        ....
        *..*
        ....
        """])


def build_straight(bm):
    voxels(bm, ["""
        .##.
        .##.
        .##.
        .##.
        """, """
        ....
        .*..
        ....
        .*..
        """])


def build_turn(bm):
    voxels(bm, ["""
        ....
        .###
        .###
        .##.
        """])


def build_tail(bm):
    voxels(bm, ["""
        .##.
        .##.
        ..#.
        ..o.
        """])


def build_floor(bm):
    voxels(bm, ["""
        ssst
        stss
        ssss
        tsss
        """], below_ground=1)


def build_wall(bm):
    voxels(bm, ["""
        wwww
        wwww
        wwww
        wwww
        """] * 3)


def make_object(name, build, location=(0, 0, 0)):
    """Run a builder on a fresh bmesh and turn the result into a mesh object called name.
    The game uses only the mesh; location just spreads the kit out for model viewers."""
    bm = bmesh.new()
    build(bm)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    # Keep only the materials this object uses, renumbering faces to match.
    used = sorted({p.material_index for p in mesh.polygons})
    mesh.polygons.foreach_set("material_index", [used.index(p.material_index) for p in mesh.polygons])
    for index in used:
        mesh.materials.append(MATERIALS[index])
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    bpy.context.scene.collection.objects.link(obj)


PIECES = {  # the dragon kit; the game finds each mesh by these names
    "head": build_head,
    "straight": build_straight,
    "turn": build_turn,
    "tail": build_tail,
}
TILES = {  # one entry per kind in core/board.gd's TILES; a new kind is one builder and one line
    "floor": build_floor,
    "wall": build_wall,
}

# One row per registry, so a GLB viewer shows a tidy catalog instead of every piece
# stacked on the origin. Each mesh is still modeled around its own cell's center.
SPACING = 1.5
for row, registry in enumerate([PIECES, TILES]):
    for column, (name, build) in enumerate(registry.items()):
        make_object(name, build, location=(column * SPACING, -row * SPACING, 0))

bpy.ops.export_scene.gltf(
    filepath="art/dragon_kit.glb", export_apply=True, export_cameras=False, export_lights=False
)
print(f"Built art/dragon_kit.glb with Blender {bpy.app.version_string}")
