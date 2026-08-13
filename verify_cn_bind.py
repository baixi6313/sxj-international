# -*- coding: utf-8 -*-
"""验证 .中国 自定义域名绑定结果：桶内域名配置 + DNSPod 记录 + 直连尝试。"""
import sys, json, hashlib, hmac, time, urllib.request, urllib.error, urllib.parse, socket
sys.path.insert(0, ".")
from tcb_api import SID, SKEY, tc3_call

BUCKET = "hygzzcn-1352601878"
REGION = "ap-hongkong"
DOMAIN = "hygzz.中国"
NAME = DOMAIN.encode("idna").decode("ascii")

def cos_req(method, path, params=None):
    params = params or {}
    host = "%s.cos.%s.myqcloud.com" % (BUCKET, REGION)
    start = int(time.time()) - 60; end = start + 600
    key_time = "%d;%d" % (start, end)
    sign_key = hmac.new(SKEY.encode(), key_time.encode(), hashlib.sha1).hexdigest()
    headers = {"Host": host}
    hdr_keys = ";".join(sorted(k.lower() for k in headers))
    hdr_str = "&".join("%s=%s" % (k.lower(), urllib.parse.quote(str(headers[k]), safe="")) for k in sorted(headers, key=lambda x: x.lower()))
    prm_keys = ";".join(sorted(k.lower() for k in params))
    prm_str = "&".join("%s=%s" % (k.lower(), urllib.parse.quote(str(params[k]), safe="")) for k in sorted(params, key=lambda x: x.lower()))
    http_string = "%s\n%s\n%s\n%s\n" % (method.lower(), path, prm_str, hdr_str)
    string_to_sign = "sha1\n%s\n%s\n" % (key_time, hashlib.sha1(http_string.encode()).hexdigest())
    signature = hmac.new(sign_key.encode(), string_to_sign.encode(), hashlib.sha1).hexdigest()
    auth = ("q-sign-algorithm=sha1&q-ak=%s&q-sign-time=%s&q-key-time=%s&q-header-list=%s&q-url-param-list=%s&q-signature=%s"
            % (SID, key_time, key_time, hdr_keys, prm_keys, signature))
    headers["Authorization"] = auth
    qs = ("?" + "&".join(("%s=%s" % (k, urllib.parse.quote(str(v), safe="")) if v != "" else k) for k, v in params.items())) if params else ""
    url = "https://" + host + urllib.parse.quote(path) + qs
    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return "ERR", str(e)

print("== 1) 桶内自定义域名配置 (GET /?domain) ==")
code, body = cos_req("GET", "/", {"domain": ""})
print(code)
print(body[:600])

print("\n== 2) DNSPod 记录 (hygzz.中国) ==")
r = tc3_call("dnspod", "DescribeRecordList", "2021-03-23", {"Domain": DOMAIN})
recs = r.get("Response", {}).get("RecordList", [])
if not recs:
    print("（无记录或接口报错）", json.dumps(r.get("Response", {}), ensure_ascii=False)[:300])
for rec in recs:
    print(" -", rec.get("Name"), rec.get("Type"), "->", rec.get("Value"), "| RecordId", rec.get("RecordId"))

print("\n== 3) 直连 http://%s/ (DNS 解析 + COS 响应，best-effort) ==" % DOMAIN)
try:
    ip = socket.gethostbyname(NAME)
    print("DNS 解析 %s -> %s" % (NAME, ip))
except Exception as e:
    print("DNS 解析失败:", e)
try:
    req = urllib.request.Request("http://%s/" % DOMAIN, method="GET")
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read(200).decode("utf-8", "replace")
        print("HTTP %d 预览:%s" % (r.status, data[:120].replace("\n", " ")))
except Exception as e:
    print("直连失败（可能 DNS 未生效/或需等几分钟）:", e)
