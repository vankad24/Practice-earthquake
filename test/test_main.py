import os
import shutil
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


# from https://stackoverflow.com/questions/7786648/how-to-call-setup-once-for-all-tests-and-teardown-after-all-are-finished
def setup_module():
    print("setup")


# @pytest.fixture(scope="module")
# def my_context():
#     # there will be added user_id for test_data user and file_name (name of the file where the test user data is stored)
#     # from https://stackoverflow.com/questions/61622565/pytest-pass-value-from-one-test-function-to-another-in-test-file
#     return {}


def teardown_module():
    print("teardown")
    # os.remove(my_context["file_name"])
    curr_dir = os.path.abspath(os.getcwd())
    print(curr_dir)

    test_file = curr_dir + "\\test_file.txt"
    test_file_1 = curr_dir + "\\test_file_1.txt"
    # static_folder = curr_dir + "\\static"

    if os.path.exists(test_file):
        os.remove(test_file)

    if os.path.exists(test_file_1):
        os.remove(test_file_1)

    fs = FileStorage()
    if (fs.STORAGE_PATH / str(1)).exists():
        fs.delete_user_folder(1)

    # if os.path.exists(static_folder):
    #     shutil.rmtree(static_folder)
    # fs.delete_user_folder(my_context["user_id"])


test_data = {"email": "testuser@example.com", "user_name": "testuser", "password": "strongpassword"}


def test_create_user():
    response = client.post(
        "/user/create",
        json=test_data,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == test_data["email"]
    assert "id" in data

    # user_id = data["id"]
    # my_context["user_id"] = user_id


def test_create_user_fail():
    response = client.post(
        "/user/create",
        json=test_data,
    )
    assert response.status_code == 400, response.text


def test_get_users_list():
    response = client.get("/users/")
    data = response.json()
    print(data)
    assert response.status_code == 200, response.text
    assert len(data) == 1
    assert data[0]["email"] == test_data["email"]
    assert data[0]["id"] == 1
    assert data[0]["files"] == []


def test_get_user_by_id():
    response = client.get(f"/user/1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == test_data["email"]
    assert data["files"] == []
    assert data["id"] == 1


def test_get_user_by_id_fail():
    response = client.get(f"/user/2000")
    assert response.status_code == 400, response.text


def test_get_user_by_email():
    response = client.post("/user/get", json={"email": test_data["email"]})
    print(response)
    data = response.json()
    assert response.status_code == 200, response.text
    assert data["email"] == test_data["email"]
    assert data["id"] == 1
    assert data["files"] == []


def test_get_user_by_email_fail():
    # if I use json parameter it doesn't work, because api waits for query parameters not json (class)
    # but if we change email to user: schemas.UserBase it's going to accept the json (we can use json param)
    # in case of create_user this function accepts the UserCreate class, so we can pass a json object
    response = client.post("/user/get", json={"email": "a@mail.ru"})
    print(response)
    assert response.status_code == 400, response.text


def test_upload_file():
    user_id = 1
    file_name = "test_file.txt"
    with open(file_name, 'wb') as f:
        f.write(bytes("some long text here", "utf-8"))
    response = client.post(f"user/{user_id}/file/upload",
                           params={
                               "data_start_date": "2020-05-05 00:00:00",
                               "data_end_date": "2020-06-05 10:20:30",
                           },
                           files={
                               "file": open(file_name, "rb")
                           })
    data = response.json()
    assert response.status_code == 200, response.text
    assert data["message"] == f"The file '{file_name}' was uploaded"


def test_upload_file_user_not_exist():
    user_id = 1000
    file_name = "test_file.txt"
    response = client.post(f"user/{user_id}/file/upload",
                           params={
                               "data_start_date": "2020-05-05 00:00:00",
                               "data_end_date": "2020-06-05 10:20:30",
                           },
                           files={
                               "file": open(file_name, "rb")
                           })
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == f"User with id '{user_id}' not found"


def test_upload_file_already_uploaded():
    user_id = 1
    file_name = "test_file.txt"
    response = client.post(f"user/{user_id}/file/upload",
                           params={
                               "data_start_date": "2020-05-05 00:00:00",
                               "data_end_date": "2020-06-05 10:20:30",
                           },
                           files={
                               "file": open(file_name, "rb")
                           })
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == f"File '{file_name}' already uploaded"


def test_get_user_files_list():
    response = client.post("/user/1/files", params={
        "from_date": "2023-01-01 00:00:00",
        "to_date": "2023-12-31 00:00:00",
        "limit": 1
    })
    data = response.json()
    assert len(data) == 1
    assert response.status_code == 200, response.text
    assert data[0]["file_name"] == "test_file.txt"
    assert data[0]["id"] == 1
    # assert data[0]["data_start_date"] == "2020-05-05T00:00:00"
    # assert data[0]["data_end_date"] == "2020-06-05T10:20:30"
    assert data[0]["author_id"] == 1


def test_get_user_files_list_fail():
    response = client.post("/user/2999/files", params={
        "from_date": "2023-01-01 00:00:00",
        "to_date": "2023-12-31 00:00:00",
        "limit": 1
    })
    assert response.status_code == 400, response.text


def test_upload_file_server_error():
    user_id = 1
    file_name = "test_file_1.txt"
    with open(file_name, 'wb') as f:
        f.write(bytes("some long text here in test_file_1.txt", "utf-8"))

    fs = FileStorage()
    fs.delete_user_folder(user_id)

    response = client.post(f"user/{user_id}/file/upload",
                           params={
                               "data_start_date": "2020-05-05 00:00:00",
                               "data_end_date": "2020-06-05 10:20:30",
                           },
                           files={
                               "file": open(file_name, "rb")
                           })
    assert response.status_code == 500, response.text
    data = response.json()
    assert data["detail"] == f"There was an error uploading the file"


def test_get_db():
    gen = get_db()
    next(gen)
    try:
        next(gen)
    except Exception as e:
        pass
    assert True














