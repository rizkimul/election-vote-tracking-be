import pandas as pd
from app.services.historical_vote_service import HistoricalVoteService
from app.repositories.historical_vote_repo import HistoricalVoteRepository
from app.database import SessionLocal, engine
from app import models
import io

# 1. Setup DB
models.Base.metadata.create_all(bind=engine)
db = SessionLocal()
repo = HistoricalVoteRepository(db)
svc = HistoricalVoteService(repo)

# 2. Create Replica Data
# Structure matching screenshot:
# Rows 0-3: Header Info
# Row 4 (Index 4): Headers (A, NO, DATA..., ..., Soreang, Pasir Jambu, ..., JUMLAH AKHIR)
# Row 5 (Index 5): Numbers (1, 2, 3...)
# Row 6 (Index 6): Data (2024, PARTAI DEMOKRAT, ...)

data = [
    ["Header 1"], # 0
    ["Header 2"], # 1
    ["Header 3"], # 2
    ["Header 4"], # 3
    ["A", "NO", "DATA PEROLEHAN", "", "Soreang", "Pasir Jambu", "JUMLAH AKHIR"], # 4 - Headers
    ["1", "2", "3", "", "4", "5", "19"], # 5 - Numbers
    [2024, "", "PARTAI DEMOKRAT", "", 9000, 2000, 11000], # 6 - Data Party
    ["", "", "", "", "", "", ""], # 7 - Empty
    [2024, "", "SAEFUL BACHRI", "", 5000, 800, 5800], # 8 - Data Candidate
]

df = pd.DataFrame(data)

# Create "Dapil 1" sheet
output = io.BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Dapil 1', header=False, index=False)
    
content = output.getvalue()

# 3. Test Import
print("Testing import...")
try:
    svc.import_votes_from_file(content)
    print("Import successful!")
    
    # Verify Data
    votes = repo.list_filtered(limit=100)
    print(f"Total Votes Imported: {len(votes)}")
    for v in votes:
        print(f"Vote: Dapil={v.dapil}, Kec={v.kecamatan}, Data={v.data}")
        
except Exception as e:
    print(f"Import Failed: {e}")
    import traceback
    traceback.print_exc()

db.close()
