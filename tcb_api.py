# -*- coding: utf-8 -*-
"""腾讯云 API 工具：TC3 签名调用 (tcb/dnspod/ssl) + COS 对象上传。
密钥从环境变量 TENCENT_SECRET_ID / TENCENT_SECRET_KEY 读取，不落盘。
"""
import hashlib, hmac, json, os, sys, time, datetime, mimetypes
import urllib.request, urllib.error, urllib.parse

SID = os.environ.get("TENCENT_SECRET_ID", "")
SKEY = os.environ.get("TENCENT_SECRET_KEY", "")

def _sha256hex(b):
    return hashlib.sha256(b).hexdigest()

def _hmac256(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def tc3_call(service, action, version, payload, region=""):
    host = service + ".tencentcloudapi.com"
    endpoint = "https://" + host
    algorithm = "TC3-HMAC-SHA256"
    ts = int(time.time())
    date = datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
    body = json.dumps(payload)
    canonical_headers = "content-type:application/json; charset=utf-8\nhost:%s\nx-tc-action:%s\n" % (host, action.lower())
    signed_headers = "content-type;host;x-tc-action"
    canonical_request = "POST\n/\n\n%s\n%s\n%s" % (canonical_headers, signed_headers, _sha256hex(body.encode("utf-8")))
    credential_scope = "%s/%s/tc3_request" % (date, service)
    string_to_sign = "%s\n%d\n%s\n%s" % (algorithm, ts, credential_scope, _sha256hex(canonical_request.encode("utf-8")))
    secret_date = _hmac256(("TC3" + SKEY).encode("utf-8"), date)
    secret_service = _hmac256(secret_date, service)
    secret_signing = _hmac256(secret_service, "tc3_request")
    signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    authorization = "%s Credential=%s/%s, SignedHeaders=%s, Signature=%s" % (algorithm, SID, credential_scope, signed_headers, signature)
    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json; charset=utf-8",
        "Host": host,
        "X-TC-Action": action,
        "X-TC-Timestamp": str(ts),
        "X-TC-Version": version,
    }
    if region:
        headers["X-TC-Region"] = region
    req = urllib.request.Request(endpoint, data=body.encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"HTTPError": e.code, "body": e.read().decode("utf-8", "replace")}
    except Exception as e:
        return {"Error": str(e)}

# ---------------- COS ----------------
def _cos_sign(method, path, headers, params, expire=600):
    start = int(time.time()) - 60
    end = start + expire
    key_time = "%d;%d" % (start, end)
    sign_key = hmac.new(SKEY.encode(), key_time.encode(), hashlib.sha1).hexdigest()
    hdr_keys = ";".join(sorted(k.lower() for k in headers))
    hdr_str = "&".join("%s=%s" % (k.lower(), urllib.parse.quote(str(headers[k]), safe="")) for k in sorted(headers, key=lambda x: x.lower()))
    prm_keys = ";".join(sorted(k.lower() for k in params))
    prm_str = "&".join("%s=%s" % (k.lower(), urllib.parse.quote(str(params[k]), safe="")) for k in sorted(params, key=lambda x: x.lower()))
    http_string = "%s\n%s\n%s\n%s\n" % (method.lower(), path, prm_str, hdr_str)
    string_to_sign = "sha1\n%s\n%s\n" % (key_time, hashlib.sha1(http_string.encode()).hexdigest())
    signature = hmac.new(sign_key.encode(), string_to_sign.encode(), hashlib.sha1).hexdigest()
    return ("q-sign-algorithm=sha1&q-ak=%s&q-sign-time=%s&q-key-time=%s&q-header-list=%s&q-url-param-list=%s&q-signature=%s"
            % (SID, key_time, key_time, hdr_keys, prm_keys, signature))

def cos_put(bucket, region, key, data, content_type):
    host = "%s.cos.%s.myqcloud.com" % (bucket, region)
    path = "/" + urllib.parse.quote(key)
    headers = {"Host": host, "Content-Type": content_type, "Content-Length": str(len(data))}
    auth = _cos_sign("put", "/" + key, headers, {})
    headers["Authorization"] = auth
    req = urllib.request.Request("https://" + host + path, data=data, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return "%d %s" % (e.code, e.read().decode("utf-8", "replace")[:300])
    except Exception as e:
        return "ERR " + str(e)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "envs"
    if cmd == "envs":
        for rg in ["ap-shanghai", "ap-guangzhou", "ap-beijing"]:
            r = tc3_call("tcb", "DescribeEnvs", "2018-06-08", {}, rg)
            resp = r.get("Response", {})
            envs = resp.get("EnvList", [])
            if envs:
                print("REGION:", rg)
                for e in envs:
                    print(json.dumps({
                        "EnvId": e.get("EnvId"), "Alias": e.get("Alias"),
                        "Status": e.get("Status"), "Region": e.get("Region"),
                        "StaticStorages": e.get("StaticStorages"),
                        "Storages": e.get("Storages"),
                    }, ensure_ascii=False, indent=1))
                break
            else:
                print(rg, "->", json.dumps(r, ensure_ascii=False)[:400])
