"""Create furniture objects and three child kitchen rooms under Rooms/Filled Rooms/House.

Children are clones of rm_house_kitchen with inheritance links back to it, plus a
"Furniture" layer of their own. rm_house_kitchen itself is left untouched.
Run with the IDE closed:  python tools/add_kitchen_variants.py
Re-running skips rooms that already exist.
"""
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARENT = "rm_house_kitchen"
CX, TOP = 683, 224  # floor centre x and top-corner y; grid cell (i, j) is a 64x32 diamond
FOLDER = "House"
FOLDER_PATH = "folders/Rooms/Filled Rooms/House.yy"

PARENT_REF = f'{{"name":"{PARENT}","path":"rooms/{PARENT}/{PARENT}.yy",}}'

# i runs down-right (along the n wall), j runs down-left (along the w wall).
# Unflipped sprites face down-right (+i), mirrored ones face down-left (+j), so counters
# on the w wall (i=0) are unflipped and counters on the n wall (j=0) are mirrored.
# Chairs: front faces +i, front+flip faces +j, back faces -i, back+flip faces -j.
# Each entry: (sprite, i, j, di, dj, flip, dy) with (i, j) the footprint's top corner.


def wall_w(sprite, j, length=1):
    return (sprite, 0, j, 1, length, False, 0)


def wall_n(sprite, i, length=1):
    return (sprite, i, 0, length, 1, True, 0)


def chair(color, i, j, kind):
    spr, flip = {"+i": (f"chair_{color}_front", False), "+j": (f"chair_{color}_front", True),
                 "-i": (f"chair_{color}_back", False), "-j": (f"chair_{color}_back", True)}[kind]
    return (spr, i + 0.25, j + 0.25, 0.5, 0.5, flip, 0)


def table_set(color, i, j):
    return [("table_2", i, j, 1, 1, False, 0),
            chair(color, i - 1, j, "+i"), chair(color, i, j - 1, "+j"),
            chair(color, i + 1, j, "-i"), chair(color, i, j + 1, "-j")]


def rug(sprite, ci, cj, size):
    return (sprite, ci - size / 2, cj - size / 2, size, size, False, 0)


def on_counter(sprite, i, j):
    return (sprite, i, j, 1, 1, True, -24)


LAYOUTS = {
    "rm_house_kitchen_a": [  # galley along both walls, dining nook at the front
        wall_w("kitchen_6", 0, 3), wall_w("kitchen_2", 3),
        wall_w("fridge_1", 6), wall_w("oven_1", 7), wall_w("kitchen_3", 8), wall_w("kitchen_4", 9),
        wall_n("kitchen_5", 1, 2), on_counter("microwave_1", 1, 0), wall_n("kitchen_1", 3),
        wall_n("kitchen_6", 6, 3), wall_n("kitchen_4", 9),
        rug("rug_square_red", 7.5, 7.5, 1.6), *table_set("red", 7, 7),
    ],
    "rm_house_kitchen_b": [  # appliances on the n wall, counter island at the front
        wall_n("fridge_1", 1), wall_n("oven_1", 2), wall_n("kitchen_2", 3),
        wall_n("kitchen_6", 6, 3), wall_n("kitchen_4", 9),
        wall_w("kitchen_5", 1, 2), wall_w("kitchen_3", 3),
        wall_w("kitchen_1", 6), wall_w("kitchen_4", 7), ("box_1", 0.25, 9.25, 0.5, 0.5, False, 0),
        rug("rug_circle_green", 7.5, 8.0, 1.4), ("kitchen_5", 7, 7, 1, 2, False, 0),
        chair("green", 6, 7, "+i"), chair("green", 6, 8, "+i"),
        chair("green", 8, 7, "-i"), chair("green", 8, 8, "-i"),
    ],
    "rm_house_kitchen_c": [  # appliances on the w wall, breakfast nook beside the counters
        wall_w("fridge_1", 0), wall_w("oven_1", 1), wall_w("kitchen_5", 2, 2),
        wall_w("kitchen_3", 6), wall_w("kitchen_4", 7), wall_w("kitchen_2", 8), wall_w("kitchen_1", 9),
        wall_n("kitchen_5", 1, 2), on_counter("microwave_1", 2, 0), wall_n("kitchen_4", 3),
        wall_n("kitchen_6", 6, 3), wall_n("kitchen_1", 9),
        rug("rug_square_yellow", 2.5, 7.5, 1.6), *table_set("blue", 2, 7),
        ("box_1", 8.25, 8.25, 0.5, 0.5, False, 0), ("box_1", 9.25, 9.25, 0.5, 0.5, False, 0),
    ],
}

