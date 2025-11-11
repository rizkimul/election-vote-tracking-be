from sqlalchemy.orm import Session
from .. import models
from typing import List, Optional

class VoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, vote: models.VoteResult):
        self.db.add(vote)
        self.db.commit()
        self.db.refresh(vote)
        return vote

    def bulk_create(self, votes: List[models.VoteResult]):
        # using bulk_save_objects for speed, but note no refresh
        self.db.bulk_save_objects(votes)
        self.db.commit()

    def list_all(self):
        return self.db.query(models.VoteResult).all()

    def list_filtered(self,
                      offset: int = 0,
                      limit: int = 20,
                      district: Optional[str] = None,
                      sub_district: Optional[str] = None,
                      village: Optional[str] = None,
                      election_year: Optional[int] = None):
        q = self.db.query(models.VoteResult)
        if district:
            q = q.filter(models.VoteResult.district == district)
        if sub_district:
            q = q.filter(models.VoteResult.sub_district == sub_district)
        if village:
            q = q.filter(models.VoteResult.village == village)
        if election_year:
            q = q.filter(models.VoteResult.election_year == election_year)
        return q.offset(offset).limit(limit).all()

    def count_filtered(self,
                       district: Optional[str] = None,
                       sub_district: Optional[str] = None,
                       village: Optional[str] = None,
                       election_year: Optional[int] = None):
        q = self.db.query(models.VoteResult)
        if district:
            q = q.filter(models.VoteResult.district == district)
        if sub_district:
            q = q.filter(models.VoteResult.sub_district == sub_district)
        if village:
            q = q.filter(models.VoteResult.village == village)
        if election_year:
            q = q.filter(models.VoteResult.election_year == election_year)
        return q.count()
