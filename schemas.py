import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: int
    email: EmailStr
    password: str
    landlord: bool = Field(False)


class UserResp(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    created_at: datetime.datetime
    landlord: bool

    class Config:
        from_attributes = True


class Property(BaseModel):
    address: str
    city: str
    state: str
    bedrooms: int
    bathrooms: float
    sqft: int
    description: str
    price: float


class PropertyCreate(Property):
    pass


class PropertyResp(Property):
    id: int
    landlord_id: int
    created_at: datetime.datetime
    landlord: UserResp

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    id: Optional[str] = None 