
from database import engine, Base
import models  # this import is needed to register models

Base.metadata.create_all(bind=engine)
