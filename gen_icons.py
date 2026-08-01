import zlib, struct, math, os

OUT = r"C:\Users\Administrator\WorkBuddy\2026-07-22-08-14-20\hygzz_cn_domestic"

def write_png(path, size, draw):
    # raw RGBA rows with filter byte 0
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            raw += bytes(draw(x, y, size))
    comp = zlib.compress(bytes(raw), 9)
    def chunk(typ, data):
        c = typ + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)

BRAND = (163, 45, 45)      # #A32D2D
WHITE = (255, 255, 255)
GOLD  = (201, 162, 75)

def make(size):
    r = size / 2.0
    dot_r = size * 0.16
    def draw(x, y, s):
        dx, dy = x - r, y - r
        d = math.hypot(dx, dy)
        # rounded background already square; draw centered white ring-dot (logo)
        if d <= dot_r:
            return WHITE
        return BRAND
    return draw

for sz in (192, 512):
    write_png(os.path.join(OUT, f"icon-{sz}.png"), sz, make(sz))
    print("wrote icon-%d.png" % sz)
