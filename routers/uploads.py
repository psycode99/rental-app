from typing import List
from fastapi import APIRouter, UploadFile, status, Depends, HTTPException, File
from fastapi.staticfiles import StaticFiles
from database import get_db
from oauth import get_current_user
import models, schemas
from sqlalchemy.orm import Session
import os

router = APIRouter(prefix='/v1/uploads', tags=['Uploads'])


@router.post("/upload_multiple_prop")
def upload_multiple_files(files: List[UploadFile] = File(...)):
    # Iterate through each file and save to FastAPI static directory
    saved_files = []
    for file in files:
        with open(os.path.join("static", file.filename), "wb") as f:
            f.write(file.file.read())
        saved_files.append(file.filename)
    print(f"------------{saved_files}")
    
    return {"message": "successfully uploaded images"}