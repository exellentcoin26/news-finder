from tests import client, database_configure, database_clear  # pyright: ignore
from flask import Flask


def test_add_admin(client: Flask.testing):
    response_create_user: Flask.response_class = client.post("/user/", json={"username": "jan", "password": "qwerty"})
    assert response_create_user.status_code == 200
    response_create_user: Flask.response_class = client.post("/user/", json={"username": "piet-joris", "password": "qwerty"})
    assert response_create_user.status_code == 200
    response_create_user: Flask.response_class = client.post("/user/", json={"username": "korneel", "password": "qwerty"})
    assert response_create_user.status_code == 200

    response_make_admin: Flask.response_class = client.post("/admin/", json={"usernames": ["Jan", "piet-joris"]})
    assert response_make_admin.status_code == 200

    response_check_admin: Flask.response_class = client.post("/admin/is-admin/", json={"username": "Jan"})
    assert response_check_admin.status_code == 200
    assert response_check_admin.get_json()["admin"]
    response_check_admin: Flask.response_class = client.post("/admin/is-admin/", json={"username": "PIET-JORIS"})
    assert response_check_admin.status_code == 200
    assert response_check_admin.get_json()["admin"]
    response_check_admin: Flask.response_class = client.post("/admin/is-admin/", json={"username": "Korneel"})
    assert response_check_admin.status_code == 200
    assert not response_check_admin.get_json()["admin"]
