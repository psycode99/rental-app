from app import schemas
import pytest


def test_create_maintenance_request_authorized(authorized_tenant, test_approve_tenant, test_property, test_tenant):
    maintenance_req = {
      "property_id": test_property[0].id,
      "tenant_id": test_tenant['id'],
      "request_date": "2024-08-02",
      "description": "Leaky faucet in the kitchen.",
      "status": "Pending",
      "landlord_deleted": False,
      "tenant_deleted": False
    }

    res = authorized_tenant.post(f'/v1/maintenance_reqs/{test_property[0].id}', json=maintenance_req)
    new_entry = schemas.MaintenanceRequestResp(**res.json())
    assert res.status_code == 201
    assert new_entry.tenant_id == test_property[0].id


def test_create_maintenance_req_nonexistent_property(authorized_tenant, test_approve_tenant, test_tenant):
    maintenance_req = {
      "property_id": 9,
      "tenant_id": test_tenant['id'],
      "request_date": "2024-08-02",
      "description": "Leaky faucet in the kitchen.",
      "status": "Pending",
      "landlord_deleted": False,
      "tenant_deleted": False
    }

    res = authorized_tenant.post(f'/v1/maintenance_reqs/9', json=maintenance_req)
    assert res.status_code == 404
    

def test_create_maintenance_req_landlord(authorized_landlord, test_property, test_tenant, test_landlord):
    maintenance_req = {
      "property_id": test_property[0].id,
      "tenant_id": test_landlord['id'],
      "request_date": "2024-08-02",
      "description": "Leaky faucet in the kitchen.",
      "status": "Pending",
      "landlord_deleted": False,
      "tenant_deleted": False
    }

    res = authorized_landlord.post(f'/v1/maintenance_reqs/{test_property[0].id}', json=maintenance_req)
    assert res.status_code == 404


def test_create_maintenance_req_non_tenant(authorized_tenant2, test_property, test_approve_tenant, test_tenant2):
    maintenance_req = {
      "property_id": test_property[0].id,
      "tenant_id": test_tenant2['id'],
      "request_date": "2024-08-02",
      "description": "Leaky faucet in the kitchen.",
      "status": "Pending",
      "landlord_deleted": False,
      "tenant_deleted": False
    }

    res = authorized_tenant2.post(f'/v1/maintenance_reqs/{test_property[0].id}', json=maintenance_req)
    assert res.status_code == 403


def test_create_maintenance_request_nonmatching_prop_id(authorized_tenant, test_approve_tenant, test_property, test_tenant):
    maintenance_req = {
      "property_id": test_property[0].id,
      "tenant_id": test_tenant['id'],
      "request_date": "2024-08-02",
      "description": "Leaky faucet in the kitchen.",
      "status": "Pending",
      "landlord_deleted": False,
      "tenant_deleted": False
    }

    res = authorized_tenant.post(f'/v1/maintenance_reqs/{test_property[1].id}', json=maintenance_req)
    assert res.status_code == 403


def test_create_maintenance_request_unauthorized(client, test_approve_tenant, test_property, test_tenant):
    maintenance_req = {
      "property_id": test_property[0].id,
      "tenant_id": test_tenant['id'],
      "request_date": "2024-08-02",
      "description": "Leaky faucet in the kitchen.",
      "status": "Pending",
      "landlord_deleted": False,
      "tenant_deleted": False
    }

    res = client.post(f'/v1/maintenance_reqs/{test_property[0].id}', json=maintenance_req)
    assert res.status_code == 401


def test_get_maintenance_reqs_authorized(authorized_landlord, test_property, test_maintenance_reqs):
    res = authorized_landlord.get(f'/v1/maintenance_reqs/{test_property[0].id}')
    assert res.status_code == 200
    assert res.json()[0].get('property_id') == test_property[0].id


def test_get_maintenance_reqs_nonexistent_property(authorized_landlord):
    res = authorized_landlord.get(f'/v1/maintenance_reqs/9')
    assert res.status_code == 404


def test_get_maintenance_reqs_empty(authorized_landlord, test_property):
    res = authorized_landlord.get(f'/v1/maintenance_reqs/{test_property[0].id}')
    assert res.status_code == 204


def test_get_maintenance_reqs_unauthorized(client, test_property, test_maintenance_reqs):
    res = client.get(f'/v1/maintenance_reqs/{test_property[0].id}')
    assert res.status_code == 401


def test_get_maintenance_reqs_user_authorized(authorized_landlord, test_property, test_maintenance_reqs):
    res = authorized_landlord.get(f'/v1/maintenance_reqs/')
    assert res.status_code == 200
    assert res.json()[0].get('property_id') == test_property[0].id


