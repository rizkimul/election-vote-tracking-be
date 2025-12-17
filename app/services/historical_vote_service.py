from .. import models, schemas
from ..repositories.historical_vote_repo import HistoricalVoteRepository
import pandas as pd
from typing import List
from io import BytesIO

class HistoricalVoteService:
    def __init__(self, repo: HistoricalVoteRepository):
        self.repo = repo

    def add_historical_vote(self, data: schemas.HistoricalVoteCreate) -> models.HistoricalVote:
        # Note: data.data is the JSON dict
        vote_dict = data.dict()
        vote = models.HistoricalVote(**vote_dict)
        return self.repo.create(vote)

    def list_historical_votes(self, page=1, size=20, **kwargs):
        offset = (page - 1) * size
        items = self.repo.list_filtered(offset=offset, limit=size, **kwargs)
        total = self.repo.count_filtered(**kwargs)
        return {"items": items, "total": total, "page": page, "size": size}

    def get_filter_options(self, dapil: str = None):
        return {
            "dapils": self.repo.get_distinct_dapils(),
            "kecamatans": self.repo.get_distinct_kecamatans(dapil)
        }

    def get_import_logs(self):
        return self.repo.get_import_logs()

    def import_votes_from_file(self, file_content: bytes, filename: str = "unknown"):
        # Create initial log entry
        log = models.ImportLog(
            filename=filename,
            status="processing",
            records_count=0
        )
        self.repo.create_import_log(log)

        try:
            # Read all sheets
            xls = pd.ExcelFile(BytesIO(file_content))
            sheet_names = xls.sheet_names
            
            objects = []
            
            # Strategy: specifically look for "Dapil" sheets
            dapil_sheets = [s for s in sheet_names if "dapil" in s.lower()]
            print(f"DEBUG: Sheets found: {sheet_names}")
            
            if not dapil_sheets:
                # Fallback: try flat format on first sheet
                print("DEBUG: No Dapil sheets found, trying flat format")
                df = pd.read_excel(xls, sheet_name=0)
                imported_count = self._import_flat_dataframe(df)
                
                # Update log on success
                log.status = "success"
                log.records_count = imported_count
                self.repo.create_import_log(log) # Actually updates existing if session logic handled, but create_import_log adds new. 
                # Repo.create_import_log implementation does 'add', 'commit'. 
                # Ideally we should update. But for now I'll just re-save. 
                # Wait, 'add' on already attached object updates it?
                # Yes, if it's the same object instance attached to session.
                # But 'create_import_log' does 'refresh'. 
                
                # To be safe and simple: just modify the object and commit.
                # Since I don't have an update method in repo, I'll relies on SQLAlchemy session identity map.
                # Or I can just set attributes and commit if session is open. 
                # But repo manages session. 
                # I will assume repo.create_import_log handles existing objects or I should have added 'update_import_log'.
                # Let's check repo again. 'add' attaches instance. 'commit' flushes changes.
                self.repo.db.commit() 
                return

            # Main Logic for Wide Format
            parsed_data = {} # Key: (dapil, kecamatan, year), Value: dict of votes
            
            for sheet in dapil_sheets:
                print(f"DEBUG: Processing sheet {sheet}")
                dapil_name = sheet 
                df = pd.read_excel(xls, sheet_name=sheet, header=None)
                
                # Dynamic Header Search
                header_row_idx = -1
                for i in range(min(15, len(df))):
                    row_vals = [str(x).strip().upper() for x in df.iloc[i].values]
                    # Look for signature columns
                    if "JUMLAH AKHIR" in row_vals or "JUMLAH" in row_vals or (row_vals.count("NAN") < len(row_vals) - 2 and "KAB. BANDUNG" in str(row_vals)):
                         # heuristic to find header row.
                         # Based on debug output: Row 3 (index 3) has "JUMLAH AKHIR" at column 10 (K) maybe?
                         pass
                    
                    # Better heuristic: Check if specific known headers exist OR we find the row with Kecamatan names.
                    # The screenshot shows "KEC. DAYEUHKOLOT", "KEC. MARGAASIH", etc.
                    # Warning: The header row usually contains Kecamatan names. 
                    # Row 3 (idx 3) in debug output had "JUMLAH AKHIR" at the end.
                    # Let's inspect row 3 from debug output: `3 NaN ... JUMLAH AKHIR`. 
                    # If this is the header row, then column indices should be aligned.
                    
                    # The code relies on finding "JUMLAH AKHIR" to stop or validate.
                    # Let's try to match non-empty values that start with "KEC.".
                    matches_kec = [x for x in row_vals if "KEC." in x]
                    if len(matches_kec) > 0:
                        header_row_idx = i
                        break
                    
                    # Fallback: look for "JUMLAH AKHIR"
                    if "JUMLAH AKHIR" in row_vals:
                         header_row_idx = i
                         break

                if header_row_idx == -1:
                    print(f"DEBUG: Could not find header row for {sheet}")
                    continue
                
                print(f"DEBUG: Found Header Row at index {header_row_idx}")

                header_row = df.iloc[header_row_idx]
                kecamatan_indices = {} # { col_idx: kec_name }
                
                # Dynamic start column? Usually col 4 (E).
                for c in range(4, len(header_row)):
                    val = str(header_row[c]).strip()
                    if val.upper() == "JUMLAH AKHIR" or val.lower() == "nan": 
                         # If we hit valid kecamatan before this, we are good.
                         if val.upper() == "JUMLAH AKHIR": break
                         # If nan, continue? or break? Usually header names are contiguous.
                         continue 
                         
                    kecamatan_indices[c] = val
                
                if not kecamatan_indices:
                     print("DEBUG: No Kecamatan columns found")
                     continue

                # Data processing
                # Start 2 rows after header?
                start_row = header_row_idx + 2 # Skip row with numbers (1,2,3)
                
                for r in range(start_row, len(df)):
                    row = df.iloc[r]
                    try:
                        # Col 1 is Year (e.g. 2024), Col 3 is Name
                        year_val = row[1]
                        if not pd.isna(year_val) and str(year_val).replace('.','').isnumeric():
                             # Handle cases like 2024.0 or string "2024"
                             try:
                                year = int(float(year_val))
                             except:
                                pass
                        
                        name_val = str(row[3]).strip()
                        if not name_val or name_val.lower() == 'nan': continue
                        
                        # Valid row.
                        # We need a year. If year is missing in this row, inherit from previous (handled by scope of 'year' variable).
                        # But initial year must be set if first row lacks it.
                        if 'year' not in locals(): year = 2024
                        
                        # print(f"DEBUG: Processing Row {r}: Name={name_val} Year={year}")

                        for col_idx, kec_name in kecamatan_indices.items():
                            try:
                                vote_val = int(row[col_idx])
                            except:
                                vote_val = 0
                            
                            if vote_val >= 0:
                                key = (dapil_name, "Kabupaten Bandung", kec_name, year) 
                                if key not in parsed_data: parsed_data[key] = {}
                                parsed_data[key][name_val] = vote_val
                                # if vote_val > 0: print(f"DEBUG: Added vote {vote_val} for {kec_name} - {name_val}")

                    except Exception as e:
                         print(f"DEBUG: Row Error at {r}: {e}")
                         continue

            # Convert to Objects
            for (d_dapil, d_kab, d_kec, d_year), votes_dict in parsed_data.items():
                total = sum(votes_dict.values())
                hv = models.HistoricalVote(
                    dapil=d_dapil,
                    kabupaten=d_kab,
                    kecamatan=d_kec,
                    desa="", 
                    election_year=d_year,
                    data=votes_dict,
                    total_votes=total
                )
                objects.append(hv)

            self.repo.bulk_create(objects)
            
            # Update log
            log.status = "success"
            log.records_count = len(objects)
            self.repo.db.commit()

        except Exception as e:
            print(f"IMPORT ERROR: {e}")
            log.status = "failed"
            log.error_message = str(e)
            self.repo.db.commit()
            raise e

    def _import_flat_dataframe(self, df: pd.DataFrame) -> int:
        # normalize columns
        df.columns = [c.lower() for c in df.columns]

        # Fill missing election_year if not present
        if "tahun" not in df.columns and "election_year" not in df.columns:
            df["election_year"] = 2024 # Default or make optional
        
        year_col = "election_year" if "election_year" in df.columns else "tahun"
        
        # Group by location keys
        group_keys = ["dapil", "kabupaten", "kecamatan", "desa", year_col]
        
        # Check if we have 'partai' and 'suara'
        if "partai" not in df.columns or "suara" not in df.columns:
            raise ValueError("Excel must have 'partai' and 'suara' columns")

        objects = []
        grouped = df.groupby(group_keys)
        
        for name, group in grouped:
            # name is tuple of values corresponding to group_keys
            dapil, kab, kec, desa, year = name
            
            # Construct vote breakdown
            vote_data = {}
            total_votes = 0
            for _, row in group.iterrows():
                p = row["partai"]
                s = int(row["suara"])
                vote_data[p] = s
                total_votes += s
            
                hv = models.HistoricalVote(
                    dapil=dapil,
                    kabupaten=kab,
                    kecamatan=kec,
                    desa=desa,
                    election_year=int(year),
                    data=vote_data,
                    total_votes=total_votes
                )
            objects.append(hv)
        
        self.repo.bulk_create(objects)
        return len(objects)

