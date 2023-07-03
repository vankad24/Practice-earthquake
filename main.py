from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import EmailStr
from sqlalchemy.orm import Session

from src import crud, models, schemas
from src.schemas import Epicenter, GenerateParams, GenerateDistanceParams
from src.storage import FileStorage
from src.database import SessionLocal, engine
import uvicorn
from src.logger import logger
import ionoplot

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

storage: FileStorage = FileStorage()


# Dependency
def get_db():
    logger.info("Creating database connection")
    db = SessionLocal()
    try:
        yield db
    finally:
        logger.info("Closing database connection")
        db.close()


@app.post("/user/create", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Create new user with email = {user.email}")
    db_user = crud.get_user_by_email(db, email=user.email)
    logger.info(f"Check if user with email {user.email} exists")
    if db_user:
        logger.error(f"Email {user.email} already registered")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    created_user = crud.create_user(db=db, user=user)
    storage.create_user_folder(created_user.id)
    logger.info("Send created user data")
    return created_user


@app.get("/users/", response_model=list[schemas.User])
def get_users_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger.info(f"Access users list with limit = {limit}")
    users = crud.get_users(db, skip=skip, limit=limit)
    logger.info("Send users list")
    return users


@app.get("/user/{user_id}", response_model=schemas.User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Get user by id = {user_id}")
    db_user = crud.get_user_by_id(db, user_id=user_id)
    logger.info(f"Check if user with id = {user_id} exists")
    if db_user is None:
        logger.error(f"User with id {user_id} not found")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    logger.info("Send user data")
    return db_user


@app.post("/user/get", response_model=schemas.User)
async def get_user_by_email(user: schemas.UserBase, db: Session = Depends(get_db)):
    """
        Я заменил email на user (UserBase) и тест заработал
        https://stackoverflow.com/questions/59929028/python-fastapi-error-422-with-post-request-when-sending-json-data
    """
    logger.info(f"Get user by email = {user.email}")
    db_user = crud.get_user_by_email(db, email=user.email)
    logger.info(f"Check if user with email {user.email} exists")
    if db_user is None:
        logger.error(f"User with email {user.email} not found")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    logger.info("Send user data")
    return db_user


# @app.post("/user/get", response_model=schemas.User)
# async def get_user_by_email(email: EmailStr, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=email)
#     if db_user is None:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
#     return db_user


@app.post("/user/{user_id}/file/upload")
async def upload_file(user_id: int, data_start_date: str, data_end_date: str, file: UploadFile,
                      db: Session = Depends(get_db)):
    logger.info(f"Upload file = '{file.filename}' for user_id = {user_id}")
    db_user = crud.get_user_by_id(db, user_id)
    logger.info(f"Check if user with id = {user_id} exists")
    if db_user is None:
        logger.error(f"User with id {user_id} not found")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with id '{user_id}' not found")
    db_file = crud.get_file(db, user_id, file.filename)
    logger.info(f"Check if file '{file.filename}' was uploaded")
    if db_file is not None:
        logger.error(f"File '{file.filename}' already uploaded")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File '{file.filename}' already uploaded")

    crud.save_user_file(db, user_id, file, data_start_date, data_end_date)
    try:
        await storage.save_uploaded_file(user_id, file)
    except Exception as e:
        logger.exception(f"Something went wrong saving the file to the user folder with user_id = {user_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"There was an error uploading the file")
    logger.info("Send info that file was uploaded successfully")
    return {"message": f"The file '{file.filename}' was uploaded"}


# @app.get("/user/{user_id}/file/download", response_class=FileResponse)
# async def download_file(user_id: int, file_name: str):
#     return "files/"+path


@app.post("/user/{user_id}/files", response_model=list[schemas.File])
async def get_user_files_list(user_id: int, from_date, to_date, limit, db: Session = Depends(get_db)):
    """ from_date and to_date accepts only the following format: yyyy-mm-dd hh:mm:ss (ex. 2020-12-01 12:39:48) """
    logger.info(f"Get user (user_id = {user_id}) files list")
    user = crud.get_user_by_id(db, user_id)
    logger.info(f"Check if the user with id = {user_id} exists")
    if user is None:
        logger.error(f"The user with id {user_id} not found")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User doesn't exist")
    files = crud.get_user_files_list(db, user_id, from_date, to_date, limit)
    logger.info(f"Send files list to the user with user_id = {user_id}")
    return files


@app.post("/user/{user_id}/generate/map", response_class=FileResponse)
def generate_map(user_id: int, params: GenerateParams, map_type: ionoplot.MapType,
                 db: Session = Depends(get_db)):
    logger.info(f"Generate images from file for user_id = {user_id} and files = {params.file_names}")
    logger.info(f"Check if files '{params.file_names}' exist")
    for name in params.file_names:
        db_file = crud.get_file(db, user_id, name)
        if db_file is None:
            logger.error(f"File '{name}' was not found")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File not found")

    hashed_name = str(hash("".join(params.file_names)))
    db_gen_file = crud.get_generated_file(db, user_id, hashed_name)
    folder_path = str(storage.get_user_folder_path(user_id))
    path = str(storage.get_user_folder_path(user_id)/hashed_name)+".png"
    if not db_gen_file:
        files = list(map(lambda x: folder_path+"/"+x,params.file_names))
        ionoplot.plot_maps(files, map_type, params.times, params.epicenter.dict(), save_path=path)
        crud.save_generated_file(db,user_id,hashed_name)

    return path

@app.post("/user/{user_id}/generate/distance_time", response_class=FileResponse)
def generate_distance_time(user_id: int, params: GenerateDistanceParams, map_type: ionoplot.MapType,
                 db: Session = Depends(get_db)):
    logger.info(f"Generate distance_time from file for user_id = {user_id} and files = {params.file_name}")
    name = params.file_name
    logger.info(f"Check if files '{name}' exist")
    db_file = crud.get_file(db, user_id, name)
    if db_file is None:
        logger.error(f"File '{name}' was not found")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File not found")

    hashed_name = str(hash(name))
    db_gen_file = crud.get_generated_file(db, user_id, hashed_name)
    folder_path = str(storage.get_user_folder_path(user_id))
    path = str(storage.get_user_folder_path(user_id)/hashed_name)+".png"
    if not db_gen_file:
        file = folder_path+"/"+name
        ionoplot.plot_distance_time(file, map_type, params.epicenter.dict(), save_path=path)
        crud.save_generated_file(db,user_id, path)

    return path


if __name__ == "__main__":
    logger.info("Starting the web server")
    uvicorn.run("main:app", host="0.0.0.0", port=8000)  # , reload=True)
    # uvicorn.run("main:app", host="0.0.0.0", port=8000)
    # http://127.0.0.1:8000/docs
