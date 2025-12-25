from typing import List, Dict, Any
from sqlalchemy import func
from .. import models
from ..repositories.event_repo import EventRepository
from ..repositories.attendee_repo import AttendeeRepository

class PrioritizationService:
    def __init__(self, event_repo: EventRepository, attendee_repo: AttendeeRepository):
        self.event_repo = event_repo
        self.attendee_repo = attendee_repo

    def get_suggestions(self) -> List[Dict[str, Any]]:
        # 1. Get Event Counts per Kecamatan
        events_query = self.event_repo.db.query(
            models.Event.kecamatan,
            func.count(models.Event.id).label('event_count')
        ).group_by(models.Event.kecamatan).all()
        
        event_map = {row.kecamatan: row.event_count for row in events_query if row.kecamatan}
        
        # 2. Get Attendee Counts per Kecamatan
        attendees_query = self.attendee_repo.db.query(
            models.Attendee.kecamatan,
            func.count(models.Attendee.id).label('attendee_count')
        ).group_by(models.Attendee.kecamatan).all()
        
        attendee_map = {row.kecamatan: row.attendee_count for row in attendees_query if row.kecamatan}
        
        # Combine list of all known kecamatans from both sources
        all_kecamatans = set(event_map.keys()) | set(attendee_map.keys())
        
        if not all_kecamatans:
            return []

        # 3. Calculate Dynamic Benchmarks (Averages)
        total_events = sum(event_map.values())
        total_attendees = sum(attendee_map.values())
        num_districts = len(all_kecamatans)
        
        avg_event_count = total_events / num_districts if num_districts > 0 else 0
        avg_attendee_count = total_attendees / num_districts if num_districts > 0 else 0

        # Define Dynamic Thresholds based on plan
        # Minim: < 50% of Average Events
        # Over-visited: > 200% of Average Events
        # Inefektif: Event > 50% Avg AND Attendee < 50% Avg
        
        threshold_minim_event = avg_event_count * 0.5
        threshold_high_event = avg_event_count * 2.0
        threshold_low_attendee = avg_attendee_count * 0.5

        results = []
        for kecamatan in all_kecamatans:
            event_count = event_map.get(kecamatan, 0)
            attendee_count = attendee_map.get(kecamatan, 0)
            
            score = 0
            reason = ""
            
            # Dynamic Logic Implementation
            if event_count < threshold_minim_event:
                # Priority: High (Need to schedule events)
                score = 80
                reason = "Wilayah ini tertinggal jauh dari standar kampanye. Prioritas Utama."
            
            elif event_count > threshold_high_event:
                # Priority: High (as per old logic "Over-visited" is high score but different reason)
                # Or maybe user wants to flag it. Keeping score high as "Important to Notice"
                score = 90
                reason = "Wilayah ini mendapatkan porsi kegiatan yang sangat masif (2x lipat standar)."
                
            elif event_count > threshold_minim_event and attendee_count < threshold_low_attendee:
                # Ineffective: Active enough, but low turnout
                score = 70
                reason = "Kegiatan sering, tapi massa sedikit. Strategi acara perlu dievaluasi."
                
            else:
                # Stable / Normal
                score = 40
                reason = "Wilayah ini berjalan on-track sesuai ritme rata-rata kampanye."

            # Special case for 0 events if not caught above
            if event_count == 0:
                 score = 85
                 reason = "Belum ada kegiatan sama sekali. Perlu segera dijadwalkan."

            results.append({
                "kecamatan": kecamatan,
                "score": score,
                "participant_count": attendee_count,
                "event_count": event_count,
                "reason": reason,
                # Optional: return stats for debugging if needed, but keeping schema clean for now
            })

        # Sort by score desc
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:15]
