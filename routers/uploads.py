from typing import List
from fastapi import APIRouter, UploadFile, status, Depends, HTTPException, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from database import get_db
from oauth import get_current_user
import models, schemas
from sqlalchemy.orm import Session
import os
from pathlib import Path
import uuid
import time

router = APIRouter(prefix='/v1/uploads', tags=['Uploads'])


UPLOAD_FOLDER = 'static/property_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_unique_filename(filename: str) -> str:
    ext = filename.rsplit('.', 1)[1].lower()
    unique_id = uuid.uuid4().hex
    timestamp = int(time.time())
    unique_filename = f"{unique_id}_{timestamp}.{ext}"
    return unique_filename

@router.post("/upload_img")
async def upload_file_img(file: UploadFile = File(...)):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")

    unique_filename = get_unique_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())

    return JSONResponse(content={"message": "File successfully uploaded", "filename": unique_filename})
