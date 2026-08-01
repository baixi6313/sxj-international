from PIL import Image, ImageDraw
import os

SRC = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\logo_jian_v3_red_wire.png"
ROOT = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\sxj-android-app\app\src\main\res"

SIZES = {
    'mipmap-mdpi': 48,
    'mipmap-hdpi': 72,
    'mipmap-xhdpi': 96,
    'mipmap-xxhdpi': 144,
    'mipmap-xxxhdpi': 192,
}

mark = Image.open(SRC).convert('RGBA')

for folder, size in SIZES.items():
    out_dir = os.path.join(ROOT, folder)
    os.makedirs(out_dir, exist_ok=True)

    # 标缩放到图标的 82%（留边距）
    mark_size = int(size * 0.82)
    m = mark.resize((mark_size, mark_size), Image.LANCZOS)
    off = (size - mark_size) // 2

    # 方形：白底
    sq = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    sq.paste(m, (off, off), m)
    sq.convert('RGB').save(os.path.join(out_dir, 'ic_launcher.png'), 'PNG')

    # 圆形：白色圆形底
    rd = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(rd)
    d.ellipse((0, 0, size, size), fill=(255, 255, 255, 255))
    rd.paste(m, (off, off), m)
    rd.convert('RGB').save(os.path.join(out_dir, 'ic_launcher_round.png'), 'PNG')

    print(f"  {folder}: {size}x{size} OK")

print("\nv3 图标生成完成")

# 预览
prev = Image.new('RGBA', (512, 512), (255, 255, 255, 255))
ps = int(512 * 0.82)
pm = mark.resize((ps, ps), Image.LANCZOS)
prev.paste(pm, ((512 - ps) // 2, (512 - ps) // 2), pm)
prev.convert('RGB').save(r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\sxj-android-app\logo_v3_preview.png", 'PNG')
print("预览: sxj-android-app/logo_v3_preview.png")
