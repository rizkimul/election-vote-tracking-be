from sqlalchemy import func
from typing import List, Dict, Any
from .. import models
from ..repositories.historical_vote_repo import HistoricalVoteRepository
from ..repositories.event_repo import EventRepository
from ..repositories.attendee_repo import AttendeeRepository
from ..repositories.activity_type_repo import ActivityTypeRepository

class AnalyticsService:
    def __init__(self, 
                 event_repo: EventRepository,
                 attendee_repo: AttendeeRepository,
                 activity_repo: ActivityTypeRepository):
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
        
        # Count active wilayah (kecamatan with activities)
        # SABADESA: "Wilayah Tersentuh" based on attendees location
        wilayah_query = self.attendee_repo.db.query(func.count(func.distinct(models.Attendee.kecamatan)))
        if kecamatan:
             wilayah_query = wilayah_query.filter(models.Attendee.kecamatan == kecamatan)

        wilayah_count = wilayah_query.scalar() or 0
        
        # Count active desa/kelurahan
        desa_query = self.attendee_repo.db.query(func.count(func.distinct(models.Attendee.desa)))
        if kecamatan:
             desa_query = desa_query.filter(models.Attendee.kecamatan == kecamatan)
        
        desa_count = desa_query.scalar() or 0
        
        return {
            "total_events": total_events,
            "total_attendees": total_attendees,
            "total_votes": 0,  # Legacy field, returning 0
            "total_votes_web": 0,
            "total_votes_import": 0,
            "wilayah_count": wilayah_count,
            "desa_count": desa_count
        }

    def get_votes_summary(self, dapil: str = None, kecamatan: str = None, source: str = 'all') -> List[Dict[str, Any]]:
        # SABADESA: Vote tracking removed. Return empty list.
        return []

    def get_heatmap_data(self, dapil: str = None, kecamatan: str = None, source: str = 'all', level: str = 'kecamatan') -> List[Dict[str, Any]]:
        # SABADESA: Aggregate participants per Kecamatan or Desa
        
        if level == 'all':
            # Fetch both and combine
            # 1. Kecamatan
            q_kec = self.attendee_repo.db.query(
                models.Attendee.kecamatan.label('region_name'), 
                func.count(models.Attendee.id).label('total')
            ).filter(models.Attendee.kecamatan != None)
            
            if dapil:
                q_kec = q_kec.join(models.Event).filter(models.Event.dapil == dapil)
            if kecamatan: # If filtered by specific kecamatan, only show that kecamatan aggregate
                q_kec = q_kec.filter(models.Attendee.kecamatan == kecamatan)
                
            q_kec = q_kec.group_by(models.Attendee.kecamatan)
            res_kec = q_kec.all()
            
            # 2. Desa
            q_desa = self.attendee_repo.db.query(
                models.Attendee.desa.label('region_name'), 
                func.count(models.Attendee.id).label('total')
            ).filter(models.Attendee.desa != None)

            if dapil:
                q_desa = q_desa.join(models.Event).filter(models.Event.dapil == dapil)
            if kecamatan:
                q_desa = q_desa.filter(models.Attendee.kecamatan == kecamatan)
                
            q_desa = q_desa.group_by(models.Attendee.desa)
            res_desa = q_desa.all()
            
            # Combine
            data = [{"kecamatan": row.region_name, "intensity": row.total, "type": "Kecamatan"} for row in res_kec]
            data.extend([{"kecamatan": row.region_name, "intensity": row.total, "type": "Desa"} for row in res_desa])
            
            return data

        group_col = models.Attendee.kecamatan
        if level == 'desa':
            group_col = models.Attendee.desa

        query = self.attendee_repo.db.query(
            group_col.label('region_name'), 
            func.count(models.Attendee.id).label('total')
        )
        
        # Join with event if we need to filter by Dapil (and Attendee doesn't have it, though Event does)
        if dapil:
            query = query.join(models.Event).filter(models.Event.dapil == dapil)
            
        if kecamatan:
            query = query.filter(models.Attendee.kecamatan == kecamatan)
            
        # Group by non-null region
        query = query.filter(group_col != None).group_by(group_col)
        
        result = query.all()
        
        # Return "kecamatan" key for backward compatibility, or use region_name
        # The frontend expects "kecamatan" currently. 
        # We map region_name to "kecamatan" key.
        return [{"kecamatan": row.region_name, "intensity": row.total, "type": level.capitalize()} for row in result]

    def get_engagement_trends(self) -> List[Dict[str, Any]]:
        # Aggregate attendees by month
        results = self.event_repo.db.query(
            models.Event.date, 
            func.count(models.Attendee.id).label('count')
        ).outerjoin(models.Attendee).group_by(models.Event.id).all()
        
        monthly_data = {}
        for event_date, count in results:
            if not event_date: continue
            month_key = event_date.strftime("%Y-%m")
            monthly_data[month_key] = monthly_data.get(month_key, 0) + count
            
        sorted_months = sorted(monthly_data.keys())
        return [{"month": m, "participants": monthly_data[m]} for m in sorted_months]

    def get_activity_distribution(self) -> List[Dict[str, Any]]:
        # Count events by Activity Type
        query = self.event_repo.db.query(
            models.ActivityType.name,
            func.count(models.Event.id).label('count')
        ).join(models.Event).group_by(models.ActivityType.name).all()
        
        return [{"name": row.name, "value": row.count} for row in query]
from sqlalchemy import func
