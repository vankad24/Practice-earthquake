from sqlalchemy.orm import Session
from fastapi import UploadFile
from . import models, schemas
from datetime import datetime


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_files_list(db: Session, user_id: int, from_date: str, to_date: str, limit: int = 100):
    return db.query(models.File).filter(models.File.author_id == user_id)\
                                .filter(models.File.upload_date.between(from_date, to_date))\
                                .order_by(models.File.upload_date.desc())\
                                .limit(limit).all()


def create_user_file(db: Session, file: schemas.FileCreate, user_id: int):
    file = models.File(**file.dict(), author_id=user_id)
    db.add(file)
    db.commit()
    db.refresh(file)
    return file


def save_user_file(db: Session, user_id, file: UploadFile, data_start_date, data_end_date):

    file1 = models.File()
    file1.author_id = user_id
    file1.file_name = file.filename
    file1.data_start_date = datetime.strptime(data_start_date, "%Y-%m-%d %H:%M:%S")
    file1.data_end_date = datetime.strptime(data_end_date, "%Y-%m-%d %H:%M:%S")
    file1.upload_date = datetime.now().replace(microsecond=0)

    db.add(file1)
    db.commit()
    db.refresh(file1)

    return file1


def user_exist(db, user_id):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        return True
    return False


def file_exist(db, user_id, file_name):
    file1 = db.query(models.File).filter(models.File.author_id == user_id)\
                                 .filter(models.File.file_name == file_name)\
                                 .all()
    if file1:
        return True
    return False


def get_file(db, user_id, file_name):
    file1 = db.query(models.File).filter(models.File.author_id == user_id)\
                                 .filter(models.File.file_name == file_name)\
                                 .first()
    return file1
