from pydantic import BaseModel

from datetime import datetime


class MistypeSchema(BaseModel):
    expected:str
    typed:str
    timestamp:datetime

    class config:
        orm_mode = True

