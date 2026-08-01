# -*- coding: utf-8 -*-
"""在 ap-hongkong 建桶部署 hygzz.top（免备案）"""
import os, sys, json, mimetypes, hashlib, hmac, time
import urllib.request, urllib.error, urllib.parse
sys.path.insert(0, ".")
from tcb_api import SID, SKEY, tc3_call

BUCKET = "hygzztop-1352601878"
REGION = "ap-hongkong"
APPID = "1352601878"
SITE = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\hygzz-top-site"
WEB_ENDPOINT = "%s.cos-website.%s.myqcloud.com" % (BUCKET, REGION)

mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("text/javascript", ".js")

def cos_req(method, path, body=b"", params=None, extra_headers=None, bucket=BUCKET, region=REGION):
    params = params or {}
    host = "%s.cos.%s.myqcloud.com" % (bucket, region)
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

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    if cmd in ("all", "create"):
        code, body = cos_req("PUT", "/")
        print("CreateBucket:", code, body[:300])

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
                if ct.startswith("text/") or "javascript" in ct or "json" in ct:
                    ct += "; charset=utf-8"
                code, body = cos_req("PUT", "/" + key, data, None, {"Content-Type": ct, "Content-Length": str(len(data))})
                total += 1
                if code == 200:
                    ok += 1
                else:
                    fails.append((key, code, body[:150]))
        print("UPLOAD: %d/%d ok" % (ok, total))
        for f in fails[:8]:
            print("FAIL:", f)

    if cmd in ("all", "website"):
        ws = ('<?xml version="1.0" encoding="UTF-8"?><WebsiteConfiguration>'
              "<IndexDocument><Suffix>index.html</Suffix></IndexDocument>"
              "<ErrorDocument><Key>index.html</Key></ErrorDocument>"
              "</WebsiteConfiguration>").encode("utf-8")
        code, body = cos_req("PUT", "/", ws, {"website": ""}, {"Content-Type": "application/xml"})
        print("PutBucketWebsite:", code, body[:200])
        policy = {"Statement": [{"Principal": {"qcs": ["qcs::cam::anyone:anyone"]}, "Effect": "Allow",
                                 "Action": ["name/cos:GetObject", "name/cos:HeadObject", "name/cos:OptionsObject"],
                                 "Resource": ["qcs::cos:%s:uid/%s:%s/*" % (REGION, APPID, BUCKET)]}],
                  "Version": "2.0"}
        code, body = cos_req("PUT", "/", json.dumps(policy).encode(), {"policy": ""}, {"Content-Type": "application/json"})
        print("PutBucketPolicy:", code, body[:200])

    if cmd in ("all", "domain"):
        xml = ('<?xml version="1.0" encoding="UTF-8"?><DomainConfiguration>'
               "<DomainRule><Status>ENABLED</Status><Name>hygzz.top</Name><Type>WEBSITE</Type></DomainRule>"
               "<DomainRule><Status>ENABLED</Status><Name>www.hygzz.top</Name><Type>WEBSITE</Type></DomainRule>"
               "</DomainConfiguration>").encode("utf-8")
        code, body = cos_req("PUT", "/", xml, {"domain": ""}, {"Content-Type": "application/xml"})
        print("PutBucketDomain:", code, body[:500])

    if cmd in ("all", "dns"):
        r = tc3_call("dnspod", "DescribeRecordList", "2021-03-23", {"Domain": "hygzz.top"})
        for rec in r.get("Response", {}).get("RecordList", []):
            if rec.get("Type") == "CNAME":
                rr = tc3_call("dnspod", "ModifyRecord", "2021-03-23", {
                    "Domain": "hygzz.top", "RecordId": rec["RecordId"],
                    "SubDomain": rec["Name"], "RecordType": "CNAME",
                    "RecordLine": "默认", "Value": WEB_ENDPOINT + "."})
                print("ModifyRecord", rec["Name"], "->", json.dumps(rr.get("Response", {}), ensure_ascii=False)[:200])

if __name__ == "__main__":
    main()
