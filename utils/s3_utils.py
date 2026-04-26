import boto3
import os

s3 = boto3.client("s3")

BUCKET = "scoutmind-storage"


# -------------------------------
# Upload file
# -------------------------------
def upload_file(local_path, s3_key):
    s3.upload_file(local_path, BUCKET, s3_key)


# -------------------------------
# Download file
# -------------------------------
def download_file(s3_key, local_path):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    s3.download_file(BUCKET, s3_key, local_path)


# -------------------------------
# Read CSV directly (optional)
# -------------------------------
def read_s3_file(s3_key):
    obj = s3.get_object(Bucket=BUCKET, Key=s3_key)
    return obj["Body"].read().decode("utf-8")