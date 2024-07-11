from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import TIMESTAMP, ForeignKey, text, Boolean, Integer, Column, String, Date, Time, Float, Text


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False, unique=False)
    last_name = Column(String, nullable=False, unique=False)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(Integer, nullable=False, unique=True)
    password = Column(String, unique=False, nullable=False)
    landlord = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)


class LandLord(Base):
    __tablename__ = 'landlords'
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False, unique=False)
    last_name = Column(String, nullable=False, unique=False)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(Integer, nullable=False, unique=True)
    landlord = Column(Boolean, default=True)
    password = Column(String, unique=False, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    property = relationship("Property", back_populates="landlord")

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False, unique=False)
    last_name = Column(String, nullable=False, unique=False)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(Integer, nullable=False, unique=True)
    landlord = Column(Boolean, default=False)
    password = Column(String, unique=False, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    maintenance_requests = relationship("MaintenanceRequest", back_populates="tenant")


class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, nullable=False)
    landlord_id = Column(Integer, ForeignKey('landlords.id', ondelete="CASCADE"), nullable=False)
    address = Column(String, unique=False, nullable=False)
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Float, nullable=False)
    sqft  = Column(Integer, nullable=True)
    price = Column(Float, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    file_1 = Column(String, nullable=True)
    file_2 = Column(String, nullable=True)
    file_3 = Column(String, nullable=True)
    # file_4 = Column(String, nullable=False)
    # file_5 = Column(String, nullable=False)

    landlord = relationship("LandLord", back_populates="property")
    bookings = relationship("Booking", back_populates="property")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="property")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone_number = Column(Integer, nullable=False)
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

    property = relationship("Property", back_populates="maintenance_requests")
    tenant = relationship("Tenant", back_populates="maintenance_requests")