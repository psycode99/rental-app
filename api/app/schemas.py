import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, constr, conint, field_validator, model_validator, root_validator
from typing import Optional, List, Literal, Annotated
from datetime import date, time, datetime, timedelta
from dateutil.relativedelta import relativedelta

class Property(BaseModel):
    address: str
    city: str
    state: str
    bedrooms: int
    bathrooms: float
    sqft: Optional[int] = None
    description: str
    price: float
    landlord_id: int
    status: Literal["available", "occupied", "under maintenance"] = "available"
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
    phone_number: str
    email: EmailStr
    password: str
    landlord: bool = False
    profile_pic: Optional[str] = None

    

class UserResp(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    created_at: datetime
    landlord: bool
    profile_pic: Optional[str] = None

    # class Config:
    #     from_attributes = True

class TenantResp(UserResp):
    tenant_application: List['TenantApplicationResp'] = []
    payments: List['PaymentResp'] = []
    pass

class PropertyResp(Property):
    model_config = ConfigDict(from_attributes=True)

    id: int
    landlord_id: int
    created_at: datetime
    # landlord: 'LandLordResp'
    bookings: List['BookingsResp'] = []
    maintenance_requests: List['MaintenanceRequestResp'] = []
    tenants : List[TenantResp] = []
    tenant_application : List['TenantApplicationResp'] = []
    payments: List['PaymentResp'] = []

    # class Config:
    #     from_attributes = True

class LandLordResp(UserResp):
    property: List[PropertyResp] = []

class Bookings(BaseModel):
    property_id: int
    name: str
    phone_number: str
    email: Optional[str] = None
    viewing_date: date
    viewing_time: time
    notes: Optional[str] = None

class BookingsCreate(Bookings):
    pass

class BookingsResp(Bookings):
    model_config = ConfigDict(from_attributes=True)
    id: int
    # property: PropertyResp

    # class Config:
    #     from_attributes = True


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

class TenantApplication(BaseModel):
    tenant_id: int
    property_id: int
    first_name: Annotated[str, 'First name of the tenant']
    last_name: Annotated[str, 'Last name of the tenant']
    date_of_birth: Annotated[date, 'Date of birth of the tenant']
    national_identity_number: Annotated[str, 'Social security number of the tenant', 
                                      lambda s: len(str(s)) == 11 and str(s).isdigit()]
    
    email_address: Annotated[EmailStr, 'Email address of the tenant']
    phone_number: Annotated[str, 'Phone number of the tenant']
    current_address: Annotated[str, 'Current address of the tenant']
    previous_address: Optional[Annotated[str, 'Previous address of the tenant']]
    
    employer_name: Annotated[str, 'Name of the tenant\'s employer']
    job_title: Annotated[str, 'Job title of the tenant']
    employment_duration: Annotated[int, 'Duration of employment in months', 
                                          conint(gt=0)]
    monthly_income: Annotated[float, 'Monthly income of the tenant']
    
    previous_landlord_name: Optional[Annotated[str, 'Name of the previous landlord']]
    previous_landlord_contact: Optional[Annotated[str, 'Contact information of the previous landlord']]
    reason_for_moving: Optional[Annotated[str, 'Reason for moving']]
    
    personal_reference_name: Optional[Annotated[str, 'Name of personal reference']]
    personal_reference_contact: Optional[Annotated[str, 'Contact information of personal reference']]
    professional_reference_name: Optional[Annotated[str, 'Name of professional reference']]
    professional_reference_contact: Optional[Annotated[str, 'Contact information of professional reference']]
    
    application_date: Annotated[date, 'Date of application']
    desired_move_in_date: Annotated[date, 'Desired move-in date']
    application_status: Annotated[Literal['pending', 'approved', 'rejected'], 'Application status'] = 'pending'
    
    # credit_score: Optional[Annotated[int, 'Credit score of the tenant', conint(ge=300, le=850)]]
    criminal_record: Optional[Annotated[str, 'Details of any criminal record']]
    # background_check_status: Optional[Annotated[Literal['completed', 'pending'], 'Background check status']]
    
    pets: Optional[Annotated[str, 'Pets owned by the tenant']]
    number_of_occupants: Annotated[int, 'Number of occupants', conint(gt=0)]
    special_requests: Optional[Annotated[str, 'Any special requests or notes']]
    file_name: Optional[str] = None


class TenantApplicationCreate(TenantApplication):
    pass


class TenantApplicationResp(TenantApplication):
    model_config = ConfigDict(from_attributes=True)

    id: int

    
    # class Config:
    #     from_attributes = True

class TenantApplicationStatus(BaseModel):
    tenant_id: int
    application_status: Annotated[Literal['pending', 'approved', 'rejected'], 'Application status']


class Payment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    tenant_id: Annotated[int, Field(ge=1)]
    property_id: Annotated[int, Field(ge=1)]
    amount: Annotated[float, Field(ge=0)]
    duration_months: Annotated[int, Field(ge=1)]
    due_date: date
    payment_date: Optional[datetime] = None
    # status: Annotated[PaymentStatus, Field(default=PaymentStatus.pending)]
    
    # class Config:
    #     from_attributes = True

    @field_validator('duration_months')
    @classmethod
    def validate_duration(cls, v):
        if v < 1:
            raise ValueError('duration_months must be at least 1')
        return v
    

class PaymentResp(Payment):
     model_config = ConfigDict(from_attributes=True)
    #  class Config:
    #     from_attributes = True
    
class PaymentCreate(BaseModel):
    tenant_id: Annotated[int, Field(ge=1)]
    property_id: Annotated[int, Field(ge=1)]
    amount: Annotated[float, Field(ge=0)]
    duration_months: Annotated[int, Field(ge=1)]

    @field_validator('duration_months')
    @classmethod
    def validate_duration(cls, v):
        if v < 1:
            raise ValueError('duration_months must be at least 1')
        return v

    @model_validator(mode='before')
    @classmethod
    def compute_due_date(cls, values):
        duration_months = values.get('duration_months')
        if duration_months is not None:
            values['due_date'] = datetime.now().date() + relativedelta(months=duration_months)
        return values
    

class PropertyTenantResp(BaseModel):
    property_id: int
    tenant_id: int


class ForgotPasswordOTP(BaseModel):
    otp: str
    email: str


class ForgotPasswordEmail(BaseModel):
    email: str


class VerifyOTP(BaseModel):
    otp: str
    typed_otp: str
    email: str


class ResetPassword(BaseModel):
    email: str
    new_password: str