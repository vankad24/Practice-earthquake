from sqlalchemy.orm import Session
from fastapi import UploadFile
from . import models, schemas
from datetime import datetime
from loguru import logger


def get_user_by_id(db: Session, user_id: int):
    logger.info(f"Get user by id = {user_id} from the database")
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    logger.info(f"Get user by email {email} from the database")
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    logger.info(f"Retrieve users list with limit = {limit} from the database")
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    logger.info(f"Add new user with email {user.email} to the database")
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_files_list(db: Session, user_id: int, from_date: str, to_date: str, limit: int = 100):
    logger.info(f"Get files list for user with user_id = {user_id} from the database")
    return db.query(models.File).filter(models.File.author_id == user_id) \
        .filter(models.File.upload_date.between(from_date, to_date)) \
        .order_by(models.File.upload_date.desc()) \
        .limit(limit).all()


def save_user_file(db: Session, user_id, file: UploadFile, data_start_date, data_end_date):
    logger.info(f"Save uploaded file info to the database for user_id = {user_id}")
    file1 = models.File()
    file1.author_id = user_id
    file1.file_name = file.filename
    # file1.data_start_date = datetime.strptime(data_start_date, "%Y-%m-%d %H:%M:%S")
    # file1.data_end_date = datetime.strptime(data_end_date, "%Y-%m-%d %H:%M:%S")
    file1.upload_date = datetime.now().replace(microsecond=0)

    db.add(file1)
    db.commit()
    db.refresh(file1)

    return file1


def get_file(db, user_id, file_name):
    logger.info(f"Get uploaded file where user_id = {user_id} and file name = '{file_name}' from the database")
    file1 = db.query(models.File).filter(models.File.author_id == user_id) \
        .filter(models.File.file_name == file_name) \
        .first()
    return file1

def get_generated_file(db, user_id, file_name):
    logger.info(f"Get generated file for user with user_id = {user_id} from the database")
    db.query(models.GenFile).filter(models.GenFile.author_id == user_id)\
        .filter(models.GenFile.file_name == file_name).first()

def save_generated_file(db, user_id, file_name):
    logger.info(f"Save generated file '{file_name}' to the database for user_id = {user_id}")
    file1 = models.GenFile()
    file1.author_id = user_id
    file1.file_name = file_name

    db.add(file1)
    db.commit()
    db.refresh(file1)

    return file1