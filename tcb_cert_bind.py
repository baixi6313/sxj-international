# -*- coding: utf-8 -*-
"""把已签发证书绑定到 COS 自定义域名"""
import sys, json
sys.path.insert(0, ".")
from tcb_api import tc3_call
from tcb_hk import cos_req
from xml.sax.saxutils import escape

CERT_ID = sys.argv[1] if len(sys.argv) > 1 else "ZcE2faYu"
DOMAIN = sys.argv[2] if len(sys.argv) > 2 else "hygzz.top"

r = tc3_call("ssl", "DescribeCertificateDetail", "2019-12-05", {"CertificateId": CERT_ID})
resp = r.get("Response", {})
pub = resp.get("CertificatePublicKey", "")
prv = resp.get("CertificatePrivateKey", "")
if not pub or not prv:
    print("证书内容未取到:", resp.get("Status"), resp.get("StatusName"))
    sys.exit(1)

xml = ('<?xml version="1.0" encoding="UTF-8"?>'
       "<DomainCertificate><CertificateInfo><CertType>CustomCert</CertType>"
       "<CustomCert><Cert>%s</Cert><PrivateKey>%s</PrivateKey></CustomCert>"
       "</CertificateInfo><DomainList><DomainName>%s</DomainName></DomainList>"
       "</DomainCertificate>" % (escape(pub), escape(prv), DOMAIN)).encode("utf-8")
code, body = cos_req("PUT", "/", xml, {"domaincertificate": ""}, {"Content-Type": "application/xml"})
print("PutDomainCert(%s): %s %s" % (DOMAIN, code, body[:300]))
