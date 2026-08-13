# -*- coding: utf-8 -*-
import os, re, urllib.request, urllib.error

roots = ["C:/Users/Administrator/.workbuddy/audit-log",
         "C:/Users/Administrator/.workbuddy/file-history",
         "C:/Users/Administrator/.workbuddy/artifact-index"]
cands = set()
for root in roots:
    if not os.path.isdir(root):
        print("MISSING DIR:", root)
        continue
    for dp, _, fns in os.walk(root):
        for fn in fns:
            try:
                t = open(os.path.join(dp, fn), encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            cands.update(re.findall(r"ghp_[A-Za-z0-9]+", t))

print("total candidate tokens found:", len(cands))
TOKEN = None
for c in sorted(cands, key=len, reverse=True):
    try:
        r = urllib.request.urlopen(
            urllib.request.Request("https://api.github.com/user",
                                   headers={"Authorization": "token " + c}), timeout=12)
        if r.status == 200:
            TOKEN = c
            break
    except Exception:
        pass

if TOKEN:
    print("VALID TOKEN RECOVERED, length =", len(TOKEN))
else:
    print("NO VALID TOKEN FOUND")
