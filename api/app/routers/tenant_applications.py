from typing import List
from fastapi import APIRouter,  HTTPException, Depends, Response, status
from sqlalchemy import desc
from sqlalchemy.orm import Session
from ..oauth import get_current_user
from .. import schemas, models, database
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate


router = APIRouter(prefix='/v1/applications', tags=['Tenant Applications'])

@router.post('/{property_id}', status_code=status.HTTP_201_CREATED, response_model=schemas.TenantApplicationResp)
def create_application(property_id: int, application: schemas.TenantApplicationCreate, db: Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
    property_check = db.query(models.Property).filter_by(id=property_id).first()
    if not property_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Property with id of {property_id} not found")
    user_check = db.query(models.Tenant).filter_by(email=current_user.email, id=application.tenant_id).first()
    if not user_check:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not registered as a tenant")
    if property_check.id  != application.property_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Property id match failure")
    
    new_application = models.TenantApplication(**application.model_dump())
    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application


@router.get('/{property_id}', status_code=status.HTTP_200_OK, response_model=List[schemas.TenantApplicationResp])
def get_applications(property_id: int, db:  Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
    property_check = db.query(models.Property).filter_by(id=property_id).first()
    if not property_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Property with id of {property_id} not found")
    applications = db.query(models.TenantApplication).filter_by(property_id=property_id).order_by(desc(models.TenantApplication.id)).all()
    if not applications:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    return applications


@router.get('/', status_code=status.HTTP_200_OK, response_model=Page[schemas.TenantApplicationResp])
def get_applications_user(db:  Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
    user_check = db.query(models.Users).filter_by(email=current_user.email).first()
    if not user_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    if current_user.landlord:
        applications = db.query(models.TenantApplication).join(models.TenantApplication.property).filter(models.Property.landlord_id == current_user.id).order_by(desc(models.TenantApplication.id))
    else:
        applications = db.query(models.TenantApplication).filter_by(tenant_id=current_user.id).order_by(desc(models.TenantApplication.id))

    if not applications.first():
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                            detail="No available applications")    
    return paginate(applications)


@router.get('/{property_id}/{app_id}', status_code=status.HTTP_200_OK, response_model=schemas.TenantApplicationResp)
def get_application(property_id: int, app_id: int, db:  Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
    property_check = db.query(models.Property).filter_by(id=property_id).first()
    if not property_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Property with id of {property_id} not found")
    application = db.query(models.TenantApplication).filter_by(id=app_id, property_id=property_id).first()
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Tenant  Application not found")
    return application




@router.put('/{property_id}/{app_id}', status_code=status.HTTP_200_OK, response_model=schemas.TenantApplicationResp)
def update_application_status(property_id: int, app_id: int, app_status: schemas.TenantApplicationStatus, db: Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
    application_check = db.query(models.TenantApplication).filter_by(id=app_id, property_id=property_id, tenant_id=app_status.tenant_id).first()
    if not application_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Tenant  Application not found")
    
    is_landlord = db.query(models.LandLord).filter_by(email=current_user.email).first()
    if not is_landlord:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail="You are not a landlord")
    
    
    if current_user.id != application_check.property.landlord_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized")
    
    application_check.application_status = app_status.application_status
    db.commit()

    if app_status.application_status == 'approved':
        # application_check.application_status = "approved"
        # db.commit()

        # prop_tenant_query = db.query(models.PropertyTenant).filter_by(
        #                                     tenant_id=app_status.tenant_id,
        #                                     property_id=property_id,
        #                                     landlord_removed=True).first()
        # if prop_tenant_query:
        #     prop_tenant_query.landlord_removed = False
        #     db.commit()
        # else:
        new_entry = models.PropertyTenant(tenant_id=app_status.tenant_id,
                                        property_id=property_id)
        db.add(new_entry)
        db.commit()

    # elif app_status.application_status == 'rejected':
    #     application_check.application_status = "rejected"
    #     db.commit()

    return application_check


# @router.delete('/{property_id}/{app_id}', status_code=status.HTTP_204_NO_CONTENT)
# def delete_application(property_id: int, app_id: int, db:  Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
#     application_check = db.query(models.TenantApplication).filter_by(id=app_id, property_id=property_id).first()
#     if not application_check:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
#                             detail="Tenant  Application not found")
    
#     is_landlord = db.query(models.LandLord).filter_by(email=current_user.email).first()
#     if not is_landlord:
#       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                           detail="You are not a landlord")
    
    
#     if current_user.id != application_check.property.landlord_id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail="You are not authorized")
    
#     db.delete(application_check)
#     db.commit()

#     return Response(status_code=status.HTTP_204_NO_CONTENT)