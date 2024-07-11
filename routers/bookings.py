from fastapi import APIRouter, Depends, HTTPException, status
from httpx import delete
from sqlalchemy.orm import Session
from oauth import get_current_user
import database, models, schemas
from typing import List

router = APIRouter(prefix='/v1/bookings', tags=["Bookings"])

@router.post("/{property_id}", status_code=status.HTTP_201_CREATED, response_model=schemas.BookingsResp)
def create_booking(property_id: int, booking: schemas.BookingsCreate,  db: Session = Depends(database.get_db)):
    property = db.query(models.Property).filter_by(id=property_id).first()
    if not property:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"property with id of {property_id} not found")
    
    new_booking = models.Booking(**booking.model_dump())
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking


@router.get('/{property_id}', status_code=status.HTTP_200_OK, response_model=List[schemas.BookingsResp])
def get_bookings(property_id: int, db: Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
    property = db.query(models.Property).filter_by(id=property_id).first()
    if not property:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= f"Property with id of {id} not found")
    
    is_landlord = db.query(models.LandLord).filter_by(email=current_user.email).first()

    if not is_landlord:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail="You are not a landlord")
    
    if current_user.id != property.landlord_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized")
    

    bookings = db.query(models.Booking).filter_by(property_id=property.id).all()

    return bookings
    

@router.delete('/{booking_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(booking_id: int, db: Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
    booking = db.query(models.Booking).filter_by(id=booking_id).first()

    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Booking doesn't exist")
    
    property = db.query(models.Property).filter_by(id=booking.property_id).first()
    landlord = db.query(models.LandLord).filter_by(id=property.landlord_id).first()

    is_landlord = db.query(models.LandLord).filter_by(email=current_user.email).first()

    if not is_landlord:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail="You are not a landlord")
    
    if current_user.id != landlord.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized"
                            )
    db.delete(booking)
    db.commit()

            