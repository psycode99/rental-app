import datetime
from pydantic import BaseModel, EmailStr, Field


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

    class Config:
        from_attributes = True