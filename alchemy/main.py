from fastapi import Depends, FastAPI, HTTPException, UploadFile
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine
import uvicorn


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/files/", response_model=schemas.File)
def create_file_for_user(
        user_id: int, file: schemas.FileCreate, db: Session = Depends(get_db)
):
    return crud.create_user_file(db=db, file=file, user_id=user_id)


@app.get("/files/", response_model=list[schemas.File])
def read_files(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    files = crud.get_files(db, skip=skip, limit=limit)
    return files


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    try:
        contents = await file.read()
        with open("files/" + file.filename, 'wb') as f:
            f.write(contents)
    except Exception as e:
        return {"message": f"There was an error uploading the file {e.args}"}
    finally:
        await file.close()
    return {"message": f"The file '{file.filename}' was uploaded"}


@app.post("/users/{user_id}/files", response_model=list[schemas.File])
async def get_user_files_list(user_id, from_date, to_date, limit, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=200, detail="User already exists")
    return crud.get_user_files_list(db, user_id, from_date, to_date, limit)


if __name__ == "__main__":
    uvicorn.run("alchemy.main:app", host="0.0.0.0", port=8000)  #, reload=True)
    # print(a)
    # uvicorn.run("main:app", host="0.0.0.0", port=8000)
    # http://127.0.0.1:8000/docs
