from fastapi import Depends, HTTPException, status
from jose  import JWTError, jwt
from datetime import timedelta, datetime, timezone
from . import schemas, models, database
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/v1/auth/login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
EXPIRATION_MINUTES = settings.expiration_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expires_in = datetime.now(timezone.utc) + timedelta(minutes=EXPIRATION_MINUTES)
    to_encode.update({"exp": expires_in})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id: str = payload.get('user_id')
        landlord: bool = payload.get('landlord')

        if id is None or landlord is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id, landlord=landlord)
    except JWTError:
        raise credentials_exception
    
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials")
    verified_token = verify_access_token(token, credentials_exception)
    if verified_token.landlord == True:
        user = db.query(models.LandLord).filter_by(id=verified_token.id).first()
    else:
       user = db.query(models.Tenant).filter_by(id=verified_token.id).first() 
    return user