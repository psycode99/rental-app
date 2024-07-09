from fastapi import Depends, status, HTTPException, APIRouter
import schemas, models, database, utils, oauth
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter('/v1/auth', tags=['Authentication'])


@router.post('/login', status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm, db: Session = Depends(database.get_db)):
    user = db.query(models.Users).filter_by(email=user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Credentials")
    verified_pwd = utils.verify_pwd(user_credentials.password, user.password)
    if not verified_pwd:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Credentials")
    
    access_token = oauth.create_access_token({"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}