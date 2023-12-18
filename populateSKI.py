#!/usr/bin/env python3
# from:
#   - https://www.pyopenssl.org/en/stable/index.html
# open the ca file, process each cert, write to ski_dir/<subject pub key identifier>
# If the SKI does not exist, serialize the Subject DN (change / to +++, () and / within text changed to |) and write that

import re
from OpenSSL import crypto
import certifi
from cryptography.hazmat.primitives.serialization import Encoding
import os

THISFILE=os.path.abspath(__file__)
CWD=os.path.dirname(THISFILE)

ski_dir=f"{CWD}/subjectKeyIdentifier"
cafile=certifi.where()
if not os.path.exists(ski_dir):
    os.mkdir(ski_dir, 0o755)

def serialized_dn(tuple_list):
    """Serialize a list of tuples into a string
    separate components by +++ instead of /
    replace instances of / in a component with |
    """
    return "+++".join([f"{x[0].decode('UTF-8')}={x[1].decode('UTF-8')}" for x in tuple_list]).replace('/','|')

def get_ca_certs(cafile):
    """Open cacerts file and parse it, returning a list of just the PEM certs"""
    with open(cafile, "r", encoding="utf8") as f:
        contents = f.read()
    f.close()

    regex = re.compile(r'(-----BEGIN CERTIFICATE-----[^-]+-----END CERTIFICATE-----)', re.DOTALL)
    return regex.findall(contents)


for cert_pem in get_ca_certs(cafile):
    print(cert_pem)
    cert = crypto.load_certificate(type = crypto.FILETYPE_PEM, buffer = cert_pem)
    ski=None
    for i in range(0,cert.get_extension_count()-1):
        try:
            ext=cert.get_extension(i)
            name = ext.get_short_name().decode('UTF-8')
            if name == "subjectKeyIdentifier":
                ski = str(ext)
            # print(f"  {ext.get_short_name().decode('UTF-8')}: {ext}")
        except:
            pass
    
    if ski:
        file = f"{ski_dir}/{ski}"
    else:
        file = f"{ski_dir}/{serialized_dn(cert.get_subject().get_components())}"
    with open(file, "w", encoding="utf8") as f:
        f.write(cert_pem)
        f.close()
    print(file)
    
