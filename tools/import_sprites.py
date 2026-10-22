"""Import a folder of PNGs into the GameMaker project as single-frame sprites.

Usage (close the GameMaker IDE first, it rewrites AthenaPlush.yyp on save):
    python tools/import_sprites.py "C:/Users/tyler/Downloads/IsometricInteriorPack1.1"

Each PNG becomes spr_<prefix>_<subfolder>_<filename> inside Sprites/<GM folder>.
Re-running skips sprites that already exist.
"""
import argparse
import json
import re
import shutil
import struct
import uuid
from pathlib import Path

ORIGINS = {"tl": 0, "tc": 1, "tr": 2, "ml": 3, "mc": 4, "mr": 5, "bl": 6, "bc": 7, "br": 8}

SPRITE_YY = """{{
  "$GMSprite":"v2",
  "%Name":"{name}",
  "bboxMode":0,
  "bbox_bottom":{h1},
  "bbox_left":0,
  "bbox_right":{w1},
  "bbox_top":0,
  "collisionKind":1,
  "collisionTolerance":0,
  "DynamicTexturePage":false,
  "edgeFiltering":false,
  "For3D":false,
  "frames":[
    {{"$GMSpriteFrame":"v1","%Name":"{frame}","name":"{frame}","resourceType":"GMSpriteFrame","resourceVersion":"2.0",}},
  ],
  "gridX":0,
  "gridY":0,
  "height":{h},
  "HTile":false,
  "layers":[
    {{"$GMImageLayer":"","%Name":"{layer}","blendMode":0,"displayName":"default","isLocked":false,"name":"{layer}","opacity":100.0,"resourceType":"GMImageLayer","resourceVersion":"2.0","visible":true,}},
  ],
  "name":"{name}",
  "nineSlice":null,
  "origin":{origin},
  "parent":{{
    "name":"{folder}",
    "path":"folders/Sprites/{folder}.yy",
  }},
  "preMultiplyAlpha":false,
  "resourceType":"GMSprite",
  "resourceVersion":"2.0",
  "sequence":{{
    "$GMSequence":"v1",
    "%Name":"{name}",
    "autoRecord":true,
    "backdropHeight":768,
    "backdropImageOpacity":0.5,
    "backdropImagePath":"",
    "backdropWidth":1366,
    "backdropXOffset":0.0,
    "backdropYOffset":0.0,
    "events":{{
      "$KeyframeStore<MessageEventKeyframe>":"",
      "Keyframes":[],
      "resourceType":"KeyframeStore<MessageEventKeyframe>",
      "resourceVersion":"2.0",
    }},
    "eventStubScript":null,
    "eventToFunction":{{}},
    "length":1.0,
    "lockOrigin":false,
    "moments":{{
      "$KeyframeStore<MomentsEventKeyframe>":"",
      "Keyframes":[],
      "resourceType":"KeyframeStore<MomentsEventKeyframe>",
      "resourceVersion":"2.0",
    }},
    "name":"{name}",
    "playback":1,
    "playbackSpeed":30.0,
    "playbackSpeedType":0,
    "resourceType":"GMSequence",
    "resourceVersion":"2.0",
    "showBackdrop":true,
    "showBackdropImage":false,
    "timeUnits":1,
    "tracks":[
      {{"$GMSpriteFramesTrack":"","builtinName":0,"events":[],"inheritsTrackColour":true,"interpolation":1,"isCreationTrack":false,"keyframes":{{"$KeyframeStore<SpriteFrameKeyframe>":"","Keyframes":[
            {{"$Keyframe<SpriteFrameKeyframe>":"","Channels":{{
                "0":{{"$SpriteFrameKeyframe":"","Id":{{"name":"{frame}","path":"sprites/{name}/{name}.yy",}},"resourceType":"SpriteFrameKeyframe","resourceVersion":"2.0",}},
              }},"Disabled":false,"id":"{key}","IsCreationKey":false,"Key":0.0,"Length":1.0,"resourceType":"Keyframe<SpriteFrameKeyframe>","resourceVersion":"2.0","Stretch":false,}},
          ],"resourceType":"KeyframeStore<SpriteFrameKeyframe>","resourceVersion":"2.0",}},"modifiers":[],"name":"frames","resourceType":"GMSpriteFramesTrack","resourceVersion":"2.0","spriteId":null,"trackColour":0,"tracks":[],"traits":0,}},
    ],
    "visibleRange":null,
    "volume":1.0,
    "xorigin":{xo},
    "yorigin":{yo},
  }},
  "swatchColours":null,
  "swfPrecision":0.5,
  "textureGroupId":{{
    "name":"Default",
    "path":"texturegroups/Default",
  }},
  "type":0,
  "VTile":false,
  "width":{w},
}}"""


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    return struct.unpack(">II", head[16:24])


