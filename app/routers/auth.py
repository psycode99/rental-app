from fastapi import Depends, status, HTTPException, APIRouter, BackgroundTasks
from .. import schemas, models, database, utils, oauth
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix='/v1/auth', tags=['Authentication']) 


@router.post('/login', status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.Users).filter_by(email=user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Credentials")
    verified_pwd = utils.verify_pwd(user_credentials.password, user.password)
    if not verified_pwd:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Credentials")
    if user.landlord == True:
        landlord = db.query(models.LandLord).filter_by(email=user_credentials.username).first()
        if not landlord:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Credentials")
        access_token = oauth.create_access_token({"user_id": landlord.id, "landlord": landlord.landlord})
    else:
        tenant = db.query(models.Tenant).filter_by(email=user_credentials.username).first()
        if not tenant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Credentials")
        access_token = oauth.create_access_token({"user_id": tenant.id, "landlord": tenant.landlord})

    return {"access_token": access_token, "token_type": "bearer"}



@router.post('/fpa_otp', status_code=status.HTTP_200_OK, response_model=schemas.ForgotPasswordOTP)
def get_otp_pwd(email: schemas.ForgotPasswordEmail, db: Session = Depends(database.get_db), background_task: BackgroundTasks = BackgroundTasks()):
    user_check = db.query(models.Users).filter_by(email=email.email).first()
    if not user_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Email not Found")
    otp = utils.generate_otp()
    background_task.add_task(utils.send_email(email.email, otp=otp))

    return {"otp": otp, "email": email.email}



@router.post('/verify_otp', status_code=status.HTTP_200_OK)
def verify_otp_pwd(data: schemas.VerifyOTP):
    if data.otp != data.typed_otp:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Code")
    
    return {"message": "success", "email":data.email}


@router.put('/reset_password', status_code=status.HTTP_200_OK)
def reset_pwd(data: schemas.ResetPassword, db: Session = Depends(database.get_db)):
    user_check = db.query(models.Users).filter_by(email=data.email).first()
    if not user_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Email not Found") 
    hashed_pwd = utils.hash_pwd(data.new_password)
    user_check.password = hashed_pwd
    db.commit()

    if user_check.landlord:
        landlord_pwd = db.query(models.LandLord).filter_by(email=data.email).first()
        landlord_pwd.password = hashed_pwd
        db.commit()
    else:
        tenant_pwd = db.query(models.Tenant).filter_by(email=data.email).first()
        tenant_pwd.password = hashed_pwd
        db.commit()

    return {"message": "password reset successful"}