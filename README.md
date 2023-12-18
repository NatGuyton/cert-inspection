# cert-inspection

A tool to get the certificates on a website and validate them.

This tool is designed to be run either by command line or as a lambda function, and will output 
either formatted text or json, respectively.

## Required modules

You can use pip to install the required modules via:

```
pip3 install -r requirements.txt
```

### Virtual Environment

If you want to create a virtual environment, either because you don't have access to install in 
the normal python library directories, or because you want to keep things clean and isolated, you
can create a virtual environment dir in this directory and install them there:

```
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
deactivate
```

If you have created a virtual environment similar to above, the "run" script will source the venv, 
and then you can run the scripts like:

```
./run populateSKI.py
```

Alternatively, instead of using run, you can edit the #! line to use the venv/bin/python3 full path
instead of "/usr/bin/env python3" in each of the python files, and run them directly.

## Usage

# Preliminary Step

Before using, you need to pre-stage a directory with the certs from your certifi module's trusted certs, 
usually found in venv/lib/python3.X/site-packages/certifi/cacert.pem.
(You may wish to append any private CAs you have to that file before this step)

to do so, run:
```
./run populateSKI.py
```

This will create a directory "subjectKeyIdentifier" and populate with cert data for performance.

# Usage

You can run with no parameters for the syntax and examples:

```
$ ./run main.py

cert-inspection

    Query a website and display the certificates it presents, performing some validation as well.

SYNTAX VARIANTS:
    ./main.py [-j|--json] [-c|--cert] [-s <servername>] hostname
    ./main.py [-j|--json] [-c|--cert] [-s <servername>] hostname:port
    ./main.py [-j|--json] [-c|--cert] [-s <servername>] url

  General use is to just give a hostname or URL.  Port 443 is assumed if not specified, and
  these will be picked out of a URL if a URL is supplied.
    ./main.py my.hostname.com
    ./main.py https://my.hostname.com:8443/

  The optional component -s <servername> is only needed if SNI is needed to indicate a specific
  hostname that is different from the main target.  For example, if you need to check a specific
  endpoint by IP address for the certificate matching a hostname, you would use syntax:
    ./main.py -s <servername> <IP address>

  The -j switch signals json rather than formatted text output, usually used in lambda.

  The -c switch signals that the cert should be printed out in the formatted text output.  It is
  normally omitted for a cleaner report.  The json output always includes it.
```

Note the -c switch to include the certs themselves, else you just get metadata.

As a short example:

```
$ ./run main.py github.com
cert-inspection: github.com:443

connection: TLSv1.3 128 bits using TLS_AES_128_GCM_SHA256
CA Trust File: /home/nat/git/cert-inspection/venv/lib/python3.8/site-packages/certifi/cacert.pem

0 (sent by server) verify:depth:0 /C=US/ST=California/L=San Francisco/O=GitHub, Inc./CN=github.com - 0: ok
  subject: /C=US/ST=California/L=San Francisco/O=GitHub, Inc./CN=github.com
  issuer: /C=US/O=DigiCert Inc/CN=DigiCert TLS Hybrid ECC SHA384 2020 CA1
  notBefore: Tue Feb 14 00:00:00 2023 GMT
  notAfter: Thu Mar 14 23:59:05 2024 GMT
  subjectAltName: DNS:github.com, DNS:www.github.com
  keyUsage: Digital Signature
  extendedKeyUsage: TLS Web Server Authentication, TLS Web Client Authentication
  basicConstraints: CA:FALSE
  serialnumber: 17034156255497985825694118641198758684
  signature_algorithm: ecdsa-with-SHA384
  fingerprint: A3:B5:9E:5F:E8:84:EE:1F:34:D9:8E:EF:85:8E:3F:B6:62:AC:10:4A
  subjectKeyIdentifier: C7:07:27:78:85:F2:9D:33:C9:4C:5E:56:7D:5C:D6:8E:72:67:EB:DE
  authorityKeyIdentifier: 0A:BC:08:29:17:8C:A5:39:6D:7A:0E:CE:33:C7:2E:B3:ED:FB:C3:7A

1 (sent by server) verify:depth:1 /C=US/O=DigiCert Inc/CN=DigiCert TLS Hybrid ECC SHA384 2020 CA1 - 0: ok
  subject: /C=US/O=DigiCert Inc/CN=DigiCert TLS Hybrid ECC SHA384 2020 CA1
  issuer: /C=US/O=DigiCert Inc/OU=www.digicert.com/CN=DigiCert Global Root CA
  notBefore: Wed Apr 14 00:00:00 2021 GMT
  notAfter: Sun Apr 13 23:59:05 2031 GMT
  keyUsage: Digital Signature, Certificate Sign, CRL Sign
  extendedKeyUsage: TLS Web Server Authentication, TLS Web Client Authentication
  basicConstraints: CA:TRUE, pathlen:0
  serialnumber: 10566067766768619126890179173671052733
  signature_algorithm: sha384WithRSAEncryption
  fingerprint: AE:C1:3C:DD:5E:A6:A3:99:8A:EC:14:AC:33:1A:D9:6B:ED:BB:77:0F
  subjectKeyIdentifier: 0A:BC:08:29:17:8C:A5:39:6D:7A:0E:CE:33:C7:2E:B3:ED:FB:C3:7A
  authorityKeyIdentifier: 03:DE:50:35:56:D1:4C:BB:66:F0:A3:E2:1B:1B:C3:97:B2:3D:D1:55

2 (in local CA trust store)
  subject: /C=US/O=DigiCert Inc/OU=www.digicert.com/CN=DigiCert Global Root CA
  issuer: /C=US/O=DigiCert Inc/OU=www.digicert.com/CN=DigiCert Global Root CA
  notBefore: Fri Nov 10 00:00:00 2006 GMT
  notAfter: Mon Nov 10 00:00:00 2031 GMT
  keyUsage: Digital Signature, Certificate Sign, CRL Sign
  basicConstraints: CA:TRUE
  serialnumber: 10944719598952040374951832963794454346
  signature_algorithm: sha1WithRSAEncryption
  fingerprint: A8:98:5D:3A:65:E5:E5:C4:B2:D7:D6:6D:40:C6:DD:2F:B1:9C:54:36
  subjectKeyIdentifier: 03:DE:50:35:56:D1:4C:BB:66:F0:A3:E2:1B:1B:C3:97:B2:3D:D1:55
```
