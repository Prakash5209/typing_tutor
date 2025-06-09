from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.ext.mutable import MutableDict
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import Annotated, Optional,Dict,List
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select, Integer
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import uuid
import string
import os
import logging

import json
import jwt


import models
from datetime import datetime
from models import User,MistakeLetter,Report,MistakeTracker
from services import deduct_mistake_letters


# from custom_algo import get_mistakes
# from ml.knn_model import Suggest


env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class UserBase(BaseModel):
    username: str
    email: str
    password: str


class GetEmail(BaseModel):
    email: str


class ResetPassword(BaseModel):
    email: str
    password: str
    verified_user: bool


class GetUser(BaseModel):
    username: str
    password: str

class UpdateUserBase(BaseModel):
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]


class MistakeLetterSchema(BaseModel):
    jon: Dict[str, List[int]]
    no_jon: Dict[str, int]


class ReportScheme(BaseModel):
    wpm: float
    rwpm: float
    accuracy: float
    second: int


class GetReportSchema(BaseModel):
    id: int
    create_at: datetime
    updated_at: datetime
    user_id: int
    session_id: str
    wpm: float
    rwpm: float
    second: int
    accuracy: float
    file_path: str

    class Config:
        orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(db: db_dependency,token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,os.getenv("JWT_SECRET_KEY"),algorithms = [os.getenv("ALGORITHM")])
        id = payload.get("id")
        username = payload.get("username")
        exp = datetime.utcfromtimestamp(payload.get("exp"))
        stmt = select(User).where((User.id == id) & (User.username == username))
        that_user = db.execute(stmt).scalar_one_or_none()
        if that_user != None and exp > datetime.utcnow():
            return payload
            # return JSONResponse(status_code = status.HTTP_200_OK,content={"message":payload})
        else:
            raise HTTPException(status=401)
    except Exception as e:
        print("verify_token",e)



@app.get("/user-info")
async def user_info(db: db_dependency,token: str = Depends(verify_token)):
    stmt = select(User).where(User.id == token.get("id"))
    res = db.execute(stmt).scalar_one_or_none()
    return res


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


@app.post("/get-email/")
async def get_email_by_username(user: GetEmail, db: db_dependency):
    try:
        stmt = select(User).where(User.email == user.email)
        that_user = db.execute(stmt).scalar_one_or_none()
        print("that_user",that_user)
        if not that_user:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return that_user.email

    except HTTPException as httpe:
        raise httpe

    except SQLAlchemyError as sqle:
        logging.exception("database query failed")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="SQLAlchemyError Exception")

    except Exception as generic_exc:
        logging.exception("Unexpected error")
        raise HTTPException(status_code=500, detail="Unexpected server error")


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
    except Exception as e:
        print("Exception", e)


@app.delete("/delete-user/{id}", status_code=status.HTTP_200_OK)
async def delete_user(id: int, db: db_dependency):
    try:
        that_user = db.query(User).get(id)
        db.delete(that_user)
        db.commit()
        return "data deleted successfully"
    except Exception as e:
        return f"Exception {e}"


@app.post("/reset-password/")
async def reset_password(user: ResetPassword, db: db_dependency):
    print("user",user)
    try:
        stmt = select(User).where(User.email == user.email)
        that_user = db.execute(stmt).scalar_one_or_none()
        print("that_user",that_user)
        that_user.password = user.password
        that_user.verified_user = user.verified_user
        db.add(that_user)
        db.commit()
        db.refresh(that_user)
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



@app.post("/character-updated")
async def update_character(character: MistakeLetterSchema, db: db_dependency, token_data: Dict = Depends(verify_token)):
    js = character.jon
    no_js = character.no_jon
    user_id = token_data.get('id')

    stmt = select(MistakeLetter).where(MistakeLetter.user_id == user_id)
    no_char_query = db.query(MistakeTracker).filter(MistakeTracker.user_id == user_id).scalar()
    db_response = db.execute(stmt).scalar_one_or_none()

    # deduct_mistake_letters(token_data.get("id"),db)
    if db_response and no_char_query:
        try:
            updated_json = db_response.jon.copy()
            for key in js:
                updated_json[key][0] += js[key][0]
                updated_json[key][1] += js[key][1]

            db_response.jon.clear()
            db_response.jon = MutableDict(updated_json)
            db.commit()
            db.refresh(db_response)

            for i in no_js:
                no_char_query.count[i] += no_js[i]

            db.commit()
            db.refresh(no_char_query)

            deduct_mistake_letters(user_id, db)
            return {
                "message":db_response,
                "status": status.HTTP_200_OK
            }

        except Exception as e:
            print("update_character",e)

    else:
        updated_json = {key: [0, 0] for key in string.ascii_lowercase}
        for i in js:
            updated_json[i][0] = js[i][0]
            updated_json[i][1] = js[i][1]
        print(updated_json)
        new_instance = MistakeLetter(user_id = user_id,jon = updated_json)
        new_mistakeTracker = MistakeTracker(user_id = user_id,count = no_js)

        db.add_all([new_instance,new_mistakeTracker])
        db.commit()
        db.refresh(new_instance)
        db.refresh(new_mistakeTracker)
        return {"message":new_instance,"status":status.HTTP_201_CREATED}

@app.post("/create-report")
async def report(report: ReportScheme, db: db_dependency, token_data: str = Depends(verify_token)):
    user_id = token_data.get("id")
    session_id = str(uuid.uuid4())
    file_src = "report/" + f"session-{session_id}.json"

    new_instance = Report(
        user_id=user_id,
        session_id=session_id,
        wpm=report.wpm,
        rwpm=report.rwpm,
        accuracy=report.accuracy,
        file_path=file_src,
        second=report.second
    )

    try:
        db.add(new_instance)
        db.commit()
        db.refresh(new_instance)
        return new_instance
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))


@app.get("/get-report", response_model=List[GetReportSchema])
async def get_report(db: db_dependency, token_data: dict = Depends(verify_token)):
    result = db.execute(select(Report).filter(Report.user_id == token_data.get("id")))
    reports = result.scalars().all()
    return reports


@app.get("/get-mistakes")
async def get_mistake_letters(db:db_dependency,token_data: dict = Depends(verify_token)):
    try:
        stmt = select(MistakeLetter).where(MistakeLetter.user_id == token_data.get("id"))
        out = db.execute(stmt)
        dd = out.scalar_one_or_none()
        print(jsonable_encoder(dd).get('jon'))
        return jsonable_encoder(dd).get('jon')
    except Exception as e:
        print(e)

