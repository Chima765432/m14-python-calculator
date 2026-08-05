def add_calculation(auth_client, a=2, b=3, type="Add"):
    return auth_client.post("/calculations", json={"a": a, "b": b, "type": type})


def test_add_returns_computed_result(auth_client):
    response = add_calculation(auth_client)
    assert response.status_code == 201
    assert response.json()["result"] == 5


def test_browse_returns_all_calculations(auth_client):
    add_calculation(auth_client)
    add_calculation(auth_client, a=4, b=5, type="Multiply")
    response = auth_client.get("/calculations")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_browse_returns_rows_in_id_order(auth_client):
    add_calculation(auth_client)
    add_calculation(auth_client, a=4, b=5, type="Multiply")
    ids = [row["id"] for row in auth_client.get("/calculations").json()]
    assert ids == sorted(ids)


def test_read_returns_one_calculation(auth_client):
    created = add_calculation(auth_client).json()
    response = auth_client.get(f"/calculations/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_read_missing_calculation_returns_404(auth_client):
    assert auth_client.get("/calculations/999").status_code == 404


def test_edit_updates_and_recomputes(auth_client):
    created = add_calculation(auth_client).json()
    response = auth_client.put(
        f"/calculations/{created['id']}", json={"a": 10, "b": 2, "type": "Divide"}
    )
    assert response.status_code == 200
    assert response.json()["result"] == 5


def test_edit_missing_calculation_returns_404(auth_client):
    response = auth_client.put("/calculations/999", json={"a": 1, "b": 1, "type": "Add"})
    assert response.status_code == 404


def test_delete_removes_calculation(auth_client):
    created = add_calculation(auth_client).json()
    assert auth_client.delete(f"/calculations/{created['id']}").status_code == 204
    assert auth_client.get(f"/calculations/{created['id']}").status_code == 404


def test_add_rejects_zero_divisor(auth_client):
    assert add_calculation(auth_client, a=10, b=0, type="Divide").status_code == 422


def test_add_rejects_unknown_type(auth_client):
    assert add_calculation(auth_client, type="Banana").status_code == 422


def test_calculations_are_scoped_to_owner(auth_client, client):
    add_calculation(auth_client)
    other = client.post(
        "/users/register",
        json={"username": "other", "email": "other@example.com", "password": "longenough1"},
    ).json()
    client.headers.update({"Authorization": f"Bearer {other['access_token']}"})
    assert client.get("/calculations").json() == []


def test_routes_reject_missing_token(client):
    assert client.get("/calculations").status_code == 401
    assert client.post("/calculations", json={"a": 1, "b": 1, "type": "Add"}).status_code == 401
    assert client.get("/calculations/1").status_code == 401
    assert client.delete("/calculations/1").status_code == 401


def test_routes_reject_invalid_token(client):
    client.headers.update({"Authorization": "Bearer not-a-real-token"})
    assert client.get("/calculations").status_code == 401


def test_user_cannot_read_another_users_calculation(auth_client, client):
    created = add_calculation(auth_client).json()
    other = client.post(
        "/users/register",
        json={"username": "other2", "email": "other2@example.com", "password": "longenough1"},
    ).json()
    client.headers.update({"Authorization": f"Bearer {other['access_token']}"})
    assert client.get(f"/calculations/{created['id']}").status_code == 404
