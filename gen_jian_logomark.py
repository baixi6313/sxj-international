from PIL import Image, ImageDraw, ImageFont

# 品牌色
RED = (163, 45, 45)      # A32D2D
GOLD = (201, 162, 75)    # C9A24B
GREY = (238, 238, 238)   # 预览底

SS = 1024          # 预览尺寸
RENDER = SS * 4    # 4x 超采样抗锯齿

def new_canvas(size=RENDER, bg=None):
    if bg is None:
        return Image.new('RGBA', (size, size), (0, 0, 0, 0))
    return Image.new('RGBA', (size, size), bg + (255,))

def draw_variation(n, bg=None):
    img = new_canvas(bg=bg)
    d = ImageDraw.Draw(img)
    cx = cy = RENDER // 2
    S = RENDER / 100.0  # 100-unit 视图 -> 像素

    if n == 1:
        # 红底金钮：红色镜身 + 细金边 + 金钮
        d.ellipse([cx-46*S, cy-46*S, cx+46*S, cy+46*S], fill=RED)
        d.ellipse([cx-41*S, cy-41*S, cx+41*S, cy+41*S], outline=GOLD, width=int(1.4*S))
        d.ellipse([cx-7.5*S, cy-7.5*S, cx+7.5*S, cy+7.5*S], fill=GOLD)

    elif n == 2:
        # 金环红钮：金线镜身 + 红钮
        d.ellipse([cx-46*S, cy-46*S, cx+46*S, cy+46*S], outline=GOLD, width=int(4*S))
        d.ellipse([cx-10*S, cy-10*S, cx+10*S, cy+10*S], fill=RED)

    elif n == 3:
        # 线框极简：单色红，外环+内细环+红钮
        d.ellipse([cx-46*S, cy-46*S, cx+46*S, cy+46*S], outline=RED, width=int(3*S))
        d.ellipse([cx-38*S, cy-38*S, cx+38*S, cy+38*S], outline=RED, width=int(1.5*S))
        d.ellipse([cx-7*S, cy-7*S, cx+7*S, cy+7*S], fill=RED)

    # 缩回预览尺寸（抗锯齿）
    img = img.resize((SS, SS), Image.LANCZOS)
    return img

# 渲染三版（透明底，放灰卡上预览）
variations = []
for n in (1, 2, 3):
    v = draw_variation(n)  # 透明底
    # 合成到灰卡
    card = Image.new('RGBA', (SS, SS), GREY + (255,))
    card = Image.alpha_composite(card, v)
    variations.append(card.convert('RGB'))

# 2x2 对比图
pad = 50
label_h = 70
cell = SS
w = cell * 2 + pad * 3
h = cell * 2 + pad * 3 + label_h * 2
grid = Image.new('RGB', (w, h), (250, 250, 250))
d = ImageDraw.Draw(grid)
try:
    font = ImageFont.truetype("C:\\Windows\\Fonts\\msyh.ttc", 34)
    small = ImageFont.truetype("C:\\Windows\\Fonts\\msyh.ttc", 22)
except:
    font = ImageFont.load_default()
    small = font

labels = ["1. 红底金钮", "2. 金环红钮", "3. 线框极简（单色红）"]
for i, img in enumerate(variations):
    row, col = divmod(i, 2)
    x = pad + col * (cell + pad)
    y = pad + row * (cell + pad + label_h)
    grid.paste(img, (x, y))
    bbox = d.textbbox((0,0), labels[i], font=font)
    tw = bbox[2]-bbox[0]
    d.text((x + (cell-tw)//2, y + cell + 18), labels[i], fill=(60,60,60), font=font)

out = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\logo_jian_comparison.png"
grid.save(out, "PNG")
print("对比图:", out)

def build_svg(n):
    red = "#A32D2D"; gold = "#C9A24B"
    if n == 1:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
<circle cx="50" cy="50" r="46" fill="{red}"/>
<circle cx="50" cy="50" r="41" fill="none" stroke="{gold}" stroke-width="1.4"/>
<circle cx="50" cy="50" r="7.5" fill="{gold}"/>
</svg>'''
    elif n == 2:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
<circle cx="50" cy="50" r="46" fill="none" stroke="{gold}" stroke-width="4"/>
<circle cx="50" cy="50" r="10" fill="{red}"/>
</svg>'''
    else:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
<circle cx="50" cy="50" r="46" fill="none" stroke="{red}" stroke-width="3"/>
<circle cx="50" cy="50" r="38" fill="none" stroke="{red}" stroke-width="1.5"/>
<circle cx="50" cy="50" r="7" fill="{red}"/>
</svg>'''

# 同时保存单张透明底 PNG + 对应 SVG
names = {1: "jian_v1_red_gold", 2: "jian_v2_gold_red", 3: "jian_v3_red_wire"}
for n, name in names.items():
    v = draw_variation(n)
    v.save(rf"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\logo_{name}.png", "PNG")
    svg = build_svg(n)
    with open(rf"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\logo_{name}.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("生成:", name)
