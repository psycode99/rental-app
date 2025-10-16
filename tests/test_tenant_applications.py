import pytest
from ..app import schemas


def test_create_tenant_application_authorized(authorized_tenant, test_property, test_tenant):
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

    res = authorized_tenant.post(f'/v1/applications/{test_property[0].id}', json=application_data)
    new_app = schemas.TenantApplicationResp(**res.json())
    assert res.status_code == 201
    assert new_app.job_title == application_data['job_title']


def test_create_tenant_application_nonexistent_property(authorized_tenant, test_property, test_tenant):
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

    res = authorized_tenant.post(f'/v1/applications/9', json=application_data)
    assert res.status_code == 404


def test_create_tenant_application_landlord(authorized_landlord, test_property, test_landlord):
    application_data = {
      "tenant_id": test_landlord['id'],
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

    res = authorized_landlord.post(f'/v1/applications/{test_property[0].id}', json=application_data)
    assert res.status_code == 403


def test_create_tenant_application_nonmatching_prop_id(authorized_tenant, test_property, test_tenant):
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

    res = authorized_tenant.post(f'/v1/applications/{test_property[1].id}', json=application_data)
    assert res.status_code == 400


def test_create_tenant_application_unauthorized(client, test_property, test_tenant):
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

    res = client.post(f'/v1/applications/{test_property[0].id}', json=application_data)
    assert res.status_code == 401


def test_get_tenant_applications_authorized(authorized_landlord, test_tenant_applications, test_property):
    res = authorized_landlord.get(f'/v1/applications/{test_property[0].id}')
    assert res.status_code == 200
    assert res.json()[0].get('job_title') == "Software Developer"


def test_get_tenant_applications_nonexistent_property(authorized_landlord, test_tenant_applications, test_property):
    res = authorized_landlord.get(f'/v1/applications/9')
    assert res.status_code == 404

    
def test_get_tenant_applications_empty(authorized_landlord, test_property):
    res = authorized_landlord.get(f'/v1/applications/{test_property[0].id}')
    assert res.status_code == 204


def test_get_tenant_applications_unauthorized(client, test_tenant_applications, test_property):
    res = client.get(f'/v1/applications/{test_property[0].id}')
    assert res.status_code == 401

    
def test_get_tenant_applications_user_authorized(authorized_landlord, test_tenant_applications, test_property):
    res = authorized_landlord.get(f'/v1/applications/')
    assert res.status_code == 200
    assert res.json().get('items')[0]["job_title"] == "Software Developer"

    
def test_get_tenant_applications_user_empty(authorized_landlord, test_property):
    res = authorized_landlord.get(f'/v1/applications/')
    assert res.status_code == 204


def test_get_tenant_applications_user_unauthorized(client, test_tenant_applications, test_property):
    res = client.get(f'/v1/applications/')
    assert res.status_code == 401

def test_get_tenant_application_authorized(authorized_landlord, test_tenant_applications, test_property):
    res = authorized_landlord.get(f'/v1/applications/{test_property[0].id}/{test_tenant_applications.id}')
    assert res.status_code == 200
    assert res.json().get('job_title') == "Software Developer"


def test_get_tenant_application_nonexistent_property(authorized_landlord, test_tenant_applications, test_property):
    res = authorized_landlord.get(f'/v1/applications/9/{test_tenant_applications.id}')
    assert res.status_code == 404


def test_get_tenant_application_nonexistent_app_id(authorized_landlord, test_tenant_applications, test_property):
    res = authorized_landlord.get(f'/v1/applications/{test_property[0].id}/9')
    assert res.status_code == 404


def test_get_tenant_application_authorized(client, test_tenant_applications, test_property):
    res = client.get(f'/v1/applications/{test_property[0].id}/{test_tenant_applications.id}')
    assert res.status_code == 401


def test_update_tenant_app_status_authorized(authorized_landlord, test_tenant_applications, test_property):
    data = {
        "tenant_id": test_tenant_applications.tenant_id,
        "application_status": "approved"
    }

    res = authorized_landlord.put(f'/v1/applications/{test_property[0].id}/{test_tenant_applications.id}', json=data)
    assert res.status_code == 200
    assert res.json().get('application_status') == data['application_status']
  

def test_update_tenant_app_status_invalid_prop_id(authorized_landlord, test_tenant_applications, test_property):
    data = {
        "tenant_id": test_tenant_applications.tenant_id,
        "application_status": "approved"
    }

    res = authorized_landlord.put(f'/v1/applications/9/{test_tenant_applications.id}', json=data)
    assert res.status_code == 404


def test_update_tenant_app_status_invalid_app_id(authorized_landlord, test_tenant_applications, test_property):
    data = {
        "tenant_id": test_tenant_applications.tenant_id,
        "application_status": "approved"
    }

    res = authorized_landlord.put(f'/v1/applications/{test_property[0].id}/9', json=data)
    assert res.status_code == 404


def test_update_tenant_app_status_authorized_tenant(authorized_tenant, test_tenant_applications, test_property):
    data = {
        "tenant_id": test_tenant_applications.tenant_id,
        "application_status": "approved"
    }

    res = authorized_tenant.put(f'/v1/applications/{test_property[0].id}/{test_tenant_applications.id}', json=data)
    assert res.status_code == 401


def test_update_tenant_app_status_wrong_user(authorized_landlord2, test_tenant_applications, test_property):
    data = {
        "tenant_id": test_tenant_applications.tenant_id,
        "application_status": "approved"
    }

    res = authorized_landlord2.put(f'/v1/applications/{test_property[0].id}/{test_tenant_applications.id}', json=data)
    assert res.status_code == 403


def test_update_tenant_app_status_unauthorized(client, test_tenant_applications, test_property):
    data = {
        "tenant_id": test_tenant_applications.tenant_id,
        "application_status": "approved"
    }

    res = client.put(f'/v1/applications/{test_property[0].id}/{test_tenant_applications.id}', json=data)
    assert res.status_code == 401