def sprite_name(prefix, png, root):
    rel = png.relative_to(root).with_suffix("")
    raw = "_".join((prefix, *rel.parts))
    name = re.sub(r"[^A-Za-z0-9_]", "_", raw)
    return re.sub(r"_+", "_", name)


def origin_xy(origin, w, h):
    code = ORIGINS[origin]
    return (w // 2 if code % 3 == 1 else w if code % 3 == 2 else 0,
            h // 2 if code in (3, 4, 5) else h if code >= 6 else 0)


def ensure_folder(yyp_text, folder):
    entry = (f'    {{"$GMFolder":"","%Name":"{folder}","folderPath":"folders/Sprites/{folder}.yy",'
             f'"name":"{folder}","resourceType":"GMFolder","resourceVersion":"2.0",}},\n')
    if f'"folderPath":"folders/Sprites/{folder}.yy"' in yyp_text:
        return yyp_text
    anchor = '"folderPath":"folders/Sprites.yy"'
    line_end = yyp_text.index("\n", yyp_text.index(anchor)) + 1
    return yyp_text[:line_end] + entry + yyp_text[line_end:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path, help="folder of PNGs (searched recursively)")
    ap.add_argument("--project", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--prefix", default="spr_int")
    ap.add_argument("--folder", default="Interior", help="GameMaker Sprites subfolder")
    ap.add_argument("--origin", choices=ORIGINS, default="bc", help="default: bottom-centre")
    a = ap.parse_args()

    yyp_path = next(a.project.glob("*.yyp"))
    yyp = ensure_folder(yyp_path.read_bytes().decode("utf-8"), a.folder)

    new = []
    for png in sorted(a.source.rglob("*.png")):
        name = sprite_name(a.prefix, png, a.source)
        sdir = a.project / "sprites" / name
        if sdir.exists():
            print(f"skip   {name}")
            continue
        w, h = png_size(png)
        frame, layer, key = (str(uuid.uuid4()) for _ in range(3))
        (sdir / "layers" / frame).mkdir(parents=True)
        shutil.copyfile(png, sdir / f"{frame}.png")
        shutil.copyfile(png, sdir / "layers" / frame / f"{layer}.png")
        xo, yo = origin_xy(a.origin, w, h)
        (sdir / f"{name}.yy").write_text(SPRITE_YY.format(
            name=name, frame=frame, layer=layer, key=key, w=w, h=h, w1=w - 1, h1=h - 1,
            origin=ORIGINS[a.origin], xo=xo, yo=yo, folder=a.folder), encoding="utf-8", newline="\n")
        new.append(name)
        print(f"add    {name} ({w}x{h})")

    if new:
        lines = "".join(
            f'    {{"id":{{"name":"{n}","path":"sprites/{n}/{n}.yy",}},}},\n' for n in new)
        anchor = '  ],\n  "resourceType":"GMProject"'
        yyp = yyp.replace(anchor, lines + anchor, 1)
        yyp_path.write_bytes(yyp.encode("utf-8"))
    print(f"\n{len(new)} sprite(s) imported into Sprites/{a.folder}")


if __name__ == "__main__":
    main()
