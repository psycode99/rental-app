from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import TIMESTAMP, ForeignKey, text, Boolean,  Integer, Column, String, Date, Time, Float, Text
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    first_name = Column(String, nullable=False, unique=False)
    last_name = Column(String, nullable=False, unique=False)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=False, unique=True)

    password = Column(String, unique=False, nullable=False)
    landlord = Column(Boolean, default=False)
    profile_pic = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)


class LandLord(Base):
    __tablename__ = 'landlords'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    first_name = Column(String, nullable=False, unique=False)
    last_name = Column(String, nullable=False, unique=False)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=False, unique=True)

    landlord = Column(Boolean, default=True)
    password = Column(String, unique=False, nullable=False)
    profile_pic = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    property = relationship("Property", back_populates="landlord", passive_deletes=True)

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    first_name = Column(String, nullable=False, unique=False)
    last_name = Column(String, nullable=False, unique=False)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=False, unique=True)

    landlord = Column(Boolean, default=False)
    password = Column(String, unique=False, nullable=False)
    profile_pic = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    payments = relationship('Payment', back_populates='tenant', passive_deletes=True)
    maintenance_requests = relationship("MaintenanceRequest", back_populates="tenant", passive_deletes=True)
    properties = relationship('Property', secondary='property_tenants', back_populates='tenants', passive_deletes=True)
    # properties = relationship('Property', back_populates='tenants')
    tenant_application = relationship("TenantApplication", back_populates="tenant", passive_deletes=True)


class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    landlord_id = Column(Integer, ForeignKey('landlords.id', ondelete="CASCADE"), nullable=False)
    address = Column(String, unique=False, nullable=False)
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Float, nullable=False)

    sqft  = Column(Integer, nullable=True)
    price = Column(Float, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, nullable=False, default="available")
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    file_1 = Column(String, nullable=True)
    file_2 = Column(String, nullable=True)
    file_3 = Column(String, nullable=True)
    # file_4 = Column(String, nullable=False)
    # file_5 = Column(String, nullable=False)

    payments = relationship('Payment', back_populates='property', passive_deletes=True)
    landlord = relationship("LandLord", back_populates="property")
    bookings = relationship("Booking", back_populates="property", passive_deletes=True)
    maintenance_requests = relationship("MaintenanceRequest", back_populates="property", passive_deletes=True)
    tenants = relationship('Tenant', secondary='property_tenants', back_populates='properties', passive_deletes=True)
    # tenants = relationship('Tenant', back_populates='properties')
    tenant_application = relationship("TenantApplication", back_populates="property", passive_deletes=True)


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey('properties.id', ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=False)
    viewing_date = Column(Date, nullable=False)
    viewing_time = Column(Time, nullable=False)
    notes = Column(Text, nullable=True)

    property = relationship("Property", back_populates="bookings")


class MaintenanceRequest(Base):
    __tablename__ = 'maintenance_requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey('properties.id', ondelete="CASCADE"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)  # Assuming tenant_id is an integer; adjust if necessary
    request_date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default='Pending')  # E.g., Pending, In Progress, Completed
    landlord_deleted = Column(Boolean, default=False)
    tenant_deleted = Column(Boolean, default=False)

    property = relationship("Property", back_populates="maintenance_requests")
    tenant = relationship("Tenant", back_populates="maintenance_requests")


class PropertyTenant(Base):
    __tablename__ = 'property_tenants'
    tenant_id = Column(Integer, ForeignKey('tenants.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    property_id = Column(Integer, ForeignKey('properties.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    # landlord_removed = Column(Boolean, default=False)
    # tenant = relationship("Tenant", back_populates="properties")
    # property = relationship("Property", back_populates="tenant")


class TenantApplication(Base):
    __tablename__ = 'tenant_applications'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    national_identity_number = Column(String(11), nullable=False)
    
    email_address = Column(String(100), nullable=False)
    phone_number = Column(String(15), nullable=False)
    current_address = Column(String(200), nullable=False)
    previous_address = Column(String(200))
    
    employer_name = Column(String(100), nullable=False)
    job_title = Column(String(100), nullable=False)
    employment_duration = Column(Integer, nullable=False)
    monthly_income = Column(Float, nullable=False)
    
    previous_landlord_name = Column(String(100))
    previous_landlord_contact = Column(String(100))
    reason_for_moving = Column(String(200))
    
    personal_reference_name = Column(String(100))
    personal_reference_contact = Column(String(100))
    professional_reference_name = Column(String(100))
    professional_reference_contact = Column(String(100))
    
    application_date = Column(Date, nullable=False)
    desired_move_in_date = Column(Date, nullable=False)
    property_id = Column(Integer, ForeignKey('properties.id', ondelete="CASCADE"), nullable=False )
    application_status = Column(String, nullable=False, default="pending")
    
    # credit_score = Column(Integer)
    criminal_record = Column(String(200))
    # background_check_status = Column(Enum('completed', 'pending', name='background_check_status'))
    
    pets = Column(String(200))
    number_of_occupants = Column(Integer, nullable=False)
    special_requests = Column(String(200))
    file_name = Column(String)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)


    tenant = relationship("Tenant", back_populates="tenant_application")
    property = relationship("Property", back_populates="tenant_application")


class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    tenant_id = Column(Integer, ForeignKey('tenants.id', ondelete="CASCADE"), nullable=False)
    property_id = Column(Integer, ForeignKey('properties.id', ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)

    duration_months = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    payment_date = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    # status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)

    tenant = relationship('Tenant', back_populates='payments')
    property = relationship('Property', back_populates='payments')

    def __init__(self, tenant_id, property_id, amount, duration_months):
        self.tenant_id = tenant_id
        self.property_id = property_id
        self.amount = amount
        self.duration_months = duration_months
        self.due_date = (datetime.now() + relativedelta(months=duration_months)).date() # Approximate months by 30 days
