"""Copy the API landing zone of P9 (data/raw/api/<source>/<run date>/*.json + manifest.json) to MinIO, byte for byte:
    s3://<bucket>/landing/api/<source>/<run date>/<file>

    python lakehouse/scripts/upload_landing.py [--collect]
--collect  first run the P9 collector (python -m api_ingest.run --source all --fetch-only; needs the network) so that a new run date appears.
The collector in api_ingest/ is reused as it is (it writes the local landing folder); this script is the only new step. Idempotent:
a file already in the bucket with the same size is skipped. Spark reads the bucket afterwards (lakehouse/spark/bronze_api.py).
"""
from __future__ import annotations

import subprocess
import sys

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from lh_env import ROOT, load_env

LANDING = ROOT / "data" / "raw" / "api"


def s3_client(env):
    return boto3.client("s3", endpoint_url=f"http://127.0.0.1:{env['LH_MINIO_PORT']}", aws_access_key_id=env["LH_MINIO_USER"],
                        aws_secret_access_key=env["LH_MINIO_PASSWORD"], region_name="us-east-1", config=Config(s3={"addressing_style": "path"}))


def main() -> None:
    if "--collect" in sys.argv:
        r = subprocess.run([sys.executable, "-m", "api_ingest.run", "--source", "all", "--fetch-only"], cwd=ROOT)
        if r.returncode:
            raise SystemExit(r.returncode)
    env = load_env()
    s3, bucket = s3_client(env), env["LH_MINIO_BUCKET"]
    up = skipped = total_bytes = 0
    for f in sorted(LANDING.glob("*/*/*")):
        if not f.is_file():
            continue
        key = "landing/api/" + f.relative_to(LANDING).as_posix()
        size = f.stat().st_size
        try:
            if s3.head_object(Bucket=bucket, Key=key)["ContentLength"] == size:
                skipped += 1
                continue
        except ClientError:
            pass
        s3.upload_file(str(f), bucket, key)
        up += 1
        total_bytes += size
    print(f"landing zone -> s3://{bucket}/landing/api/: uploaded {up} files ({total_bytes / 1e6:.2f} MB), skipped {skipped} already present")


if __name__ == "__main__":
    main()
