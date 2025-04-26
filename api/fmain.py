from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from schema import MistypeSchema
from models import MistypeModel

database_url = "mysql+mysqlconnector://root@localhost:3307/keystroke"
engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "okay"}


@app.post("/mistype")
def mistype_record(payload: MistypeSchema):
    db = SessionLocal()
    new_record = MistypeModel(
        expected=payload.expected,
        typed=payload.typed,
        timestamp=payload.timestamp
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    db.close()
    return {"message": "mistyped char recorded", "data": payload}


@app.get("/suggestions")
def get_suggestions():
    output_file = "../output.txt"
    try:
        with open(output_file, "r") as file:
            content = file.read()
            return {"text": content.strip()}
    except FileNotFoundError:
        return {"error": "Output file not found."}
    except Exception as e:
        return {"error": str(e)}
