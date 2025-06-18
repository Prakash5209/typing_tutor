from sqlalchemy.orm import Session
from models import MistakeLetter,MistakeTracker
from sqlalchemy.ext.mutable import MutableDict


# mistake trakcer
def deduct_mistake_letters(user_id: int, db: Session):
    mistakeletter = db.query(MistakeLetter).filter(MistakeLetter.user_id == user_id).first()
    mistaketracker = db.query(MistakeTracker).filter(MistakeTracker.user_id == user_id).first()
    # print("mistakeletter", mistakeletter.jon)
    # print("mistaketracker", mistaketracker.count)

    updated_jon = mistakeletter.jon.copy()

    for i in mistaketracker.count:
        if mistaketracker.count[i] >= 5:
            if updated_jon[i][0] >= 1 and updated_jon[i][1] >= 1:
                updated_jon[i][0] -= 1
                updated_jon[i][1] -= 1
            elif updated_jon[i][0] >= 1:
                updated_jon[i][0] -= 1
            elif updated_jon[i][1] >= 1:
                updated_jon[i][1] -= 1

            mistaketracker.count[i] = 0

    mistakeletter.jon.clear()
    mistakeletter.jon = MutableDict(updated_jon)

    db.commit()
    db.refresh(mistakeletter)
    db.refresh(mistaketracker)

    # print("AFTER UPDATE:")
    # print("mistakeletter", mistakeletter.jon)
    # print("mistaketracker", mistaketracker.count)