OBJECT_YY = """{{
  "$GMObject":"",
  "%Name":"{name}",
  "eventList":[{events}],
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
CREATE_EVENT = ('{"$GMEvent":"v1","%Name":"","collisionObjectId":null,"eventNum":0,"eventType":0,'
                '"isDnD":false,"name":"","resourceType":"GMEvent","resourceVersion":"2.0",},')


def ref(kind, name):
    return f'{{"name":"{name}","path":"{kind}/{name}/{name}.yy",}}'


def write_object(name, sprite=None, parent=None, create_code=None):
    d = ROOT / "objects" / name
    d.mkdir(exist_ok=True)
    text = OBJECT_YY.format(
        name=name, events=CREATE_EVENT if create_code else "",
        parent=ref("objects", parent) if parent else "null",
        sprite=ref("sprites", sprite) if sprite else "null")
    (d / f"{name}.yy").write_text(text, encoding="utf-8", newline="\n")
    if create_code:
        (d / "Create_0.gml").write_text(create_code, encoding="utf-8", newline="\n")


def object_for(sprite):
    name = "obj_" + sprite
    if re.fullmatch(r"kitchen_\d", sprite):
        name = "obj_kitchen_counter_" + sprite[-1]
    return name


def place(entry):
    sprite, i, j, di, dj, flip, dy = entry
    ci, cj = i + di / 2, j + dj / 2
    x = round(CX + (ci - cj) * 32)
    y = round(TOP + (ci + cj) * 16 + (di + dj) * 8) + dy
    return object_for(sprite), x, y, -1.0 if flip else 1.0


def instance(name, obj, x, y, scale_x):
    return (f'{{"$GMRInstance":"v4","%Name":"{name}","colour":4294967295,"frozen":false,'
            f'"hasCreationCode":false,"ignore":false,"imageIndex":0,"imageSpeed":1.0,'
            f'"inheritCode":false,"inheritedItemId":null,"inheritItemSettings":false,'
            f'"isDnd":false,"name":"{name}","objectId":{ref("objects", obj)},"properties":[],'
            f'"resourceType":"GMRInstance","resourceVersion":"2.0","rotation":0.0,'
            f'"scaleX":{scale_x},"scaleY":1.0,"x":{x}.0,"y":{y}.0,}},')


FURNITURE_LAYER = (
    '    {"$GMRInstanceLayer":"","%Name":"Furniture","depth":0,"effectEnabled":true,"effectType":null,'
    '"gridX":32,"gridY":32,"hierarchyFrozen":false,"inheritLayerDepth":false,'
    '"inheritLayerSettings":false,"inheritSubLayers":true,"inheritVisibility":true,'
    '"instances":[\n{instances}\n      ],"layers":[],"name":"Furniture","properties":[],'
    '"resourceType":"GMRInstanceLayer","resourceVersion":"2.0","userdefinedDepth":true,'
    '"visible":true,},\n')
INSTANCE_RE = re.compile(r'\{"\$GMRInstance":"v4".*?"y":[-\d.]+,\}', re.S)


def new_name(used):
    while (nm := "inst_" + uuid.uuid4().hex[:8].upper()) in used:
        pass
    used.add(nm)
    return nm


def build_room(room, entries, parent_text):
    text = parent_text.replace(PARENT, room)
    used = set(re.findall(r'"%Name":"(inst_\w+)"', parent_text))
    order = []

    def inherit(match):
        s = match.group(0)
        parent_name = re.search(r'"%Name":"(inst_\w+)"', s).group(1)
        nm = new_name(used)
        s = s.replace(parent_name, nm)
        s = s.replace('"inheritItemSettings":false', '"inheritItemSettings":true')
        s = s.replace('"inheritedItemId":null',
                      f'"inheritedItemId":{{"name":"{parent_name}","path":"rooms/{PARENT}/{PARENT}.yy",}}')
        order.append(nm)
        return s

    text = INSTANCE_RE.sub(inherit, text)
    for flag in ("inheritLayerDepth", "inheritLayerSettings", "inheritSubLayers", "inheritVisibility"):
        text = text.replace(f'"{flag}":false', f'"{flag}":true')

    lines = []
    for entry in entries:
        obj, x, y, sx = place(entry)
        nm = new_name(used)
        order.append(nm)
        lines.append("        " + instance(nm, obj, x, y, sx))
    marker = '"resourceType":"GMRInstanceLayer","resourceVersion":"2.0","userdefinedDepth":false,"visible":true,},\n'
    at = text.index(marker) + len(marker)
    text = text[:at] + FURNITURE_LAYER.replace("{instances}", "\n".join(lines)) + text[at:]

    text = re.sub(r'"instanceCreationOrder":\[.*?\n  \],',
                  '"instanceCreationOrder":[\n' + "".join(
                      f'    {{"name":"{n}","path":"rooms/{room}/{room}.yy",}},\n' for n in order) + "  ],",
                  text, count=1, flags=re.S)
    text = text.replace('"inheritCode":false,\n  "inheritCreationOrder":false,\n  "inheritLayers":false,',
                        '"inheritCode":true,\n  "inheritCreationOrder":false,\n  "inheritLayers":false,', 1)
    text = text.replace('"inheritRoomSettings":false', '"inheritRoomSettings":true', 1)
    text = text.replace('"inheritViewSettings":false', '"inheritViewSettings":true', 1)
    text = text.replace('"inheritPhysicsSettings":false', '"inheritPhysicsSettings":true', 1)
    text = text.replace('"parentRoom":null', f'"parentRoom":{PARENT_REF}', 1)
    text = re.sub(r'"parent":\{\s*"name":"House",\s*"path":"folders/Rooms/Templates/House.yy",\s*\}',
                  f'"parent":{{\n    "name":"{FOLDER}",\n    "path":"{FOLDER_PATH}",\n  }}', text, count=1)
    return text


def main():
    write_object("obj_furniture", create_code="depth = -y;\n")
    write_object("obj_rug", create_code="depth = 55; // above the floor layer (60), below walls (50)\n")
    sprites = sorted({e[0] for entries in LAYOUTS.values() for e in entries})
    objects = ["obj_furniture", "obj_rug"]
    for spr in sprites:
        name = object_for(spr)
        write_object(name, f"spr_int_objects_{spr}", "obj_rug" if spr.startswith("rug_") else "obj_furniture")
        objects.append(name)

    yyp_path = ROOT / "AthenaPlush.yyp"
    yyp = yyp_path.read_text(encoding="utf-8")
    folder_line = (f'    {{"$GMFolder":"","%Name":"{FOLDER}","folderPath":"{FOLDER_PATH}",'
                   f'"name":"{FOLDER}","resourceType":"GMFolder","resourceVersion":"2.0",}},\n')
    if FOLDER_PATH not in yyp:
        anchor = '    {"$GMFolder":"","%Name":"Filled Rooms"'
        at = yyp.index("\n", yyp.index(anchor)) + 1
        yyp = yyp[:at] + folder_line + yyp[at:]
    for n in objects:
        entry = f'    {{"id":{{"name":"{n}","path":"objects/{n}/{n}.yy",}},}},\n'
        if entry not in yyp:
            yyp = yyp.replace('    {"id":{"name":"obj_player"', entry + '    {"id":{"name":"obj_player"', 1)

    parent_text = (ROOT / "rooms" / PARENT / f"{PARENT}.yy").read_text(encoding="utf-8")
    for room, entries in LAYOUTS.items():
        path = ROOT / "rooms" / room / f"{room}.yy"
        if path.exists():
            print("skip", room)
            continue
        path.parent.mkdir(exist_ok=True)
        path.write_text(build_room(room, entries, parent_text), encoding="utf-8", newline="\n")
        res = f'    {{"id":{{"name":"{room}","path":"rooms/{room}/{room}.yy",}},}},\n'
        yyp = yyp.replace('    {"id":{"name":"rm_init"', res + '    {"id":{"name":"rm_init"', 1)
        node = f'    {{"roomId":{{"name":"{room}","path":"rooms/{room}/{room}.yy",}},}},\n'
        kitchen_node = f'    {{"roomId":{{"name":"{PARENT}","path":"rooms/{PARENT}/{PARENT}.yy",}},}},\n'
        yyp = yyp.replace(kitchen_node, kitchen_node + node, 1)
        print("created", room, f"({len(entries)} furniture items)")
    yyp_path.write_text(yyp, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
