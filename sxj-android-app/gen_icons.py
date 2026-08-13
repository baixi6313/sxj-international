import zlib, struct, os

def write_png(path, w, h, rgba):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw.extend(rgba[y*w*4:(y+1)*w*4])
    comp = zlib.compress(bytes(raw), 9)
    with open(path, 'wb') as f:
        def chunk(typ, data):
            f.write(struct.pack('>I', len(data)))
            f.write(typ)
            f.write(data)
            f.write(struct.pack('>I', zlib.crc32(typ+data) & 0xffffffff))
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
        chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
        chunk(b'IDAT', comp)
        chunk(b'IEND', b'')

def make_icon(size):
    buf = bytearray(size*size*4)
    cx = cy = size/2.0
    R = size*0.40
    for i in range(size*size):
        x = i % size; y = i // size
        dx = x+0.5-cx; dy = y+0.5-cy
        d = (dx*dx+dy*dy)**0.5
        if d <= R:
            r,g,b = (255,255,255)          # white ring fill
        else:
            r,g,b = (0xA3,0x2D,0x2D)        # brand red bg
        if d <= R*0.42:
            r,g,b = (0xC9,0xA2,0x4B)        # gold core dot
        idx = i*4
        buf[idx]=r; buf[idx+1]=g; buf[idx+2]=b; buf[idx+3]=255
    return bytes(buf)

base = "C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27/sxj-android-app/app/src/main/res"
densities = {
    'mipmap-mdpi': 48,
    'mipmap-hdpi': 72,
    'mipmap-xhdpi': 96,
    'mipmap-xxhdpi': 144,
    'mipmap-xxxhdpi': 192,
}
for folder, size in densities.items():
    data = make_icon(size)
    p = os.path.join(base, folder, 'ic_launcher.png')
    write_png(p, size, size, data)
    pr = os.path.join(base, folder, 'ic_launcher_round.png')
    write_png(pr, size, size, data)
    print('wrote', p, size)
print('icons done')
