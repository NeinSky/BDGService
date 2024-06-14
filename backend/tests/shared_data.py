import random
import string

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

admin = {
    "username": "admin",
    "password": "admin"
}


def get_random_string(size=10):
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))


def get_header(token: str):
    return {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }


def get_new_user(username: str = get_random_string(),
                 password: str = get_random_string()):
    return {
        "username": username,
        "email": get_random_string(20),
        "full_name": get_random_string(20),
        "birthday": "2024-01-01T22:33:28.499Z",
        "password": password
    }


def change_user(username):
    return {
        "username": username,
        "email": get_random_string(20),
        "full_name": get_random_string(20),
        "birthday": "1900-01-01",
        "id": 0,
        "is_admin": False,
        "disabled": False,
    }


def get_admin_token():
    response = client.post('/token', data=admin)
    return response.json()['access_token']


def login(username, password):
    data = {
        "username": username,
        "password": password,
    }

    response = client.post('/token', data=data)
    return response.json()['access_token']


def remove_user(idx):
    token = get_admin_token()
    client.delete(f'/admins/users/{idx}', headers=get_header(token))
