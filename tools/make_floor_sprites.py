"""Generate flat-colour 64x32 isometric floor diamonds as placeholder art.

Usage:
    python tools/make_floor_sprites.py <output_dir>
    python tools/import_sprites.py <output_dir> --origin mc
"""
import struct
import sys
import zlib
from pathlib import Path

W, H = 64, 32
FLOORS = {
    "wood": ((196, 150, 98), (150, 108, 64)),
    "darkwood": ((120, 80, 52), (84, 54, 34)),
    "carpet": ((110, 130, 160), (80, 98, 124)),
    "tile": ((222, 230, 234), (160, 176, 186)),
}


def diamond_rows(fill, edge):
    rows = []
    for y in range(H):
        half = 32 * (1 - abs(y + 0.5 - 16) / 16)
        left, right = round(32 - half), round(32 + half)
        row = bytearray([0])
        for x in range(W):
            if not left <= x < right:
                row += bytes((0, 0, 0, 0))
            elif x < left + 2 or x >= right - 2 or y in (0, H - 1):
                row += bytes((*edge, 255))
            else:
                row += bytes((*fill, 255))
        rows.append(bytes(row))
    return b"".join(rows)


def write_png(path, raw):
    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw))
           + chunk(b"IEND", b""))
    path.write_bytes(png)


if __name__ == "__main__":
    out = Path(sys.argv[1]) / "floors"
    out.mkdir(parents=True, exist_ok=True)
    for name, (fill, edge) in FLOORS.items():
        write_png(out / f"{name}.png", diamond_rows(fill, edge))
        print("wrote", out / f"{name}.png")
