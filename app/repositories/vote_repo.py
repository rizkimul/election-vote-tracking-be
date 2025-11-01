from sqlalchemy.orm import Session
from .. import models
from typing import List

class VoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, vote: models.VoteResult):
        self.db.add(vote)
        self.db.commit()
        self.db.refresh(vote)
        return vote

    def bulk_create(self, votes: List[models.VoteResult]):
        self.db.bulk_save_objects(votes)
        self.db.commit()

    def list_all(self):
        return self.db.query(models.VoteResult).all()
