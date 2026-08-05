import pytest
from sqlalchemy.orm import sessionmaker

from app.database import Base, engine


@pytest.fixture
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    from fastapi.testclient import TestClient

    from app.database import get_db
    from main import app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def live_server():
    import socket
    import subprocess
    import time

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    process = subprocess.Popen(
        ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001"]
    )
    for _ in range(40):
        try:
            with socket.create_connection(("127.0.0.1", 8001), timeout=0.5):
                break
        except OSError:
            time.sleep(0.5)
    else:
        process.terminate()
        raise RuntimeError("server did not start")

    yield "http://127.0.0.1:8001"
    process.terminate()
    process.wait()


@pytest.fixture
def auth_client(client):
    payload = {
        "username": "owner",
        "email": "owner@example.com",
        "password": "longenough1",
    }
    response = client.post("/users/register", json=payload)
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
