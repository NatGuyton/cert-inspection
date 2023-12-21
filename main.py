#!/usr/bin/env python3

import os
import sys
import datetime
import argparse
import certifi
import socket
import json
from OpenSSL import crypto  # https://www.pyopenssl.org/en/stable/api/crypto.html
from OpenSSL import SSL     # https://www.pyopenssl.org/en/stable/api/ssl.html

# from https://www.openssl.org/docs/man1.0.2/man1/verify.html since there does not seem to be a way to query for the code
VALIDATE_ERROR = {
    0: "ok",
    2: "unable to get issuer certificate",
    3: "unable to get certificate CRL",
    4: "unable to decrypt certificate's signature",
    5: "unable to decrypt CRL's signature",
    6: "unable to decode issuer public key",
    7: "certificate signature failure",
    8: "CRL signature failure",
    9: "certificate is not yet valid",
    10: "certificate has expired",
    11: "CRL is not yet valid",
    12: "CRL has expired",
    13: "format error in certificate's notBefore field",
    14: "format error in certificate's notAfter field",
    15: "format error in CRL's lastUpdate field",
    16: "format error in CRL's nextUpdate field",
    17: "out of memory",
    18: "self signed certificate",
    19: "self signed certificate in certificate chain",
    20: "unable to get local issuer certificate",
    21: "unable to verify the first certificate",
    22: "certificate chain too long",
    23: "certificate revoked",
    24: "invalid CA certificate",
    25: "path length constraint exceeded",
    26: "unsupported certificate purpose",
    27: "certificate not trusted",
    28: "certificate rejected",
    29: "subject issuer mismatch",
    30: "authority and subject key identifier mismatch",
    31: "authority and issuer serial number mismatch",
    32: "key usage does not include certificate signing"
}

FILE=os.path.abspath(__file__)
TRUSTED_CERT_DIR=f"{os.path.dirname(FILE)}/subjectKeyIdentifier"
if not os.path.exists(TRUSTED_CERT_DIR):
    raise SystemExit(f"Cannot find trusted cert dir {TRUSTED_CERT_DIR} - you need to run populateSKI.py first.")

# hold the cert validation results, indexed by depth
verified={}

def get_date_from_asn1(asn1_timestamp):
    # https://docs.python.org/3/library/datetime.html
    return f"{datetime.datetime.strptime(asn1_timestamp, '%Y%m%d%H%M%S%fZ').ctime()} GMT"

def x509_dn(x509obj_component_tuples):
    """x509_dn
    The crypto lib get_subject().get_components() and get_issuer().get_components()
    returns a list of tuples that need to be put together to form the DN string
    """
    result=""
    for x, y in x509obj_component_tuples:
        result=f"{result}/{x.decode('UTF-8')}={y.decode('UTF-8')}"
    return result

def serialized_dn(tuple_list):
    """Serialize a list of tuples into a string
    Similar to the x509_dn function, but suitable for use as a filename
    separate components by +++ instead of /
    replace instances of / in a component with |
    """
    return "+++".join([f"{x[0].decode('UTF-8')}={x[1].decode('UTF-8')}" for x in tuple_list]).replace('/','|')

def verify(conn, x509, errnum, depth, returncode):
    """The callback function for OpenSSL.SSL.Context.verify()
    Always exit with True so that the caller can continue with the connection.
    This is a callback function so that we can keep track of the verification
    results.
    """
    if depth not in verified:
        # verified[depth]=f"verify:depth:{depth} {x509_dn(x509.get_subject().get_components())} - {errnum}: {VALIDATE_ERROR[errnum]}"
        verified[depth]=f"verify:depth:{depth} - {errnum}: {VALIDATE_ERROR[errnum]}"
    elif errnum:
        verified[depth]=f"{verified[depth]} - {errnum}: {VALIDATE_ERROR[errnum]}"
    return True

def get_cert_details(cert):
    this_cert = {}

    # cert is an crypto.X509 object (https://www.pyopenssl.org/en/stable/api/crypto.html)
    this_cert['subject'] = x509_dn(cert.get_subject().get_components())
    this_cert['serialized_subject'] = serialized_dn(cert.get_subject().get_components())
    this_cert['issuer'] = x509_dn(cert.get_issuer().get_components())
    this_cert['notBefore'] = get_date_from_asn1(cert.get_notBefore().decode('UTF-8'))  # ASN.1 TIME: YYYYMMDDhhmmssZ
    this_cert['notAfter'] = get_date_from_asn1(cert.get_notAfter().decode('UTF-8'))    # ASN.1 TIME: YYYYMMDDhhmmssZ
    this_cert['expired'] = cert.has_expired()
    this_cert['SHA-1 fingerprint'] = cert.digest("sha1").decode("UTF-8")
    this_cert['serialnumber'] = cert.get_serial_number()
    this_cert['version'] = cert.get_version()
    this_cert['signature_algorithm'] = cert.get_signature_algorithm().decode("UTF-8")
    for i in range(0,cert.get_extension_count()-1):
        try:
            ext=cert.get_extension(i)
            this_cert[ext.get_short_name().decode('UTF-8')] = str(ext)
        except:
            pass
    ## the PEM cert itself
    this_cert['cert'] = crypto.dump_certificate(type=crypto.FILETYPE_PEM, cert=cert).decode('UTF-8')

    return this_cert

