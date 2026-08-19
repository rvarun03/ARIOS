import boto3
from botocore.exceptions import ClientError
from core.config import settings
import uuid
from pathlib import Path
from fastapi import UploadFile

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

    def upload_file(
        self,
        file:UploadFile,
        folder: str = "uploads"
    ) -> dict:
            
        try:

            original_file_name = file.filename or "uploaded_file"

            safe_file_name = Path(original_file_name).name.replace(
                "",
                "_"
            )

            unique_file_name = f"{uuid.uuid4().hex}_{safe_file_name}"

            s3_key = f"{folder}/{unique_file_name}"

            extra_args = {}

            if file.content_type:
                extra_args["ContentType"] = file.content_type

            file.file.seek(0)

            self.client.upload_fileobj(
                Fileobj=file.file,
                Bucket=self.bucket_name,
                Key=s3_key,
                ExtraArgs=extra_args if extra_args else None
            ) 

            return {
                "uploaded": True,
                "bucket": self.bucket_name,
                "region": self.region,
                "s3_key": s3_key,
                "s3_uri": f"s3://{self.bucket_name}/{s3_key}",
                "file_name": original_file_name,
                "content_type": file.content_type
            }
        
        except:
            pass
