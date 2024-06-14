from .shared_data import client, get_random_string, get_new_user, remove_user, login, get_header, change_user


def get_user():
    name = get_random_string()
    pwd = get_random_string()
    user = get_new_user(name, pwd)

    response = client.post('/register', json=user)
    assert response.status_code == 200

    data = response.json()
    idx = data["id"]

    return user, idx


def test_registration():
    user, idx = get_user()
    remove_user(idx)


def test_permissions_normal_user():
    user, idx = get_user()

    try:
        name = get_random_string()
        pwd = get_random_string()
        usr = get_new_user(name, pwd)
        edited = change_user(name)

        token = login(user['username'], user['password'])
        headers = get_header(token)

        response = client.get("/admins", headers=headers)
        assert response.status_code == 403

        response = client.post("/admins", json=usr, headers=headers)
        assert response.status_code == 403

        response = client.patch("/admins", json=edited, headers=headers)
        assert response.status_code == 403

        response = client.delete("/admins/1", headers=headers)
        assert response.status_code == 403

        response = client.patch("/admins/ban/1", headers=headers)
        assert response.status_code == 403

        response = client.patch("/admins/unban/1", headers=headers)
        assert response.status_code == 403

        response = client.patch("/admins/promote/1", headers=headers)
        assert response.status_code == 403

        response = client.patch("/admins/demote/1", headers=headers)
        assert response.status_code == 403
    finally:
        remove_user(idx)


def test_change_password():
    user, idx = get_user()

    try:
        token = login(user['username'], user['password'])
        headers = get_header(token)
        user['password'] = 'NEWPASS'

        data = {
            "password": user["password"]
        }

        response = client.patch('/change_password', json=data, headers=headers)
        assert response.status_code == 200

        response = client.post('/token', data=user)
        assert response.status_code == 200
    finally:
        remove_user(idx)
