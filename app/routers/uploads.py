import base64
from typing import List
from fastapi import APIRouter, UploadFile, status, Depends, HTTPException, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import app.credentials as credentials
from ..database import get_db
from ..oauth import get_current_user
from .. import models, schemas
from sqlalchemy.orm import Session
import os
from pathlib import Path
import uuid
import time
from typing import Optional
import requests

router = APIRouter(prefix='/v1/uploads', tags=['Uploads'])

imagekit_url = "https://upload.imagekit.io/api/v1/files/upload"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
TENANT_APPLICATIONS_ALLOWED_EXT = {'pdf'}

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
async def upload_file_img(file: UploadFile = File(...)):
    if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="File type not allowed")

    content = await file.read()
    encoded_content = base64.b64encode(content).decode('utf-8')
    # imagekit_file = { "file": open(file, 'rb')}
    payload  = {
        "file": encoded_content,
        'fileName': 'property',
        'publicKey': credentials.imagekit_public_api_key,
        'folder': '/Rently/Property_Images'
    }
    headers = {
        "Accept": "application/json",
        "Authorization": credentials.imagekit_api_base64
    }

    imagekit_resp = requests.post(imagekit_url, data=payload, headers=headers)
    image_url = imagekit_resp.json().get('url')

    return JSONResponse(content={"message": "File successfully uploaded", "filename": image_url})


@router.post("/upload_profile_pic")
async def upload_profile_pic(file: UploadFile = File(...)):
    if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="File type not allowed")

    content = await file.read()
    encoded_content = base64.b64encode(content).decode('utf-8')
    # imagekit_file = { "file": open(file, 'rb')}
    payload  = {
        "file": encoded_content,
        'fileName': 'user',
        'publicKey': credentials.imagekit_public_api_key,
        'folder': '/Rently/User_Profile_Pics'
    }
    headers = {
        "Accept": "application/json",
        "Authorization": credentials.imagekit_api_base64
    }

    imagekit_resp = requests.post(imagekit_url, data=payload, headers=headers)
    image_url = imagekit_resp.json().get('url')

    return JSONResponse(content={"message": "File successfully uploaded", "filename": image_url})


@router.post("/upload_imgs")
async def upload_files_imgs(files: List[UploadFile] = File(...)):
    if len(files) > 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="can not upload more than 3 files")
    filenames = []
    
    for file in files:
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            raise HTTPException(status_code=400, detail=f"File type not allowed: {file.filename}")
        
        content = await file.read()
        encoded_content = base64.b64encode(content).decode('utf-8')
        # imagekit_file = { "file": open(file, 'rb')}
        payload  = {
            "file": encoded_content,
            'fileName': 'property',
            'publicKey': credentials.imagekit_public_api_key,
            'folder': '/Rently/Property_Images'
        }
        headers = {
            "Accept": "application/json",
            "Authorization": credentials.imagekit_api_base64
        }

        imagekit_resp = requests.post(imagekit_url, data=payload, headers=headers)
        image_url = imagekit_resp.json().get('url')
    
        filenames.append(image_url)
    
    return JSONResponse(content={"message": "Files successfully uploaded", "filenames": filenames})



@router.post("/upload_application")
async def upload_file_doc(file: UploadFile = File(...)):
    if not allowed_file(file.filename, TENANT_APPLICATIONS_ALLOWED_EXT):
        raise HTTPException(status_code=400, detail="File type not allowed")

    content = await file.read()
    encoded_content = base64.b64encode(content).decode('utf-8')
    # imagekit_file = { "file": open(file, 'rb')}
    payload  = {
        "file": encoded_content,
        'fileName': 'tenant_app',
        'publicKey': credentials.imagekit_public_api_key,
        'folder': '/Rently/Tenant_Applications'
    }
    headers = {
        "Accept": "application/json",
        "Authorization": credentials.imagekit_api_base64
    }

    imagekit_resp = requests.post(imagekit_url, data=payload, headers=headers)
    doc_url = imagekit_resp.json().get('url')

    return JSONResponse(content={"message": "File successfully uploaded", "filename": doc_url})



@router.post("/upload_applications")
async def upload_files(files: List[UploadFile] = File(...)):
    if len(files) > 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="can not upload more than 3 files")
    filenames = []
    
    for file in files:
        if not allowed_file(file.filename, TENANT_APPLICATIONS_ALLOWED_EXT):
            raise HTTPException(status_code=400, detail=f"File type not allowed: {file.filename}")

        content = await file.read()
        encoded_content = base64.b64encode(content).decode('utf-8')
        # imagekit_file = { "file": open(file, 'rb')}
        payload  = {
            "file": encoded_content,
            'fileName': 'tenant_app',
            'publicKey': credentials.imagekit_public_api_key,
            'folder': '/Rently/Tenant_Applications'
        }
        headers = {
            "Accept": "application/json",
            "Authorization": credentials.imagekit_api_base64
        }

        imagekit_resp = requests.post(imagekit_url, data=payload, headers=headers)
        doc_url = imagekit_resp.json().get('url')
        
        filenames.append(doc_url)
    
    return JSONResponse(content={"message": "Files successfully uploaded", "filenames": filenames})