from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session
from oauth import get_current_user
import schemas, models, database
from typing import List


router = APIRouter(prefix='/v1/maintenance_reqs', tags=["Maintenance Requests"])

@router.post('/{property_id}', status_code=status.HTTP_201_CREATED, response_model=schemas.MaintenanceRequestResp)
def create_maintenance_request(property_id: int, maintenance_request: schemas.MaintenanceRequestCreate, db:  Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
    property_check = db.query(models.Property).filter_by(id=property_id).first()
    if not property_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"property with the id of {property_id} not found")
    
    user_check =  db.query(models.Tenant).filter_by(email=current_user.email, id=maintenance_request.tenant_id).first()
    if not user_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User is not a Tenant"
                            )

    tenant_check = db.query(models.PropertyTenant).filter_by(tenant_id=user_check.id, property_id=property_id).first()
    if not tenant_check:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail="You are not a tenant for this property")
    
    if property_id != maintenance_request.property_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid Property ID property in request body "
                            )
    
    new_maintenance_req = models.MaintenanceRequest(**maintenance_request.model_dump())
    db.add(new_maintenance_req)
    db.commit()
    db.refresh(new_maintenance_req)

    return new_maintenance_req
    

@router.get('/{property_id}', status_code=status.HTTP_200_OK, response_model=List[schemas.MaintenanceRequestResp])
def get_maintenance_reqs(property_id: int, db: Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
    property_check = db.query(models.Property).filter_by(id=property_id).first()
    if not property_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Property with id of {property_id} not found")
    maintenance_reqs = db.query(models.MaintenanceRequest).filter_by(property_id=property_id).all()
    if not maintenance_reqs:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    return maintenance_reqs
    
    # if current_user.landlord:
    #     # just being extra careful.. i'm not dumb i clearly see the user is a landlord
    #     landlord_check = db.query(models.LandLord).filter_by(email=current_user.email).first()
    #     if not landlord_check:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
    #                             detail="You are no landlord")
    #     property_check = db.query(models.Property).filter_by(id=property_id, landlord_id=landlord_check.id).first()
    
    #     if not property_check:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                             detail="You do not own this property")
        
        # maintenance_reqs = db.query(models.MaintenanceRequest).filter_by(property_id=property_id, landlord_deleted=False).all()

        # return maintenance_reqs
    
    # else:
    #     # if user is a tenant
    #     tenant_check = db.query(models.Tenant).filter_by(email=current_user.email).first()
    #     #tenant_check
    #     if not tenant_check:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                             detail="You are not a tenant")

    #     #tenant belongs to property check
    #     tenant_property_check = db.query(models.PropertyTenant).filter_by(tenant_id=tenant_check.id, property_id=property_id).first()
    #     if not tenant_property_check:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                             detail="You have not rented this property")
        
        # Get maintenance requests
    
        


@router.get('/{property_id}/{MR_id}', status_code=status.HTTP_200_OK, response_model=schemas.MaintenanceRequestResp)
def get_maintenance_req(property_id: int, MR_id: int,  db: Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
    property_check = db.query(models.Property).filter_by(id=property_id).first()
    if not property_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Property with id of {property_id} not found")
 
    
    maintenance_req = db.query(models.MaintenanceRequest).filter_by(id=MR_id, property_id=property_id).first()
    if not maintenance_req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Maintenance Request not found")

    return maintenance_req
    


@router.put('/{property_id}/{MR_id}', status_code=status.HTTP_200_OK, response_model=schemas.MaintenanceRequestResp)
def update_maintenance_req(property_id: int, MR_id: int, MR: schemas.MaintenanceRequestCreate, db: Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
    property_check = db.query(models.Property).filter_by(id=property_id).first()
    if not property_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Property with id of {property_id} not found")
    
    maintenance_req_check = db.query(models.MaintenanceRequest).filter_by(id=MR_id, tenant_id=MR.tenant_id, property_id=MR.property_id, landlord_deleted=False).first()
    if not maintenance_req_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Maintenance Request not found")
    
    stmt = (
        update(models.MaintenanceRequest).
        where(models.MaintenanceRequest.id == MR_id).
        values(**MR.model_dump())
    )

    db.execute(stmt)
    db.commit()
    return maintenance_req_check


# @router.delete('/{property_id}/{MR_id}', status_code=status.HTTP_204_NO_CONTENT)
# def delete_maintenance_req(property_id: int, MR_id: int, db: Session = Depends(database.get_db), current_user: int = Depends(get_current_user)):
#     property_check = db.query(models.Property).filter_by(id=property_id).first()
#     if not property_check:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Property with id {property_id} not found"
#         )
    
#     maintenance_req_check = db.query(models.MaintenanceRequest).filter_by(id=MR_id, landlord_deleted=False).first()
#     if not maintenance_req_check:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Maintenance Request not found"
#         )
    
#     if current_user.landlord:
#         maintenance_req_check.landlord_deleted = True
#     else:
#         maintenance_req_check.tenant_deleted = True

#     db.commit()

#     if maintenance_req_check.landlord_deleted and maintenance_req_check.tenant_deleted:
#         db.delete(maintenance_req_check)
#         db.commit()
        
#     return Response(status_code=status.HTTP_204_NO_CONTENT)



