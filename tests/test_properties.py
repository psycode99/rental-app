from app import schemas
import pytest


def test_create_property(test_landlord, authorized_landlord):
    property_data = {
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
    }

    res = authorized_landlord.post('/v1/properties', json=property_data)
    new_property = schemas.PropertyResp(**res.json())
    
    assert new_property.state == "SC"
    assert new_property.landlord_id == test_landlord['id']
    assert res.status_code == 201



def test_create_property_forbidden(test_tenant, authorized_tenant):
    property_data = {
      "landlord_id": test_tenant['id'],
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
    }

    res = authorized_tenant.post('/v1/properties', json=property_data)
    assert res.status_code == 403


def test_create_property_unauthorized(test_landlord, client):
    property_data = {
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
    }

    res = client.post('/v1/properties', json=property_data)
    assert res.status_code == 401


def test_get_properties(client, test_property):
    res = client.get('/v1/properties')
    assert res.status_code == 200
    assert res.json()[0].get('bedrooms') == 3


def test_get_property(client, test_property):
    res = client.get(f'/v1/properties/{test_property[0].id}')
    assert res.status_code == 200
    assert res.json().get('bedrooms') == 3


def test_delete_property_authorized(authorized_landlord, test_property, test_booking, test_tenant_applications, test_payments, test_maintenance_reqs ):
    res = authorized_landlord.delete(f"/v1/properties/{test_property[0].id}")
    assert res.status_code == 204


def test_delete_property_authorized_nonexistent_property(authorized_landlord, test_property):
    res = authorized_landlord.delete(f"/v1/properties/7")
    assert res.status_code == 404


def test_delete_property_authorized_wrong_property(authorized_landlord2, test_property):
    res = authorized_landlord2.delete(f"/v1/properties/{test_property[0].id}")
    assert res.status_code == 403


def test_delete_property_authorized_tenant(authorized_tenant, test_property):
    res = authorized_tenant.delete(f"/v1/properties/{test_property[0].id}")
    assert res.status_code == 401


def test_delete_property_unauthorized(client, test_property):
    res = client.delete(f"/v1/properties/{test_property[0].id}")
    assert res.status_code == 401


def test_update_property_authorized(authorized_landlord, test_landlord, test_property):
    property_data = {
      "landlord_id": test_landlord['id'],
      "address": "123 Elm St",
      "bedrooms": 5,
      "bathrooms": 2.5,
      "sqft": 1500,
      "price": 450000.0,
      "city": "Sample City",
      "state": "SC",
      "description": "A lovely 3-bedroom house.",
      "status": "available",
      "file_1": "path/to/file1.jpg",
      "file_2": "path/to/file2.jpg",
      "file_3": "path/to/file3.jpg"
    }

    res = authorized_landlord.put(f'/v1/properties/{test_property[0].id}', json=property_data)
    updated_data = schemas.PropertyResp(**res.json())
    assert updated_data.price == 450000.0
    assert res.status_code == 200
    assert res.json().get('bedrooms') == 5


def test_update_property_authorized_nonexistent_property(authorized_landlord, test_landlord, test_property):
    property_data = {
      "landlord_id": test_landlord['id'],
      "address": "123 Elm St",
      "bedrooms": 5,
      "bathrooms": 2.5,
      "sqft": 1500,
      "price": 450000.0,
      "city": "Sample City",
      "state": "SC",
      "description": "A lovely 3-bedroom house.",
      "status": "available",
      "file_1": "path/to/file1.jpg",
      "file_2": "path/to/file2.jpg",
      "file_3": "path/to/file3.jpg"
    }

    res = authorized_landlord.put(f'/v1/properties/9', json=property_data)
    assert res.status_code == 404


def test_update_property_authorized_tenant(authorized_tenant, test_landlord, test_property):
    property_data = {
      "landlord_id": test_landlord['id'],
      "address": "123 Elm St",
      "bedrooms": 5,
      "bathrooms": 2.5,
      "sqft": 1500,
      "price": 450000.0,
      "city": "Sample City",
      "state": "SC",
      "description": "A lovely 3-bedroom house.",
      "status": "available",
      "file_1": "path/to/file1.jpg",
      "file_2": "path/to/file2.jpg",
      "file_3": "path/to/file3.jpg"
    }

    res = authorized_tenant.put(f'/v1/properties/{test_property[0].id}', json=property_data)
    assert res.status_code == 401


def test_update_property_authorized_wrong_property(authorized_landlord2, test_landlord2, test_property):
    property_data = {
      "landlord_id": test_landlord2['id'],
      "address": "123 Elm St",
      "bedrooms": 5,
      "bathrooms": 2.5,
      "sqft": 1500,
      "price": 450000.0,
      "city": "Sample City",
      "state": "SC",
      "description": "A lovely 3-bedroom house.",
      "status": "available",
      "file_1": "path/to/file1.jpg",
      "file_2": "path/to/file2.jpg",
      "file_3": "path/to/file3.jpg"
    }

    res = authorized_landlord2.put(f'/v1/properties/{test_property[0].id}', json=property_data)
    assert res.status_code == 403


def test_update_property_unauthorized(client, test_landlord, test_property):
    property_data = {
      "landlord_id": test_landlord['id'],
      "address": "123 Elm St",
      "bedrooms": 5,
      "bathrooms": 2.5,
      "sqft": 1500,
      "price": 450000.0,
      "city": "Sample City",
      "state": "SC",
      "description": "A lovely 3-bedroom house.",
      "status": "available",
      "file_1": "path/to/file1.jpg",
      "file_2": "path/to/file2.jpg",
      "file_3": "path/to/file3.jpg"
    }

    res = client.put(f'/v1/properties/{test_property[0].id}', json=property_data)
    assert res.status_code == 401