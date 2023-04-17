import os
import json

import modal

stub = modal.Stub("s3")
image = modal.Image.debian_slim().pip_install("boto3")


@stub.function(image=image, secret=modal.Secret.from_name("aws"))
def store(obj: dict, path: str, bucket_name="aline-ai") -> bool:
    import boto3
    session = boto3.Session(
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    )
    s3 = session.client("s3")
    file_contents = json.dumps(obj)
    s3.put_object(Bucket=bucket_name, Key=path, Body=file_contents)
    return True
