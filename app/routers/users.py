from fastapi import APIRouter, FastAPI, Response, status, Depends, HTTPException
from sqlalchemy import update
from ..oauth import get_current_user
from .. import schemas, utils, models
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List


router = APIRouter(prefix='/v1/users', tags=['Users'])

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResp)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    email_query = db.query(models.Users).filter_by(email=user.email).first()
    if email_query:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User with this email already exists")
    
    phone_no_query = db.query(models.Users).filter_by(phone_number=user.phone_number).first()
    if phone_no_query:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User with this phone number already exists")
    
    hashed_pwd = utils.hash_pwd(user.password)
    user.password = hashed_pwd

    model_dict = user.model_dump()

    if user.landlord == True:
        email_query = db.query(models.LandLord).filter_by(email=user.email).first()
        if email_query:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="User with this email already exists")
        
        phone_no_query = db.query(models.LandLord).filter_by(phone_number=user.phone_number).first()
        if phone_no_query:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="User with this phone number already exists")
        new_user = models.LandLord(**model_dict)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        all_user = models.Users(**user.model_dump())
        db.add(all_user)
        db.commit()
    else:
        email_query = db.query(models.Tenant).filter_by(email=user.email).first()
        if email_query:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="User with this email already exists")
        
        phone_no_query = db.query(models.Tenant).filter_by(phone_number=user.phone_number).first()
        if phone_no_query:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="User with this phone number already exists")
        new_user = models.Tenant(**model_dict)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    
        all_user = models.Users(**user.model_dump())
        db.add(all_user)
        db.commit()


    return new_user

@router.get('/landlords/{id}', status_code=status.HTTP_200_OK, response_model=schemas.LandLordResp)
def get_landlord(id: int, db: Session = Depends(get_db)):
    query = db.query(models.LandLord).filter_by(id=id).first()

    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Landlord does not exist")
    
    return query


@router.get('/tenants/{id}', status_code=status.HTTP_200_OK, response_model=schemas.TenantResp)
def get_tenant(id: int, db: Session = Depends(get_db)):
    query = db.query(models.Tenant).filter_by(id=id).first()

    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Tenant does not exist")
    
    return query


@router.get('/{property_id}', status_code=status.HTTP_200_OK, response_model=List[schemas.TenantResp])
def get_tenants(property_id: int, db: Session = Depends(get_db)):
    query = db.query(models.PropertyTenant).filter_by(property_id=property_id).all()

    if not query:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, 
                            detail="no tenants found for this property")
    tenants = []
    for tenant in query:
        data = db.query(models.Tenant).filter_by(id=tenant.tenant_id).first()
        tenants.append(data)
    
    return tenants


@router.delete('/{property_id}/{tenant_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_tenant(property_id: int, tenant_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    landlord_check = db.query(models.LandLord).filter_by(id=current_user.id, email=current_user.email).first()
    if not landlord_check:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="you are not a landlord")
    property_tenant_check = db.query(models.PropertyTenant).filter_by(property_id=property_id, tenant_id=tenant_id).first()
    if not property_tenant_check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="relationship not available")
    ownership_check = db.query(models.Property).filter_by(id=property_id, landlord_id=current_user.id).first()
    if not ownership_check:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="you do not own this property")
    # property_tenant_check.landlord_removed = True
    db.delete(property_tenant_check)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/{user_id}', status_code=status.HTTP_200_OK, response_model=schemas.UserResp)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    
    user_check = db.query(models.Users).filter_by(email=current_user.email).first()
    if not user_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="user not found")
    
    email_query = db.query(models.Users).filter_by(email=user.email).first()
    if email_query:
        if current_user.email == user.email:
            pass
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='user with that email already exists')
    
    phone_no_query = db.query(models.Users).filter_by(phone_number=user.phone_number).first()
    if phone_no_query:
        if current_user.phone_number == user.phone_number:
            pass
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='user with that phone number already exists')
    
    user.password = utils.hash_pwd(user.password)
    if user_check.landlord:
        stmt = (
            update(models.Users).
            where(models.Users.email == current_user.email).
            values(**user.model_dump())
        )

        stmt_2 =  (
            update(models.LandLord).
            where(models.LandLord.email == current_user.email).
            values(**user.model_dump())
        )
        db.execute(stmt)
        db.execute(stmt_2)
        db.commit()

    else:
        stmt = (
        update(models.Users).
        where(models.Users.email == current_user.email).
        values(**user.model_dump())
        )

        stmt_2 =  (
            update(models.Tenant).
            where(models.Tenant.email == current_user.email).
            values(**user.model_dump())
        )
        db.execute(stmt)
        db.execute(stmt_2)
        db.commit()

    db.refresh(user_check)
    return user_check


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    user_check = db.query(models.Users).filter_by(email=current_user.email).first()
    if not user_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="user not found")
    if user_check.landlord:
        landlord_d = db.query(models.LandLord).filter_by(email=current_user.email).first()
        if not landlord_d:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='landlord not found')
        # if current_user.id != user_id:
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        #                     detail="you are unauthorized")
        db.delete(user_check)
        db.delete(landlord_d)
        db.commit()
    else:
        tenant_d = db.query(models.Tenant).filter_by(email=current_user.email).first()
        if not tenant_d:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='tenant not found')
        # if current_user.id != user_id:
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        #                     detail="you are unauthorized")
        db.delete(user_check)
        db.delete(tenant_d)
        db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)