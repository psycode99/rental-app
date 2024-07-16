from typing import List
from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy import update
from database import get_db
from oauth import get_current_user
import models, schemas
from sqlalchemy.orm import Session
import os

router = APIRouter(prefix='/v1/properties', tags=['Properties'])

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PropertyResp)
def create_property(property: schemas.PropertyCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
   is_landlord = db.query(models.LandLord).filter_by(email=current_user.email).first()
   if not is_landlord:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                          detail="You are not authorized to create properties")
   
   if is_landlord.id  != property.landlord_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Landlord id match failure")
   new_property = models.Property(**property.model_dump())
   db.add(new_property)
   db.commit()
   db.refresh(new_property)

   return new_property


@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.PropertyResp])
def get_properties(db: Session = Depends(get_db)):
   properties = db.query(models.Property).all()

   if not properties:
      raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
   
   return properties


@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.PropertyResp)
def get_property(id: int, db: Session = Depends(get_db)):
   property = db.query(models.Property).filter_by(id=id).first()

   if not property:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                          detail=f"Property with the id of {id} not found")
   
   return property


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_property(id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
   property = db.query(models.Property).filter_by(id=id).first()

   if not property:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                          detail=f"Property with id of {id} not found")
   
   is_landlord = db.query(models.LandLord).filter_by(email=current_user.email).first()

   if not is_landlord:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail="You are not a landlord")

   if property.landlord_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                          detail="You are not authorized to delete this post")
   
   db.delete(property)
   db.commit()
   
   return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.PropertyResp)
def update_property(id: int,  property: schemas.PropertyCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
   property_update = db.query(models.Property).filter_by(id=id).first()
   if not property_update:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                          detail=f"Property with the id of {id} not found")
   
   
   is_landlord = db.query(models.LandLord).filter_by(email=current_user.email).first()

   if not is_landlord:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail="You are not a landlord")
   
   if property_update.landlord_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                          detail="You are not authorized")
   
   stmt = (
      update(models.Property).where(models.Property.id==id).values(**property.model_dump())
   )

   db.execute(stmt)
   db.commit()

   return property_update
   
    