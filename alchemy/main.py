from fastapi import Depends, FastAPI, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

import crud, models, schemas
from alchemy.storage import FileStorage
from database import SessionLocal, engine
import uvicorn


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

storage: FileStorage = FileStorage()

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
    created_user = crud.create_user(db=db, user=user)
    storage.create_user_folder(created_user.id)
    return created_user


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


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.post("/users/{user_id}/uploadfile/")
async def create_upload_file(user_id: int, data_start_date:int, data_end_date:int, file: UploadFile):

    if not crud.user_exist(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with id '{user_id}' not found")
    if crud.file_exist(user_id, file.filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File '{file.filename}' already uploaded")

    crud.save_user_file(user_id, file, data_start_date, data_end_date)
    try:
        await storage.save_user_file(user_id, file)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"There was an error uploading the file")

    return {"message": f"The file '{file.filename}' was uploaded"}

@app.get("/getfile/", response_class=FileResponse)
async def get_file(path: str):
    return "files/"+path

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # uvicorn.run("main:app", host="0.0.0.0", port=8000)
    # http://127.0.0.1:8000/docs