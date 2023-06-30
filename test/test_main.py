from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base
from main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_user():
    response = client.post(
        "/user/create",
        json={"email": "testuser@example.com", "user_name": "testuser", "password": "strongpassword"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data
    user_id = data["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["files"] == []
    assert data["id"] == user_id


def test_get_users_list():
    response = client.get("/users/")
    print(response.json())
    assert response.status_code == 200, response.text


def test_get_user_by_email_failed():
    response = client.post("/user/get", json={"email": "a@mail.ru"})
    print(response)
    assert response.status_code == 400, response.text
