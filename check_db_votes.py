from app.database import SessionLocal
from app.models import HistoricalVote

db = SessionLocal()
count = db.query(HistoricalVote).count()
print(f"Total Historical Votes: {count}")

if count > 0:
    first = db.query(HistoricalVote).first()
    print(f"Sample: {first.kecamatan} - {first.data}")
