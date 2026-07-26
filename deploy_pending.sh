#!/usr/bin/env bash
# 用法: bash deploy_pending.sh <CF_API_TOKEN>
# Token 仅作命令行参数传入, 不写入本文件, 不落盘。
set -e
TOKEN="$1"
ACCT="f26b8425a338a0e385a391781198f360"
NODE="C:/Users/Administrator/.workbuddy/binaries/node/versions/22.22.2/node.exe"
WR="C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27/wrangler-tmp"
WS="C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20"
WS2="C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27"

if [ -z "$TOKEN" ]; then
  echo "ERROR: 请提供 Cloudflare API Token 作为第一个参数"
  exit 1
fi

export CLOUDFLARE_API_TOKEN="$TOKEN"
export CLOUDFLARE_ACCOUNT_ID="$ACCT"

cd "$WR"
# 清缓存避免权限错误
rm -rf node_modules/.cache/wrangler

echo "=== [1/3] 国内版 hygzz-cn (已含共通值替换) ==="
"$NODE" node_modules/wrangler/bin/wrangler.js pages deploy "$WS/hygzz_cn_domestic" --project-name=hygzz-cn

echo "=== [2/3] H5 sxj-mini (已含共通值替换) ==="
"$NODE" node_modules/wrangler/bin/wrangler.js pages deploy "$WS2/sxj-mini/h5" --project-name=sxj-mini

echo "=== [3/3] 白皮书 sxj-whitepaper (新建项目) ==="
mkdir -p "$WS2/whitepaper-dist"
cp "$WS2/whitepaper.html" "$WS2/whitepaper-dist/index.html"
"$NODE" node_modules/wrangler/bin/wrangler.js pages deploy "$WS2/whitepaper-dist" --project-name=sxj-whitepaper

# ---- 可选/需额外权限 ----
# 国际版 hygzz-com 已是最新(无中文"地板"词), 如需重部署取消下一行注释:
# "$NODE" node_modules/wrangler/bin/wrangler.js pages deploy "$WS/hygzz_cn" --project-name=hygzz-com

# #85 绑定 app.hygzz.cn 到 sxj-mini —— 需 Zone:DNS:Edit 权限, 建议改用 Cloudflare 后台操作:
#   Pages 项目 sxj-mini → Custom domains → 输入 app.hygzz.cn → 按提示加 CNAME 记录

echo "=== 全部部署完成 ==="
echo "国内版:  https://hygzz-cn.pages.dev"
echo "H5:      https://sxj-mini.pages.dev"
echo "白皮书:  https://sxj-whitepaper.pages.dev"
