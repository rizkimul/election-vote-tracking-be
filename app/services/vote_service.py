from typing import List
from .. import models, schemas
import datetime
from sqlalchemy.orm import Session

class VoteService:
    def __init__(self, vote_repo):
        self.vote_repo = vote_repo

    def add_vote(self, data: schemas.VoteCreate) -> models.VoteResult:
        vote = models.VoteResult(**data.dict())
        return self.vote_repo.create(vote)

    def list_votes(self) -> List[models.VoteResult]:
        return self.vote_repo.list_all()

    def import_votes_from_dataframe(self, df):
        # df: pandas.DataFrame
        objects = []
        for _, row in df.iterrows():
            v = models.VoteResult(
                district = row["district"],
                sub_district = row["sub_district"],
                village = row["village"],
                total_votes = int(row["total_votes"]),
                election_year = int(row["election_year"]),
            )
            objects.append(v)
        self.vote_repo.bulk_create(objects)
