from fastapi import FastAPI, Depends, status, HTTPException
from pydantic import BaseModel
from typing import Annotated, Optional
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging
from sqlalchemy.exc import SQLAlchemyError


import models
from datetime import datetime
from models import User


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


class UserBase(BaseModel):
    username: str
    email: str
    password: str


class GetUser(BaseModel):
    username: str
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
async def get_user():
    print(dir(datetime))
    print("Time test", datetime.utcnow())
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


@app.post("/get-user/")
async def get_user(user: GetUser, db: db_dependency):
    try:
        stmt = select(User).where((User.username == user.username) &
                                  (User.password == user.password))
        # stmt = db.query(User).select(
        #     (User.username == user.username) & (User.password == user.password)
        # )
        that_user = db.execute(stmt).scalar_one_or_none()
        if not that_user:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail="user not found")
        return that_user
    except HTTPException as httpe:
        raise httpe

    except SQLAlchemyError as sqle:
        logging.exception("database query failed")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="SQLAlchemyError Exception")

    except Exception as generic_exc:
        logging.exception("Unexpected error")
        raise HTTPException(status_code=500, detail="Unexpected server error")


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
