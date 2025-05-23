from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Annotated, Optional,Dict,List
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select
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
from models import User,MistakeLetter,Report


env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


class UserBase(BaseModel):
    username: str
    email: str
    password: str


class GetEmailByUsername(BaseModel):
    username: str


class ResetPassword(BaseModel):
    email: str
    password: str


class GetUser(BaseModel):
    username: str
    password: str


class UpdateUserBase(BaseModel):
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]


class MistakeLetterSchema(BaseModel):
    jon: Dict[str, List[int]]


class ReportScheme(BaseModel):
    # id: Optional[int]
    wpm: float
    rwpm: float
    accuracy: float


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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


# get email only from Username
@app.post("/get-email/")
async def get_email_by_username(user: GetEmailByUsername, db: db_dependency):
    try:
        stmt = select(User).where(User.username == user.username)
        that_user = db.execute(stmt).scalar_one_or_none()
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


@app.post("/reset-password/")
async def reset_password(user: ResetPassword, db: db_dependency):
    try:
        stmt = select(User).where(User.email == user.email)
        that_user = db.execute(stmt).scalar_one_or_none()
        that_user.password = user.password
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

@app.post("/character-updated")
async def update_character(character: MistakeLetterSchema, db: db_dependency, token_data: Dict = Depends(verify_token)):
    print("token_data",token_data)
    # if token_data.status_code != 200:
    #     return token_data
    js = character.jon
    # user_id = json.loads(token_data.body)["message"]["id"]
    user_id = token_data.get('id')
    
    instance = db.scalar(select(MistakeLetter).where(MistakeLetter.user_id == user_id))
    
    if instance is None:
        # Create new record
        char_dict = {key: [0, 0] for key in string.ascii_lowercase}
        for i in js:
            char_dict[i][0] += js[i][0]
            char_dict[i][1] += js[i][1]
            
        new_instance = MistakeLetter(user_id=user_id, jon=char_dict)
        try:
            db.add(new_instance)
            db.commit()
            db.refresh(new_instance)
            return {"message": "character created", "status": status.HTTP_201_CREATED}
        except Exception as e:
            db.rollback()
            print("update_character new", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="failed to create new character object"
            )
    else:
        # Creating a completely new dictionary instead of modifying a copy
        updated_json = {key: [0, 0] for key in string.ascii_lowercase}
        
        for key in instance.jon:
            updated_json[key] = list(instance.jon[key])
            
        # Then update with new values
        for i in js:
            updated_json[i][0] += js[i][0]
            updated_json[i][1] += js[i][1]
        
        try:
            instance.jon = updated_json
            db.commit()
            return {
                "message": "character updated",
                "status": status.HTTP_200_OK
            }
        except Exception as e:
            db.rollback()
            print("update_character update", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="failed to update the character json"
            )



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
        file_path=file_src
    )

    try:
        db.add(new_instance)
        db.commit()
        db.refresh(new_instance)
        return new_instance
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

