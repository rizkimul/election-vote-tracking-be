from sqlalchemy.orm import Session
from .. import models
from typing import List, Optional

class HistoricalVoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, vote: models.HistoricalVote):
        self.db.add(vote)
        self.db.commit()
        self.db.refresh(vote)
        return vote

    def bulk_create(self, votes: List[models.HistoricalVote]):
        self.db.bulk_save_objects(votes)
        self.db.commit()

    def list_filtered(self,
                      offset: int = 0,
                      limit: int = 20,
                      dapil: Optional[str] = None,
                      kabupaten: Optional[str] = None,
                      kecamatan: Optional[str] = None,
                      desa: Optional[str] = None,
                      election_year: Optional[int] = None,
                      source: Optional[str] = None):
        q = self.db.query(models.HistoricalVote)
        if dapil:
            q = q.filter(models.HistoricalVote.dapil == dapil)
        if kabupaten:
            q = q.filter(models.HistoricalVote.kabupaten == kabupaten)
        if kecamatan:
            q = q.filter(models.HistoricalVote.kecamatan == kecamatan)
        if desa:
            q = q.filter(models.HistoricalVote.desa == desa)
        if election_year:
            q = q.filter(models.HistoricalVote.election_year == election_year)
        if source:
            q = q.filter(models.HistoricalVote.source == source)
        return q.offset(offset).limit(limit).all()

    def count_filtered(self,
                       dapil: Optional[str] = None,
                       kabupaten: Optional[str] = None,
                       kecamatan: Optional[str] = None,
                       desa: Optional[str] = None,
                       election_year: Optional[int] = None,
                       source: Optional[str] = None):
        q = self.db.query(models.HistoricalVote)
        if dapil:
            q = q.filter(models.HistoricalVote.dapil == dapil)
        if kabupaten:
            q = q.filter(models.HistoricalVote.kabupaten == kabupaten)
        if kecamatan:
            q = q.filter(models.HistoricalVote.kecamatan == kecamatan)
        if desa:
            q = q.filter(models.HistoricalVote.desa == desa)
        if election_year:
            q = q.filter(models.HistoricalVote.election_year == election_year)
        if source:
            q = q.filter(models.HistoricalVote.source == source)
        return q.count()

    def get_distinct_dapils(self) -> List[str]:
        return [r[0] for r in self.db.query(models.HistoricalVote.dapil).distinct().filter(models.HistoricalVote.dapil != None).order_by(models.HistoricalVote.dapil).all()]

    def get_distinct_kecamatans(self, dapil: Optional[str] = None) -> List[str]:
        q = self.db.query(models.HistoricalVote.kecamatan).distinct().filter(models.HistoricalVote.kecamatan != None)
        if dapil:
            q = q.filter(models.HistoricalVote.dapil == dapil)
        return [r[0] for r in q.order_by(models.HistoricalVote.kecamatan).all()]


    def create_import_log(self, log: models.ImportLog):
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_import_logs(self, limit: int = 50):
        return self.db.query(models.ImportLog).order_by(models.ImportLog.created_at.desc()).limit(limit).all()
