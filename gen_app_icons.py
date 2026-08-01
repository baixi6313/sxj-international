from PIL import Image, ImageDraw
import os

# 源图路径
SRC = r'C:\Users\Administrator\.workbuddy\clipboard-images\clipboard-2026-07-30T19-16-08-841Z-fb57a7e5.png'

# 输出目录：Android 工程的 mipmap 目录
ROOT = r'C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\sxj-android-app\app\src\main\res'

# Android 标准 launcher 图标尺寸
SIZES = {
    'mipmap-mdpi': 48,
    'mipmap-hdpi': 72,
    'mipmap-xhdpi': 96,
    'mipmap-xxhdpi': 144,
    'mipmap-xxxhdpi': 192,
}

def make_square_icon(src_img, size, round=False):
    """
    把源图居中放入正方形画布，缩放适配，可选圆形裁剪。
    画布尺寸 = 源图长边的约 1.05 倍，给一点安全边距。
    """
    # 保持源图比例，缩放到目标正方形的 75% 以内（留出边距）
    src_w, src_h = src_img.size
    max_src = max(src_w, src_h)
    canvas_size = int(max_src * 1.05)

    # 在画布上居中放置源图
    canvas = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
    x = (canvas_size - src_w) // 2
    y = (canvas_size - src_h) // 2
    canvas.paste(src_img, (x, y), src_img if src_img.mode == 'RGBA' else None)

    # 缩放到目标尺寸
    icon = canvas.resize((size, size), Image.LANCZOS)

    if round:
        # 圆形 mask
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        # 把 icon 裁剪成圆形（透明背景）
        round_icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        round_icon.paste(icon, (0, 0), mask)
        return round_icon
    else:
        return icon

# 读取源图并转成 RGBA（保留透明度）
src = Image.open(SRC).convert('RGBA')

# 生成两套图标
for folder, size in SIZES.items():
    out_dir = os.path.join(ROOT, folder)
    os.makedirs(out_dir, exist_ok=True)

    # 方形
    square = make_square_icon(src, size, round=False)
    # 如果背景透明，改成白色背景（PNG-24，无透明）
    bg = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    if square.mode == 'RGBA':
        bg.paste(square, (0, 0), square)
    else:
        bg.paste(square, (0, 0))
    bg.convert('RGB').save(os.path.join(out_dir, 'ic_launcher.png'), 'PNG')

    # 圆形
    round_icon = make_square_icon(src, size, round=True)
    bg_round = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    bg_round.paste(round_icon, (0, 0), round_icon)
    bg_round.convert('RGB').save(os.path.join(out_dir, 'ic_launcher_round.png'), 'PNG')

    print(f"  {folder}: {size}x{size} OK")

print("\n图标生成完成！")

# 额外生成一个预览图
preview_size = 512
preview_square = make_square_icon(src, preview_size, round=False)
preview_round = make_square_icon(src, preview_size, round=True)
preview = Image.new('RGBA', (preview_size * 2 + 40, preview_size + 40), (245, 245, 245, 255))
preview.paste(preview_square, (20, 20), preview_square)
preview.paste(preview_round, (preview_size + 40, 20), preview_round)
preview_path = r'C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\sxj-android-app\logo_preview.png'
preview.convert('RGB').save(preview_path, 'PNG')
print(f"预览图已保存: {preview_path}")
