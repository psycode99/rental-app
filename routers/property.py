from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from database import get_db
from oauth import get_current_user
import models, schemas
from sqlalchemy.orm import Session
import os

router = APIRouter(prefix='/v1/properties', tags=['Properties'])

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PropertyResp)
def create_property(property: schemas.PropertyCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
   new_property = models.Property(landlord_id=current_user.id, **property.model_dump())
   db.add(new_property)
   db.commit()
   db.refresh(new_property)

   return new_property
    