#!/usr/bin/env python3
"""
Lambda to act as a reverse proxy to S3.
Value-add is that it provides a means of setting browser cache headers to minimize fetching of static assets
"""

import os
import boto3
import json
import base64 
import sys
import re 
from botocore.exceptions import ClientError

# Example CONFIG value
CONFIG = """{
  "path": {
    "/v1": "s3://bucketname/path",
    "/error" : "s3://altbucketname/errorpath"
  },
  {
    "cache": {
      "/v1/build": 86400,
      "/v1": 300,
      "/error": 86400
    }
  }
}"""

if "CONFIG" in os.environ:
    configdata = json.loads(os.environ["CONFIG"])
else:
    configdata = json.loads(CONFIG)

# Break out the path data for multiple use iterations
for path, target in configdata["path"].items():
    result = re.search(r"s3://([^/]+)(/.*)", target)
    if not result:
        raise ValueError(f'path target for "{path}": "{target}" does not match format s3://<bucket>/<path>')

    bucket = result.group(1)
    b_path = result.group(2)
    configdata["path"][path] = {"bucket": bucket, "bucket_path": b_path}

def get_bucket_and_bucket_file(file, configdata):
    """Given the input file request, return the bucket and mapping for the stored file"""
    for path, target in configdata["path"].items():
        if file.startswith(path):
            return target["bucket"], f'{target["bucket_path"]}{file[len(path):]}'
    return None, None

def get_cache_header(file, configdata):
    """Given the input file request, return the cache-control header value, if any"""
    for path, cache_seconds in configdata["cache"].items():
        if file.startswith(path):
            return f"max-age={cache_seconds}"
    return None

s3 = boto3.client('s3')

def lambda_handler(event, context):
    file = event["requestContext"]["path"]

    # Match file to bucket and path
    bucket, bucket_file = get_bucket_and_bucket_file(file, configdata)
    if not bucket:
        # no mapping, return 404
        body = f"404 not found: {file}"
        if os.environ.get("DEBUG"):
            body = f"404 not found: {file} - (no mapping to a bucket)"
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "text/html"},
            "body": body
        }

    if bucket_file.endswith("/"):
        # directory, append index.html
        bucket_file += "index.html" 
    if bucket_file.startswith("/"):
        # remove leading slash
        bucket_file = bucket_file[1:]
    
    try:
        response = s3.get_object(Bucket=bucket, Key=bucket_file)
    except ClientError as e:
        body = f"404 not found: {file}"
        if os.environ.get("DEBUG"):
            body = f"404 not found: {file} - (no s3://{bucket}/{bucket_file}) - {e}"
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "text/html"},
            "body": body
        }
    
    # Start the headers dict
    headers = {"Content-Type": response["ContentType"]}

    # Add cache header, if any
    cache_header = get_cache_header(file, configdata)
    if cache_header:
        headers["Cache-Control"] = cache_header
    
    # Return the text objects
    if response["ContentType"] in ["text/html","text/css","application/javascript","application/json","image/svg+xml"]:
        return {
            "statusCode": 200,
            "isBase64Encoded": False,
            "headers": headers,
            "body": response["Body"].read().decode("utf-8")
        }
    # Return the binary objects
    else:
        headers["Content-Encoding"] = "base64"
        return {
            "statusCode": 200,
            "isBase64Encoded": True,
            "headers": headers,
            "body": base64.b64encode(response["Body"].read()).decode("utf-8")
        }
    
if __name__ == "__main__":
    # Running from command line
    # os.environ["AWS_PROFILE"] = "yourprofilename"

    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = "/"
    
    event = {"requestContext": {"path": query}}
    response = lambda_handler(event, None)
    print(response)

