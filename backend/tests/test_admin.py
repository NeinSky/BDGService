from .shared_data import client, get_new_user, get_admin_token , change_user, get_random_string, get_header


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
    username = get_random_string()
    password = get_random_string()
    new_user = get_new_user(username, password)
    edited_user = change_user(username)

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
    response = client.patch('/admins', json=edited_user, headers=get_header(token))
    assert response.status_code == 400

    # Изменение пользователя с верными данными
    edited_user['id'] = idx
    response = client.patch('/admins', json=edited_user, headers=get_header(token))
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
