from app import schemas
import pytest
from jose import jwt
from app.oauth import SECRET_KEY, ALGORITHM
from fastapi import HTTPException

def test_login(client, test_tenant):
    res = client.post('/v1/auth/login', data={"username":test_tenant['email'], "password":test_tenant['password']})
    login_resp = schemas.Token(**res.json())
    payload = jwt.decode(login_resp.access_token, key=SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get('user_id')
    assert user_id == test_tenant['id']
    assert res.status_code == 200



@pytest.mark.parametrize("email, password, status_code", [
    ("meeka@email.com", "qwerty", 403),
    ("mike@gmail.com", "1234", 403),
    ('mike@gmail.com',  "gggg", 403) ,
    (None, "1234", 422),    
    ("meeka@gmail.com", None, 422)
    ])
def test_invalid_logins(client, email, password, status_code):
    res = client.post('/v1/auth/login', data={"username":email, "password":password})
    assert res.status_code == status_code