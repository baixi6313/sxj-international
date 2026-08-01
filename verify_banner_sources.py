import os

MARKERS = ["beta-banner", "测试版", "BETA", "prov-note", "bb-row", "bb-badge", "非实地实施产品"]
# "非实地实施"(无"产品") 是诚实声明，保留，不计入横幅

ROOTS = {
    "微信小程序": r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\sxj-mini\weapp-client",
    "安卓App内嵌": r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\sxj-android-app\app\src\main\assets\www",
}

SKIP_DIRS = {"node_modules", "cloudfunctions", ".git", ".workbuddy"}

def walk(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if f.lower().endswith((".html", ".wxml", ".wxss", ".js", ".css", ".json")):
                yield os.path.join(dp, f)

total_hit = 0
for label, root in ROOTS.items():
    print(f"\n===== {label} ({root}) =====")
    found = False
    for fp in walk(root):
        try:
            data = open(fp, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        hits = {m: data.count(m) for m in MARKERS if m in data}
        if hits:
            found = True
            total_hit += 1
            rel = os.path.relpath(fp, root)
            print(f"  [横幅残留] {rel}  {hits}")
    if not found:
        print("  ✅ 无横幅残留（源码干净）")

print("\n==> 含横幅残留的文件数:", total_hit)
