from fastapi import APIRouter, Depends
from typing import List, Dict, Any, Optional
from ..deps import get_analytics_service, get_current_user
from ..services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/global")
def get_global_stats(dapil: Optional[str] = None, kecamatan: Optional[str] = None, source: Optional[str] = 'all', svc: AnalyticsService = Depends(get_analytics_service), user = Depends(get_current_user)):
    return svc.get_global_stats(dapil=dapil, kecamatan=kecamatan, source=source)

@router.get("/votes/summary")
def get_votes_summary(dapil: Optional[str] = None, kecamatan: Optional[str] = None, source: Optional[str] = 'all', svc: AnalyticsService = Depends(get_analytics_service), user = Depends(get_current_user)):
    return svc.get_votes_summary(dapil=dapil, kecamatan=kecamatan, source=source)

@router.get("/heatmap")
def get_heatmap_data(dapil: Optional[str] = None, kecamatan: Optional[str] = None, source: Optional[str] = 'all', svc: AnalyticsService = Depends(get_analytics_service), user = Depends(get_current_user)):
    return svc.get_heatmap_data(dapil=dapil, kecamatan=kecamatan, source=source)

@router.get("/engagement/trends")
def get_engagement_trends(svc: AnalyticsService = Depends(get_analytics_service), user = Depends(get_current_user)):
    return svc.get_engagement_trends()

@router.get("/activities/distribution")
def get_activity_distribution(svc: AnalyticsService = Depends(get_analytics_service), user = Depends(get_current_user)):
    return svc.get_activity_distribution()


