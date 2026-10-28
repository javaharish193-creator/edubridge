import os
import uuid
import time
from typing import Optional
from jose import jwt
from app.config import settings

def save_uploaded_file(file_bytes: bytes, original_filename: str) -> tuple[str, int]:
    """
    Saves file to local storage and returns (file_key, file_size_bytes)
    """
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    ext = os.path.splitext(original_filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    target_path = os.path.join(settings.STORAGE_DIR, unique_name)
    
    with open(target_path, "wb") as f:
        f.write(file_bytes)
        
    return unique_name, len(file_bytes)

def generate_signed_url(file_key: Optional[str], expires_in: int = 900) -> Optional[str]:
    """
    Generates a secure signed URL valid for expires_in seconds (default 900s = 15m).
    """
    if not file_key:
        return None
    
    # If it's already an external HTTP link, return it
    if file_key.startswith("http://") or file_key.startswith("https://"):
        return file_key
        
    payload = {
        "k": file_key,
        "exp": int(time.time()) + expires_in
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return f"{settings.API_V1_PREFIX}/files/{token}"

def verify_signed_url_token(token: str) -> Optional[str]:
    """
    Verifies token and returns the file_path if valid and unexpired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        file_key = payload.get("k")
        if not file_key:
            return None
        file_path = os.path.join(settings.STORAGE_DIR, file_key)
        if os.path.exists(file_path):
            return file_path
        return None
    except Exception:
        return None
