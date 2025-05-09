from fastapi import FastAPI, Depends, status
from pydantic import BaseModel
from typing import Annotated, Optional
from database import engine, SessionLocal
from sqlalchemy.orm import Session


import models
from datetime import datetime
from models import User


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


class UserBase(BaseModel):
    username: str
    email: str
    password: str


class UpdateUserBase(BaseModel):
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# test
@app.get("/test/")
async def get_user(email: str, username: str, password: str, confirm_password: str):
    print("server test", email, username, password, confirm_password)
    return "return server"


@app.post("/create-user/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    try:
        new_user = User(username=user.username, email=user.email,
                        password=user.password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return f"{status.HTTP_201_CREATED}: {user}"
    except Exception as e:
        print("Exception", e)


@app.get("/get-user/{id}", status_code=status.HTTP_200_OK)
async def get_user(id: int, db: db_dependency):
    try:
        user_id = db.query(User).get(id)
        return user_id
    except Exception as e:
        print("Exception", e)


@app.patch("/update-user-details/{id}", status_code=status.HTTP_200_OK)
async def update_user(id: int, user: UpdateUserBase, db: db_dependency):
    try:
        that_user = db.query(User).get(id)
        that_user.username = user.username
        that_user.email = user.email
        db.add(that_user)
        db.commit()
        db.refresh(that_user)
        print(that_user)
    except Exception as e:
        print("Exception", e)


@app.delete("/delete-user/{id}", status_code=status.HTTP_200_OK)
async def delete_user(id: int, db: db_dependency):
    try:
        that_user = db.query(User).get(id)
        print(that_user)
        db.delete(that_user)
        db.commit()
        return "data deleted successfully"
    except Exception as e:
        return f"Exception {e}"
