from fastapi import APIRouter, FastAPI, status, Depends, HTTPException
import schemas, utils, models
from database import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix='/v1/users', tags=['Users'])

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResp)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_pwd = utils.hash_pwd(user.password)
    user.password = hashed_pwd

    model_dict = user.model_dump()
    del model_dict['landlord']

    if user.landlord == True:
        new_user = models.LandLord(**model_dict)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    else:
        new_user = models.Tenant(**model_dict)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    
    all_user = models.Users(**user.model_dump())
    db.add(all_user)
    db.commit()


    return new_user

@router.get('/', status_code=status.HTTP_200_OK, response_model=schemas.UserResp)
def get_user(id: int, db: Session = Depends(get_db)):
    query = db.query(models.Users).filter_by(id=id).first()

    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"User does not exist")
    
    return query