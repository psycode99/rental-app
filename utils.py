from passlib.hash import bcrypt
import os
from fastapi import UploadFile, HTTPException
from pathlib import Path
from typing import Optional, List
import uuid
import time

PROFILE_PIC_UPLOAD_DIR = Path("static/profile_pics")
PROFILE_PIC_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def hash_pwd(pwd):
    return bcrypt.hash(pwd)

def verify_pwd(pwd, hashed_pwd):
    return bcrypt.verify(pwd, hashed_pwd)


def allowed_file(filename: str, allowed) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed


def get_unique_filename(filename: str) -> str:
    ext = filename.rsplit('.', 1)[1].lower()
    unique_id = uuid.uuid4().hex
    timestamp = int(time.time())
    unique_filename = f"{unique_id}_{timestamp}.{ext}"
    return unique_filename


def save_pic(file: UploadFile, allowed_exts, upload_path: str) -> Optional[str]:
    if file:
        if not allowed_file(file.filename, allowed_exts):
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        unique_filename = get_unique_filename(file.filename)
        file_path = upload_path / unique_filename
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        
        return str(file_path)
    return None


def save_files(files: List[UploadFile], allowed_exts, upload_path: str) -> List[str]:
    if len(files) > 3:
        raise HTTPException(status_code=400, detail="Cannot upload more than 3 files")

    file_paths = []
    
    for file in files:
        if not allowed_file(file.filename, allowed_exts):
            raise HTTPException(status_code=400, detail=f"File type not allowed: {file.filename}")

        file_path = upload_path / file.filename
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        
        file_paths.append(str(file_path))
    
    return file_paths