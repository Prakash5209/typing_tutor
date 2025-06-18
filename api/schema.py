from pydantic import BaseModel
from typing import Annotated, Optional,Dict,List
from datetime import datetime


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

