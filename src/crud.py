from sqlalchemy.orm import Session

from . import models, schemas


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


def save_user_file(user_id, file, data_start_date, data_end_date):
    return None


def user_exist(user_id):
    return True


def file_exist(user_id, filename):
    return False

