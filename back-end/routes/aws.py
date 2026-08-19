from fastapi import APIRouter, UploadFile, File
from fastapi import APIRouter

from services.s3_service import S3Service

router=APIRouter()

s3_service = S3Service()

@router.get("/test/s3")
def test_s3_connection():
    return s3_service.test_connection()

@router.post("/upload/s3")
def upload_file_to_s3(
    file:UploadFile = File(...)
):
    upload_result= s3_service.upload_file(
        file=file,
        folder="uploads"
    )

    return upload_result