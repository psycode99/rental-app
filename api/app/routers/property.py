from typing import List, Optional
from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy import update, desc
from ..database import get_db
from ..oauth import get_current_user
from .. import models, schemas
from sqlalchemy.orm import Session
from fastapi import status as st
import os
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page

router = APIRouter(prefix='/v1/properties', tags=['Properties'])


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PropertyResp) 
def create_property(property: schemas.PropertyCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
   is_landlord = db.query(models.LandLord).filter_by(email=current_user.email, id=property.landlord_id).first()
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


@router.get('/', status_code=status.HTTP_200_OK, response_model=Page[schemas.PropertyResp])
def get_properties(db: Session = Depends(get_db)) -> Page[schemas.PropertyResp]:
    # Create the query object
    properties_query = db.query(models.Property).order_by(desc(models.Property.id))

    # Check if any properties exist
    if not properties_query.first():
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    
    # Pass the query object to paginate
    return paginate(properties_query)


@router.get('/user', status_code=status.HTTP_200_OK, response_model=Page[schemas.PropertyResp])
def get_properties(db: Session = Depends(get_db), current_user: int = Depends(get_current_user)) -> Page[schemas.PropertyResp]:
    if current_user.landlord:
        properties = db.query(models.Property).filter_by(landlord_id=current_user.id).order_by(desc(models.Property.id))
    else:
        properties = db.query(models.Property).join(models.Property.tenants).filter(models.Tenant.id == current_user.id).order_by(desc(models.Property.id))
      
    return paginate(properties)


@router.post('/search', status_code=status.HTTP_200_OK, response_model=Page[schemas.PropertyResp])
def search(
    db: Session = Depends(get_db),
    state: Optional[str] = None,
    city: Optional[str] = None,
    status: Optional[str] = "available",
    price: Optional[float] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[float] = None
) -> Page[schemas.PropertyResp]:
    # Start with the base query
    query = db.query(models.Property)

    # Apply filters conditionally
    if state:
        query = query.filter(models.Property.state.ilike(f"%{state}%")).order_by(desc(models.Property.id))
    if city:
        query = query.filter(models.Property.city.ilike(f"%{city}%")).order_by(desc(models.Property.id))
    if status:
        query = query.filter(models.Property.status == status).order_by(desc(models.Property.id))
    if price is not None:
        query = query.filter(models.Property.price <= price).order_by(desc(models.Property.id))
    if bedrooms is not None:
        query = query.filter(models.Property.bedrooms >= bedrooms).order_by(desc(models.Property.id))
    if bathrooms is not None:
        query = query.filter(models.Property.bathrooms >= bathrooms).order_by(desc(models.Property.id))

    # Check if the filtered query returns any results
    if query.count() == 0:
        raise HTTPException(status_code=st.HTTP_204_NO_CONTENT)

    # Return paginated results
    return paginate(query)


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
                          detail="You are not authorized to delete this property")
   
   db.delete(property)
   db.commit()
   
   return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.PropertyResp)
def update_property(id: int,  property: schemas.PropertyCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
   property_update = db.query(models.Property).filter_by(id=id).first()
   if not property_update:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                          detail=f"Property with the id of {id} not found")
   
   
   is_landlord = db.query(models.LandLord).filter_by(email=current_user.email, id=property.landlord_id).first()

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
   
    