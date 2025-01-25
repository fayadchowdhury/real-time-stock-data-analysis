from s3fs import S3FileSystem
import json
import logging

def push_to_cloud(s3_params: dict, index_name: str, date: str, data) -> None:
    logger = logging.getLogger("push")
    try:
        s3_access_key = s3_params["access_key"]
        s3_access_key_secret = s3_params["access_key_secret"]
        s3_bucket_name = s3_params["bucket_name"]
        s3 = S3FileSystem(
            anon=False,
            key=s3_access_key,
            secret=s3_access_key_secret
        )
        filename = f"s3://{s3_bucket_name}/{index_name}-{date}.json"
        with s3.open(filename, "w") as file:
            json.dump(data, file)
        logger.debug(f"Data pushed to {filename}")
    except Exception as e:
        logger.error(e)