def process(hostname: str, port: int = 443, servername: str = None):
    """Process a target"""
    results = {'certs': {}}

    cafile=certifi.where()
    results['cafile'] = cafile

    # Create a context
    # https://www.pyopenssl.org/en/stable/api/ssl.html
    context = SSL.Context(method=SSL.TLS_METHOD)
    context.load_verify_locations(cafile=cafile)
    context.set_verify(SSL.VERIFY_PEER, callback=verify) # Default VERIFY_NONE
    context.set_verify_depth(10)
    context.set_timeout(10)

    # Establish the connection
    conn = SSL.Connection(
        context, socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    )
    try:
        conn.connect((hostname, port))
    except socket.gaierror:
        raise ValueError(f"Cannot resolve hostname {hostname}")
    conn.setblocking(1)
    if servername:
        conn.set_tlsext_host_name(servername.encode()) # SNI; needs to be before handshake step
    conn.do_handshake()
    results['connection'] = {
        'hostname': hostname,
        'port': port,
        'servername': servername,
        'cipher': conn.get_cipher_name(),
        'protocol': conn.get_cipher_version(),
        'bits': conn.get_cipher_bits()
    }

    # Get cert details
    trusted=False
    last_issuer_dn=[]
    last_issuer_SKID=None
    last_idx=0

    for (idx, cert) in enumerate(conn.get_peer_cert_chain()):
        last_issuer_dn=[]
        last_issuer_SKID=None
        last_idx=idx

        this_cert = get_cert_details(cert)
        try:
            this_cert["validation"] = verified[idx]
        except KeyError:
            pass # No validation for the trusted root ca on disk
        this_cert['fromServer'] = True
        this_cert['trusted'] = False

        # See if it is in the CA trust store, either by SKID or DN
        # this_cert['trusted'] = False 
        if "subjectKeyIdentifier" in this_cert:
            if os.path.exists(f"{TRUSTED_CERT_DIR}/{this_cert['subjectKeyIdentifier']}"):
                this_cert['trusted'] = True
                trusted = True
        else:
            if os.path.exists(f"{TRUSTED_CERT_DIR}/{this_cert['serialized_subject']}"):
                this_cert['trusted'] = True
                trusted = True

        if "authorityKeyIdentifier" in this_cert:
            if "keyid:" in this_cert['authorityKeyIdentifier']:  # handle old syntax
                this_cert['authorityKeyIdentifier'] = this_cert['authorityKeyIdentifier'][6:].split("\n")[0]
            last_issuer_SKID = this_cert['authorityKeyIdentifier']
        last_issuer_dn = cert.get_issuer().get_components()

        results['certs'][idx] = this_cert

    conn.shutdown()
    conn.close()

    # See if need to get Trusted CA from local trust store
    if not trusted:
        # Cert not trusted, but look in trust store
        rootcafile=None
        if os.path.exists(f"{TRUSTED_CERT_DIR}/{last_issuer_SKID}"):
            rootcafile = f"{TRUSTED_CERT_DIR}/{last_issuer_SKID}"
        elif os.path.exists(f"{TRUSTED_CERT_DIR}/{serialized_dn(last_issuer_dn)}"):
            rootcafile = f"{TRUSTED_CERT_DIR}/{serialized_dn(last_issuer_dn)}"

        if rootcafile:
            # load this as the trusted root
            with open(rootcafile, "r", encoding="utf8") as f:
                trusted_cert_pem = f.read()
                f.close()
            cert = crypto.load_certificate(type = crypto.FILETYPE_PEM, buffer = trusted_cert_pem)
            this_cert = get_cert_details(cert)  
            if "authorityKeyIdentifier" in this_cert:
                if "keyid:" in this_cert['authorityKeyIdentifier']:  # handle old syntax
                    this_cert['authorityKeyIdentifier'] = this_cert['authorityKeyIdentifier'][6:].split("\n")[0]
            this_cert["trusted"] = True
            this_cert['fromServer'] = False
            if 'validation' not in this_cert:
                this_cert['validation'] = ""
            results['certs'][last_idx + 1] = this_cert

    return(results)


def get_host_port_from_input(input: str):
    """Get the hostname and port from the input
    Input could be a url with hostname[:port] or just a hostname[:port]
    """
    if input.startswith('https://'):
        input = input[8:]
    if input.startswith('http://'):
        input = input[7:]

    # If "/" exists in input variable, remove it and anything after it
    if input.find('/') > 0:
        input = input[:input.find('/')]    

    if ':' in input:
        hostname, port = input.split(':')
        port = int(port)
    else:
        hostname = input
        port = 443
    return hostname, port

