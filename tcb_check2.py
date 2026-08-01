# -*- coding: utf-8 -*-
import json, sys
sys.path.insert(0, ".")
from tcb_api import tc3_call, SID, SKEY
import hashlib, hmac, time, urllib.request, urllib.error, urllib.parse

# 1) DNSPod 域名列表
r = tc3_call("dnspod", "DescribeDomainList", "2021-03-23", {})
resp = r.get("Response", {})
doms = resp.get("DomainList", [])
print("=== DNSPod 域名 ===")
if doms:
    for d in doms:
        print(d.get("Name"), "| status:", d.get("Status"), "| DNS:", d.get("DNSStatus", ""), "| grade:", d.get("Grade"))
else:
    print(json.dumps(r, ensure_ascii=False)[:500])

# 2) COS GetService (列出桶, 验证COS开通)
def cos_get_service():
    host = "service.cos.myqcloud.com"
    start = int(time.time()) - 60
    end = start + 600
    key_time = "%d;%d" % (start, end)
    sign_key = hmac.new(SKEY.encode(), key_time.encode(), hashlib.sha1).hexdigest()
    http_string = "get\n/\n\nhost=%s\n" % host
    string_to_sign = "sha1\n%s\n%s\n" % (key_time, hashlib.sha1(http_string.encode()).hexdigest())
    signature = hmac.new(sign_key.encode(), string_to_sign.encode(), hashlib.sha1).hexdigest()
    auth = ("q-sign-algorithm=sha1&q-ak=%s&q-sign-time=%s&q-key-time=%s&q-header-list=host&q-url-param-list=&q-signature=%s"
            % (SID, key_time, key_time, signature))
    req = urllib.request.Request("https://" + host + "/", headers={"Host": host, "Authorization": auth})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return "ERR", str(e)

print("=== COS GetService ===")
code, body = cos_get_service()
print("HTTP", code)
print(body[:1500])
