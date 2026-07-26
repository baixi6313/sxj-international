#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cloudflare Pages 部署 - Assets Upload 完整流程"""
import os, sys, json, hashlib, base64, mimetypes, time
import requests
from pathlib import Path

CF_TOKEN = os.environ.get("CF_TOKEN", "")
ACCT = os.environ.get("ACCT", "")
API = "https://api.cloudflare.com/client/v4"

if not CF_TOKEN or not ACCT:
    print("ERROR: 需要设置 CF_TOKEN 和 ACCT")
    sys.exit(1)

API_HEADERS = {"Authorization": f"Bearer {CF_TOKEN}"}


def get_upload_token(project_name):
    """获取 upload JWT token (有效期 300 秒)"""
    url = f"{API}/accounts/{ACCT}/pages/projects/{project_name}/upload-token"
    r = requests.get(url, headers=API_HEADERS, timeout=30)
    data = r.json()
    if data.get("success"):
        jwt = data["result"]["jwt"]
        print(f"  upload token 获取成功 (前20字符: {jwt[:20]}...)")
        return jwt
    print(f"  upload token 获取失败: {data.get('errors')}")
    return None


def upload_assets(jwt, file_map):
    """上传文件到 assets storage"""
    url = f"{API}/pages/assets/upload"
    headers = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}

    # 构造上传数组
    upload_items = []
    for h, (fname, content, mime) in file_map.items():
        upload_items.append({
            "key": h,
            "value": base64.b64encode(content).decode(),
            "metadata": {"contentType": mime},
            "base64": True
        })

    # 分批上传（每批最大 50MB）
    batch_size = 50 * 1024 * 1024  # 50MB
    current_batch = []
    current_size = 0
    uploaded = 0

    for item in upload_items:
        item_size = len(item["value"])
        if current_size + item_size > batch_size and current_batch:
            # 上传当前批次
            r = requests.post(url, headers=headers, json=current_batch, timeout=120)
            if r.ok:
                uploaded += len(current_batch)
                print(f"    批次上传: {len(current_batch)} 文件 (累计 {uploaded})")
            else:
                print(f"    批次上传失败: {r.status_code} {r.text[:200]}")
                return False
            current_batch = []
            current_size = 0
        current_batch.append(item)
        current_size += item_size

    # 上传最后一批
    if current_batch:
        r = requests.post(url, headers=headers, json=current_batch, timeout=120)
        if r.ok:
            uploaded += len(current_batch)
            print(f"    最后批次上传: {len(current_batch)} 文件 (累计 {uploaded})")
        else:
            print(f"    上传失败: {r.status_code} {r.text[:200]}")
            return False

    return True


def upsert_hashes(jwt, hashes):
    """通知 Cloudflare 新文件已上传"""
    url = f"{API}/pages/assets/upsert-hashes"
    headers = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json={"hashes": hashes}, timeout=30)
    if r.ok:
        print(f"  upsert hashes 成功 ({len(hashes)} 个)")
        return True
    print(f"  upsert hashes 失败: {r.status_code} {r.text[:200]}")
    return False


def create_deployment(project_name, manifest):
    """创建部署 (manifest only, 文件已通过 assets upload 上传)"""
    url = f"{API}/accounts/{ACCT}/pages/projects/{project_name}/deployments"
    # multipart/form-data, manifest 作为 form field
    files = {"manifest": (None, json.dumps(manifest), "application/json")}
    r = requests.post(url, headers=API_HEADERS, files=files, timeout=60)
    data = r.json()
    if data.get("success"):
        result = data["result"]
        print(f"  部署创建成功!")
        print(f"  部署ID: {result.get('id')}")
        print(f"  URL: {result.get('url')}")
        return result
    print(f"  部署创建失败: {data.get('errors')}")
    return None


def deploy(project_name, dir_path):
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

    # 计算 SHA256, 构造 manifest 和 file_map
    manifest = {}
    file_map = {}  # hash -> (filename, content, mime)
    for f in files_list:
        rel = str(f.relative_to(base)).replace("\\", "/")
        content = f.read_bytes()
        h = hashlib.sha256(content).hexdigest()
        manifest[rel] = h
        mime = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
        file_map[h] = (f.name, content, mime)

    total = len(files_list)
    total_size = sum(f.stat().st_size for f in files_list)
    print(f"  文件数: {total}, 总大小: {total_size/1024:.1f} KB")

    # 步骤1: 获取 upload token
    print("\n[1/4] 获取 upload token...")
    jwt = get_upload_token(project_name)
    if not jwt:
        return None

    # 步骤2: 上传文件
    print("[2/4] 上传文件到 assets storage...")
    if not upload_assets(jwt, file_map):
        return None

    # 步骤3: Upsert hashes
    print("[3/4] Upsert hashes...")
    if not upsert_hashes(jwt, list(file_map.keys())):
        return None

    # 步骤4: 创建部署
    print("[4/4] 创建部署...")
    result = create_deployment(project_name, manifest)
    if not result:
        return None

    deploy_url = result.get("url", "").replace("https://", "")
    deploy_id = result.get("id")

    # 等待部署完成
    print("\n  等待部署完成...")
    for i in range(6):
        time.sleep(5)
        r = requests.get(f"{API}/accounts/{ACCT}/pages/projects/{project_name}/deployments/{deploy_id}",
                         headers=API_HEADERS, timeout=30)
        if r.ok:
            rd = r.json().get("result", {})
            stage = rd.get("latest_stage", {})
            print(f"    [{i+1}] {stage.get('name')} -> {stage.get('status')}")
            if stage.get("status") == "success":
                break

    # 验证可访问性
    print("\n  验证可访问性...")
    test_urls = [f"https://{deploy_url}", f"https://{project_name}.pages.dev"]
    for test_url in test_urls:
        try:
            r = requests.get(test_url, timeout=15, allow_redirects=True)
            print(f"    {test_url} -> HTTP {r.status_code} ({len(r.content)} bytes)")
        except Exception as e:
            print(f"    {test_url} -> 错误: {e}")

    return {"project": project_name, "deploy_id": deploy_id, "url": deploy_url}


if __name__ == "__main__":
    base_dir = "C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20"
    results = []

    # 国内版 (1个文件)
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
