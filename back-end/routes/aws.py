from fastapi import APIRouter

from services.s3_service import S3Service

router=APIRouter()

s3_service = S3Service()

@router.get("/test/s3")
def test_s3_connection():
    return s3_service.test_connection()