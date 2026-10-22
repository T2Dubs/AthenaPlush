"""Create floor/wall objects and fill each house room with a floor and two back walls.

Run after tools/import_sprites.py and tools/make_floor_sprites.py, with the IDE closed:
    python tools/add_floors_and_walls.py

Floor: N x N iso diamond centred on (CX, CY). Walls run along the up-left ("w") and
up-right ("n") edges. Re-running skips rooms that already have a "Floor" layer.
"""
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
N, CX, CY = 10, 683, 384
TILE_W, TILE_H = 64, 32

FLOOR_SPRITES = {
    "wood": "spr_int_floors_wood",
    "darkwood": "spr_int_floors_darkwood",
    "carpet": "spr_int_floors_carpet",
    "tile": "spr_int_floors_tile",
}
WALL_SPRITES = {
    "blue": "spr_int_tiles_wall_2_dark_blue",
    "red": "spr_int_tiles_wall_2_dark_red",
    "pink": "spr_int_tiles_wall_2_pink",
    "yellow": "spr_int_tiles_wall_2_pink_light_yellow",
}
THEMES = {  # room -> (floor, wall)
    "rm_house_kitchen": ("tile", "yellow"),
    "rm_house_bedroom": ("wood", "pink"),
    "rm_house_livingRoom": ("darkwood", "blue"),
    "rm_house_diningRoom": ("darkwood", "red"),
    "rm_house_office": ("carpet", "blue"),
    "rm_house_bathroom": ("tile", "pink"),
}

OBJECT_YY = """{{
  "$GMObject":"",
  "%Name":"{name}",
  "eventList":[],
  "managed":true,
  "name":"{name}",
  "overriddenProperties":[],
  "parent":{{
    "name":"Objects",
    "path":"folders/Objects.yy",
  }},
  "parentObjectId":{parent},
  "persistent":false,
  "physicsAngularDamping":0.1,
  "physicsDensity":0.5,
  "physicsFriction":0.2,
  "physicsGroup":1,
  "physicsKinematic":false,
  "physicsLinearDamping":0.1,
  "physicsObject":false,
  "physicsRestitution":0.1,
  "physicsSensor":false,
  "physicsShape":1,
  "physicsShapePoints":[],
  "physicsStartAwake":true,
  "properties":[],
  "resourceType":"GMObject",
  "resourceVersion":"2.0",
  "solid":false,
  "spriteId":{sprite},
  "spriteMaskId":null,
  "visible":true,
}}"""


LAYER_TEMPLATE = (
    '    {"$GMRInstanceLayer":"","%Name":"Instances","depth":0,"effectEnabled":true,"effectType":null,'
    '"gridX":32,"gridY":32,"hierarchyFrozen":false,"inheritLayerDepth":false,'
    '"inheritLayerSettings":false,"inheritSubLayers":true,"inheritVisibility":true,'
    '"instances":[],"layers":[],"name":"Instances","properties":[],'
    '"resourceType":"GMRInstanceLayer","resourceVersion":"2.0","userdefinedDepth":false,'
    '"visible":true,},\n')


def ref(kind, name):
    return f'{{"name":"{name}","path":"{kind}/{name}/{name}.yy",}}'


def write_object(name, sprite=None, parent=None):
    d = ROOT / "objects" / name
    d.mkdir(exist_ok=True)
    text = OBJECT_YY.format(
        name=name,
        parent=ref("objects", parent) if parent else "null",
        sprite=ref("sprites", sprite) if sprite else "null")
    (d / f"{name}.yy").write_text(text, encoding="utf-8", newline="\n")


def instance(name, obj, x, y, scale_x=1.0):
    return (f'{{"$GMRInstance":"v4","%Name":"{name}","colour":4294967295,"frozen":false,'
            f'"hasCreationCode":false,"ignore":false,"imageIndex":0,"imageSpeed":1.0,'
            f'"inheritCode":false,"inheritedItemId":null,"inheritItemSettings":false,'
            f'"isDnd":false,"name":"{name}","objectId":{ref("objects", obj)},"properties":[],'
            f'"resourceType":"GMRInstance","resourceVersion":"2.0","rotation":0.0,'
            f'"scaleX":{scale_x},"scaleY":1.0,"x":{x}.0,"y":{y}.0,}},')


