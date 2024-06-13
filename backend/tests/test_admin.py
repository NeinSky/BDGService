from fastapi.testclient import TestClient
import random
import string
from main import app

client = TestClient(app)

admin = "admin"
password = "admin"


def get_random_string(size=10):
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))


username = get_random_string(20)

new_user = {
    "username": username,
    "email": get_random_string(20),
    "full_name": get_random_string(20),
    "birthday": "2024-06-13T22:33:28.499Z",
    "password": get_random_string(20)
}

change_user = {
    "username": username,
    "email": get_random_string(20),
    "full_name": get_random_string(20),
    "birthday": "1900-01-01",
    "id": 0,
    "is_admin": False,
    "disabled": False,
}


def get_header(token: str):
    return {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }


def test_unauthorized_access():
    response = client.get("/admins")
    assert response.status_code == 401

    response = client.post("/admins")
    assert response.status_code == 401

    response = client.patch("/admins")
    assert response.status_code == 401

    response = client.delete("/admins/1")
    assert response.status_code == 401

    response = client.patch("/admins/ban/1")
    assert response.status_code == 401

    response = client.patch("/admins/unban/1")
    assert response.status_code == 401

    response = client.patch("/admins/promote/1")
    assert response.status_code == 401

    response = client.patch("/admins/demote/1")
    assert response.status_code == 401


def test_authorized_access():
    # Авторизация
    response = client.post('/token', data={
        'username': 'admin',
        'password': 'admin'
    })
    assert response.status_code == 200

    # Получение списка админов
    data = response.json()
    token = data['access_token']
    response = client.get('/admins', headers=get_header(token))
    assert response.status_code == 200

    # Новый пользователь
    response = client.post('/admins', json=new_user, headers=get_header(token))
    assert response.status_code == 200

    # Изменение пользователя с неверным ID
    data = response.json()
    idx = data["id"]
    response = client.patch('/admins', json=change_user, headers=get_header(token))
    assert response.status_code == 400

    # Изменение пользователя с верными данными
    change_user['id'] = idx
    response = client.patch('/admins', json=change_user, headers=get_header(token))
    assert response.status_code == 200

    # Бан
    response = client.patch(f"/admins/ban/{idx}", headers=get_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data['disabled'] == True

    # Анбан
    response = client.patch(f"/admins/unban/{idx}", headers=get_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data['disabled'] == False

    # Админ
    response = client.patch(f"/admins/promote/{idx}", headers=get_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data['is_admin'] == True

    # Не админ
    response = client.patch(f"/admins/demote/{idx}", headers=get_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data['is_admin'] == False

    # Удаление пользователя
    response = client.delete(f'/admins/{idx}', headers=get_header(token))
    assert response.status_code == 200
