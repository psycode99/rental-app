from fastapi.testclient import TestClient
from app.main import app
from app import models, schemas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db, Base
from app.oauth import create_access_token
import pytest

DATABASE_URL = f"postgresql://postgres:wordpress@localhost:5432/rental-mgt_test"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
TestSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@pytest.fixture(scope="function")
def session():
    """
    it deletes the previous tables when a new test is started.
    It then creates the new database tables before our code is run
    
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    """
    this creates a new session via the TestSessionLocal
    and stores it in the db variable and then yields this db variable back.
    We can then use the new session via the db variable to query the database.
    """
    db = TestSessionLocal() 
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app=app)


@pytest.fixture
def test_landlord(client):
    user_data =   {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "phone_number": "1234567890",
      "landlord": True,
      "password": "1234",
      "profile_pic": "path/to/profile_pic.jpg"
    }
    res = client.post('/v1/users', json=user_data)
    assert res.status_code == 201
    new_landlord = res.json()
    new_landlord['password'] = user_data['password']
    return new_landlord


@pytest.fixture
def test_landlord2(client):
    user_data =   {
      "first_name": "James",
      "last_name": "Smith",
      "email": "james.smith@example.com",
      "phone_number": "12314567890",
      "landlord": True,
      "password": "1234",
      "profile_pic": "path/to/profile_pic.jpg"
    }
    res = client.post('/v1/users', json=user_data)
    assert res.status_code == 201
    new_landlord = res.json()
    new_landlord['password'] = user_data['password']
    return new_landlord


@pytest.fixture
def test_tenant(client):
    user_data =   {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone_number": "1234567891",
        "password": "1234",
        "profile_pic": "path/to/profile_pic.jpg"
    }
    res = client.post('/v1/users', json=user_data)
    assert res.status_code == 201
    new_tenant = res.json()
    new_tenant['password'] = user_data['password']
    return new_tenant


@pytest.fixture
def test_tenant2(client):
    user_data =   {
        "first_name": "Jennifer",
        "last_name": "Stone",
        "email": "jenny.stone@example.com",
        "phone_number": "134567891",
        "password": "1234",
        "profile_pic": "path/to/profile_pic.jpg"
    }
    res = client.post('/v1/users', json=user_data)
    assert res.status_code == 201
    new_tenant = res.json()
    new_tenant['password'] = user_data['password']
    return new_tenant


@pytest.fixture
def token_landlord(test_landlord):
    return create_access_token({
        "user_id": test_landlord['id'],
        "landlord": True
    })


@pytest.fixture
def token_landlord2(test_landlord2):
    return create_access_token({
        "user_id": test_landlord2['id'],
        "landlord": True
    })



@pytest.fixture
def token_tenant(test_tenant):
    return create_access_token({
        "user_id": test_tenant['id'],
        "landlord": False
    })


@pytest.fixture
def token_tenant2(test_tenant2):
    return create_access_token({
        "user_id": test_tenant2['id'],
        "landlord": False
    })


@pytest.fixture
def authorized_landlord(client, token_landlord):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token_landlord}"
    }
    return client


@pytest.fixture
def authorized_landlord2(client, token_landlord2):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token_landlord2}"
    }
    return client


@pytest.fixture
def authorized_tenant(client, token_tenant):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token_tenant}"
    }
    return client

@pytest.fixture
def authorized_tenant2(client, token_tenant2):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token_tenant2}"
    }
    return client


@pytest.fixture
def test_property(test_landlord, test_landlord2, session):
    property_data =[
    {
      "landlord_id": test_landlord['id'],
      "address": "123 Elm St",
      "bedrooms": 3,
      "bathrooms": 2.5,
      "sqft": 1500,
      "price": 250000.0,
      "city": "Sample City",
      "state": "SC",
      "description": "A lovely 3-bedroom house.",
      "status": "available",
      "file_1": "path/to/file1.jpg",
      "file_2": "path/to/file2.jpg",
      "file_3": "path/to/file3.jpg"
    },
    {
      "landlord_id": test_landlord2['id'],
      "address": "456 Oak St",
      "bedrooms": 4,
      "bathrooms": 3.5,
      "sqft": 2000,
      "price": 350000.0,
      "city": "Another City",
      "state": "AC",
      "description": "A spacious 4-bedroom house.",
      "status": "available",
      "file_1": "path/to/file1.jpg",
      "file_2": "path/to/file2.jpg",
      "file_3": "path/to/file3.jpg"
    }
    ]

    def property_model(property):
        return models.Property(**property)
    

    property_mapping = map(property_model, property_data)
    session.add_all(list(property_mapping))
    session.commit()
    properties = session.query(models.Property).all()
    return properties


@pytest.fixture
def test_booking(session, test_property):
    booking_data = {
      "property_id": test_property[0].id,
      "name": "Alice Johnson",
      "email": "alice.johnson@example.com",
      "phone_number": "1231231234",
      "viewing_date": "2024-08-07",
      "viewing_time": "15:30:00",
      "notes": "Looking forward to seeing the property."
    }

    new_booking = models.Booking(**booking_data)
    session.add(new_booking)
    session.commit()
    

@pytest.fixture
def test_tenant_applications(session, test_tenant, test_property):
    application_data = {
      "tenant_id": test_tenant['id'],
      "first_name": "Jane",
      "last_name": "Smith",
      "date_of_birth": "1990-05-15",
      "national_identity_number": "12345678901",
      "email_address": "jane.smith@example.com",
      "phone_number": "0987654321",
      "current_address": "789 Maple St",
      "previous_address": "789 Old St",
      "employer_name": "Sample Employer",
      "job_title": "Software Developer",
      "employment_duration": 3,
      "monthly_income": 5000.0,
      "previous_landlord_name": "Old Landlord",
      "previous_landlord_contact": "1112223333",
      "reason_for_moving": "New job",
      "personal_reference_name": "Friend",
      "personal_reference_contact": "4445556666",
      "professional_reference_name": "Manager",
      "professional_reference_contact": "7778889999",
      "application_date": "2024-08-02",
      "desired_move_in_date": "2024-09-01",
      "property_id": test_property[0].id,
      "application_status": "pending",
      "criminal_record": "None",
      "pets": "None",
      "number_of_occupants": 1,
      "special_requests": "None",
      "file_name": "resume.pdf"
    }

    new_app = models.TenantApplication(**application_data)
    session.add(new_app)
    session.commit()
    application = session.query(models.TenantApplication).filter_by(id=1).first()
    return application


@pytest.fixture
def test_approve_tenant(session, test_tenant_applications, test_landlord):
    test_tenant_applications.status = "approved"
    session.commit()
    prop_tenant = models.PropertyTenant(tenant_id=test_tenant_applications.tenant_id,
                                        property_id=test_tenant_applications.property_id)
    session.add(prop_tenant)
    session.commit()


@pytest.fixture
def test_maintenance_reqs(session, test_tenant, test_property, test_approve_tenant):
    maintenance_req_data =  {
      "property_id": test_property[0].id,
      "tenant_id": test_tenant['id'],
      "request_date": "2024-08-02",
      "description": "Leaky faucet in the kitchen.",
      "status": "Pending",
      "landlord_deleted": False,
      "tenant_deleted": False
    }

    new_req = models.MaintenanceRequest(**maintenance_req_data)
    session.add(new_req)
    session.commit()
    reqs = session.query(models.MaintenanceRequest).all()
    return reqs


@pytest.fixture
def test_payments(session, test_property, test_tenant, test_approve_tenant):
    payment_data = {
      "tenant_id": test_tenant['id'],
      "property_id": test_property[0].id,
      "amount": 1200.0,
      "duration_months": 12,
    #   "due_date": "2025-08-02",
    #   "payment_date": "2024-08-02T12:00:00"
    }

    new_payment = models.Payment(**payment_data)
    session.add(new_payment)
    session.commit()