def layout(floor_obj, wall_obj):
    """Return [(object, x, y, scale_x)] for the floor, then the walls."""
    floors, walls = [], []
    top = CY - N * TILE_H // 2
    for i in range(N):
        for j in range(N):
            floors.append((floor_obj, CX + (i - j) * TILE_W // 2,
                           top + (i + j + 1) * TILE_H // 2, 1.0))
    seg_w, seg_h = TILE_W // 2, TILE_H // 2
    for k in range(N):
        # w wall: up-left edge rises left to right; sprite sits on its low (left) end
        walls.append((wall_obj, CX - N * seg_w + seg_w // 2 + k * seg_w,
                      CY - seg_h // 2 - k * seg_h + seg_h // 2, 1.0))
        # n wall: up-right edge falls left to right; mirrored sprite
        walls.append((wall_obj, CX + seg_w // 2 + k * seg_w,
                      top + seg_h // 2 + k * seg_h + seg_h // 2, -1.0))
    return floors, walls


def layer_json(name, depth, instances):
    layer = LAYER_TEMPLATE
    layer = layer.replace('"%Name":"Instances"', f'"%Name":"{name}"', 1)
    layer = layer.replace('"name":"Instances"', f'"name":"{name}"', 1)
    layer = layer.replace('"depth":0', f'"depth":{depth}', 1)
    layer = layer.replace('"userdefinedDepth":false', '"userdefinedDepth":true', 1)
    body = "\n".join("        " + i for i in instances)
    return layer.replace('"instances":[]', f'"instances":[\n{body}\n      ]', 1)


def main():
    write_object("obj_floor")
    write_object("obj_wall")
    for key, sprite in FLOOR_SPRITES.items():
        write_object(f"obj_floor_{key}", sprite, "obj_floor")
    for key, sprite in WALL_SPRITES.items():
        write_object(f"obj_wall_{key}", sprite, "obj_wall")

    yyp_path = ROOT / "AthenaPlush.yyp"
    yyp = yyp_path.read_text(encoding="utf-8")
    names = (["obj_floor", "obj_wall"] + [f"obj_floor_{k}" for k in FLOOR_SPRITES]
             + [f"obj_wall_{k}" for k in WALL_SPRITES])
    anchor = '    {"id":{"name":"obj_player"'
    for n in names:
        entry = f'    {{"id":{{"name":"{n}","path":"objects/{n}/{n}.yy",}},}},\n'
        if entry not in yyp:
            yyp = yyp.replace(anchor, entry + anchor, 1)
    yyp_path.write_text(yyp, encoding="utf-8", newline="\n")

    for room, (floor, wall) in THEMES.items():
        path = ROOT / "rooms" / room / f"{room}.yy"
        text = path.read_text(encoding="utf-8")
        if '"name":"Floor"' in text:
            print("skip", room)
            continue
        floors, walls = layout(f"obj_floor_{floor}", f"obj_wall_{wall}")
        used, lines_by_layer, order = set(), {}, []
        for layer_name, items in (("Walls", walls), ("Floor", floors)):
            lines = []
            for obj, x, y, sx in items:
                while (nm := "inst_" + uuid.uuid4().hex[:8].upper()) in used:
                    pass
                used.add(nm)
                lines.append(instance(nm, obj, x, y, sx))
                order.append(f'{{"name":"{nm}","path":"rooms/{room}/{room}.yy",}},')
            lines_by_layer[layer_name] = lines

        end_marker = '"resourceType":"GMRInstanceLayer","resourceVersion":"2.0","userdefinedDepth":false,"visible":true,},\n'
        insert_at = text.index(end_marker) + len(end_marker)
        new_layers = (layer_json("Walls", 50, lines_by_layer["Walls"])
                      + layer_json("Floor", 60, lines_by_layer["Floor"]))
        text = text[:insert_at] + new_layers + text[insert_at:]
        text = text.replace('"instanceCreationOrder":[\n',
                            '"instanceCreationOrder":[\n    ' + "\n    ".join(order) + "\n", 1)
        path.write_text(text, encoding="utf-8", newline="\n")
        print("filled", room)


if __name__ == "__main__":
    main()
