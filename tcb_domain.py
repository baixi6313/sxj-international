# -*- coding: utf-8 -*-
"""hygzz.top 绑定：DNSPod 解析 + COS 自定义域名"""
import sys, json
sys.path.insert(0, ".")
from tcb_api import tc3_call
from tcb_upload import cos_req

TARGET = "hygzz-1352601878.cos-website.ap-guangzhou.myqcloud.com."
cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

if cmd in ("all", "dns"):
    # 已有记录
    r = tc3_call("dnspod", "DescribeRecordList", "2021-03-23", {"Domain": "hygzz.top"})
    recs = r.get("Response", {}).get("RecordList", [])
    print("=== 现有记录 ===")
    for rec in recs:
        print(rec.get("RecordId"), rec.get("Name"), rec.get("Type"), rec.get("Value"), rec.get("Status"))
    existing = {(rec.get("Name"), rec.get("Type")) for rec in recs}
    for name in ("@", "www"):
        if (name, "CNAME") in existing:
            print(name, "CNAME 已存在，跳过")
            continue
        r = tc3_call("dnspod", "CreateRecord", "2021-03-23", {
            "Domain": "hygzz.top", "SubDomain": name, "RecordType": "CNAME",
            "RecordLine": "默认", "Value": TARGET})
        print("CreateRecord", name, "->", json.dumps(r.get("Response", {}), ensure_ascii=False)[:300])

if cmd in ("all", "cosdomain"):
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           "<DomainConfiguration>"
           "<DomainRule><Status>ENABLED</Status><Name>hygzz.top</Name><Type>WEBSITE</Type></DomainRule>"
           "<DomainRule><Status>ENABLED</Status><Name>www.hygzz.top</Name><Type>WEBSITE</Type></DomainRule>"
           "</DomainConfiguration>").encode("utf-8")
    code, body = cos_req("PUT", "/", xml, {"domain": ""}, {"Content-Type": "application/xml"})
    print("PutBucketDomain:", code, body[:600])
