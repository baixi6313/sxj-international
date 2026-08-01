#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cloudflare Pages Direct Upload 部署脚本 (requests 版)"""
import os, sys, json, hashlib, mimetypes, time
import requests
from pathlib import Path

CF_TOKEN = os.environ.get("CF_TOKEN", "")
ACCT = os.environ.get("ACCT", "")
API = "https://api.cloudflare.com/client/v4"

if not CF_TOKEN or not ACCT:
    print("ERROR: 需要设置 CF_TOKEN 和 ACCT 环境变量")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {CF_TOKEN}"}

def deploy(project_name, dir_path, production_branch="main"):
    print(f"\n{'='*60}")
    print(f"部署项目: {project_name}")
    print(f"{'='*60}")

    base = Path(dir_path)
    skip_dirs = {".git", ".github", "node_modules", "__pycache__"}
    skip_exts = {".md", ".bat"}
    skip_names = {".gitignore", "CNAME", ".DS_Store"}

    # 收集文件
    files_list = []
    for f in sorted(base.rglob("*")):
        if not f.is_file():
            continue
        parts = set(f.relative_to(base).parts)
        if parts & skip_dirs:
            continue
        if f.suffix in skip_exts or f.name in skip_names:
            continue
        files_list.append(f)

    if not files_list:
        print("  没有可部署的文件")
        return None

    # 计算 SHA256，构造 manifest（key 以 / 开头）
    manifest = {}
    file_map = {}  # hash -> (filename, content, mime)
    for f in files_list:
        rel = "/" + str(f.relative_to(base)).replace("\\", "/")
        content = f.read_bytes()
        h = hashlib.sha256(content).hexdigest()
        manifest[rel] = h
        mime = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
        file_map[h] = (f.name, content, mime)

    total = len(files_list)
    total_size = sum(f.stat().st_size for f in files_list)
    print(f"  文件数: {total}, 总大小: {total_size/1024:.1f} KB")
    for f in files_list:
        rel = "/" + str(f.relative_to(base)).replace("\\", "/")
        print(f"    {rel} ({f.stat().st_size/1024:.1f} KB)")

    # 构造 multipart
    # manifest part: name="manifest", content_type="application/json"
    # 文件 parts: name=hash, filename=文件名, content_type=mime
    multipart = [("manifest", (None, json.dumps(manifest), "application/json"))]
    for h, (fname, content, mime) in file_map.items():
        multipart.append((h, (fname, content, mime)))

    print(f"\n  manifest: {json.dumps(manifest)[:200]}...")
    print(f"  multipart parts: {len(multipart)} (1 manifest + {len(file_map)} files)")

    # 创建部署
    print("\n  创建部署...")
    url = f"{API}/accounts/{ACCT}/pages/projects/{project_name}/deployments"
    resp = requests.post(url, headers=HEADERS, files=multipart, timeout=120)
    data = resp.json()

    if not data.get("success"):
        print(f"  部署失败: {data.get('errors')}")
        return None

    result = data["result"]
    deploy_id = result.get("id")
    deploy_url = result.get("url")
    print(f"  部署成功!")
    print(f"  部署ID: {deploy_id}")
    print(f"  部署URL: https://{deploy_url}")

    # 等待部署完成
    print("\n  等待部署完成...")
    for i in range(6):
        time.sleep(5)
        r = requests.get(f"{API}/accounts/{ACCT}/pages/projects/{project_name}/deployments/{deploy_id}",
                         headers=HEADERS, timeout=30)
        if r.ok:
            rd = r.json().get("result", {})
            stage = rd.get("latest_stage", {})
            status = stage.get("status")
            name = stage.get("name")
            print(f"    [{i+1}] {name} -> {status}")
            if status == "success":
                aliases = rd.get("aliases")
                print(f"    别名: {aliases}")
                break
            if status == "failure":
                print(f"    部署失败!")
                break

    # 验证可访问性
    print("\n  验证可访问性...")
    for test_url in [f"https://{deploy_url}", f"https://{project_name}.pages.dev"]:
        try:
            r = requests.get(test_url, timeout=15, allow_redirects=True)
            print(f"    {test_url} -> HTTP {r.status_code} ({len(r.content)} bytes)")
        except Exception as e:
            print(f"    {test_url} -> 错误: {e}")

    return {"project": project_name, "deploy_id": deploy_id, "url": deploy_url}


if __name__ == "__main__":
    base_dir = "C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20"
    results = []

    # 国内版 (先部署简单的，1个文件)
    r2 = deploy("hygzz-cn", f"{base_dir}/hygzz_cn_domestic")
    if r2:
        results.append(r2)

    # 国际版 (6个文件)
    r1 = deploy("hygzz-com", f"{base_dir}/hygzz_cn")
    if r1:
        results.append(r1)

    print(f"\n{'='*60}")
    print("部署汇总")
    print(f"{'='*60}")
    for r in results:
        print(f"\n项目: {r['project']}")
        print(f"  部署ID: {r['deploy_id']}")
        print(f"  地址: https://{r['url']}")
        print(f"  主域名: https://{r['project']}.pages.dev")
