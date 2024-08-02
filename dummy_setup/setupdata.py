from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
from app.utils import hash_pwd
from app.models import Base, Users, LandLord, Tenant, Property, TenantApplication, Payment, MaintenanceRequest, Booking

# Replace with your actual database URL
DATABASE_URL = f"postgresql://postgres:wordpress@localhost:5432/rental-mgt"

# Create an engine
engine = create_engine(DATABASE_URL)

# Create tables based on the defined models
Base.metadata.create_all(engine)

# Create a session
session = Session(bind=engine)

# Dummy data
try:
    # Add a landlord
    landlord_user = Users(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        password=hash_pwd("1234"),
        landlord=True,
        profile_pic="path/to/profile_pic.jpg",
        created_at=datetime.now()
    )
    session.add(landlord_user)
    session.flush()  # To get the user ID

    landlord = LandLord(
        # id=landlord_user.id,  # Ensure the landlord ID matches the user ID
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        password=hash_pwd("1234"),
        profile_pic="path/to/profile_pic.jpg",
        created_at=datetime.now()
    )
    session.add(landlord)
    session.flush()  # To get the landlord ID

    # Add properties
    property_1 = Property(
        landlord_id=landlord.id,
        address="123 Elm St",
        bedrooms=3,
        bathrooms=2.5,
        sqft=1500,
        price=250000.0,
        city="Sample City",
        state="SC",
        description="A lovely 3-bedroom house.",
        status="available",
        created_at=datetime.now(),
        file_1="path/to/file1.jpg",
        file_2="path/to/file2.jpg",
        file_3="path/to/file3.jpg"
    )
    session.add(property_1)

    property_2 = Property(
        landlord_id=landlord.id,
        address="456 Oak St",
        bedrooms=4,
        bathrooms=3.5,
        sqft=2000,
        price=350000.0,
        city="Another City",
        state="AC",
        description="A spacious 4-bedroom house.",
        status="available",
        created_at=datetime.now(),
        file_1="path/to/file1.jpg",
        file_2="path/to/file2.jpg",
        file_3="path/to/file3.jpg"
    )
    session.add(property_2)
    session.flush()  # To get property IDs

    # Add a tenant
    tenant_user = Users(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        phone_number="0987654321",
        password=hash_pwd("1234"),
        landlord=False,
        profile_pic="path/to/profile_pic.jpg",
        created_at=datetime.now()
    )
    session.add(tenant_user)
    session.flush()  # To get the user ID

    tenant = Tenant(
        # id=tenant_user.id,  # Ensure the tenant ID matches the user ID
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        phone_number="0987654321",
        password=hash_pwd("1234"),
        profile_pic="path/to/profile_pic.jpg",
        created_at=datetime.now()
    )
    session.add(tenant)
    session.flush()  # To get tenant ID

    # Add tenant applications
    application = TenantApplication(
        tenant_id=tenant.id,
        first_name=tenant.first_name,
        last_name=tenant.last_name,
        date_of_birth=date(1990, 5, 15),
        national_identity_number="12345678901",
        email_address=tenant.email,
        phone_number=tenant.phone_number,
        current_address="789 Maple St",
        previous_address="789 Old St",
        employer_name="Sample Employer",
        job_title="Software Developer",
        employment_duration=3,
        monthly_income=5000.0,
        previous_landlord_name="Old Landlord",
        previous_landlord_contact="1112223333",
        reason_for_moving="New job",
        personal_reference_name="Friend",
        personal_reference_contact="4445556666",
        professional_reference_name="Manager",
        professional_reference_contact="7778889999",
        application_date=date.today(),
        desired_move_in_date=date.today() + timedelta(days=30),
        property_id=property_1.id,
        application_status="pending",
        criminal_record="None",
        pets="None",
        number_of_occupants=1,
        special_requests="None",
        file_name="resume.pdf",
        created_at=datetime.now()
    )
    session.add(application)

    # Add a payment
    payment = Payment(
        tenant_id=tenant.id,
        property_id=property_1.id,
        amount=1200.0,
        duration_months=12,
        # due_date=datetime.now().date() + relativedelta(months=12),
        # payment_date=datetime.now()
    )
    session.add(payment)

    # Add maintenance request
    maintenance_request = MaintenanceRequest(
        property_id=property_1.id,
        tenant_id=tenant.id,
        request_date=date.today(),
        description="Leaky faucet in the kitchen.",
        status="Pending",
        landlord_deleted=False,
        tenant_deleted=False
    )
    session.add(maintenance_request)

    # Add a booking
    booking = Booking(
        property_id=property_1.id,
        name="Alice Johnson",
        email="alice.johnson@example.com",
        phone_number="1231231234",
        viewing_date=date.today() + timedelta(days=5),
        viewing_time=time(15, 30),  # 3:30 PM
        notes="Looking forward to seeing the property."
    )
    session.add(booking)

    # Commit the transactions
    session.commit()

except Exception as e:
    session.rollback()
    print(f"An error occurred: {e}")
finally:
    session.close()
