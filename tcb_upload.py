# -*- coding: utf-8 -*-
"""上传 hygzz-top-site 到 COS 桶并开启静态网站托管 + 公共读"""
import os, sys, json, mimetypes, hashlib, hmac, time
import urllib.request, urllib.error, urllib.parse
sys.path.insert(0, ".")
from tcb_api import cos_put, SID, SKEY

BUCKET = "hygzz-1352601878"
REGION = "ap-guangzhou"
SITE = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\hygzz-top-site"

mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("text/javascript", ".js")

def cos_req(method, path, body=b"", params=None, extra_headers=None):
    params = params or {}
    host = "%s.cos.%s.myqcloud.com" % (BUCKET, REGION)
    start = int(time.time()) - 60
    end = start + 600
    key_time = "%d;%d" % (start, end)
    sign_key = hmac.new(SKEY.encode(), key_time.encode(), hashlib.sha1).hexdigest()
    headers = {"Host": host}
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
    qs = ("?" + "&".join("%s=%s" % (k, urllib.parse.quote(str(v), safe="")) if v != "" else k for k, v in params.items())) if params else ""
    url = "https://" + host + path + qs
    req = urllib.request.Request(url, data=body if body else None, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return "ERR", str(e)

cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

if cmd in ("all", "upload"):
    total, ok, fails = 0, 0, []
    for dp, _, fns in os.walk(SITE):
        for fn in fns:
            p = os.path.join(dp, fn)
            key = os.path.relpath(p, SITE).replace("\\", "/")
            if key == "CNAME":
                continue
            with open(p, "rb") as f:
                data = f.read()
            ct = mimetypes.guess_type(fn)[0] or "application/octet-stream"
            if ct.startswith("text/") or ct in ("application/javascript", "text/javascript", "application/json", "application/manifest+json"):
                ct += "; charset=utf-8"
            st = cos_put(BUCKET, REGION, key, data, ct)
            total += 1
            if st == 200:
                ok += 1
            else:
                fails.append((key, st))
    print("UPLOAD: %d/%d ok" % (ok, total))
    for k, s in fails[:10]:
        print("FAIL:", k, s)

if cmd in ("all", "website"):
    ws = ('<?xml version="1.0" encoding="UTF-8"?>'
          "<WebsiteConfiguration>"
          "<IndexDocument><Suffix>index.html</Suffix></IndexDocument>"
          "<ErrorDocument><Key>index.html</Key></ErrorDocument>"
          "</WebsiteConfiguration>").encode("utf-8")
    code, body = cos_req("PUT", "/", ws, {"website": ""}, {"Content-Type": "application/xml"})
    print("PutBucketWebsite:", code, body[:200])

if cmd in ("all", "acl"):
    policy = {
        "Statement": [{
            "Principal": {"qcs": ["qcs::cam::anyone:anyone"]},
            "Effect": "Allow",
            "Action": ["name/cos:GetObject", "name/cos:HeadObject", "name/cos:OptionsObject"],
            "Resource": ["qcs::cos:%s:uid/1352601878:%s/*" % (REGION, BUCKET)],
        }],
        "Version": "2.0",
    }
    body = json.dumps(policy).encode("utf-8")
    code, resp = cos_req("PUT", "/", body, {"policy": ""}, {"Content-Type": "application/json"})
    print("PutBucketPolicy:", code, resp[:200])
