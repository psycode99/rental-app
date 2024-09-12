from typing import List
from fastapi import APIRouter, UploadFile, status, Depends, HTTPException, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from ..database import get_db
from ..oauth import get_current_user
from .. import models, schemas
from sqlalchemy.orm import Session
import os
from pathlib import Path
import uuid
import time
from typing import Optional

router = APIRouter(prefix='/v1/uploads', tags=['Uploads'])


UPLOAD_FOLDER = Path('static/property_uploads')
TENANT_APPLICATIONS = Path('static/tenant_applications')
PROFILE_PIC_UPLOAD_DIR = Path("static/profile_pics")


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
TENANT_APPLICATIONS_ALLOWED_EXT = {'pdf'}

Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(TENANT_APPLICATIONS).mkdir(parents=True, exist_ok=True)
PROFILE_PIC_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def allowed_file(filename: str, allowed) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed

def get_unique_filename(filename: str) -> str:
    ext = filename.rsplit('.', 1)[1].lower()
    unique_id = uuid.uuid4().hex
    timestamp = int(time.time())
    unique_filename = f"{unique_id}_{timestamp}.{ext}"
    return unique_filename



@router.post("/upload_img")
def upload_file_img(file: UploadFile = File(...)):
    if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="File type not allowed")

    unique_filename = get_unique_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    try:
        with open(file_path, "wb") as f:
            # file.file is a SpooledTemporaryFile, which can be used directly
            f.write(file.file.read())  # Read the contents of the file and write it to the disk
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

    return JSONResponse(content={"message": "File successfully uploaded", "filename": unique_filename})


@router.post("/upload_profile_pic")
def upload_profile_pic(file: UploadFile = File(...)):
    if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="File type not allowed")

    unique_filename = get_unique_filename(file.filename)
    file_path = os.path.join(PROFILE_PIC_UPLOAD_DIR, unique_filename)
    
    try:
        with open(file_path, "wb") as f:
            # file.file is a SpooledTemporaryFile, which can be used directly
            f.write(file.file.read())  # Read the contents of the file and write it to the disk
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

    return JSONResponse(content={"message": "File successfully uploaded", "filename": unique_filename})


@router.post("/upload_imgs")
def upload_files_imgs(files: List[UploadFile] = File(...)):
    if len(files) > 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="can not upload more than 3 files")
    filenames = []
    
    for file in files:
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            raise HTTPException(status_code=400, detail=f"File type not allowed: {file.filename}")

        unique_filename = get_unique_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        try:
            with open(file_path, "wb") as f:
            # file.file is a SpooledTemporaryFile, which can be used directly
                f.write(file.file.read())  # Read the contents of the file and write it to the disk
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File upload failed: {e}")
        
        filenames.append(unique_filename)
    
    return JSONResponse(content={"message": "Files successfully uploaded", "filenames": filenames})



@router.post("/upload_application")
def upload_file_doc(file: UploadFile = File(...)):
    if not allowed_file(file.filename, TENANT_APPLICATIONS_ALLOWED_EXT):
        raise HTTPException(status_code=400, detail="File type not allowed")

    unique_filename = get_unique_filename(file.filename)
    file_path = os.path.join(TENANT_APPLICATIONS, unique_filename)
    
    try:
        with open(file_path, "wb") as f:
        # file.file is a SpooledTemporaryFile, which can be used directly
            f.write(file.file.read())  # Read the contents of the file and write it to the disk
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

    return JSONResponse(content={"message": "File successfully uploaded", "filename": unique_filename})



@router.post("/upload_applications")
def upload_files(files: List[UploadFile] = File(...)):
    if len(files) > 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="can not upload more than 3 files")
    filenames = []
    
    for file in files:
        if not allowed_file(file.filename, TENANT_APPLICATIONS_ALLOWED_EXT):
            raise HTTPException(status_code=400, detail=f"File type not allowed: {file.filename}")

        unique_filename = get_unique_filename(file.filename)
        file_path = os.path.join(TENANT_APPLICATIONS, unique_filename)

        try:
            with open(file_path, "wb") as f:
            # file.file is a SpooledTemporaryFile, which can be used directly
                f.write(file.file.read())  # Read the contents of the file and write it to the disk
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File upload failed: {e}")
        
        filenames.append(unique_filename)
    
    return JSONResponse(content={"message": "Files successfully uploaded", "filenames": filenames})