def lambda_handler(event, context):
    """lambda interface"""
    pretty=False
    host = None
    results = "nope"
    include_event = False

    if event:
        if "queryStringParameters" in event:
            if "host" in event["queryStringParameters"]:
                host = event["queryStringParameters"]['host']
            
                hostname, port = get_host_port_from_input(host)
                if "servername" in event["queryStringParameters"]:
                    servername=event["queryStringParameters"]["servername"]
                else:
                    servername=hostname
                
                if "pretty" in event["queryStringParameters"]:
                    pretty=True
                if "include_event" in event["queryStringParameters"]:
                    include_event=True

                # # Clear any global vars
                verified={}
                # print(f"processing {hostname} {port} {servername}")
            
                try:
                    results = process(hostname, port, servername)
                except Exception as exc:
                    results = {"error": str(exc)}
            else:
                results = "No query parameter 'host' given"
        else: 
            results = "No query parameters given"
    else:
        event = "No event given"

    headers = {'content-type': 'application/json'}
    # Ref: https://repost.aws/knowledge-center/malformed-502-api-gateway

    # jsonify and perhaps include event input, prettify output
    body = {
        'results': results
    }
    if include_event:
        body['event'] = event
    if pretty:
        body = json.dumps(body, indent=4)
    else:
        body = json.dumps(body)

    return { 
        'statusCode': 200,
        'isBase64Encoded': 'false',
        'headers': headers,
        'body': body
    }


def ifprint(key, dictionary, padding="  ", label=None):
    if key in dictionary:
        if not label:
            label = key
        print(f"{padding}{label}: {dictionary[key]}")

def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(description='cert-inspection inputs')
    parser.add_argument('-s','--servername', help='Server name if SNI is needed', default=None)
    parser.add_argument('-j','--json', help='Print json output', action='store_true', default=False)
    parser.add_argument('-c','--cert', help='Print out cert if formatted text output (included in json by default, omitted in formatted text output by default)', action='store_true', default=False)
    args, other_input = parser.parse_known_args()

    # Get the main input (hostname, hostname:port, url with those)
    if len(other_input) < 1:
        raise SystemExit(f"""
cert-inspection

    Query a website and display the certificates it presents, performing some validation as well.

SYNTAX VARIANTS:
    {sys.argv[0]} [-j|--json] [-c|--cert] [-s <servername>] hostname
    {sys.argv[0]} [-j|--json] [-c|--cert] [-s <servername>] hostname:port
    {sys.argv[0]} [-j|--json] [-c|--cert] [-s <servername>] url

  General use is to just give a hostname or URL.  Port 443 is assumed if not specified, and
  these will be picked out of a URL if a URL is supplied.
    {sys.argv[0]} my.hostname.com
    {sys.argv[0]} https://my.hostname.com:8443/

  The optional component -s <servername> is only needed if SNI is needed to indicate a specific
  hostname that is different from the main target.  For example, if you need to check a specific
  endpoint by IP address for the certificate matching a hostname, you would use syntax:
    {sys.argv[0]} -s <servername> <IP address>

  The -j switch signals json rather than formatted text output, usually used in lambda.

  The -c switch signals that the cert should be printed out in the formatted text output.  It is
  normally omitted for a cleaner report.  The json output always includes it.
""")

    hostname, port = get_host_port_from_input(other_input[0])
    servername = hostname
    if args.servername:
        servername = args.servername

    results = process(hostname, port, servername)

    if args.json:
        print(json.dumps(results, indent=4))
    else:
        # Give the formatted text output
        if hostname != servername:
            print(f"cert-inspection: {servername} on {hostname}:{port}\n")
        else:
            print(f"cert-inspection: {hostname}:{port}\n")
        print(f"connection: {results['connection']['protocol']} {results['connection']['bits']} bits using {results['connection']['cipher']}")
        print(f"CA Trust File: {results['cafile']}")

        for depth, cert in results['certs'].items():
            extra_attr=[] # indicate sent from server, in local trust store, etc.
            if cert['fromServer']:
                extra_attr.append("sent by server")
            if cert['trusted']:
                extra_attr.append("in local CA trust store")
            if extra_attr:
                extra_attr_str = f" ({', '.join(extra_attr)})"
            else:
                extra_attr_str = ""

            try:
                print(f"\n{depth}{extra_attr_str} {cert['validation']}")
            except KeyError:
                print(f"\n{depth}{extra_attr_str}")

            # ifprint('trusted',cert)
            ifprint("subject", cert)
            ifprint("issuer", cert)
            ifprint("notBefore", cert)
            ifprint("notAfter", cert)
            ifprint("subjectAltName", cert)
            ifprint('keyUsage',cert)
            ifprint('extendedKeyUsage',cert)
            ifprint('basicConstraints',cert)
            ifprint('serialnumber',cert)
            ifprint('signature_algorithm', cert)
            ifprint('SHA-1 fingerprint',cert, label="fingerprint")
            ifprint('subjectKeyIdentifier',cert)
            ifprint('authorityKeyIdentifier',cert)
            if args.cert:
                print(f"\n{cert['cert']}")


if __name__ == '__main__':
    main()
