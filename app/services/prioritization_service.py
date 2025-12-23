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
        
        results = []
        for kecamatan in all_kecamatans:
            event_count = event_map.get(kecamatan, 0)
            attendee_count = attendee_map.get(kecamatan, 0)
            
            # Logic: 
            # - High events (> 5) -> "Sering dikunjungi" (Flag as observation)
            # - Low events (< 2) -> "Perlu perhatian" (Priority)
            # - High events but Low attendees -> "Inefektif"
            
            score = 0
            reason = ""
            
            if event_count > 5:
                score = 10 # High score implies "Attention needed" or just "Top list"?
                # Request was: "munculkan juga daerah yang terlalu sering dikunjungi"
                # If we want to verify "frequency", we can say high score but reason is "High Frequency"
                # Let's start with a base score.
                # Usually Prioritization means "Where should I go next?". 
                # If it's visited too often, maybe priority is LOW to go again? 
                # BUT user wants it SHOWN.
                # Let's map score to "Interest Level".
                
                # Let's invert: 
                # Priority is normally for "Missing" areas.
                # But let's follow the frontend logic which probably sorts by score desc.
                # If I want to show "Too often", I can give it a distinct score or reason.
                pass
            
            # Simple Scoring for MVP SABADESA
            # We want to surface:
            # 1. Areas with Very High activity (Observation)
            # 2. Areas with Low activity (Action needed)
            
            if event_count == 0:
                 # Won't be in this loop unless in attendee_map (unlikely if no events)
                 # We need a master list of Kecamatans to show true zeros, but omitting for now.
                 pass
            elif event_count < 3:
                score = 80
                reason = "Kegiatan masih minim, perlu ditingkatkan"
            elif event_count > 8:
                score = 90
                reason = "Frekuensi kunjungan sangat tinggi (Over-visited)"
            elif attendee_count < 50 and event_count > 3:
                score = 70
                reason = "Kegiatan cukup tapi partisipan rendah (Evaluasi)"
            else:
                score = 40
                reason = "Kondisi kegiatan terpantau stabil"

            results.append({
                "kecamatan": kecamatan,
                "score": score,
                "participant_count": attendee_count, # Replaces actual_votes
                "event_count": event_count,
                "reason": reason
            })

        # Sort by score desc to show important ones first (High freq or Low freq)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:15]
