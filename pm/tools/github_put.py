#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Push a single file to a GitHub repo via Contents API. Reads token from GH_PAT env var.
Usage: GH_PAT=xxx python github_put.py <owner> <repo> <path> <localfile>
光锥运维部 · 通用工具（替代明文硬编码 PAT 的推送脚本）。
"""
import os, sys, base64, json, urllib.request, urllib.error

API = "https://api.github.com"

def api(method, path, token, data=None):
    url = API + path
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "User-Agent": "sxj-ops"}
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}

def main():
    token = os.environ.get("GH_PAT")
    if not token:
        sys.exit("ERROR: 请设置环境变量 GH_PAT")
    owner, repo, path, local = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    with open(local, encoding="utf-8") as f:
        content = f.read()
    b64 = base64.b64encode(content.encode()).decode()
    st, data = api("GET", f"/repos/{owner}/{repo}/contents/{path}", token)
    sha = data.get("sha") if st == 200 else None
    st2, resp = api("PUT", f"/repos/{owner}/{repo}/contents/{path}", token,
                    {"message": f"chore: update {path}", "content": b64, **({"sha": sha} if sha else {})})
    print(f"PUT {owner}/{repo}/{path} -> HTTP {st2}  {resp.get('message','')}")

if __name__ == "__main__":
    main()
