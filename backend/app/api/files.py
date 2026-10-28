import os
import mimetypes
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from app.services.storage_service import verify_signed_url_token

router = APIRouter(prefix="/files", tags=["Files"])

@router.get("/{token}")
def get_signed_file(token: str):
    file_path = verify_signed_url_token(token)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "FILE_NOT_FOUND", "message": "File does not exist or signed access link has expired"}
        )
    
    media_type, _ = mimetypes.guess_type(file_path)
    filename = os.path.basename(file_path)
    return FileResponse(
        path=file_path,
        media_type=media_type or "application/octet-stream",
        filename=filename
    )
