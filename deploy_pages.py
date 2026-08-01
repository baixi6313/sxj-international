#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cloudflare Pages Direct Upload 部署脚本"""
import os, sys, json, hashlib, time
import urllib.request, urllib.error

CF_TOKEN = os.environ.get("CF_TOKEN", "")
ACCT = os.environ.get("ACCT", "")
API = "https://api.cloudflare.com/client/v4"

if not CF_TOKEN or not ACCT:
    print("ERROR: CF_TOKEN 和 ACCT 环境变量必须设置")
    sys.exit(1)

def api_call(method, path, data=None, extra_headers=None):
    url = f"{API}{path}"
    headers = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        try:
            return json.loads(err_body)
        except Exception:
            return {"success": False, "errors": [{"message": err_body}]}

def upload_one(upload_url, jwt, file_rel, content):
    url = f"{upload_url}/{file_rel}"
    req = urllib.request.Request(
        url, data=content, method="PUT",
        headers={"Authorization": f"Bearer {jwt}", "Content-Type": "application/octet-stream"}
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.status in (200, 201)
    except urllib.error.HTTPError as e:
        print(f"    [上传失败] {file_rel}: HTTP {e.code} {e.read().decode()[:200]}")
        return False

def deploy(project_name, dir_path, production_branch="main"):
    print(f"\n{'='*60}")
    print(f"部署项目: {project_name}")
    print(f"目录: {dir_path}")
    print(f"{'='*60}")

    # 1. 创建项目（若已存在则跳过）
    print("[1/4] 创建 Pages 项目...")
    res = api_call("POST", f"/accounts/{ACCT}/pages/projects",
                   {"name": project_name, "production_branch": production_branch})
    if res.get("success"):
        print(f"  ✓ 项目创建成功: {res['result']['name']}")
        subdomain = res['result'].get('subdomain', '')
        if subdomain:
            print(f"  预览域名: https://{subdomain}.pages.dev")
    else:
        # 可能已存在，尝试获取
        res2 = api_call("GET", f"/accounts/{ACCT}/pages/projects/{project_name}")
        if res2.get("success"):
            print(f"  ✓ 项目已存在，复用: {res2['result']['name']}")
        else:
            print(f"  ✗ 创建失败: {res.get('errors')}")
            return None

    # 2. 收集文件
    print("[2/4] 收集文件...")
    from pathlib import Path
    base = Path(dir_path)
    files = {}
    skip_dirs = {".git", ".github", "node_modules", "__pycache__"}
    skip_exts = {".md", ".bat"}
    skip_names = {".gitignore", "CNAME", ".DS_Store"}
    for f in base.rglob("*"):
        if not f.is_file():
            continue
        parts = set(f.relative_to(base).parts)
        if parts & skip_dirs:
            continue
        if f.suffix in skip_exts or f.name in skip_names:
            continue
        rel = str(f.relative_to(base)).replace("\\", "/")
        files[rel] = f
    total = len(files)
    total_size = sum(f.stat().st_size for f in files.values())
    print(f"  共 {total} 个文件, {total_size/1024:.1f} KB")
    for rel in sorted(files):
        print(f"    - {rel} ({files[rel].stat().st_size/1024:.1f} KB)")

    if not files:
        print("  ✗ 没有可部署的文件")
        return None

    # 3. 创建部署 (manifest)
    print("[3/4] 创建部署...")
    manifest = {}
    for rel, f in files.items():
        content = f.read_bytes()
        sha1 = hashlib.sha1(content).hexdigest()
        manifest[rel] = {"hashType": "sha1", "hash": sha1}
    res = api_call("POST", f"/accounts/{ACCT}/pages/projects/{project_name}/deployments",
                   {"manifest": manifest})
    if not res.get("success"):
        print(f"  ✗ 部署创建失败: {res.get('errors')}")
        return None
    result = res["result"]
    upload_url = result.get("upload_url")
    jwt = result.get("jwt")
    deploy_id = result.get("id")
    print(f"  ✓ 部署已创建: {deploy_id}")
    print(f"  上传地址: {upload_url}")

    # 4. 上传文件
    print("[4/4] 上传文件...")
    ok = 0
    failed = []
    for i, (rel, f) in enumerate(sorted(files.items()), 1):
        content = f.read_bytes()
        if upload_one(upload_url, jwt, rel, content):
            ok += 1
            print(f"  [{i}/{total}] ✓ {rel}")
        else:
            failed.append(rel)
            print(f"  [{i}/{total}] ✗ {rel}")
        # 小延迟避免限流
        if i % 10 == 0:
            time.sleep(0.2)

    print(f"\n上传结果: {ok}/{total} 成功")
    if failed:
        print(f"失败文件: {failed}")

    # 获取部署详情（拿到 URL）
    time.sleep(2)
    detail = api_call("GET", f"/accounts/{ACCT}/pages/projects/{project_name}/deployments/{deploy_id}")
    url = None
    alias_url = None
    if detail.get("success"):
        r = detail["result"]
        url = r.get("url")
        aliases = r.get("aliases") or []
        if aliases:
            alias_url = aliases[0]
        env = r.get("environment")
        staged = r.get("latest_stage", {})
        print(f"\n  部署状态: {staged.get('name')} -> {staged.get('status')}")
        print(f"  环境: {env}")

    print(f"\n>>> {project_name} 部署完成 <<<")
    if url:
        print(f"    访问地址: https://{url}")
    if alias_url:
        print(f"    别名地址: https://{alias_url}")
    return {"project": project_name, "deploy_id": deploy_id, "url": url, "alias": alias_url}


if __name__ == "__main__":
    base_dir = "C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20"
    results = []

    # 国际版 -> hygzz-com
    r1 = deploy("hygzz-com", f"{base_dir}/hygzz_cn")
    if r1:
        results.append(r1)

    # 国内版 -> hygzz-cn
    r2 = deploy("hygzz-cn", f"{base_dir}/hygzz_cn_domestic")
    if r2:
        results.append(r2)

    print(f"\n{'='*60}")
    print("全部部署汇总")
    print(f"{'='*60}")
    for r in results:
        print(f"\n项目: {r['project']}")
        print(f"  部署ID: {r['deploy_id']}")
        if r.get("url"):
            print(f"  地址: https://{r['url']}")
        if r.get("alias"):
            print(f"  别名: https://{r['alias']}")
    print(f"\n共部署 {len(results)} 个项目")
