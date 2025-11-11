from typing import List
from .. import models, schemas
import pandas as pd

class VoteService:
    def __init__(self, vote_repo):
        self.vote_repo = vote_repo

    def add_vote(self, data: schemas.VoteCreate) -> models.VoteResult:
        vote = models.VoteResult(**data.dict())
        return self.vote_repo.create(vote)

    def list_votes(self,
                   page: int = 1,
                   size: int = 20,
                   district: str | None = None,
                   sub_district: str | None = None,
                   village: str | None = None,
                   election_year: int | None = None):
        offset = (page - 1) * size
        items = self.vote_repo.list_filtered(offset=offset, limit=size,
                                             district=district,
                                             sub_district=sub_district,
                                             village=village,
                                             election_year=election_year)
        total = self.vote_repo.count_filtered(district=district,
                                              sub_district=sub_district,
                                              village=village,
                                              election_year=election_year)
        return {"items": items, "total": total, "page": page, "size": size}

    def import_votes_from_dataframe(self, df: pd.DataFrame):
        # normalize columns to lowercase to be tolerant of Excel column names
        df.columns = [c.lower() for c in df.columns]
        required = {"district","sub_district","village","total_votes","election_year"}
        if not required.issubset(set(df.columns)):
            raise ValueError(f"Missing required columns: {required - set(df.columns)}")
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