def test_get_maintenance_reqs_user_empty(authorized_landlord):
    res = authorized_landlord.get(f'/v1/maintenance_reqs/')
    assert res.status_code == 204


def test_get_maintenance_reqs_user_unauthorized(client, test_maintenance_reqs):
    res = client.get(f'/v1/maintenance_reqs/')
    assert res.status_code == 401


def test_get_maintenance_req_authorized(authorized_landlord, test_property, test_maintenance_reqs):
    res = authorized_landlord.get(f'/v1/maintenance_reqs/{test_property[0].id}/{test_maintenance_reqs[0].id}')
    assert res.status_code == 200
    assert res.json().get('property_id') == test_property[0].id


def test_get_maintenance_req_nonexistent_property(authorized_landlord, test_maintenance_reqs):
    res = authorized_landlord.get(f'/v1/maintenance_reqs/9/{test_maintenance_reqs[0].id}')
    assert res.status_code == 404


def test_get_maintenance_req_nonexistent_req(authorized_landlord, test_property, test_maintenance_reqs):
    res = authorized_landlord.get(f'/v1/maintenance_reqs/{test_property[0].id}/9')
    assert res.status_code == 404


def test_get_maintenance_req_unauthorized(client, test_property, test_maintenance_reqs):
    res = client.get(f'/v1/maintenance_reqs/{test_property[0].id}/{test_maintenance_reqs[0].id}')
    assert res.status_code == 401


def test_update_maintenance_req_authorized(authorized_landlord, test_maintenance_reqs, test_property, test_tenant):
    maintenance_req = {
      "property_id": test_property[0].id,
      "tenant_id": test_tenant['id'],
      "request_date": "2024-08-02",
      "description": "Leaky faucet in the kitchen.",
      "status": "Completed",
      "landlord_deleted": False,
      "tenant_deleted": False
    }

    res = authorized_landlord.put(f'/v1/maintenance_reqs/{test_property[0].id}/{test_maintenance_reqs[0].id}', json=maintenance_req)
    assert res.status_code == 200
    assert res.json().get('status') == "Completed"


def test_update_maintenance_req_nonexistent_property(authorized_landlord, test_maintenance_reqs, test_property, test_tenant):
    maintenance_req = {
      "property_id": test_property[0].id,
      "tenant_id": test_tenant['id'],
      "request_date": "2024-08-02",
      "description": "Leaky faucet in the kitchen.",
      "status": "Completed",
      "landlord_deleted": False,
      "tenant_deleted": False
    }

    res = authorized_landlord.put(f'/v1/maintenance_reqs/9/{test_maintenance_reqs[0].id}', json=maintenance_req)
    assert res.status_code == 404


def test_update_maintenance_req_invalid_req(authorized_landlord, test_maintenance_reqs, test_property, test_tenant):
    maintenance_req = {
      "property_id": test_property[0].id,
      "tenant_id": test_tenant['id'],
      "request_date": "2024-08-02",
      "description": "Leaky faucet in the kitchen.",
      "status": "Completed",
      "landlord_deleted": False,
      "tenant_deleted": False
    }

    res = authorized_landlord.put(f'/v1/maintenance_reqs/{test_property[0].id}/9', json=maintenance_req)
    assert res.status_code == 404


def test_update_maintenance_req_wrong_user(authorized_landlord2, test_maintenance_reqs, test_property, test_tenant):
    maintenance_req = {
      "property_id": test_property[0].id,
      "tenant_id": test_tenant['id'],
      "request_date": "2024-08-02",
      "description": "Leaky faucet in the kitchen.",
      "status": "Completed",
      "landlord_deleted": False,
      "tenant_deleted": False
    }

    res = authorized_landlord2.put(f'/v1/maintenance_reqs/{test_property[0].id}/{test_maintenance_reqs[0].id}', json=maintenance_req)
    assert res.status_code == 403

   
def test_update_maintenance_req_unauthorized(client, test_maintenance_reqs, test_property, test_tenant):
    maintenance_req = {
      "property_id": test_property[0].id,
      "tenant_id": test_tenant['id'],
      "request_date": "2024-08-02",
      "description": "Leaky faucet in the kitchen.",
      "status": "Completed",
      "landlord_deleted": False,
      "tenant_deleted": False
    }

    res = client.put(f'/v1/maintenance_reqs/{test_property[0].id}/{test_maintenance_reqs[0].id}', json=maintenance_req)
    assert res.status_code == 401