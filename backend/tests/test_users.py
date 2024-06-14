from .shared_data import client, remove_user, login, get_header, get_random_string
from .test_auth import get_user
from datetime import datetime


def test_unauthorized_user():
    response = client.get('/users')
    assert response.status_code == 401

    response = client.get('/users/subscribe/1')
    assert response.status_code == 401

    response = client.get('/users/unsubscribe/1')
    assert response.status_code == 401

    response = client.get('/users/subscribe/list')
    assert response.status_code == 401

    response = client.get('/users/alert')
    assert response.status_code == 401


def test_get_users():
    user_1, idx_1 = get_user()
    user_2, idx_2 = get_user()
    user_3, idx_3 = get_user()

    try:
        token = login(user_1["username"], user_1["password"])
        headers = get_header(token)

        response = client.get('/users', headers=headers)
        assert response.status_code == 200

        data = response.json()
        names = [elem['full_name'] for elem in data]
        assert user_1['full_name'] in names
        assert user_2['full_name'] in names
        assert user_3['full_name'] in names
    finally:
        remove_user(idx_1)
        remove_user(idx_2)
        remove_user(idx_3)


def test_subscribtion():
    user_1, idx_1 = get_user()
    user_2, idx_2 = get_user()
    user_3, idx_3 = get_user()

    try:
        token = login(user_1["username"], user_1["password"])
        headers = get_header(token)

        # Подписываемся и проверяем
        response = client.get(f'/users/subscribe/{idx_2}', headers=headers)
        assert response.status_code == 200

        response = client.get(f'/users/subscribe/{idx_3}', headers=headers)
        assert response.status_code == 200

        # Ошибка. Уже подписаны
        response = client.get(f'/users/subscribe/{idx_3}', headers=headers)
        assert response.status_code == 400

        # Ловим ошибку, т.к. такого ID быть не должно
        response = client.get('/users/subscribe/0', headers=headers)
        assert response.status_code == 400

        # Проверяем наши подписки
        response = client.get('users/subscribe/list', headers=headers)
        assert response.status_code == 200

        data = response.json()
        names = [elem['full_name'] for elem in data]
        assert user_2['full_name'] in names
        assert user_3['full_name'] in names

        # Отписываемся
        response = client.get(f'/users/unsubscribe/{idx_2}', headers=headers)
        assert response.status_code == 200

        # И ещё раз, получая ошибку
        response = client.get(f'/users/unsubscribe/{idx_2}', headers=headers)
        assert response.status_code == 400

        # Проверяем наши подписки
        response = client.get('users/subscribe/list', headers=headers)
        data = response.json()
        names = [elem['full_name'] for elem in data]
        assert user_2['full_name'] not in names  # А этого уже быть не должно
        assert user_3['full_name'] in names

        # Отписываемся от последнего, чтобы почистить таблицу подписок и спокойно удалить лишние записи
        response = client.get(f'/users/unsubscribe/{idx_3}', headers=headers)
        assert response.status_code == 200

    finally:
        remove_user(idx_1)
        remove_user(idx_2)
        remove_user(idx_3)


def test_alert():
    user_1, idx_1 = get_user()
    user_2, idx_2 = get_user()
    # user_3, idx_3 = get_user()
    user_3 = {
        "username": get_random_string(20),
        "email": get_random_string(20),
        "full_name": get_random_string(20),
        "birthday": datetime.today().strftime('%Y-%m-%d'),
        "password": get_random_string(20)
    }

    response = client.post('/register', json=user_3)
    assert response.status_code == 200

    data = response.json()
    idx_3 = data["id"]

    token = login(user_1["username"], user_1["password"])
    headers = get_header(token)

    try:
        # Подписываемся и проверяем
        response = client.get(f'/users/subscribe/{idx_2}', headers=headers)
        assert response.status_code == 200

        response = client.get(f'/users/subscribe/{idx_3}', headers=headers)
        assert response.status_code == 200

        response = client.get('users/alert', headers=headers)
        assert response.status_code == 200

        data = response.json()
        names = [elem['full_name'] for elem in data]
        # Этого быть не должно. Если сегодня не 2024-01-01 и мы в прошлом...
        assert user_2['full_name'] not in names
        # А у этого сегодня ДР
        assert user_3['full_name'] in names

    finally:
        #  Отписываемся, чтобы почистить базу подписок
        client.get(f'/users/unsubscribe/{idx_2}', headers=headers)
        client.get(f'/users/unsubscribe/{idx_3}', headers=headers)

        remove_user(idx_1)
        remove_user(idx_2)
        remove_user(idx_3)
