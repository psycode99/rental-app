from app import schemas
import pytest
from jose import jwt
from app.oauth import SECRET_KEY, ALGORITHM
from fastapi import HTTPException

from tests.conftest import authorized_landlord2, client

def test_root(client):
    res = client.get('/')
    assert res.status_code == 200
    assert res.json().get('message') == "rental api"


def test_create_landlord(client):
    landlord_data = {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "phone_number": "1234567890",
      "landlord": True,
      "password": "1234",
      "profile_pic": "path/to/profile_pic.jpg"
    }
    res = client.post('/v1/users', json=landlord_data)
    new_landlord = schemas.LandLordResp(**res.json())
    assert new_landlord.email == "john.doe@example.com"
    assert res.status_code == 201


def test_create_tenant(client):
    tenant_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone_number": "1234567891",
        "password": "1234",
        "profile_pic": "path/to/profile_pic.jpg"
    }
    res = client.post('/v1/users', json=tenant_data)
    new_tenant = schemas.TenantResp(**res.json())
    assert new_tenant.email == "jane.smith@example.com"
    assert res.status_code == 201


def test_create_same_user(client, test_tenant):
    user_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone_number": "1234567891",
        "password": "1234",
        "profile_pic": "path/to/profile_pic.jpg"
    }
    res = client.post('/v1/users', json=user_data)
    assert res.status_code == 409


def test_get_tenants(client, test_tenant, test_property, test_tenant_applications, test_approve_tenant):
    res = client.get(f'/v1/users/{test_property[0].id}')
    assert res.status_code == 200
    assert res.json()[0].get('email') == "jane.smith@example.com"


def test_get_tenant(client, test_tenant):
    res = client.get(f"/v1/users/tenants/{test_tenant['id']}")
    assert res.status_code == 200
    assert res.json().get('email') == "jane.smith@example.com"


def test_get_landlord(client, test_landlord):
    res = client.get(f"/v1/users/landlords/{test_landlord['id']}")
    assert res.status_code == 200
    assert res.json().get('email') == "john.doe@example.com"


def test_remove_tenant(authorized_landlord, test_tenant, test_property, test_tenant_applications, test_approve_tenant):
    res = authorized_landlord.delete(f'/v1/users/{test_property[0].id}/{test_tenant["id"]}')
    assert res.status_code == 204


def test_remove_tenant_unauthorized(client, test_tenant, test_property, test_tenant_applications, test_approve_tenant):
    res = client.delete(f'/v1/users/{test_property[0].id}/{test_tenant["id"]}')
    assert res.status_code == 401


def test_remove_tenant_unauthorized_landlord(authorized_landlord2, test_tenant, test_property, test_tenant_applications, test_approve_tenant):
    res = authorized_landlord2.delete(f'/v1/users/{test_property[0].id}/{test_tenant["id"]}')
    assert res.status_code == 401


def test_update_user(authorized_landlord, test_landlord):
    user_data =   {
      "first_name": "Jon",
      "last_name": "Doe",
      "email": "jon.doe@example.com",
      "phone_number": "1234567890",
      "landlord": True,
      "password": "1234",
      "profile_pic": "path/to/profile_pic.jpg"
    }
    res = authorized_landlord.put(f'/v1/users/{test_landlord["id"]}', json=user_data)
    assert res.status_code == 200
    assert res.json().get('first_name') == "Jon"


@pytest.mark.parametrize("first_name, last_name, email, phone_number, landlord, password, status_code",[
    ("Jon", "Doe", "john.doe@example.com", "1234567890", True, "1234", 403),
    ("Jon", "Doe", "jo.doe@example.com", "1234567890", True, "1234", 403),
    ("Jon", "Doe", "jo.doe@example.com", "123456789", True, "1234", 401)
])
def test_update_user_authorized_wrong_user(test_landlord, test_landlord2, authorized_landlord2, first_name, last_name, 
                                  email, phone_number, landlord, password, status_code):
    user_data =   {
      "first_name": first_name,
      "last_name": last_name,
      "email": email,
      "phone_number": phone_number,
      "landlord": landlord,
      "password": password
    }
    res = authorized_landlord2.put(f'/v1/users/{test_landlord["id"]}', json=user_data)
    assert res.status_code == status_code


@pytest.mark.parametrize("first_name, last_name, email, phone_number, landlord, password, status_code",[
    ("Jon", "Doe", "john.doe@example.com", "1234567890", True, "1234", 401),
    ("Jon", "Doe", "jo.doe@example.com", "1234567890", True, "1234", 401),
    ("Jon", "Doe", "jo.doe@example.com", "123456789", True, "1234", 401)
])
def test_update_user_unauthorized_user(test_landlord, test_landlord2, client, first_name, last_name, 
                                  email, phone_number, landlord, password, status_code):
    user_data =   {
      "first_name": first_name,
      "last_name": last_name,
      "email": email,
      "phone_number": phone_number,
      "landlord": landlord,
      "password": password
    }
    res = client.put(f'/v1/users/{test_landlord["id"]}', json=user_data)
    assert res.status_code == status_code



def test_delete_user_authorized(authorized_landlord, test_landlord, test_property, test_payments):
    res = authorized_landlord.delete(f'/v1/users/{test_landlord["id"]}')
    assert res.status_code == 204


def test_delete_user_wrong_auth_user(authorized_landlord2, test_landlord, test_property, test_payments):
    res = authorized_landlord2.delete(f'/v1/users/{test_landlord["id"]}')
    assert res.status_code == 401



@pytest.mark.parametrize("user_id, status_code", [
    (3, 401),
    (6, 401)
])
def test_delete_user_fail(authorized_landlord2, client, user_id, status_code, test_landlord, test_property, test_payments):
    if status_code == 401:
        res = authorized_landlord2.delete(f'/v1/users/{user_id}')
        assert res.status_code == status_code
    elif status_code == 6:
        res = client.delete(f'/v1/users/{user_id}')
        assert res.status_code == status_code
    