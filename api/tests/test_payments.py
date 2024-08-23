from app import schemas


def test_make_rent_payment_authorized(authorized_tenant, test_approve_tenant, test_tenant, test_property):
    payment_data = {
      "tenant_id": test_tenant['id'],
      "property_id": test_property[0].id,
      "amount": 1200.0,
      "duration_months": 12
    }

    res = authorized_tenant.post(f'/v1/payments/{test_property[0].id}', json=payment_data)
    new_payment = schemas.PaymentResp(**res.json())
    assert res.status_code == 200
    assert new_payment.tenant_id == test_tenant['id']


def test_make_rent_payment_wrong_user(authorized_tenant2, test_approve_tenant, test_tenant, test_tenant2, test_property):
    payment_data = {
      "tenant_id": test_tenant['id'],
      "property_id": test_property[0].id,
      "amount": 1200.0,
      "duration_months": 12
    }

    res = authorized_tenant2.post(f'/v1/payments/{test_property[0].id}', json=payment_data)
    assert res.status_code == 401


def test_make_rent_payment_landlord(authorized_landlord, test_approve_tenant, test_landlord, test_property):
    payment_data = {
      "tenant_id": test_landlord['id'],
      "property_id": test_property[0].id,
      "amount": 1200.0,
      "duration_months": 12
    }

    res = authorized_landlord.post(f'/v1/payments/{test_property[0].id}', json=payment_data)
    assert res.status_code == 403


def test_make_rent_payment_nomatch(authorized_tenant2, test_tenant, test_tenant2, test_property):
    payment_data = {
      "tenant_id": test_tenant2['id'],
      "property_id": test_property[0].id,
      "amount": 1200.0,
      "duration_months": 12
    }

    res = authorized_tenant2.post(f'/v1/payments/{test_property[0].id}', json=payment_data)
    assert res.status_code == 404


def test_make_rent_payment_unauthorized(client, test_approve_tenant, test_tenant, test_property):
    payment_data = {
      "tenant_id": test_tenant['id'],
      "property_id": test_property[0].id,
      "amount": 1200.0,
      "duration_months": 12
    }

    res = client.post(f'/v1/payments/{test_property[0].id}', json=payment_data)
    assert res.status_code == 401


def test_get_payments_property_authorized(authorized_landlord, test_payments, test_property):
    res = authorized_landlord.get(f'/v1/payments/{test_property[0].id}')
    assert res.status_code == 200
    assert res.json()[0].get('amount') == 1200.0


def test_get_payments_property_unauthorized(client, test_payments, test_property):
    res = client.get(f'/v1/payments/{test_property[0].id}')
    assert res.status_code == 401


def test_get_payments_property_nonexistent_property(authorized_landlord, test_payments):
    res = authorized_landlord.get(f'/v1/payments/9')
    assert res.status_code == 404


def test_get_payments_property_empty(authorized_landlord, test_property):
    res = authorized_landlord.get(f'/v1/payments/{test_property[0].id}')
    assert res.status_code == 204


def test_get_payments_user_authorized(authorized_landlord, test_payments):
    res = authorized_landlord.get(f'/v1/payments/')
    assert res.status_code == 200
    assert res.json()[0].get('amount') == 1200.0


def test_get_payments_user_unauthorized(client, test_payments):
    res = client.get(f'/v1/payments/')
    assert res.status_code == 401


def test_get_payments_property_empty(authorized_landlord):
    res = authorized_landlord.get(f'/v1/payments/')
    assert res.status_code == 204
    
