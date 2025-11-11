from typing import List
from .. import models, schemas
import pandas as pd
from datetime import datetime, date

class EngagementService:
    def __init__(self, engagement_repo):
        self.engagement_repo = engagement_repo

    def add_engagement(self, data: schemas.EngagementCreate):
        ent = models.Engagement(**data.dict())
        return self.engagement_repo.create(ent)

    def list_engagements(self,
                         page: int = 1,
                         size: int = 20,
                         district: str | None = None,
                         event_type: str | None = None,
                         date_from: date | None = None,
                         date_to: date | None = None,
                         min_participants: int | None = None):
        offset = (page - 1) * size
        items, total = self.engagement_repo.list_filtered(offset=offset,
                                                          limit=size,
                                                          district=district,
                                                          event_type=event_type,
                                                          date_from=date_from,
                                                          date_to=date_to,
                                                          min_participants=min_participants)
        return {"items": items, "total": total, "page": page, "size": size}

    def heatmap(self):
        return self.engagement_repo.heatmap_data()

    def import_engagements_from_dataframe(self, df: pd.DataFrame):
        # normalize columns to lowercase
        df.columns = [c.lower() for c in df.columns]
        required = {"nik","name","district","sub_district","village","hamlet","rt_rw","event_type","participants","date"}
        if not required.issubset(set(df.columns)):
            raise ValueError(f"Missing required columns: {required - set(df.columns)}")
        objects = []
        for _, row in df.iterrows():
            # parse date safely
            d = row["date"]
            if not isinstance(d, (datetime, date)):
                d = pd.to_datetime(d).date()
            ent = models.Engagement(
                nik = str(row["nik"]),
                name = str(row["name"]),
                district = row["district"],
                sub_district = row["sub_district"],
                village = row["village"],
                hamlet = row["hamlet"],
                rt_rw = str(row["rt_rw"]),
                event_type = row["event_type"],
                participants = int(row["participants"]),
                date = d,
                lat = float(row["lat"]) if "lat" in df.columns and not pd.isna(row.get("lat")) else None,
                lng = float(row["lng"]) if "lng" in df.columns and not pd.isna(row.get("lng")) else None,
            )
            objects.append(ent)
        # bulk insert via repo.bulk_create not present for engagements; use db session saving
        # we'll commit each for safety (you can optimize later)
        for o in objects:
            self.engagement_repo.create(o)
