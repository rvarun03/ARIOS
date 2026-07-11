
from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import UploadFile, HTTPException

class FileStorageService:

    BASE_UPLOAD_DIR = Path("uploads")

    ALLOWED_SOURCE_TYPES = {
        "pdf": "pdfs",
        "image": "images"
    }

    def save_uploaded_file(
        self,
        file:UploadFile,
        source_type: str    
    )-> dict:
        
        if source_type not in self.ALLOWED_SOURCE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="File upload currently supports only pdf and image"
            )
        
        folder_name = self.ALLOWED_SOURCE_TYPES[source_type]

        upload_dir = self.BASE_UPLOAD_DIR / folder_name

        upload_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        original_file_name = file.filename or "uploaded_file"

        file_extension = Path(original_file_name).suffix

        saved_file_name = f"{uuid4().hex}{file_extension}"

        saved_file_path = upload_dir / saved_file_name

        with saved_file_path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        file_size = saved_file_path.stat().st_size

        return {
            "file_name": original_file_name,
            "file_path": str(saved_file_path),
            "file_type": file.content_type,
            "file_size": file_size
        }