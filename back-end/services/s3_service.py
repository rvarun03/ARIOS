import boto3
from botocore.exceptions import ClientError
from core.config import settings

class S3Service:

    def __init__(self):

        self.bucket_name = settings.AWS_S3_BUCKET_NAME
        self.region = settings.AWS_REGION

        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=self.region
        )

    def test_connection(self) -> dict:
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=1
            )

            return {
                "connected": True,
                "bucket": self.bucket_name,
                "region": self.region,
                "object_count": response.get("KeyCount", 0)
            }
        except ClientError as error:
            return {
                "connected": False,
                "error": str(error)
            }
