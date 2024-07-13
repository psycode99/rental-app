import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import date, time

class Property(BaseModel):
    address: str
    city: str
    state: str
    bedrooms: int
    bathrooms: float
    sqft: int
    description: str
    price: float
    file_1: Optional[str] = None
    file_2: Optional[str] = None
    file_3: Optional[str] = None
    # file_4: str
    # file_5: str

class PropertyCreate(Property):
    pass

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: int
    email: EmailStr
    password: str
    landlord: bool = False

class UserResp(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    created_at: datetime.datetime
    landlord: bool

    class Config:
        from_attributes = True

class TenantResp(UserResp):
    pass

class PropertyResp(Property):
    id: int
    landlord_id: int
    created_at: datetime.datetime
    # landlord: 'LandLordResp'
    bookings: List['BookingsResp'] = []
    maintenance_requests: List['MaintenanceRequestResp'] = []

    class Config:
        from_attributes = True

class LandLordResp(UserResp):
    property: List[PropertyResp] = []

class Bookings(BaseModel):
    property_id: int
    name: str
    phone_number: int
    email: Optional[str] = None
    viewing_date: date
    viewing_time: time
    notes: Optional[str] = None

class BookingsCreate(Bookings):
    pass

class BookingsResp(Bookings):
    id: int
    # property: PropertyResp

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    id: Optional[str] = None
    landlord: bool


class MaintenanceRequest(BaseModel):
    property_id: int
    tenant_id: int
    request_date: date
    description: str
    status: Optional[str] = 'Pending'
    landlord_deleted: Optional[bool] = False
    tenant_deleted: Optional[bool] = False


class MaintenanceRequestResp(MaintenanceRequest):
    id: int
    tenant: TenantResp


class MaintenanceRequestCreate(MaintenanceRequest):
    pass