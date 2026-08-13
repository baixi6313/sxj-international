# -*- coding: utf-8 -*-
"""绑定 hygzz.中国 自定义域名到 COS 桶（修正：补齐 Content-Length 头，否则 COS 验签失败）"""
import sys, json, hashlib, hmac, time, urllib.request, urllib.error, urllib.parse
sys.path.insert(0, ".")
from tcb_api import SID, SKEY, tc3_call

BUCKET = "hygzzcn-1352601878"
REGION = "ap-hongkong"
WEB_ENDPOINT = "%s.cos-website.%s.myqcloud.com" % (BUCKET, REGION)
DOMAIN = "hygzz.中国"
# COS PUT /?domain 要求 IDN 用 punycode（ACE）形式，否则报 DomainRule Name is invalid
NAME = DOMAIN.encode("idna").decode("ascii")   # hygzz.中国 -> hygzz.xn--fiqs8s

def cos_req(method, path, body=b"", params=None, extra_headers=None):
    params = params or {}
    host = "%s.cos.%s.myqcloud.com" % (BUCKET, REGION)
    start = int(time.time()) - 60
    end = start + 600
    key_time = "%d;%d" % (start, end)
    sign_key = hmac.new(SKEY.encode(), key_time.encode(), hashlib.sha1).hexdigest()
    headers = {"Host": host}
    if body:
        headers["Content-Length"] = str(len(body))   # 关键修复：签名必须包含实际发送的所有头
    if extra_headers:
        headers.update(extra_headers)
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
    req = urllib.request.Request(url, data=body if body else None, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return "ERR", str(e)

xml_body = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<DomainConfiguration>'
            '<DomainRule><Status>ENABLED</Status><Name>%s</Name><Type>WEBSITE</Type></DomainRule>'
            '</DomainConfiguration>') % NAME
code, body = cos_req("PUT", "/", xml_body.encode("utf-8"), {"domain": ""}, {"Content-Type": "application/xml"})
print("[1] BindDomain %s -> %s | %s" % (DOMAIN, code, body[:300]))

if code in (200, 204):
    print("\n✅ 桶已认领域名 hygzz.中国。等 DNS 生效（1-5 分钟），访问 https://%s/ 即可。" % DOMAIN)
else:
    print("\n⚠️ 绑定仍失败，可能需要改 NS 或控制台手动加自定义源站域名。")
