from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from oauth import get_current_user
import schemas, models, database
from typing import List

router = APIRouter(prefix='/v1/payments', tags=['Payments'])

@router.post('/{property_id}', status_code=status.HTTP_200_OK, response_model=schemas.PaymentResp)
def make_rent_payment(property_id: int, payment: schemas.PaymentCreate, db: Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
    check = db.query(models.PropertyTenant).filter_by(tenant_id=current_user.id, property_id=property_id).first()
    if not check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="property and tenant match failed")
    
    payment_status = True
    if not payment_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Payment Failed")
    
    new_payment = models.Payment(**payment.model_dump())
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return new_payment


@router.get('/{property_id}', status_code=status.HTTP_200_OK, response_model=List[schemas.PaymentResp])
def get_payment_hostory(property_id: int, db: Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
    property_check = db.query(models.Property).filter_by(id=property_id).first()
    if not property_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Property with id of {property_id} not found")
    
    payment_history = db.query(models.Payment).filter_by(tenant_id=current_user.id, property_id=property_id).all()

    if not payment_history:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                            detail="No available payments")
    
    return payment_history

    


