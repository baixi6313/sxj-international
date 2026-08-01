# -*- coding: utf-8 -*-
"""生成事现鉴 App 极简 logo 三方案(铜镜/瓦当/太极图) + 手机预览。
所有图形用 Pillow 纯几何绘制，透明背景，品牌色 红#A32D2D + 米白#F5F0E6。"""
import os, base64, io
from PIL import Image, ImageDraw

RED   = (163, 45, 45, 255)     # A32D2D
CREAM = (245, 240, 230, 255)   # F5F0E6
GOLD  = (201, 162, 75, 255)    # C9A24B

OUT = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\logo_clean"
os.makedirs(OUT, exist_ok=True)

def base(sz):
    return Image.new("RGBA", (sz, sz), (0, 0, 0, 0))

def logo_jing(sz):  # 铜镜·鉴：实心红盘 + 细内环 + 中心钮(负空间)
    img = base(sz); d = ImageDraw.Draw(img); c = sz / 2; R = sz * 0.47
    d.ellipse([c-R, c-R, c+R, c+R], fill=RED)
    d.ellipse([c-R*0.80, c-R*0.80, c+R*0.80, c+R*0.80], outline=CREAM, width=max(2, int(sz*0.022)))
    d.ellipse([c-R*0.13, c-R*0.13, c+R*0.13, c+R*0.13], fill=CREAM)
    d.ellipse([c-R*0.13, c-R*0.13, c+R*0.13, c+R*0.13], outline=GOLD, width=max(1, int(sz*0.008)))
    return img

def logo_taiji(sz):  # 太极·衡：红/米白两仪 + 双睛
    img = base(sz); d = ImageDraw.Draw(img); c = sz / 2; R = sz * 0.47
    d.ellipse([c-R, c-R, c+R, c+R], fill=CREAM)
    d.pieslice([c-R, c-R, c+R, c+R], -90, 90, fill=RED)      # 右半红
    r2 = R / 2
    d.ellipse([c-r2, c-R, c+r2, c], fill=RED)                # 上小半圆红
    d.ellipse([c-r2, c, c+r2, c+R], fill=CREAM)              # 下小半圆米白
    d.ellipse([c-R*0.11, c-R*0.11, c+R*0.11, c+R*0.11], fill=CREAM)  # 上睛
    d.ellipse([c-R*0.11, c+R*0.11-2*R*0.11, c+R*0.11, c+R*0.11], fill=RED)  # 下睛
    return img

def logo_wadang(sz):  # 瓦当·环：米白盘面 + 粗红边环 + 中心红钮
    img = base(sz); d = ImageDraw.Draw(img); c = sz / 2; R = sz * 0.47
    d.ellipse([c-R, c-R, c+R, c+R], fill=CREAM)
    d.ellipse([c-R, c-R, c+R, c+R], fill=RED)
    d.ellipse([c-R*0.74, c-R*0.74, c+R*0.74, c+R*0.74], fill=CREAM)  # 抠出红环
    d.ellipse([c-R*0.15, c-R*0.15, c+R*0.15, c+R*0.15], fill=RED)   # 中心钮
    return img

MAKERS = {"A_铜镜": logo_jing, "B_太极": logo_taiji, "C_瓦当": logo_wadang}

# 1) 主图 1024
masters = {}
for name, fn in MAKERS.items():
    im = fn(1024)
    p = os.path.join(OUT, "master_%s.png" % name)
    im.save(p)
    masters[name] = p
    print("master:", name, p)

# 2) 各密度 mipmap(方/圆同图) — 备用推送
dens = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
for name, fn in MAKERS.items():
    big = fn(1024)
    for dn, px in dens.items():
        small = big.resize((px, px), Image.LANCZOS)
        ddir = os.path.join(OUT, name, "mipmap-" + dn)
        os.makedirs(ddir, exist_ok=True)
        small.save(os.path.join(ddir, "ic_launcher.png"))
        small.save(os.path.join(ddir, "ic_launcher_round.png"))
print("mipmap 已生成(每方案 10 个)")

# 3) 手机预览 HTML(内嵌 base64，自含可看)
def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

phone = ('<div style="display:inline-block;width:150px;height:300px;background:#111;border-radius:22px;'
         'padding:14px 12px;box-sizing:border-box;vertical-align:top;margin:6px;">'
         '<div style="height:26px"></div>'
         '<img src="data:image/png;base64,%s" style="width:108px;height:108px;display:block;margin:8px auto;border-radius:24px;"/>'
         '<div style="color:#fff;text-align:center;font:700 15px/1.4 system-ui;margin-top:10px;">事现鉴</div>'
         '<div style="color:#9aa; text-align:center;font:400 10px/1.4 system-ui;margin-top:4px;">公共事实验证</div>'
         '</div>')

cards = ""
for name, fn in MAKERS.items():
    mp = masters[name]
    cards += '<div style="text-align:center;margin:10px;">'
    cards += phone % b64(mp)
    cards += '<div style="font:700 14px system-ui;margin-top:8px;color:#A32D2D">%s</div>' % name
    cards += '<img src="data:image/png;base64,%s" style="width:64px;height:64px;display:block;margin:6px auto;"/>' % b64(mp)
    cards += '</div>'

html = """<!doctype html><html lang=zh><head><meta charset=utf-8>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>事现鉴 极简 Logo 三方案</title></head>
<body style="margin:0;background:#f5f0e6;color:#222;font-family:system-ui;padding:24px;">
<h2 style="color:#A32D2D">事现鉴 App · 极简 Logo 三方案</h2>
<p style="font:400 13px/1.6 system-ui;max-width:620px;color:#555">
参考母题：<b>铜镜</b>(鉴=照见真相之镜)、<b>瓦当</b>(汉唐圆形瓦当边环+中心钮)、<b>太极图</b>(两仪平衡，对应真/假、共济/贡献/负贡献)。
全部为纯几何、透明底、仅用品牌红 #A32D2D + 米白 #F5F0E6，去渐变去高光，干净克制。</p>
<div style="display:flex;flex-wrap:wrap;gap:18px;align-items:flex-start;margin-top:18px;">%s</div>
<p style="font:400 12px/1.6 system-ui;color:#888;margin-top:24px">推荐：A 铜镜·鉴——最贴合「鉴」本义，最安静。选定后我会生成全档密度图标、替换 App 资源并重新编译；同时把国内站(hygzz.top)导航 logo 一并换掉。</p>
</body></html>""" % cards

prev = os.path.join(OUT, "logo_preview.html")
with open(prev, "w", encoding="utf-8") as f:
    f.write(html)
print("preview:", prev)
