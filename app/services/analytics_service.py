from sqlalchemy import func
from typing import List, Dict, Any
from .. import models
from ..repositories.historical_vote_repo import HistoricalVoteRepository
from ..repositories.event_repo import EventRepository
from ..repositories.attendee_repo import AttendeeRepository
from ..repositories.activity_type_repo import ActivityTypeRepository

class AnalyticsService:
    def __init__(self, 
                 vote_repo: HistoricalVoteRepository,
                 event_repo: EventRepository,
                 attendee_repo: AttendeeRepository,
                 activity_repo: ActivityTypeRepository):
        self.vote_repo = vote_repo
        self.event_repo = event_repo
        self.attendee_repo = attendee_repo
        self.activity_repo = activity_repo

    def get_global_stats(self, dapil: str = None, kecamatan: str = None, source: str = 'all') -> Dict[str, int]:
        # Count total events (Basic filtering)
        event_query = self.event_repo.db.query(models.Event)
        if dapil:
            event_query = event_query.filter(models.Event.dapil == dapil)
        total_events = event_query.count()
        
        # Count total attendees
        attendee_query = self.attendee_repo.db.query(models.Attendee)
        if kecamatan:
             attendee_query = attendee_query.filter(models.Attendee.kecamatan == kecamatan)
        total_attendees = attendee_query.count()
        
        # Total votes from historical data - Logic Modified to split Web vs Import
        base_vote_query = self.vote_repo.db.query(func.sum(models.HistoricalVote.total_votes))
        
        if dapil:
            base_vote_query = base_vote_query.filter(models.HistoricalVote.dapil == dapil)
        if kecamatan:
            base_vote_query = base_vote_query.filter(models.HistoricalVote.kecamatan == kecamatan)
            
        # 1. Total Votes (All)
        total_votes = base_vote_query.scalar() or 0
        
        # 2. Web Votes (source='manual')
        web_vote_query = base_vote_query.filter(models.HistoricalVote.source == 'manual')
        total_votes_web = web_vote_query.scalar() or 0
        
        # 3. Import Votes (source != 'manual' or 'import')
        # Assuming anything not manual is import for now, or explicitly check 'import'
        # To be safe and cover 'import' or nulls if any (though migration set default), let's use != manual
        import_vote_query = base_vote_query.filter(models.HistoricalVote.source != 'manual')
        total_votes_import = import_vote_query.scalar() or 0
        

        # Count active wilayah (kecamatan)
        wilayah_query = self.vote_repo.db.query(func.count(func.distinct(models.HistoricalVote.kecamatan)))
        # We generally want wilayah count based on the relevant filter scope. 
        # If we removed the source filter from UI, this should probably reflect "Active Areas" generally.
        if dapil:
            wilayah_query = wilayah_query.filter(models.HistoricalVote.dapil == dapil)
        
        wilayah_count = wilayah_query.scalar() or 0
        
        return {
            "total_events": total_events,
            "total_attendees": total_attendees,
            "total_votes": total_votes,
            "total_votes_web": total_votes_web,
            "total_votes_import": total_votes_import,
            "wilayah_count": wilayah_count
        }

    def get_votes_summary(self, dapil: str = None, kecamatan: str = None, source: str = 'all') -> List[Dict[str, Any]]:
        # Aggregate votes by party from JSON `data` column
        # Using Python side aggregation for flexibility with JSON structure
        
        # If source filter is removed from UI, we probably want 'all' by default here
        filter_source = source if source != 'all' else None
        
        votes = self.vote_repo.list_filtered(limit=100000, dapil=dapil, kecamatan=kecamatan, source=filter_source)
        
        party_totals = {}
        
        for v in votes:
            if v.data:
                try:
                    # data might be a dict or a string depending on serialization
                    data_source = v.data
                    if isinstance(data_source, dict):
                        for party, count in data_source.items():
                            # Fix: Ensure count is treated as integer
                            safe_count = int(count) if count is not None else 0
                            party_totals[party] = party_totals.get(party, 0) + safe_count
                except Exception as e:
                    # Log error or skip bad record
                    continue
        
        # Format for frontend chart { "name": "Partai A", "value": 100 }
        result = [{"name": k, "value": v} for k, v in party_totals.items()]
        # Sort by value desc
        result.sort(key=lambda x: x["value"], reverse=True)
        return result

    def get_heatmap_data(self, dapil: str = None, kecamatan: str = None, source: str = 'all') -> List[Dict[str, Any]]:
        # Aggregate total votes per Kecamatan for Heatmap
        # Returning list of { "kecamatan": "Name", "intensity": 1234 }
        
        # We can use SQL group by for this
        Vote = models.HistoricalVote
        query = self.vote_repo.db.query(
            Vote.kecamatan, 
            func.sum(Vote.total_votes).label('total')
        )
        
        if source and source != 'all':
            query = query.filter(Vote.source == source)
        
        if dapil:
            query = query.filter(Vote.dapil == dapil)
        if kecamatan:
            query = query.filter(Vote.kecamatan == kecamatan)
            
        result = query.group_by(Vote.kecamatan).all()
        
        return [{"kecamatan": row.kecamatan, "intensity": row.total, "type": "votes"} for row in result]

    def get_engagement_trends(self) -> List[Dict[str, Any]]:
        # Aggregate attendees by month
        # Event.date is a python date object in SQLAlchemy result if defined as Date
        
        # Get all events with their attendee counts
        results = self.event_repo.db.query(
            models.Event.date, 
            func.count(models.Attendee.id).label('count')
        ).outerjoin(models.Attendee).group_by(models.Event.id).all()
        
        monthly_data = {}
        for event_date, count in results:
            if not event_date: continue
            # event_date is datetime.date object
            month_key = event_date.strftime("%Y-%m")
            monthly_data[month_key] = monthly_data.get(month_key, 0) + count
            
        # Sort and Format
        sorted_months = sorted(monthly_data.keys())
        # Return last 6 months or all
        return [{"month": m, "participants": monthly_data[m]} for m in sorted_months]

    def get_activity_distribution(self) -> List[Dict[str, Any]]:
        # Count events by Activity Type
        query = self.event_repo.db.query(
            models.ActivityType.name,
            func.count(models.Event.id).label('count')
        ).join(models.Event).group_by(models.ActivityType.name).all()
        
        # Consistent colors could be mapped here or on frontend
        # For now just return name/value
        return [{"name": row.name, "value": row.count} for row in query]
from sqlalchemy import func
