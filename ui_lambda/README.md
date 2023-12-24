# Lambda proxy for S3 content

This lambda is responsible for delivering S3 content (usually a React app) from an S3 bucket or three.   It allows for path mapping to particular buckets, as well as per-path mapping of browser cache headers.   It is configurable by an environment variable with a json payload.

Warning: The API Gateway to Lambda interface does not handle responses > 6 MB.  

## Configuration

The CONFIG lambda environment variable should have a json structure with "path" and "cache" arrays.   The path array elements should be a path key and a value consisting of S3 bucket and path value in the format of s3://<bucketname>/<path>, whereas the cache array elements should be a path key and an integer, representing the number of seconds the browser should be instructed to cache the content.

More specific paths should be listed before general ones, such as /v1/static before /v1, as the first path key to match the url will be used.

Example:
```
CONFIG = {
    "path": {
        "/v1": "s3://mybucket/v1",
        "/error": "s3://otherbucket/error"
    },
    "cache": {
        "/v1/static": 86400,
        "/v1": 300,
        "/error": 86400
    }
}
```

Coded as it is now, the runtime should be set to "main.lambda_handler" in Lambda -> Code -> Runtime Settings, else it will look for lambda_function.py instead of main.py.

## Lambda creation

Zip the contents of this file and create as a lambda function from a zip file

API Gateway should point GET /{proxy+} to this as a lambda proxy.
API Gateway should also point GET / to this as a lambda proxy.
API Gateway should already point GET /api or similar to the api function you may be using.

Make sure to redeploy the API when making changes.

S3 bucket should be private, but have an access policy granting the lambda execution role access to the contents, similar to:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "RevproxyAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::xxxxxxxxxxxx:role/service-role/s3_revproxy-role-3b6flana"
            },
            "Action": "s3:*",
            "Resource": "arn:aws:s3:::cert-inspection.guyton.net/*"
        }
    ]
}
```

