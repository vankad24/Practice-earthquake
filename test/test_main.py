import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.database import Base
from main import app, get_db
from src.storage import FileStorage

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
    user_id = data["id"]
    fs = FileStorage()
    fs.delete_user_folder(user_id)
    assert data["email"] == "testuser@example.com"
    assert "id" in data


def test_create_user_fail():
    response = client.post(
        "/user/create",
        json={"email": "testuser@example.com", "user_name": "testuser", "password": "strongpassword"},
    )
    assert response.status_code == 400, response.text


def test_get_users_list():
    response = client.get("/users/")
    data = response.json()
    print(data)
    assert response.status_code == 200, response.text
    assert data[0]["email"] == "testuser@example.com"
    assert data[0]["id"] == 1
    assert data[0]["files"] == []


def test_get_user_by_id():
    response = client.get(f"/user/1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["files"] == []
    assert data["id"] == 1


def test_get_user_by_id_failed():
    response = client.get(f"/user/2000")
    assert response.status_code == 400, response.text


def test_get_user_by_email():
    response = client.post("/user/get", json={"email": "testuser@example.com"})
    print(response)
    assert response.status_code == 200, response.text


def test_get_user_by_email_failed():
    response = client.post("/user/get", json={"email": "a@mail.ru"})
    print(response)
    assert response.status_code == 400, response.text

# def test_upload_file():
#     user_id = 1
#     file_name = "test_file.txt"
#     with open(file_name, 'wb') as f:
#         f.write(bytes("some long text here", "utf-8"))
#     response = client.post(f"user/{user_id}/file/upload",
#                            json={
#                                 "data_start_date": "2020-05-05 00:00:00",
#                                 "data_end_date": "2020-06-05 10:20:30",
#                            },
#                            files={
#                                "file": open(file_name, "rb")
#                            })
#     assert response.status_code == 200, response.text
#     os.remove(file_name)
