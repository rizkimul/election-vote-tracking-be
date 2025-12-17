from typing import List, Dict, Any
from sqlalchemy import func
from .. import models
from ..repositories.historical_vote_repo import HistoricalVoteRepository
from ..repositories.event_repo import EventRepository

class PrioritizationService:
    def __init__(self, vote_repo: HistoricalVoteRepository, event_repo: EventRepository):
        self.vote_repo = vote_repo
        self.event_repo = event_repo

    def get_suggestions(self) -> List[Dict[str, Any]]:
        # 1. Get Votes per Kecamatan
        votes_query = self.vote_repo.db.query(
            models.HistoricalVote.kecamatan,
            func.sum(models.HistoricalVote.total_votes).label('total_votes')
        ).group_by(models.HistoricalVote.kecamatan).all()

        vote_map = {row.kecamatan: row.total_votes for row in votes_query if row.kecamatan}

        # 2. Get Events per Kecamatan
        # Since location is JSON, we process in Python for simplicity in this MVP
        # Fetching all events might be heavy in prod, but fine for MVP
        results_tuple = self.event_repo.list_filtered(limit=5000) 
        all_events = results_tuple[0] # list_filtered returns (items, total)
        
        event_counts = {}
        for event in all_events:
            # Assume location_hierarchy is dict like {"kecamatan": "Name"}
            # In SQLite it comes out as dict if stored as JSON
            if event.location_hierarchy and isinstance(event.location_hierarchy, dict):
                kec = event.location_hierarchy.get("kecamatan")
                if kec:
                    event_counts[kec] = event_counts.get(kec, 0) + 1

        # 3. Calculate Score
        results = []
        for kecamatan, actual_votes in vote_map.items():
            # Heuristic: Target is 30% growth from historical (or 1000 minimum)
            target_votes = max(actual_votes * 1.3, 1000) 
            gap = target_votes - actual_votes
            
            # Ensure gap is positive for scoring
            gap = max(0, gap)
            
            event_count = event_counts.get(kecamatan, 0)
            
            # Score: High Gap + Low Events = High Score
            # Formula: Gap * (1 / (Events + 1))
            urgency_score = gap * (10 / (event_count + 1))
            
            results.append({
                "kecamatan": kecamatan,
                "score": int(urgency_score),
                "actual_votes": actual_votes,
                "target_votes": int(target_votes),
                "event_count": event_count,
                "reason": self._generate_reason(gap, event_count)
            })

        # Sort by score desc
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:10] # Top 10 recommendations

    def _generate_reason(self, gap, events):
        if events == 0:
            return "Belum ada kegiatan di wilayah ini"
        if gap > 2000:
            return "Potensi suara sangat tinggi, perlu intensifikasi"
        if gap > 500:
            return "Perlu penguatan basis suara"
        return "Maintenance rutin diperlukan"
