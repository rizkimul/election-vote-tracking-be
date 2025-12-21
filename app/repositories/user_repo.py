from sqlalchemy.orm import Session
from .. import models

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_nik(self, nik: str):
        return self.db.query(models.User).filter(models.User.nik == nik).first()

    def create(self, user: models.User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: models.User):
        self.db.commit()
        self.db.refresh(user)
        return user

