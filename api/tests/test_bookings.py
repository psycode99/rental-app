from ..app import schemas


def test_create_booking(client, test_property):
    booking_data = {
      "property_id": test_property[0].id,
      "name": "Alice Johnson",
      "email": "alice.johnson@example.com",
      "phone_number": "1231231234",
      "viewing_date": "2024-08-07",
      "viewing_time": "15:30:00",
      "notes": "Looking forward to seeing the property."
    }

    res = client.post(f'/v1/bookings/{test_property[0].id}', json=booking_data)
    new_booking = schemas.BookingsResp(**res.json())
    assert new_booking.email == booking_data['email']
    assert res.status_code == 201


def test_create_booking_nonexistent_property(client):
    booking_data = {
      "property_id": 6,
      "name": "Alice Johnson",
      "email": "alice.johnson@example.com",
      "phone_number": "1231231234",
      "viewing_date": "2024-08-07",
      "viewing_time": "15:30:00",
      "notes": "Looking forward to seeing the property."
    }

    res = client.post(f'/v1/bookings/6', json=booking_data)
    assert res.status_code == 404


def test_create_booking_property_id_match(client, test_property):
    booking_data = {
      "property_id": test_property[0].id,
      "name": "Alice Johnson",
      "email": "alice.johnson@example.com",
      "phone_number": "1231231234",
      "viewing_date": "2024-08-07",
      "viewing_time": "15:30:00",
      "notes": "Looking forward to seeing the property."
    }

    res = client.post(f'/v1/bookings/{test_property[1].id}', json=booking_data)
    assert res.status_code == 400


def test_create_booking_twice(client, test_booking, test_property):
    booking_data = {
      "property_id": test_property[0].id,
      "name": "Alice Johnson",
      "email": "alice.johnson@example.com",
      "phone_number": "1231231234",
      "viewing_date": "2024-08-07",
      "viewing_time": "15:30:00",
      "notes": "Looking forward to seeing the property."
    }

    res = client.post(f'/v1/bookings/{test_property[0].id}', json=booking_data)
    assert res.status_code == 409


def test_get_bookings_authorized(authorized_landlord, test_property, test_booking):
    res = authorized_landlord.get(f'/v1/bookings/{test_property[0].id}')
    assert res.status_code == 200
    assert res.json()[0].get("name") == "Alice Johnson"
    

def test_get_bookings_authorized_empty(authorized_landlord, test_property):
    res = authorized_landlord.get(f'/v1/bookings/{test_property[0].id}')
    assert res.status_code == 204


def test_get_bookings_unauthorized(client, test_property, test_booking):
    res = client.get(f'/v1/bookings/{test_property[0].id}')
    assert res.status_code == 401


def test_get_bookings_user_authorized(authorized_landlord, test_property, test_booking):
    res = authorized_landlord.get(f'/v1/bookings/')
    assert res.status_code == 200
    assert res.json().get("items")[0]['name'] == "Alice Johnson"
    

def test_get_bookings_user_authorized_empty(authorized_landlord, test_property):
    res = authorized_landlord.get(f'/v1/bookings/')
    assert res.status_code == 204


def test_get_bookings_user_unauthorized(client, test_property, test_booking):
    res = client.get(f'/v1/bookings/')
    assert res.status_code == 401

def test_get_booking_authorized(authorized_landlord, test_property, test_booking):
    res = authorized_landlord.get(f"/v1/bookings/{test_property[0].id}/{test_booking.id}")
    assert res.status_code == 200
    assert res.json().get("name") == "Alice Johnson"


def test_get_booking_authorized_nonexistent_property(authorized_landlord, test_booking):
    res = authorized_landlord.get(f"/v1/bookings/9/{test_booking.id}")
    assert res.status_code == 404


def test_get_booking_authorized_nonexistent_booking(authorized_landlord, test_property):
    res = authorized_landlord.get(f"/v1/bookings/{test_property[0].id}/9")
    assert res.status_code == 404


def test_get_booking_unauthorized(client, test_property, test_booking):
    res = client.get(f"/v1/bookings/{test_property[0].id}/{test_booking.id}")
    assert res.status_code == 401


def test_delete_booking_authorized(authorized_landlord, test_booking):
    res = authorized_landlord.delete(f'/v1/bookings/{test_booking.id}')
    assert res.status_code == 204


def test_delete_nonexistent_booking(authorized_landlord):
    res = authorized_landlord.delete(f'/v1/bookings/9')
    assert res.status_code == 404


def test_delete_booking_authorized_tenant(authorized_tenant, test_booking):
    res = authorized_tenant.delete(f'/v1/bookings/{test_booking.id}')
    assert res.status_code == 401


def test_delete_booking_authorized_wrong_property(authorized_landlord2, test_booking):
    res = authorized_landlord2.delete(f'/v1/bookings/{test_booking.id}')
    assert res.status_code == 401


def test_delete_booking_unauthorized(client, test_booking):
    res = client.delete(f'/v1/bookings/{test_booking.id}')
    assert res.status_code == 401


